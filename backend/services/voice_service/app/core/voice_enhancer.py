"""
Voice Enhancer
Handles voice quality improvement, noise reduction, and audio processing
"""
import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import io

logger = logging.getLogger(__name__)

@dataclass
class AudioMetrics:
    """Audio quality metrics"""
    sample_rate: int
    duration: float
    channels: int
    bit_depth: int
    noise_level: float
    signal_strength: float
    snr_ratio: float  # Signal-to-noise ratio

@dataclass
class EnhancementResult:
    """Voice enhancement result"""
    enhanced_audio: bytes
    original_metrics: AudioMetrics
    enhanced_metrics: AudioMetrics
    enhancements_applied: list
    improvement_score: float
    processing_time: float

class VoiceEnhancer:
    """Voice quality enhancement and audio processing"""
    
    def __init__(self):
        self.enhancement_settings = {
            "noise_reduction": True,
            "volume_normalization": True,
            "quality_enhancement": True,
            "format_standardization": True
        }
        
        self.target_sample_rate = 16000  # Standard for voice processing
        self.target_bit_depth = 16
        self.noise_threshold = 0.02
        self.volume_target = 0.7
        
    def enhance_audio(self, audio_data: bytes, content_type: str = "audio/wav") -> EnhancementResult:
        """Main audio enhancement function"""
        import time
        start_time = time.time()
        
        try:
            # Parse audio data
            audio_array, sample_rate = self._parse_audio(audio_data, content_type)
            original_metrics = self._analyze_audio(audio_array, sample_rate)
            
            # Apply enhancements
            enhanced_array = audio_array.copy()
            enhancements_applied = []
            
            # 1. Noise reduction
            if self.enhancement_settings["noise_reduction"]:
                enhanced_array = self._reduce_noise(enhanced_array)
                enhancements_applied.append("noise_reduction")
            
            # 2. Volume normalization
            if self.enhancement_settings["volume_normalization"]:
                enhanced_array = self._normalize_volume(enhanced_array)
                enhancements_applied.append("volume_normalization")
            
            # 3. Quality enhancement
            if self.enhancement_settings["quality_enhancement"]:
                enhanced_array = self._enhance_quality(enhanced_array)
                enhancements_applied.append("quality_enhancement")
            
            # 4. Format standardization
            if self.enhancement_settings["format_standardization"]:
                enhanced_array, sample_rate = self._standardize_format(enhanced_array, sample_rate)
                enhancements_applied.append("format_standardization")
            
            # Convert back to bytes
            enhanced_audio_bytes = self._array_to_bytes(enhanced_array, sample_rate)
            enhanced_metrics = self._analyze_audio(enhanced_array, sample_rate)
            
            # Calculate improvement score
            improvement_score = self._calculate_improvement(original_metrics, enhanced_metrics)
            
            processing_time = time.time() - start_time
            
            return EnhancementResult(
                enhanced_audio=enhanced_audio_bytes,
                original_metrics=original_metrics,
                enhanced_metrics=enhanced_metrics,
                enhancements_applied=enhancements_applied,
                improvement_score=improvement_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {e}")
            # Return original audio with basic metrics
            processing_time = time.time() - start_time
            basic_metrics = AudioMetrics(
                sample_rate=22050,  # Default
                duration=0.0,
                channels=1,
                bit_depth=16,
                noise_level=0.0,
                signal_strength=0.0,
                snr_ratio=0.0
            )
            
            return EnhancementResult(
                enhanced_audio=audio_data,
                original_metrics=basic_metrics,
                enhanced_metrics=basic_metrics,
                enhancements_applied=["error_fallback"],
                improvement_score=0.0,
                processing_time=processing_time
            )
    
    def _parse_audio(self, audio_data: bytes, content_type: str) -> Tuple[np.ndarray, int]:
        """Parse audio data into numpy array"""
        try:
            import librosa
            
            # Use librosa to load audio from bytes
            audio_array, sample_rate = librosa.load(
                io.BytesIO(audio_data), 
                sr=None,  # Keep original sample rate
                mono=True  # Convert to mono
            )
            
            return audio_array, sample_rate
            
        except ImportError:
            logger.warning("librosa not available, using basic audio parsing")
            return self._basic_audio_parse(audio_data)
        except Exception as e:
            logger.warning(f"Audio parsing failed, using fallback: {e}")
            return self._basic_audio_parse(audio_data)
    
    def _basic_audio_parse(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """Basic audio parsing fallback"""
        # Simple WAV parsing for fallback
        # This is a very basic implementation
        try:
            # Skip WAV header (44 bytes) and convert to numpy array
            if len(audio_data) > 44:
                audio_bytes = audio_data[44:]  # Skip WAV header
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                # Normalize to float
                audio_array = audio_array.astype(np.float32) / 32768.0
                return audio_array, 16000  # Default sample rate
            else:
                # Create silence for very short audio
                return np.zeros(1600, dtype=np.float32), 16000
        except Exception:
            # Ultimate fallback
            return np.zeros(1600, dtype=np.float32), 16000
    
    def _analyze_audio(self, audio_array: np.ndarray, sample_rate: int) -> AudioMetrics:
        """Analyze audio quality metrics"""
        try:
            duration = len(audio_array) / sample_rate
            channels = 1  # We convert to mono
            bit_depth = 16  # Standard
            
            # Calculate signal strength (RMS)
            signal_strength = np.sqrt(np.mean(audio_array ** 2))
            
            # Estimate noise level (using quieter portions)
            sorted_audio = np.sort(np.abs(audio_array))
            noise_level = np.mean(sorted_audio[:len(sorted_audio)//10])  # Bottom 10%
            
            # Calculate SNR
            if noise_level > 0:
                snr_ratio = 20 * np.log10(signal_strength / noise_level)
            else:
                snr_ratio = 60.0  # Very high SNR if no noise detected
            
            return AudioMetrics(
                sample_rate=sample_rate,
                duration=duration,
                channels=channels,
                bit_depth=bit_depth,
                noise_level=float(noise_level),
                signal_strength=float(signal_strength),
                snr_ratio=float(snr_ratio)
            )
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return AudioMetrics(
                sample_rate=sample_rate,
                duration=0.0,
                channels=1,
                bit_depth=16,
                noise_level=0.0,
                signal_strength=0.0,
                snr_ratio=0.0
            )
    
    def _reduce_noise(self, audio_array: np.ndarray) -> np.ndarray:
        """Simple noise reduction"""
        try:
            # Simple spectral gating noise reduction
            # This is a basic implementation
            
            # Calculate RMS in windows
            window_size = 1024
            threshold_factor = 0.1
            
            enhanced = audio_array.copy()
            
            for i in range(0, len(audio_array) - window_size, window_size):
                window = audio_array[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                
                # If RMS is below threshold, reduce amplitude
                if rms < threshold_factor * np.sqrt(np.mean(audio_array ** 2)):
                    enhanced[i:i + window_size] *= 0.1
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            return audio_array
    
    def _normalize_volume(self, audio_array: np.ndarray) -> np.ndarray:
        """Normalize audio volume"""
        try:
            # Normalize to target volume
            current_max = np.max(np.abs(audio_array))
            
            if current_max > 0:
                normalization_factor = self.volume_target / current_max
                return audio_array * normalization_factor
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Volume normalization failed: {e}")
            return audio_array
    
    def _enhance_quality(self, audio_array: np.ndarray) -> np.ndarray:
        """Enhance audio quality"""
        try:
            # Simple quality enhancement using smoothing
            # Apply a light smoothing filter to reduce artifacts
            
            from scipy import signal
            
            # Design a low-pass filter to remove high-frequency noise
            nyquist = 0.5 * 16000  # Assuming 16kHz sample rate
            cutoff = 8000  # 8kHz cutoff
            normalized_cutoff = cutoff / nyquist
            
            b, a = signal.butter(4, normalized_cutoff, btype='low')
            enhanced = signal.filtfilt(b, a, audio_array)
            
            return enhanced
            
        except ImportError:
            logger.warning("scipy not available for quality enhancement")
            return audio_array
        except Exception as e:
            logger.error(f"Quality enhancement failed: {e}")
            return audio_array
    
    def _standardize_format(self, audio_array: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, int]:
        """Standardize audio format"""
        try:
            # Resample to target sample rate if needed
            if sample_rate != self.target_sample_rate:
                try:
                    import librosa
                    resampled = librosa.resample(
                        audio_array, 
                        orig_sr=sample_rate, 
                        target_sr=self.target_sample_rate
                    )
                    return resampled, self.target_sample_rate
                except ImportError:
                    logger.warning("librosa not available for resampling")
                    return audio_array, sample_rate
            
            return audio_array, sample_rate
            
        except Exception as e:
            logger.error(f"Format standardization failed: {e}")
            return audio_array, sample_rate
    
    def _array_to_bytes(self, audio_array: np.ndarray, sample_rate: int) -> bytes:
        """Convert numpy array back to bytes"""
        try:
            # Convert to 16-bit integers
            audio_int16 = (audio_array * 32767).astype(np.int16)
            
            # Create WAV header
            wav_header = self._create_wav_header(len(audio_int16), sample_rate)
            
            # Combine header and data
            return wav_header + audio_int16.tobytes()
            
        except Exception as e:
            logger.error(f"Array to bytes conversion failed: {e}")
            return b""
    
    def _create_wav_header(self, data_length: int, sample_rate: int) -> bytes:
        """Create WAV file header"""
        try:
            import struct
            
            # WAV header format
            chunk_id = b'RIFF'
            chunk_size = 36 + data_length * 2  # 2 bytes per sample
            format_type = b'WAVE'
            subchunk1_id = b'fmt '
            subchunk1_size = 16
            audio_format = 1  # PCM
            num_channels = 1
            byte_rate = sample_rate * num_channels * 2  # 2 bytes per sample
            block_align = num_channels * 2
            bits_per_sample = 16
            subchunk2_id = b'data'
            subchunk2_size = data_length * 2
            
            header = struct.pack('<4sI4s4sIHHIIHH4sI',
                               chunk_id, chunk_size, format_type,
                               subchunk1_id, subchunk1_size, audio_format,
                               num_channels, sample_rate, byte_rate,
                               block_align, bits_per_sample,
                               subchunk2_id, subchunk2_size)
            
            return header
            
        except Exception as e:
            logger.error(f"WAV header creation failed: {e}")
            return b""
    
    def _calculate_improvement(self, original: AudioMetrics, enhanced: AudioMetrics) -> float:
        """Calculate improvement score (0-1)"""
        try:
            improvements = []
            
            # SNR improvement
            if original.snr_ratio > 0:
                snr_improvement = (enhanced.snr_ratio - original.snr_ratio) / original.snr_ratio
                improvements.append(max(0, min(1, snr_improvement)))
            
            # Noise reduction
            if original.noise_level > 0:
                noise_reduction = (original.noise_level - enhanced.noise_level) / original.noise_level
                improvements.append(max(0, min(1, noise_reduction)))
            
            # Signal strength optimization (closer to target is better)
            signal_improvement = 1 - abs(enhanced.signal_strength - self.volume_target)
            improvements.append(max(0, min(1, signal_improvement)))
            
            return np.mean(improvements) if improvements else 0.0
            
        except Exception as e:
            logger.error(f"Improvement calculation failed: {e}")
            return 0.0
    
    def configure_enhancement(self, settings: Dict[str, Any]) -> bool:
        """Configure enhancement settings"""
        try:
            for key, value in settings.items():
                if key in self.enhancement_settings:
                    self.enhancement_settings[key] = value
                elif key == "target_sample_rate":
                    self.target_sample_rate = value
                elif key == "noise_threshold":
                    self.noise_threshold = value
                elif key == "volume_target":
                    self.volume_target = value
            
            logger.info(f"Enhancement settings updated: {settings}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure enhancement: {e}")
            return False
    
    def get_enhancement_info(self) -> Dict[str, Any]:
        """Get current enhancement configuration"""
        return {
            "settings": self.enhancement_settings.copy(),
            "target_sample_rate": self.target_sample_rate,
            "target_bit_depth": self.target_bit_depth,
            "noise_threshold": self.noise_threshold,
            "volume_target": self.volume_target,
            "available_enhancements": [
                "noise_reduction",
                "volume_normalization", 
                "quality_enhancement",
                "format_standardization"
            ]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for voice enhancer"""
        dependencies = {}
        
        try:
            import librosa
            dependencies["librosa"] = "available"
        except ImportError:
            dependencies["librosa"] = "missing"
        
        try:
            import scipy
            dependencies["scipy"] = "available"
        except ImportError:
            dependencies["scipy"] = "missing"
        
        try:
            import numpy
            dependencies["numpy"] = "available"
        except ImportError:
            dependencies["numpy"] = "missing"
        
        return {
            "status": "healthy",
            "dependencies": dependencies,
            "enhancement_settings": self.enhancement_settings,
            "features_available": [
                "basic_enhancement" if dependencies["numpy"] == "available" else "none",
                "advanced_resampling" if dependencies["librosa"] == "available" else "basic",
                "quality_filters" if dependencies["scipy"] == "available" else "basic"
            ]
        }
