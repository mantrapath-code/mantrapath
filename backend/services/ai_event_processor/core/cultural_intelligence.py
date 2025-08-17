import asyncio
import time
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

import structlog
from langdetect import detect

from models.ai_models import CulturalContext, AIMetrics

logger = structlog.get_logger(__name__)

class CulturalIntelligenceProcessor:
    """
    Cultural Intelligence Processing Service
    
    Provides:
    - Cultural context detection and adaptation
    - Cross-cultural communication patterns
    - Culturally-appropriate response generation
    - Regional mental health approaches
    - Cultural sensitivity validation
    """
    
    def __init__(self):
        self.cultural_configs = {}
        self.cultural_patterns = {}
        self.is_initialized = False
        self.metrics = AIMetrics()
        
        # Supported cultural contexts
        self.supported_cultures = {
            'en': 'western_individualistic',
            'hi': 'indian_collectivistic', 
            'ar': 'arabic_islamic',
            'es': 'latin_expressive',
            'fr': 'french_intellectual',
            'de': 'german_direct',
            'ja': 'japanese_subtle',
            'zh': 'chinese_confucian',
            'ko': 'korean_hierarchical',
            'bn': 'bengali_literary',
            'ta': 'tamil_traditional',
            'te': 'telugu_regional'
        }
        
    async def start(self):
        """Initialize cultural intelligence processor"""
        try:
            logger.info("Starting Cultural Intelligence Processor")
            
            # Load cultural configurations
            await self._load_cultural_configs()
            
            # Load cultural patterns
            await self._load_cultural_patterns()
            
            self.is_initialized = True
            logger.info("Cultural Intelligence Processor started successfully")
            
        except Exception as e:
            logger.error("Failed to start Cultural Intelligence Processor", error=str(e))
            raise
    
    async def stop(self):
        """Stop cultural intelligence processor"""
        try:
            logger.info("Stopping Cultural Intelligence Processor")
            
            self.cultural_configs.clear()
            self.cultural_patterns.clear()
            self.is_initialized = False
            
            logger.info("Cultural Intelligence Processor stopped")
            
        except Exception as e:
            logger.error("Error stopping Cultural Intelligence Processor", error=str(e))
    
    async def _load_cultural_configs(self):
        """Load cultural configuration data"""
        try:
            # Define cultural configurations inline for now
            # In production, this would load from cultural_config.yaml
            
            self.cultural_configs = {
                'western_individualistic': {
                    'communication_style': 'direct',
                    'emotional_expression': 'open',
                    'therapy_approach': 'cognitive_behavioral',
                    'family_involvement': 'minimal',
                    'religious_integration': 'optional',
                    'crisis_response': 'individual_focused'
                },
                'indian_collectivistic': {
                    'communication_style': 'respectful',
                    'emotional_expression': 'family_oriented',
                    'therapy_approach': 'holistic_ayurvedic',
                    'family_involvement': 'central',
                    'religious_integration': 'important',
                    'crisis_response': 'family_community_involved'
                },
                'arabic_islamic': {
                    'communication_style': 'formal_respectful',
                    'emotional_expression': 'spiritual_framed',
                    'therapy_approach': 'islamic_psychology',
                    'family_involvement': 'significant',
                    'religious_integration': 'essential',
                    'crisis_response': 'community_elder_involvement'
                },
                'japanese_subtle': {
                    'communication_style': 'indirect',
                    'emotional_expression': 'understated',
                    'therapy_approach': 'mindfulness_based',
                    'family_involvement': 'considerate',
                    'religious_integration': 'cultural_spiritual',
                    'crisis_response': 'subtle_intervention'
                }
            }
            
            logger.info("Cultural configurations loaded")
            
        except Exception as e:
            logger.error("Error loading cultural configurations", error=str(e))
            raise
    
    async def _load_cultural_patterns(self):
        """Load cultural communication patterns"""
        try:
            self.cultural_patterns = {
                'emotional_expressions': {
                    'indian_collectivistic': {
                        'stress': ['family burden', 'duty conflict', 'societal pressure'],
                        'joy': ['family success', 'community celebration', 'spiritual fulfillment'],
                        'sadness': ['separation from family', 'social disappointment', 'spiritual crisis']
                    },
                    'arabic_islamic': {
                        'stress': ['spiritual disconnect', 'community obligation', 'family honor'],
                        'joy': ['spiritual closeness', 'community harmony', 'family pride'],
                        'sadness': ['spiritual struggle', 'community conflict', 'family concern']
                    },
                    'japanese_subtle': {
                        'stress': ['social harmony disruption', 'work-life imbalance', 'obligation burden'],
                        'joy': ['group achievement', 'seasonal appreciation', 'harmonious relationships'],
                        'sadness': ['disappointing others', 'social isolation', 'failure to meet expectations']
                    }
                },
                'therapy_preferences': {
                    'indian_collectivistic': {
                        'preferred_approaches': ['family therapy', 'spiritual counseling', 'ayurvedic wellness'],
                        'avoid': ['individual blame', 'family criticism', 'religious dismissal']
                    },
                    'arabic_islamic': {
                        'preferred_approaches': ['islamic counseling', 'community support', 'spiritual guidance'],
                        'avoid': ['religious contradiction', 'family dishonor', 'cultural insensitivity']
                    },
                    'western_individualistic': {
                        'preferred_approaches': ['cognitive behavioral', 'individual empowerment', 'self-actualization'],
                        'avoid': ['family interference', 'religious imposition', 'collectivist pressure']
                    }
                }
            }
            
            logger.info("Cultural patterns loaded")
            
        except Exception as e:
            logger.error("Error loading cultural patterns", error=str(e))
            raise
    
    async def detect_cultural_context(
        self, 
        text: str = None, 
        language: str = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> CulturalContext:
        """
        Detect cultural context from text, language, and user profile
        
        Args:
            text: Text content to analyze for cultural markers
            language: Language code
            user_profile: User profile information
            
        Returns:
            CulturalContext with detected cultural information
        """
        try:
            start_time = time.time()
            
            # Primary detection from language
            if language and language in self.supported_cultures:
                culture = self.supported_cultures[language]
                confidence = 0.8
            else:
                # Try to detect from text
                if text:
                    detected_lang = detect(text)
                    if detected_lang in self.supported_cultures:
                        culture = self.supported_cultures[detected_lang]
                        language = detected_lang
                        confidence = 0.7
                    else:
                        culture = 'western_individualistic'
                        language = 'en'
                        confidence = 0.5
                else:
                    culture = 'western_individualistic'
                    language = 'en'
                    confidence = 0.5
            
            # Enhance detection with user profile
            if user_profile:
                profile_culture = user_profile.get('cultural_background')
                if profile_culture and profile_culture in self.cultural_configs:
                    culture = profile_culture
                    confidence = min(confidence + 0.2, 1.0)
            
            # Get cultural configuration
            cultural_config = self.cultural_configs.get(culture, {})
            
            # Create cultural context
            context = CulturalContext(
                culture=culture,
                language=language,
                region=user_profile.get('region') if user_profile else None,
                adaptation_rules=cultural_config,
                confidence=confidence
            )
            
            # Update metrics
            self.metrics.cultural_adaptations += 1
            
            processing_time = (time.time() - start_time) * 1000
            logger.debug(
                "Cultural context detected",
                culture=culture,
                language=language,
                confidence=confidence,
                processing_time_ms=processing_time
            )
            
            return context
            
        except Exception as e:
            logger.error("Cultural context detection failed", error=str(e))
            # Return default context
            return CulturalContext(
                culture='western_individualistic',
                language='en',
                adaptation_rules=self.cultural_configs.get('western_individualistic', {}),
                confidence=0.3
            )
    
    async def adapt_response(
        self, 
        response: str,
        cultural_context: CulturalContext,
        response_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Adapt a response based on cultural context
        
        Args:
            response: Original response text
            cultural_context: Cultural context to adapt for
            response_type: Type of response (therapy, support, information)
            
        Returns:
            Dictionary with adapted response and cultural notes
        """
        try:
            start_time = time.time()
            
            culture = cultural_context.culture
            adaptation_rules = cultural_context.adaptation_rules
            
            adapted_response = response
            cultural_notes = []
            
            # Apply cultural adaptations based on rules
            if culture == 'indian_collectivistic':
                adapted_response = await self._adapt_for_indian_culture(
                    response, response_type, adaptation_rules
                )
                cultural_notes.append("Adapted for family-oriented perspective")
                
            elif culture == 'arabic_islamic':
                adapted_response = await self._adapt_for_arabic_culture(
                    response, response_type, adaptation_rules
                )
                cultural_notes.append("Adapted for Islamic cultural values")
                
            elif culture == 'japanese_subtle':
                adapted_response = await self._adapt_for_japanese_culture(
                    response, response_type, adaptation_rules
                )
                cultural_notes.append("Adapted for subtle communication style")
            
            # Add respectful language patterns
            if adaptation_rules.get('communication_style') == 'formal_respectful':
                adapted_response = self._add_respectful_language(adapted_response)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'original_response': response,
                'adapted_response': adapted_response,
                'cultural_adaptations': cultural_notes,
                'culture': culture,
                'confidence': cultural_context.confidence,
                'processing_time_ms': processing_time
            }
            
        except Exception as e:
            logger.error("Response adaptation failed", error=str(e))
            return {
                'original_response': response,
                'adapted_response': response,
                'cultural_adaptations': [],
                'culture': cultural_context.culture,
                'confidence': 0.0,
                'processing_time_ms': 0.0
            }
    
    async def _adapt_for_indian_culture(
        self, 
        response: str, 
        response_type: str,
        rules: Dict[str, Any]
    ) -> str:
        """Adapt response for Indian cultural context"""
        
        # Add family consideration
        if 'family' not in response and response_type in ['therapy', 'support']:
            response = response + " Consider discussing this with trusted family members if appropriate."
        
        # Add respectful tone
        if response_type == 'therapy':
            response = "With respect for your cultural values, " + response.lower()
        
        # Spiritual/holistic framing
        if 'stress' in response.lower() or 'anxiety' in response.lower():
            response += " Mind-body wellness practices like yoga or meditation might also be beneficial."
        
        return response
    
    async def _adapt_for_arabic_culture(
        self, 
        response: str, 
        response_type: str,
        rules: Dict[str, Any]
    ) -> str:
        """Adapt response for Arabic/Islamic cultural context"""
        
        # Add spiritual framing where appropriate
        if response_type in ['support', 'therapy']:
            response = "May this guidance be beneficial to you. " + response
        
        # Family and community consideration
        if 'decision' in response.lower() and response_type == 'therapy':
            response += " You may also wish to seek counsel from trusted family or community elders."
        
        # Respectful language
        response = response.replace("you should", "you might consider")
        response = response.replace("you must", "it may be beneficial to")
        
        return response
    
    async def _adapt_for_japanese_culture(
        self, 
        response: str, 
        response_type: str,
        rules: Dict[str, Any]
    ) -> str:
        """Adapt response for Japanese cultural context"""
        
        # Soften direct statements
        response = response.replace("You should", "Perhaps you might consider")
        response = response.replace("This will", "This may")
        response = response.replace("definitely", "possibly")
        
        # Add consideration for others
        if response_type == 'therapy' and 'family' not in response:
            response += " Please also consider what feels comfortable for those around you."
        
        # Subtle suggestion rather than direct advice
        response = response.replace("I recommend", "One possibility might be")
        response = response.replace("Do this", "This approach might be helpful")
        
        return response
    
    def _add_respectful_language(self, response: str) -> str:
        """Add respectful language patterns"""
        
        # Replace casual language with formal
        replacements = {
            "hey": "greetings",
            "yeah": "yes",
            "okay": "certainly",
            "sure": "of course",
            "cool": "excellent",
            "awesome": "wonderful"
        }
        
        for casual, formal in replacements.items():
            response = response.replace(casual, formal)
        
        return response
    
    async def validate_cultural_sensitivity(
        self, 
        content: str,
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """
        Validate content for cultural sensitivity
        
        Args:
            content: Content to validate
            cultural_context: Cultural context to validate against
            
        Returns:
            Validation results with sensitivity score and issues
        """
        try:
            start_time = time.time()
            
            issues = []
            warnings = []
            sensitivity_score = 1.0
            
            culture = cultural_context.culture
            content_lower = content.lower()
            
            # Check for potentially insensitive content
            if culture == 'arabic_islamic':
                # Check for religious sensitivity
                if any(word in content_lower for word in ['haram', 'forbidden', 'sin']):
                    warnings.append("Contains religious terminology - ensure appropriate context")
                    sensitivity_score -= 0.1
                
                # Check for gender considerations
                if 'dating' in content_lower or 'boyfriend' in content_lower or 'girlfriend' in content_lower:
                    issues.append("Contains dating references that may not align with cultural values")
                    sensitivity_score -= 0.3
            
            elif culture == 'indian_collectivistic':
                # Check for family sensitivity
                if 'leave your family' in content_lower or 'ignore family' in content_lower:
                    issues.append("Contains advice that conflicts with family-oriented values")
                    sensitivity_score -= 0.4
                
                # Check for individual vs collective framing
                if content_lower.count('you') > content_lower.count('family') * 3:
                    warnings.append("Consider adding family/community perspective")
                    sensitivity_score -= 0.1
            
            elif culture == 'japanese_subtle':
                # Check for directness that might be uncomfortable
                if any(word in content_lower for word in ['must', 'should', 'definitely', 'wrong']):
                    warnings.append("Consider softer language for cultural comfort")
                    sensitivity_score -= 0.2
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'sensitivity_score': max(sensitivity_score, 0.0),
                'issues': issues,
                'warnings': warnings,
                'is_culturally_appropriate': len(issues) == 0,
                'culture': culture,
                'processing_time_ms': processing_time
            }
            
        except Exception as e:
            logger.error("Cultural sensitivity validation failed", error=str(e))
            return {
                'sensitivity_score': 0.5,
                'issues': ["Validation failed"],
                'warnings': [],
                'is_culturally_appropriate': False,
                'culture': cultural_context.culture,
                'processing_time_ms': 0.0
            }
    
    async def get_cultural_preferences(
        self, 
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """Get cultural preferences for therapy and support"""
        try:
            culture = cultural_context.culture
            
            # Get therapy preferences
            therapy_prefs = self.cultural_patterns.get('therapy_preferences', {}).get(culture, {})
            
            # Get emotional expression patterns
            emotion_patterns = self.cultural_patterns.get('emotional_expressions', {}).get(culture, {})
            
            return {
                'therapy_approaches': therapy_prefs.get('preferred_approaches', []),
                'approaches_to_avoid': therapy_prefs.get('avoid', []),
                'emotional_expression_patterns': emotion_patterns,
                'communication_style': cultural_context.adaptation_rules.get('communication_style'),
                'family_involvement_level': cultural_context.adaptation_rules.get('family_involvement'),
                'religious_integration': cultural_context.adaptation_rules.get('religious_integration')
            }
            
        except Exception as e:
            logger.error("Error getting cultural preferences", error=str(e))
            return {}
    
    def _update_metrics(self, processing_time_ms: float):
        """Update processing metrics"""
        self.metrics.cultural_adaptations += 1
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get cultural intelligence metrics"""
        return {
            'total_adaptations': self.metrics.cultural_adaptations,
            'supported_cultures': len(self.supported_cultures),
            'cultural_configs_loaded': len(self.cultural_configs),
            'is_initialized': self.is_initialized
        }
    
    def health_check(self) -> bool:
        """Check if cultural intelligence processor is healthy"""
        return self.is_initialized and len(self.cultural_configs) > 0
