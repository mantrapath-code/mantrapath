"""
Cultural Adaptation Service
Provides culturally-aware translation with context understanding
Specializes in meditation and mindfulness terminology across cultures
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CulturalContext(Enum):
    """Cultural context types"""
    WESTERN_SECULAR = "western_secular"
    BUDDHIST_TRADITIONAL = "buddhist_traditional"
    HINDU_VEDANTIC = "hindu_vedantic"
    CHRISTIAN_CONTEMPLATIVE = "christian_contemplative"
    ISLAMIC_SUFI = "islamic_sufi"
    SECULAR_SCIENTIFIC = "secular_scientific"
    MODERN_WELLNESS = "modern_wellness"

@dataclass
class CulturalRule:
    """Cultural adaptation rule"""
    source_term: str
    target_language: str
    cultural_context: CulturalContext
    adapted_translation: str
    explanation: str
    formality_level: str  # formal, informal, respectful

class CulturalAdaptationService:
    """
    Service for culturally-aware translation adaptation
    """
    
    def __init__(self):
        self.cultural_rules = self._load_cultural_rules()
        self.cultural_contexts = self._load_cultural_contexts()
        self.formality_patterns = self._load_formality_patterns()
        logger.info("Cultural adaptation service initialized")
    
    def _load_cultural_rules(self) -> Dict[str, List[CulturalRule]]:
        """
        Load cultural adaptation rules for meditation terms
        """
        rules = {}
        
        # Meditation term adaptations
        meditation_rules = [
            CulturalRule(
                source_term="meditation",
                target_language="ar",
                cultural_context=CulturalContext.ISLAMIC_SUFI,
                adapted_translation="مراقبة (muraqaba)",
                explanation="Islamic contemplative practice",
                formality_level="respectful"
            ),
            CulturalRule(
                source_term="meditation",
                target_language="ar",
                cultural_context=CulturalContext.SECULAR_SCIENTIFIC,
                adapted_translation="تأمل (ta'amul)",
                explanation="Secular mindfulness practice",
                formality_level="formal"
            ),
            CulturalRule(
                source_term="prayer",
                target_language="hi",
                cultural_context=CulturalContext.HINDU_VEDANTIC,
                adapted_translation="ध्यान (dhyan)",
                explanation="Vedantic contemplative practice",
                formality_level="respectful"
            ),
            CulturalRule(
                source_term="mindfulness",
                target_language="zh",
                cultural_context=CulturalContext.BUDDHIST_TRADITIONAL,
                adapted_translation="正念 (zhèng niàn)",
                explanation="Traditional Buddhist awareness practice",
                formality_level="formal"
            ),
            CulturalRule(
                source_term="mindfulness",
                target_language="zh",
                cultural_context=CulturalContext.SECULAR_SCIENTIFIC,
                adapted_translation="专注 (zhuān zhù)",
                explanation="Scientific attention training",
                formality_level="formal"
            ),
            CulturalRule(
                source_term="enlightenment",
                target_language="ja",
                cultural_context=CulturalContext.BUDDHIST_TRADITIONAL,
                adapted_translation="悟り (satori)",
                explanation="Zen enlightenment experience",
                formality_level="respectful"
            ),
            CulturalRule(
                source_term="spiritual",
                target_language="fr",
                cultural_context=CulturalContext.CHRISTIAN_CONTEMPLATIVE,
                adapted_translation="spirituel contemplatif",
                explanation="Christian contemplative tradition",
                formality_level="formal"
            ),
            CulturalRule(
                source_term="chakra",
                target_language="es",
                cultural_context=CulturalContext.WESTERN_SECULAR,
                adapted_translation="centro energético",
                explanation="Energy center without religious connotation",
                formality_level="informal"
            )
        ]
        
        # Group rules by source term
        for rule in meditation_rules:
            if rule.source_term not in rules:
                rules[rule.source_term] = []
            rules[rule.source_term].append(rule)
        
        return rules
    
    def _load_cultural_contexts(self) -> Dict[str, Dict[str, Any]]:
        """
        Load cultural context information by language/region
        """
        return {
            'en': {
                'primary_contexts': [CulturalContext.WESTERN_SECULAR, CulturalContext.MODERN_WELLNESS],
                'religious_sensitivity': 'low',
                'formality_preference': 'informal',
                'meditation_tradition': 'eclectic'
            },
            'ar': {
                'primary_contexts': [CulturalContext.ISLAMIC_SUFI],
                'religious_sensitivity': 'high',
                'formality_preference': 'respectful',
                'meditation_tradition': 'islamic_contemplative'
            },
            'hi': {
                'primary_contexts': [CulturalContext.HINDU_VEDANTIC, CulturalContext.BUDDHIST_TRADITIONAL],
                'religious_sensitivity': 'high',
                'formality_preference': 'respectful',
                'meditation_tradition': 'vedantic_yoga'
            },
            'zh': {
                'primary_contexts': [CulturalContext.BUDDHIST_TRADITIONAL, CulturalContext.SECULAR_SCIENTIFIC],
                'religious_sensitivity': 'medium',
                'formality_preference': 'formal',
                'meditation_tradition': 'buddhist_zen'
            },
            'ja': {
                'primary_contexts': [CulturalContext.BUDDHIST_TRADITIONAL],
                'religious_sensitivity': 'high',
                'formality_preference': 'respectful',
                'meditation_tradition': 'zen'
            },
            'th': {
                'primary_contexts': [CulturalContext.BUDDHIST_TRADITIONAL],
                'religious_sensitivity': 'very_high',
                'formality_preference': 'respectful',
                'meditation_tradition': 'theravada'
            },
            'es': {
                'primary_contexts': [CulturalContext.WESTERN_SECULAR, CulturalContext.CHRISTIAN_CONTEMPLATIVE],
                'religious_sensitivity': 'medium',
                'formality_preference': 'formal',
                'meditation_tradition': 'contemporary'
            },
            'fr': {
                'primary_contexts': [CulturalContext.WESTERN_SECULAR, CulturalContext.CHRISTIAN_CONTEMPLATIVE],
                'religious_sensitivity': 'low',
                'formality_preference': 'formal',
                'meditation_tradition': 'philosophical'
            }
        }
    
    def _load_formality_patterns(self) -> Dict[str, Dict[str, str]]:
        """
        Load formality patterns by language
        """
        return {
            'ja': {
                'respectful_suffix': 'です',
                'honorific_prefix': 'ご',
                'formal_particle': 'は'
            },
            'ko': {
                'respectful_suffix': '습니다',
                'honorific_infix': '시',
                'formal_particle': '은/는'
            },
            'th': {
                'respectful_suffix': 'ครับ/ค่ะ',
                'royal_language': 'ราชาศัพท์',
                'monk_reference': 'พระ'
            },
            'de': {
                'formal_pronoun': 'Sie',
                'informal_pronoun': 'du',
                'respectful_title': 'verehrte/r'
            },
            'fr': {
                'formal_pronoun': 'vous',
                'informal_pronoun': 'tu',
                'respectful_title': 'vénérable'
            }
        }
    
    async def adapt_translation(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adapt translation for cultural context
        """
        # Extract context information
        cultural_context = self._determine_cultural_context(
            target_language, context
        )
        
        user_preferences = context.get('user_preferences', {}) if context else {}
        meditation_style = context.get('meditation_style', 'general') if context else 'general'
        
        # Apply cultural adaptations
        adapted_text = await self._apply_cultural_rules(
            original_text,
            translated_text,
            target_language,
            cultural_context,
            user_preferences
        )
        
        # Apply formality adjustments
        adapted_text = await self._adjust_formality(
            adapted_text,
            target_language,
            cultural_context,
            user_preferences
        )
        
        # Generate cultural notes
        cultural_notes = self._generate_cultural_notes(
            original_text,
            adapted_text,
            source_language,
            target_language,
            cultural_context
        )
        
        return {
            'adapted_text': adapted_text,
            'cultural_context': cultural_context.value,
            'adaptations_applied': self._count_adaptations(translated_text, adapted_text),
            'cultural_notes': cultural_notes,
            'formality_level': self._get_formality_level(target_language, user_preferences),
            'metadata': {
                'meditation_style': meditation_style,
                'religious_sensitivity': self._get_religious_sensitivity(target_language),
                'adaptation_confidence': self._calculate_adaptation_confidence(
                    original_text, adapted_text, target_language
                )
            }
        }
    
    def _determine_cultural_context(
        self,
        target_language: str,
        context: Optional[Dict[str, Any]]
    ) -> CulturalContext:
        """
        Determine appropriate cultural context
        """
        # User-specified context takes priority
        if context and 'cultural_context' in context:
            try:
                return CulturalContext(context['cultural_context'])
            except ValueError:
                pass
        
        # Check user's meditation tradition preference
        if context and 'meditation_tradition' in context:
            tradition = context['meditation_tradition'].lower()
            if 'buddhist' in tradition:
                return CulturalContext.BUDDHIST_TRADITIONAL
            elif 'hindu' in tradition or 'vedic' in tradition:
                return CulturalContext.HINDU_VEDANTIC
            elif 'christian' in tradition:
                return CulturalContext.CHRISTIAN_CONTEMPLATIVE
            elif 'sufi' in tradition or 'islamic' in tradition:
                return CulturalContext.ISLAMIC_SUFI
            elif 'secular' in tradition or 'scientific' in tradition:
                return CulturalContext.SECULAR_SCIENTIFIC
        
        # Default based on language
        language_defaults = {
            'ar': CulturalContext.ISLAMIC_SUFI,
            'hi': CulturalContext.HINDU_VEDANTIC,
            'zh': CulturalContext.BUDDHIST_TRADITIONAL,
            'ja': CulturalContext.BUDDHIST_TRADITIONAL,
            'th': CulturalContext.BUDDHIST_TRADITIONAL,
            'ti': CulturalContext.BUDDHIST_TRADITIONAL,  # Tibetan
            'es': CulturalContext.WESTERN_SECULAR,
            'fr': CulturalContext.WESTERN_SECULAR,
            'de': CulturalContext.WESTERN_SECULAR,
            'it': CulturalContext.CHRISTIAN_CONTEMPLATIVE,
            'pt': CulturalContext.WESTERN_SECULAR
        }
        
        return language_defaults.get(target_language, CulturalContext.WESTERN_SECULAR)
    
    async def _apply_cultural_rules(
        self,
        original_text: str,
        translated_text: str,
        target_language: str,
        cultural_context: CulturalContext,
        user_preferences: Dict[str, Any]
    ) -> str:
        """
        Apply cultural adaptation rules
        """
        adapted_text = translated_text
        
        # Apply term-specific rules
        original_lower = original_text.lower()
        
        for term, rules in self.cultural_rules.items():
            if term.lower() in original_lower:
                # Find matching rule
                matching_rule = None
                
                for rule in rules:
                    if (rule.target_language == target_language and 
                        rule.cultural_context == cultural_context):
                        matching_rule = rule
                        break
                
                if matching_rule:
                    # Apply the cultural adaptation
                    import re
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    adapted_text = pattern.sub(matching_rule.adapted_translation, adapted_text)
        
        return adapted_text
    
    async def _adjust_formality(
        self,
        text: str,
        target_language: str,
        cultural_context: CulturalContext,
        user_preferences: Dict[str, Any]
    ) -> str:
        """
        Adjust formality level based on cultural context
        """
        formality_level = user_preferences.get('formality', 'auto')
        
        if formality_level == 'auto':
            # Determine based on cultural context
            if cultural_context in [CulturalContext.BUDDHIST_TRADITIONAL, 
                                   CulturalContext.HINDU_VEDANTIC,
                                   CulturalContext.ISLAMIC_SUFI]:
                formality_level = 'respectful'
            elif cultural_context == CulturalContext.SECULAR_SCIENTIFIC:
                formality_level = 'formal'
            else:
                formality_level = 'informal'
        
        # Apply language-specific formality patterns
        if target_language in self.formality_patterns:
            patterns = self.formality_patterns[target_language]
            
            if formality_level == 'respectful' and target_language == 'ja':
                # Add respectful endings in Japanese
                if not text.endswith('です') and not text.endswith('ます'):
                    text = text.rstrip('。') + 'です。'
            
            elif formality_level == 'respectful' and target_language == 'th':
                # Add respectful particles in Thai
                if not any(text.endswith(suffix) for suffix in ['ครับ', 'ค่ะ', 'นะครับ', 'นะคะ']):
                    text += 'ครับ'  # Default to male form, should be personalized
        
        return text
    
    def _generate_cultural_notes(
        self,
        original_text: str,
        adapted_text: str,
        source_language: str,
        target_language: str,
        cultural_context: CulturalContext
    ) -> List[str]:
        """
        Generate notes about cultural adaptations
        """
        notes = []
        
        if adapted_text != original_text:
            notes.append(f"Text adapted for {cultural_context.value} context")
        
        # Context-specific notes
        if cultural_context == CulturalContext.BUDDHIST_TRADITIONAL:
            notes.append("Translation uses traditional Buddhist terminology")
        elif cultural_context == CulturalContext.ISLAMIC_SUFI:
            notes.append("Translation uses Islamic contemplative terms")
        elif cultural_context == CulturalContext.HINDU_VEDANTIC:
            notes.append("Translation uses Vedantic spiritual terminology")
        elif cultural_context == CulturalContext.SECULAR_SCIENTIFIC:
            notes.append("Translation uses secular, scientific terminology")
        
        # Language-specific notes
        if target_language in ['ar', 'hi', 'th'] and 'meditation' in original_text.lower():
            notes.append("Meditation terms adapted for cultural sensitivity")
        
        return notes
    
    def _count_adaptations(self, original: str, adapted: str) -> int:
        """
        Count number of adaptations applied
        """
        if original == adapted:
            return 0
        
        # Simple word difference count
        original_words = set(original.split())
        adapted_words = set(adapted.split())
        
        return len(original_words.symmetric_difference(adapted_words))
    
    def _get_formality_level(self, target_language: str, user_preferences: Dict[str, Any]) -> str:
        """
        Get formality level for the target language
        """
        if 'formality' in user_preferences:
            return user_preferences['formality']
        
        # Default formality by language
        language_formality = {
            'ja': 'respectful',
            'ko': 'respectful', 
            'th': 'respectful',
            'ar': 'respectful',
            'hi': 'respectful',
            'de': 'formal',
            'fr': 'formal',
            'zh': 'formal',
            'es': 'formal',
            'en': 'informal'
        }
        
        return language_formality.get(target_language, 'formal')
    
    def _get_religious_sensitivity(self, target_language: str) -> str:
        """
        Get religious sensitivity level for target language
        """
        if target_language in self.cultural_contexts:
            return self.cultural_contexts[target_language]['religious_sensitivity']
        return 'medium'
    
    def _calculate_adaptation_confidence(
        self,
        original_text: str,
        adapted_text: str,
        target_language: str
    ) -> float:
        """
        Calculate confidence in cultural adaptation
        """
        base_confidence = 0.8
        
        # Higher confidence for languages with defined cultural rules
        if target_language in ['ar', 'hi', 'zh', 'ja', 'th']:
            base_confidence = 0.9
        
        # Lower confidence if no adaptations were made
        if original_text == adapted_text:
            base_confidence *= 0.7
        
        return base_confidence
