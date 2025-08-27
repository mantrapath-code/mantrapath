"""
Microsoft Translator Implementation
Provides enterprise-grade translation via Microsoft Cognitive Services
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode
import logging

from engines.base_translator import BaseTranslator
from config.settings import (
    MICROSOFT_TRANSLATOR_API_KEY,
    MICROSOFT_TRANSLATOR_REGION,
    SUPPORTED_LANGUAGES
)

logger = logging.getLogger(__name__)

class MicrosoftTranslator(BaseTranslator):
    """Microsoft Translator API implementation"""
    
    def __init__(self):
        self.api_key = MICROSOFT_TRANSLATOR_API_KEY
        self.region = MICROSOFT_TRANSLATOR_REGION
        self.base_url = "https://api.cognitive.microsofttranslator.com"
        self.session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Ocp-Apim-Subscription-Region': self.region,
                'Content-Type': 'application/json',
                'User-Agent': 'MantraPath-Translation-Service/1.0'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate text using Microsoft Translator
        """
        if not self.api_key:
            logger.warning("Microsoft Translator API key not configured")
            return await self._fallback_translation(text, target_language, source_language)
        
        try:
            session = await self._get_session()
            
            # Build request parameters
            params = {
                'api-version': '3.0',
                'to': target_language
            }
            
            if source_language:
                params['from'] = source_language
            
            # Add cultural adaptation hints
            if context and context.get('domain') == 'meditation':
                params['category'] = 'generalnn'  # Use general neural for better meditation content
            
            # Prepare request body
            body = [{
                'text': text
            }]
            
            # Add context hints for better translation
            if context:
                if context.get('formality'):
                    body[0]['textType'] = 'html' if context['formality'] == 'formal' else 'plain'
                
                if context.get('cultural_context'):
                    # Microsoft Translator supports cultural adaptation
                    body[0]['textType'] = 'plain'
            
            url = f"{self.base_url}/translate?" + urlencode(params)
            
            async with session.post(url, json=body) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result and len(result) > 0:
                        translation_data = result[0]
                        translations = translation_data.get('translations', [])
                        
                        if translations:
                            translation = translations[0]
                            
                            # Calculate confidence score
                            confidence = self._calculate_confidence(
                                text, 
                                translation.get('text', ''),
                                context
                            )
                            
                            return {
                                'translated_text': translation.get('text', ''),
                                'source_language': translation_data.get('detectedLanguage', {}).get('language') or source_language,
                                'target_language': target_language,
                                'confidence_score': confidence,
                                'engine': 'microsoft',
                                'metadata': {
                                    'detected_language_confidence': translation_data.get('detectedLanguage', {}).get('score', 0.0),
                                    'api_version': '3.0',
                                    'cultural_adaptation': bool(context and context.get('cultural_context'))
                                }
                            }
                
                logger.error(f"Microsoft Translator API error: {response.status}")
                return await self._fallback_translation(text, target_language, source_language)
                
        except Exception as e:
            logger.error(f"Microsoft Translator error: {str(e)}")
            return await self._fallback_translation(text, target_language, source_language)
    
    async def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts in batch
        """
        if not self.api_key:
            logger.warning("Microsoft Translator API key not configured")
            return [
                await self._fallback_translation(text, target_language, source_language)
                for text in texts
            ]
        
        try:
            session = await self._get_session()
            
            # Build request parameters
            params = {
                'api-version': '3.0',
                'to': target_language
            }
            
            if source_language:
                params['from'] = source_language
            
            # Prepare batch request body
            body = [{'text': text} for text in texts]
            
            url = f"{self.base_url}/translate?" + urlencode(params)
            
            async with session.post(url, json=body) as response:
                if response.status == 200:
                    results = await response.json()
                    
                    translations = []
                    for i, result in enumerate(results):
                        if result.get('translations'):
                            translation = result['translations'][0]
                            
                            confidence = self._calculate_confidence(
                                texts[i],
                                translation.get('text', ''),
                                context
                            )
                            
                            translations.append({
                                'translated_text': translation.get('text', ''),
                                'source_language': result.get('detectedLanguage', {}).get('language') or source_language,
                                'target_language': target_language,
                                'confidence_score': confidence,
                                'engine': 'microsoft',
                                'metadata': {
                                    'detected_language_confidence': result.get('detectedLanguage', {}).get('score', 0.0),
                                    'batch_index': i
                                }
                            })
                        else:
                            translations.append(
                                await self._fallback_translation(texts[i], target_language, source_language)
                            )
                    
                    return translations
                
                logger.error(f"Microsoft Translator batch API error: {response.status}")
                return [
                    await self._fallback_translation(text, target_language, source_language)
                    for text in texts
                ]
                
        except Exception as e:
            logger.error(f"Microsoft Translator batch error: {str(e)}")
            return [
                await self._fallback_translation(text, target_language, source_language)
                for text in texts
            ]
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language using Microsoft Translator
        """
        if not self.api_key:
            return {
                'language': 'en',
                'confidence': 0.5,
                'engine': 'microsoft',
                'is_reliable': False
            }
        
        try:
            session = await self._get_session()
            
            params = {
                'api-version': '3.0'
            }
            
            body = [{'text': text}]
            
            url = f"{self.base_url}/detect?" + urlencode(params)
            
            async with session.post(url, json=body) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result and len(result) > 0:
                        detection = result[0]
                        
                        return {
                            'language': detection.get('language', 'unknown'),
                            'confidence': detection.get('score', 0.0),
                            'engine': 'microsoft',
                            'is_reliable': detection.get('isTranslationSupported', False),
                            'alternatives': detection.get('alternatives', [])
                        }
                
                return {
                    'language': 'unknown',
                    'confidence': 0.0,
                    'engine': 'microsoft',
                    'is_reliable': False
                }
                
        except Exception as e:
            logger.error(f"Microsoft language detection error: {str(e)}")
            return {
                'language': 'unknown',
                'confidence': 0.0,
                'engine': 'microsoft',
                'is_reliable': False,
                'error': str(e)
            }
    
    async def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        """
        if not self.api_key:
            return list(SUPPORTED_LANGUAGES.keys())
        
        try:
            session = await self._get_session()
            
            params = {
                'api-version': '3.0',
                'scope': 'translation'
            }
            
            url = f"{self.base_url}/languages?" + urlencode(params)
            
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if 'translation' in result:
                        return list(result['translation'].keys())
                
                return list(SUPPORTED_LANGUAGES.keys())
                
        except Exception as e:
            logger.error(f"Microsoft supported languages error: {str(e)}")
            return list(SUPPORTED_LANGUAGES.keys())
    
    def _calculate_confidence(
        self,
        original: str,
        translated: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate translation confidence score
        """
        if not original or not translated:
            return 0.0
        
        # Base confidence
        confidence = 0.8  # Microsoft Translator is generally reliable
        
        # Adjust based on text length
        if len(original) < 10:
            confidence *= 0.9  # Short texts are less reliable
        elif len(original) > 100:
            confidence *= 1.1  # Longer texts provide more context
        
        # Adjust based on domain
        if context and context.get('domain') == 'meditation':
            confidence *= 0.95  # Meditation terms may need cultural adaptation
        
        # Check for obvious translation issues
        if translated == original:
            confidence *= 0.7  # Might indicate no translation occurred
        
        if len(translated) < len(original) * 0.3:
            confidence *= 0.8  # Suspiciously short translation
        
        return min(confidence, 1.0)
    
    async def _fallback_translation(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fallback translation when API is unavailable
        """
        return {
            'translated_text': text,  # Return original text as fallback
            'source_language': source_language or 'unknown',
            'target_language': target_language,
            'confidence_score': 0.1,
            'engine': 'microsoft_fallback',
            'metadata': {
                'fallback_reason': 'API unavailable or error',
                'is_fallback': True
            }
        }
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close())
