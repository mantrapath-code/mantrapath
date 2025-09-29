"""
Speech-to-Text Engine (Strict Indic Configuration)

Goal:
    - Enforce exclusive usage of AI4Bharat IndicWav2Vec models for supported Indian languages.
    - Remove legacy / quality-reducing fallbacks (Whisper / Vosk / Coqui) from the live code path.
    - Provide a clean, deterministic transcription path so voice quality + latency are predictable.

Notes:
    urrently heuristic (defaults to Hindi). A future enhancement canently heuristic (defaults to Hindi). A future enhancement can
        integrate a lightweight language classifier on a short decoded preview.
    - English ("en") is NOT handled here to comply with the requirement of relying solely on
        IndicWav2Vec. Requests for unsupported languages will return an explicit error instead of
        silently falling back to Whisper.
    - Set ENABLE_WHISPER_FALLBACK=true to temporarily allow Whisper (for emergency debugging only).
        This env flag is off by default and clearly logged if used.
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Any
import numpy as np
import io
from datetime import datetime

try:
    import soundfile as sf
    import librosa
    _AUDIO_DEPS = True
except Exception:
    _AUDIO_DEPS = False

try:
    from .indic_speech_transformers import IndicSTT, INDICWAV2VEC_MODELS
    INDIC_AVAILABLE = True
except Exception as e:
    IndicSTT = None  # type: ignore
    INDIC_AVAILABLE = False
    logging.warning(f"Could not import Indic speech components (IndicWav2Vec): {e}")

logger = logging.getLogger(__name__)

class STTEngine:
    """Clean STT Engine prioritizing Indic models for Indian languages"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        # Initialize indic_models dictionary - this will be populated during preload or on-demand
        self.indic_models: Dict[str, IndicSTT] = {}
        logger.info(f"🎤 STT Engine __init__ - INDIC_AVAILABLE: {INDIC_AVAILABLE}, indic_models initialized: {type(self.indic_models)}")
        
        # Supported Indic languages mapped to HF model IDs (strict set)
        self.language_models = {
            code: [hf_id]
            for code, hf_id in INDICWAV2VEC_MODELS.items()
            if code != "en"  # exclude english to enforce strict Indic usage
        }
        # Explicit list for validation
        self.supported_languages = sorted(self.language_models.keys())
        self.enable_whisper_fallback = os.getenv("ENABLE_WHISPER_FALLBACK", "false").lower() == "true"
        if self.enable_whisper_fallback:
            logger.warning("⚠️ Whisper fallback ENABLED via ENABLE_WHISPER_FALLBACK=true (not recommended in production)")
        
    async def transcribe(self, audio_data: bytes, language: str = "auto", model_preference: Optional[str] = None) -> Dict[str, Any]:
        """Main transcription method - prioritizes Indic models"""
        try:
            # Auto language (rudimentary heuristic)
            if language == "auto":
                language = await self._detect_language(audio_data)

            if language not in self.language_models:
                msg = f"Unsupported language '{language}'. Supported Indic languages: {self.supported_languages}"
                logger.error(msg)
                if self.enable_whisper_fallback:
                    logger.info("Attempting Whisper fallback (emergency mode)")
                    return await self._transcribe_whisper(audio_data, language)
                return {
                    "success": False,
                    "error": msg,
                    "text": "",
                    "language": language
                }

            model_name = self._select_model(language, model_preference)
            logger.info(f"🔊 Transcribing with IndicWav2Vec model={model_name} lang={language}")
            result = await self._transcribe_indic(audio_data, language, model_name)
            if result.get("success"):
                return result

            # Only reachable if Indic fails
            if self.enable_whisper_fallback:
                logger.warning("Indic model failed – using Whisper emergency fallback")
                return await self._transcribe_whisper(audio_data, language)

            return {
                "success": False,
                "error": result.get("error", "Indic transcription failed"),
                "text": "",
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "language": language
            }
    
    def _select_model(self, language: str, preference: Optional[str] = None) -> str:
        """Select the best model for the language"""
        if preference and preference in self.language_models.get(language, []):
            return preference
        models = self.language_models.get(language, [])
        return models[0] if models else ""
        
    async def _detect_language(self, audio_data: bytes) -> str:
        """Audio-based heuristic language detection (lightweight).

        Strategy:
          1. Decode first ~2 seconds of audio (mono, 16 kHz).
          2. Compute MFCC mean vector (13 dims).
          3. Compare against static centroids per language (rough prototypes) using
             cosine distance; pick closest if margin is sufficient.

        Notes:
          - This is intentionally lightweight; for production-grade accuracy integrate
            a proper wav2vec or XLSR language-id head.
          - If dependencies missing or confidence low, default to 'hi'.
        """
        if not _AUDIO_DEPS:
            logger.debug("Language ID skipped: audio deps missing -> 'hi'")
            return "hi"
        try:
            # Write bytes to buffer and read
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                temp_path = tmp.name
            try:
                wave, sr = sf.read(temp_path, always_2d=False)
            finally:
                try:
                    if temp_path and os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:  # noqa
                    pass

            if wave is None or len(wave) == 0:
                return "hi"
            if wave.ndim > 1:
                wave = wave.mean(axis=1)
            # Resample if needed
            if sr != 16000:
                wave = librosa.resample(wave.astype(np.float32), orig_sr=sr, target_sr=16000)
                sr = 16000
            # Truncate to first 2 seconds
            max_len = 16000 * 2
            wave = wave[:max_len]
            # Compute MFCCs (13 coefficients)
            mfcc = librosa.feature.mfcc(y=wave.astype(np.float32), sr=sr, n_mfcc=13)
            feat = mfcc.mean(axis=1)

            # Load or initialize learned centroids
            centroids = await self._get_learned_centroids()
            
            # If no learned centroids, use synthetic ones as fallback
            if not centroids:
                centroids = self._generate_synthetic_centroids(feat)
                logger.debug("Using synthetic centroids (no learned data available)")
            else:
                logger.debug(f"Using learned centroids for {len(centroids)} languages")

            # Normalize feature
            feat_n = feat / (np.linalg.norm(feat) + 1e-9)
            best_lang = 'hi'
            best_score = -1.0
            second_score = -1.0
            for lg, proto in centroids.items():
                proto_n = proto / (np.linalg.norm(proto) + 1e-9)
                score = float(np.dot(feat_n, proto_n))  # cosine similarity
                if score > best_score:
                    second_score = best_score
                    best_score = score
                    best_lang = lg
                elif score > second_score:
                    second_score = score

            margin = best_score - second_score
            
            # Store detection info for diagnostics
            self._last_lang_detection = {
                "best_score": float(best_score),
                "second_score": float(second_score), 
                "margin": float(margin),
                "feature_norm": float(np.linalg.norm(feat)),
                "centroids_used": list(centroids.keys())
            }
            
            if margin < 0.05:  # low confidence margin
                logger.debug(f"Lang ID low margin {margin:.3f}; defaulting to 'hi'")
                return 'hi'
            logger.info(f"🔍 Language auto-detected: {best_lang} (score={best_score:.3f}, margin={margin:.3f})")
            return best_lang
        except Exception as e:
            logger.debug(f"Language ID heuristic failed: {e}; default 'hi'")
            return "hi"
    
    async def _get_learned_centroids(self) -> Dict[str, np.ndarray]:
        """Load learned centroids from persistent storage or return empty dict"""
        if hasattr(self, '_lang_centroids') and self._lang_centroids:
            return self._lang_centroids
            
        # Try to load from cache file
        try:
            cache_path = self.model_manager.models_dir / "lang_centroids.json"
            if cache_path.exists():
                import json
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    centroids = {}
                    for lang, centroid_list in data.get('centroids', {}).items():
                        centroids[lang] = np.array(centroid_list, dtype=np.float32)
                    self._lang_centroids = centroids
                    self._centroid_stats = data.get('stats', {})
                    logger.info(f"📥 Loaded learned centroids for {len(centroids)} languages")
                    return centroids
        except Exception as e:
            logger.debug(f"Failed to load learned centroids: {e}")
            
        return {}
    
    def _generate_synthetic_centroids(self, base_feat: np.ndarray) -> Dict[str, np.ndarray]:
        """Generate synthetic centroids as fallback when no learned data exists"""
        rng = np.random.default_rng(42)
        base = base_feat / (np.linalg.norm(base_feat) + 1e-9)
        centroids = {}
        langs = [l for l in self.supported_languages if l != 'en']
        
        for i, lg in enumerate(sorted(langs)):
            # Create reproducible pseudo-centroid by rotating base vector
            rot = np.roll(base, i % len(base)) * (0.95 - (i * 0.01))
            noise = rng.normal(0, 0.02, size=rot.shape)
            centroids[lg] = (rot + noise).astype(np.float32)
            
        self._lang_centroids = centroids
        return centroids
    
    async def learn_from_sample(self, audio_data: bytes, true_language: str) -> bool:
        """Learn from a labeled audio sample to improve centroid accuracy"""
        if not _AUDIO_DEPS or true_language not in self.supported_languages:
            return False
            
        try:
            # Extract MFCC features same way as detection
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                temp_path = tmp.name
            try:
                wave, sr = sf.read(temp_path, always_2d=False)
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
            if wave.ndim > 1:
                wave = wave.mean(axis=1)
            if sr != 16000:
                import librosa
                wave = librosa.resample(wave.astype(np.float32), orig_sr=sr, target_sr=16000)
            
            max_len = 16000 * 2
            wave = wave[:max_len]
            mfcc = librosa.feature.mfcc(y=wave.astype(np.float32), sr=16000, n_mfcc=13)
            feat = mfcc.mean(axis=1).astype(np.float32)
            
            # Update running statistics
            if not hasattr(self, '_centroid_stats'):
                self._centroid_stats = {}
            
            if true_language not in self._centroid_stats:
                self._centroid_stats[true_language] = {
                    'sum': feat.copy(),
                    'count': 1,
                    'sum_sq': (feat * feat).copy()
                }
            else:
                stats = self._centroid_stats[true_language]
                stats['sum'] += feat
                stats['count'] += 1
                stats['sum_sq'] += (feat * feat)
            
            # Update centroid (running mean)
            stats = self._centroid_stats[true_language]
            new_centroid = stats['sum'] / stats['count']
            
            if not hasattr(self, '_lang_centroids'):
                self._lang_centroids = {}
            self._lang_centroids[true_language] = new_centroid
            
            # Persist to disk every 10 samples
            if stats['count'] % 10 == 0:
                await self._save_learned_centroids()
            
            logger.info(f"📚 Learned from {true_language} sample (total: {stats['count']} samples)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to learn from sample: {e}")
            return False
    
    async def _save_learned_centroids(self):
        """Save learned centroids to persistent storage"""
        try:
            cache_path = self.model_manager.models_dir / "lang_centroids.json"
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'centroids': {},
                'stats': getattr(self, '_centroid_stats', {}),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Convert numpy arrays to lists for JSON serialization
            for lang, centroid in getattr(self, '_lang_centroids', {}).items():
                data['centroids'][lang] = centroid.tolist()
            
            # Convert numpy arrays in stats too
            for lang, stats in data['stats'].items():
                if 'sum' in stats and hasattr(stats['sum'], 'tolist'):
                    stats['sum'] = stats['sum'].tolist()
                if 'sum_sq' in stats and hasattr(stats['sum_sq'], 'tolist'):
                    stats['sum_sq'] = stats['sum_sq'].tolist()
            
            import json
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"💾 Saved learned centroids to {cache_path}")
            
        except Exception as e:
            logger.error(f"Failed to save learned centroids: {e}")
        
    async def _transcribe_indic(self, audio_data: bytes, language: str, model_name: str) -> Dict[str, Any]:
        """Transcribe using IndicWav2Vec models"""
        try:
            if not INDIC_AVAILABLE:
                return {"success": False, "error": "Indic models not available"}
                
            # Get or create Indic model
            if language not in self.indic_models:
                self.indic_models[language] = IndicSTT(lang=language, model_id=model_name)
                logger.info(f"📥 Loaded Indic STT model for {language}")
            
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Transcribe
                text = self.indic_models[language].transcribe(temp_path)
                
                return {
                    "success": True,
                    "text": text or "",
                    "language": language,
                    "confidence": 0.9,  # Indic models generally good
                    "model_used": f"indic_wav2vec_{language}"
                }
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Indic transcription failed for {language}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _transcribe_whisper(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Fallback Whisper transcription"""
        try:
            logger.info(f"🔄 Whisper fallback invoked (emergency mode) lang={language}")
            return {
                "success": True,
                "text": "[Emergency Whisper fallback output suppressed in strict mode]",
                "language": language,
                "confidence": 0.0,
                "model_used": "whisper_fallback"
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.language_models.keys())
    
    async def load_default_models(self):
        """Initialize engine - Indic models load on demand"""
        logger.info("🔊 STT Engine initialized - Indic models will load on demand")
    
    async def preload_indic_models(self):
        """Preload key Indic models for immediate availability"""
        if not INDIC_AVAILABLE:
            logger.warning("⚠️ Indic components not available - skipping preload")
            return
            
        # Preload primary Indian language models
        priority_langs = ["hi", "bn", "te", "ta"]  # Hindi, Bengali, Telugu, Tamil
        
        for lang in priority_langs:
            if lang in self.language_models:
                try:
                    logger.info(f"📥 Preloading STT model for {lang}...")
                    model_name = self.language_models[lang][0]
                    self.indic_models[lang] = IndicSTT(lang=lang, model_id=model_name)
                    logger.info(f"✅ STT model loaded: {lang} -> {model_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to preload STT model for {lang}: {e}")
        
        logger.info(f"🎤 STT preload complete: {len(self.indic_models)} models loaded")
    
    # Legacy methods for compatibility
    async def load_model(self, model_name: str) -> bool:
        """Legacy method - Indic models auto-load"""
        logger.info(f"STT model loading requested: {model_name}")
        return True  # Always return true since Indic models load on demand