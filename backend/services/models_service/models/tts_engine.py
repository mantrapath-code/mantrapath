"""
Text-to-Speech Engine (Indic + MMS)

Enhancements in this revision:
    - Replace placeholder sine-wave MMS fallback with real Meta MMS-TTS generation via
        Hugging Face Transformers pipeline (through IndicTTS wrapper with engine='mms').
    - Add lightweight audio post-processing (normalization + fade) for more natural sound.
    - Enforce removal of legacy Coqui / eSpeak / Festival usage in the live path.

The engine attempts Indic-TTS (ai4bharat) first where available, otherwise directly
uses MMS. Both paths unify on the same output shaping so downstream services receive
consistent WAV bytes + metadata.
"""

import asyncio
import logging
import os
import tempfile
import io
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import soundfile as sf

try:
    from .indic_speech_transformers import IndicTTS, LANG2ISO3
    INDIC_AVAILABLE = True
except Exception as e:
    IndicTTS = None  # type: ignore
    INDIC_AVAILABLE = False
    logging.warning(f"Could not import Indic / MMS TTS components: {e}")

logger = logging.getLogger(__name__)

class TTSEngine:
    """Clean TTS Engine prioritizing Indic models for Indian languages"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        # Initialize indic_models dictionary - this will be populated during preload or on-demand
        self.indic_models: Dict[str, IndicTTS] = {}
        logger.info(f"🔊 TTS Engine __init__ - INDIC_AVAILABLE: {INDIC_AVAILABLE}, indic_models initialized: {type(self.indic_models)}")
        
        # Language mapping: Indic models FIRST, MMS as fallback
        self.language_models = {
            # Indian languages - use Indic-TTS
            "hi": ["indic_tts_hi", "facebook/mms-tts-hin"],
            "bn": ["indic_tts_bn", "facebook/mms-tts-ben"], 
            "te": ["indic_tts_te", "facebook/mms-tts-tel"],
            "ta": ["indic_tts_ta", "facebook/mms-tts-tam"],
            "mr": ["indic_tts_mr", "facebook/mms-tts-mar"],
            "gu": ["indic_tts_gu", "facebook/mms-tts-guj"],
            "kn": ["indic_tts_kn", "facebook/mms-tts-kan"],
            "ml": ["indic_tts_ml", "facebook/mms-tts-mal"],
            "pa": ["indic_tts_pa", "facebook/mms-tts-pan"],
            "or": ["indic_tts_or", "facebook/mms-tts-ori"],
            "as": ["indic_tts_as", "facebook/mms-tts-asm"],
            # English and others - MMS primary
            "en": ["facebook/mms-tts-eng"],
            "auto": ["facebook/mms-tts-eng"]  # Auto-detection defaults to English
        }
    
    async def load_default_models(self):
        """Load default TTS models (Hindi Indic-TTS and MMS)"""
        logger.info("🔊 TTS Engine: Loading default models...")
        
        try:
            # Load default Hindi models
            default_lang = "hi"  # Hindi
            if default_lang in self.language_models:
                logger.info(f"🔊 TTS Engine: Loading default {default_lang} models...")
                
                # Load MMS-TTS first (preferred - more reliable than AI4Bharat Indic-TTS)
                if INDIC_AVAILABLE and default_lang not in self.indic_models:
                    self.indic_models[default_lang] = IndicTTS(lang=default_lang, engine="mms")
                    logger.info(f"✅ TTS Engine: Loaded {default_lang} MMS-TTS model")
                
                # Also load MMS as fallback
                mms_key = f"{default_lang}_mms"
                if mms_key not in self.indic_models:
                    self.indic_models[mms_key] = IndicTTS(lang=default_lang, engine="mms")
                    logger.info(f"✅ TTS Engine: Loaded {default_lang} MMS-TTS model")
                
                logger.info("✅ TTS Engine: Default Hindi models loaded successfully")
                return True
            else:
                logger.warning(f"⚠️ TTS Engine: Default language {default_lang} not in supported languages")
                return False
        except Exception as e:
            logger.error(f"❌ TTS Engine: Failed to load default models: {e}")
            return False
        
    async def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None, model_preference: Optional[str] = None) -> Dict[str, Any]:
        """Main synthesis method - prioritizes Indic models"""
        try:
            logger.info(f"🔊 Synthesizing TTS for language: {language}, text: {text[:50]}...")
            
            # Get the best model for this language
            model_name = self._select_model(language, model_preference)
            
            # Use Indic model if available
            if model_name and "indic_tts" in model_name:
                result = await self._synthesize_indic(text, language, voice)
                if result.get("success"):
                    return result
                logger.warning("⚠️ Indic model failed – switching to MMS")

            return await self._synthesize_mms(text, language)
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_data": None
            }
    
    def _select_model(self, language: str, preference: Optional[str] = None) -> str:
        """Select the best model for the language"""
        if preference and preference in self.language_models.get(language, []):
            return preference
        models = self.language_models.get(language, []) or self.language_models.get("en", [])
        return models[0] if models else "facebook/mms-tts-eng"
        
    async def _synthesize_indic(self, text: str, language: str, voice: Optional[str] = None) -> Dict[str, Any]:
        """Synthesize using Indic-TTS models"""
        try:
            if not INDIC_AVAILABLE:
                return {"success": False, "error": "Indic models not available"}

            if language not in self.indic_models:
                self.indic_models[language] = IndicTTS(lang=language, engine="mms")
                logger.info(f"📥 Loaded MMS-TTS model for {language}")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                out_path = self.indic_models[language].speak(text, out_path=tmp.name)
                logger.info(f"🔊 IndicTTS speak returned path: '{out_path}'")
                
                # Check if file was actually created
                if not out_path or not os.path.exists(out_path):
                    logger.error(f"❌ TTS file not created: path='{out_path}', exists={os.path.exists(out_path) if out_path else False}")
                    return {"success": False, "error": f"TTS file not created: {out_path}"}
                
                # Check file size
                file_size = os.path.getsize(out_path)
                logger.info(f"🔊 TTS file size: {file_size} bytes")
                if file_size == 0:
                    return {"success": False, "error": "TTS generated empty file"}

            # Read & enhance
            audio_np, sr = sf.read(out_path)
            audio_np = self._post_process(audio_np, sr)
            audio_bytes = self._to_wav_bytes(audio_np, sr)

            duration = len(audio_np) / sr
            return {
                "success": True,
                "audio_data": audio_bytes,
                "sample_rate": sr,
                "duration": duration,
                "model_used": f"indic_tts_{language}"
            }
        except Exception as e:
            logger.error(f"Indic TTS synthesis failed for {language}: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if 'out_path' in locals() and out_path and os.path.exists(out_path):
                try:
                    os.unlink(out_path)
                except:  # noqa
                    pass
    
    async def _synthesize_mms(self, text: str, language: str) -> Dict[str, Any]:
        """MMS TTS synthesis using Transformers pipeline (via IndicTTS engine='mms')."""
        try:
            if not INDIC_AVAILABLE:
                return {"success": False, "error": "MMS components not available"}

            if language not in self.indic_models or not isinstance(self.indic_models[language], IndicTTS):
                self.indic_models[language] = IndicTTS(lang=language, engine="mms")
                logger.info(f"📥 Loaded MMS TTS model for {language}")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                out_path = self.indic_models[language].speak(text, out_path=tmp.name)
                logger.info(f"🔊 MMS TTS speak returned path: '{out_path}'")
                
                # Check if file was actually created
                if not out_path or not os.path.exists(out_path):
                    logger.error(f"❌ MMS TTS file not created: path='{out_path}', exists={os.path.exists(out_path) if out_path else False}")
                    return {"success": False, "error": f"MMS TTS file not created: {out_path}"}
                
                # Check file size
                file_size = os.path.getsize(out_path)
                logger.info(f"🔊 MMS TTS file size: {file_size} bytes")
                if file_size == 0:
                    return {"success": False, "error": "MMS TTS generated empty file"}

            audio_np, sr = sf.read(out_path)
            audio_np = self._post_process(audio_np, sr)
            audio_bytes = self._to_wav_bytes(audio_np, sr)
            duration = len(audio_np) / sr

            return {
                "success": True,
                "audio_data": audio_bytes,
                "sample_rate": sr,
                "duration": duration,
                "model_used": f"mms_tts_{language}",
            }
        except Exception as e:
            logger.error(f"MMS TTS synthesis failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if 'out_path' in locals() and out_path and os.path.exists(out_path):
                try:
                    os.unlink(out_path)
                except:  # noqa
                    pass

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.language_models.keys())
    
    async def load_default_models(self):
        """Initialize engine - Indic models load on demand"""
        logger.info("🔊 TTS Engine initialized - Indic models will load on demand")
    
    async def preload_indic_models(self):
        """Preload key Indic models for immediate availability"""
        if not INDIC_AVAILABLE:
            logger.warning("⚠️ Indic components not available - skipping preload")
            return
            
        # Preload primary Indian language models using MMS engine
        priority_langs = ["hi", "bn", "te", "ta"]  # Hindi, Bengali, Telugu, Tamil
        
        for lang in priority_langs:
            try:
                logger.info(f"📥 Preloading TTS model for {lang}...")
                # Use MMS engine directly for reliable loading
                self.indic_models[lang] = IndicTTS(lang=lang, engine="mms")
                logger.info(f"✅ TTS model loaded: {lang} -> MMS")
            except Exception as e:
                logger.error(f"❌ Failed to preload TTS model for {lang}: {e}")
        
        logger.info(f"🔊 TTS preload complete: {len(self.indic_models)} models loaded")
    
    # Legacy methods for compatibility
    async def load_model(self, model_name: str) -> bool:
        """Legacy method - Indic models auto-load"""
        logger.info(f"TTS model loading requested: {model_name}")
        return True  # Always return true since Indic models load on demand
    
    async def clone_voice(self, reference_audio: bytes, text: str, language: str = "en") -> Dict[str, Any]:
        """Voice cloning - simplified implementation"""
        logger.info("🎭 Voice cloning requested - using standard voice for now")
        return await self.synthesize(text, language)

    # ------------------------------------------------------------------
    # Audio helpers
    # ------------------------------------------------------------------
    def _post_process(self, audio: Any, sr: int) -> np.ndarray:
        """Apply simple normalization & gentle fade to reduce clicks."""
        try:
            audio_np = np.asarray(audio, dtype=np.float32)
            if audio_np.ndim > 1:
                audio_np = audio_np.mean(axis=1)
            # Normalize
            peak = np.max(np.abs(audio_np)) or 1.0
            audio_np = audio_np / peak * 0.97
            # 5 ms fade in/out
            fade_len = int(sr * 0.005)
            if fade_len > 10 and fade_len * 2 < len(audio_np):
                fade_in = np.linspace(0.0, 1.0, fade_len)
                fade_out = np.linspace(1.0, 0.0, fade_len)
                audio_np[:fade_len] *= fade_in
                audio_np[-fade_len:] *= fade_out
            return audio_np
        except Exception as e:
            logger.debug(f"Post-process failed: {e}")
            return np.asarray(audio, dtype=np.float32)

    def _to_wav_bytes(self, audio_np: np.ndarray, sr: int) -> bytes:
        buf = io.BytesIO()
        sf.write(buf, audio_np, sr, format='WAV')
        return buf.getvalue()

    async def load_default_models(self) -> bool:
        """Load default TTS models for enhanced voice stack"""
        try:
            logger.info("🔊 Loading default TTS models...")
            
            if not INDIC_AVAILABLE:
                logger.warning("⚠️ Indic TTS components not available")
                return False
            
            # Load Hindi model as default (most commonly used)
            default_language = "hi"
            if default_language in self.language_models:
                logger.info(f"📥 Loading default TTS model for {default_language}")
                self.indic_models[default_language] = IndicTTS(lang=default_language, engine="mms")
                logger.info(f"✅ Default TTS model loaded: {default_language}")
                return True
            else:
                logger.warning(f"⚠️ Default language {default_language} not found in available models")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load default TTS models: {e}")
            return False