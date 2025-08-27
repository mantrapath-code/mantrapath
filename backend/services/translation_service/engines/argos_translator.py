"""
Argos Translate Engine for offline translation with Indian language support
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
import time

logger = logging.getLogger(__name__)

try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False
    logger.warning("Argos Translate not available. Install with: pip install argostranslate")

class ArgosTranslator:
    """Argos Translate engine for offline translation"""
    
    def __init__(self):
        self.is_initialized = False
        self.available_languages = set()
        self.installed_packages = []
        
    async def initialize(self) -> bool:
        """Initialize Argos Translate engine"""
        if not ARGOS_AVAILABLE:
            logger.error("Argos Translate library not available")
            return False
            
        try:
            # Update package index
            argostranslate.package.update_package_index()
            
            # Get available packages
            available_packages = argostranslate.package.get_available_packages()
            
            # Install Indian language packages if available
            indian_language_codes = ['hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 'as', 'mr', 'ur']
            
            for package in available_packages:
                # Install packages for Indian languages
                if (package.from_code in ['en'] and package.to_code in indian_language_codes) or \
                   (package.from_code in indian_language_codes and package.to_code in ['en']):
                    try:
                        argostranslate.package.install_from_path(package.download())
                        self.installed_packages.append(package)
                        logger.info(f"Installed Argos package: {package.from_code} -> {package.to_code}")
                    except Exception as e:
                        logger.warning(f"Failed to install package {package.from_code}->{package.to_code}: {e}")
            
            # Get available languages after installation
            self.available_languages = set()
            for package in self.installed_packages:
                self.available_languages.add(package.from_code)
                self.available_languages.add(package.to_code)
            
            self.is_initialized = True
            logger.info(f"Argos Translate initialized with {len(self.installed_packages)} packages")
            logger.info(f"Available languages: {sorted(self.available_languages)}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Argos Translate: {str(e)}")
            return False
    
    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate text using Argos Translate
        """
        start_time = time.time()
        
        if not self.is_initialized:
            await self.initialize()
            
        if not ARGOS_AVAILABLE:
            raise Exception("Argos Translate not available")
        
        try:
            # Check if language pair is supported
            if source_language not in self.available_languages or target_language not in self.available_languages:
                logger.warning(f"Language pair {source_language}->{target_language} not available in Argos")
                raise Exception(f"Language pair not supported: {source_language} -> {target_language}")
            
            # Perform translation
            translated_text = argostranslate.translate.translate(text, source_language, target_language)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Calculate confidence based on translation quality heuristics
            confidence = self._calculate_confidence(text, translated_text, source_language, target_language)
            
            return {
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language,
                'confidence_score': confidence,
                'engine': 'argos',
                'processing_time_ms': processing_time,
                'offline': True
            }
            
        except Exception as e:
            logger.error(f"Argos translation failed: {str(e)}")
            raise
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language using simple heuristics (Argos doesn't have built-in detection)
        """
        # Simple language detection based on character sets
        detection_result = {
            'language': 'en',  # Default to English
            'confidence': 0.5,
            'engine': 'argos_heuristic'
        }
        
        # Check for common Indian language patterns
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):  # Devanagari
            detection_result['language'] = 'hi'
            detection_result['confidence'] = 0.8
        elif any(ord(char) >= 0x0980 and ord(char) <= 0x09FF for char in text):  # Bengali
            detection_result['language'] = 'bn'
            detection_result['confidence'] = 0.8
        elif any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in text):  # Tamil
            detection_result['language'] = 'ta'
            detection_result['confidence'] = 0.8
        elif any(ord(char) >= 0x0C00 and ord(char) <= 0x0C7F for char in text):  # Telugu
            detection_result['language'] = 'te'
            detection_result['confidence'] = 0.8
        
        return detection_result
    
    def _calculate_confidence(self, source_text: str, translated_text: str, 
                            source_lang: str, target_lang: str) -> float:
        """Calculate translation confidence based on heuristics"""
        
        # Basic confidence calculation
        confidence = 0.7  # Base confidence for Argos
        
        # Penalize if translation is same as source (likely untranslated)
        if source_text.strip() == translated_text.strip():
            confidence = 0.3
        
        # Boost confidence for supported Indian languages
        indian_languages = ['hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 'as', 'mr', 'ur']
        if target_lang in indian_languages:
            confidence += 0.1
        
        # Consider text length (longer texts might be more accurate)
        if len(source_text) > 100:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Argos Translate is healthy"""
        return {
            'status': 'healthy' if self.is_initialized and ARGOS_AVAILABLE else 'unhealthy',
            'available': ARGOS_AVAILABLE,
            'initialized': self.is_initialized,
            'installed_packages': len(self.installed_packages),
            'available_languages': sorted(self.available_languages) if self.available_languages else []
        }
