"""
Cultural Context Processor
Handles cultural adaptation and context processing for cross-service workflows
"""
import logging
from typing import Dict, Any, Optional, List, Callable
import re

from ..models import CulturalContext, WorkflowResult

logger = logging.getLogger(__name__)


class CulturalProcessor:
    """
    Cultural context processing and adaptation system
    
    Handles cultural awareness and adaptations for voice-driven workflows
    """
    
    def __init__(self):
        self.language_detection_patterns = self._initialize_language_patterns()
        self.cultural_adaptations = self._initialize_cultural_adaptations()
        self.text_normalizers = self._initialize_text_normalizers()
        
        logger.info("Cultural Processor initialized")
    
    async def process_cultural_context(
        self,
        voice_input: str,
        cultural_preferences: Optional[Dict[str, Any]] = None
    ) -> CulturalContext:
        """Process and determine cultural context from voice input and preferences"""
        
        # Detect language from voice input
        detected_language = await self._detect_language(voice_input)
        
        # Use preferences if available, otherwise use detected
        language = (cultural_preferences or {}).get("language", detected_language)
        
        # Get cultural region from preferences or infer from language
        cultural_region = (cultural_preferences or {}).get("cultural_region")
        if not cultural_region:
            cultural_region = self._infer_cultural_region(language)
        
        # Determine communication style
        communication_style = (cultural_preferences or {}).get("communication_style")
        if not communication_style:
            communication_style = self._infer_communication_style(language, cultural_region)
        
        # Determine formality level
        formality_level = (cultural_preferences or {}).get("formality_level")
        if not formality_level:
            formality_level = self._infer_formality_level(language, cultural_region)
        
        # Get cultural sensitivities
        cultural_sensitivities = self._get_cultural_sensitivities(language, cultural_region)
        
        # Get timezone and date format preferences
        timezone = (cultural_preferences or {}).get("timezone")
        date_format = (cultural_preferences or {}).get("date_format")
        if not date_format:
            date_format = self._get_default_date_format(cultural_region)
        
        return CulturalContext(
            language=language,
            cultural_region=cultural_region,
            communication_style=communication_style,
            formality_level=formality_level,
            cultural_sensitivities=cultural_sensitivities,
            time_zone=timezone,
            date_format=date_format
        )
    
    async def normalize_text(
        self, 
        text: str, 
        cultural_context: CulturalContext
    ) -> str:
        """Normalize text based on cultural context"""
        
        language = cultural_context.language
        normalizer = self.text_normalizers.get(language, self.text_normalizers["default"])
        
        # Apply language-specific normalization
        normalized_text = normalizer(text)
        
        # Apply cultural adaptations to text
        if cultural_context.formality_level == "formal":
            normalized_text = self._apply_formal_adaptations(normalized_text, language)
        
        return normalized_text
    
    async def adapt_action_parameters(
        self,
        parameters: Dict[str, Any],
        cultural_adaptations: Dict[str, Any],
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """Adapt action parameters based on cultural context"""
        
        adapted_params = parameters.copy()
        
        # Apply language-specific adaptations
        language = cultural_context.language
        if language in self.cultural_adaptations:
            lang_adaptations = self.cultural_adaptations[language]
            
            # Adapt text content
            if "content" in adapted_params and isinstance(adapted_params["content"], str):
                adapted_params["content"] = self._adapt_text_content(
                    adapted_params["content"], lang_adaptations, cultural_context
                )
            
            # Adapt response style
            if "response_style" not in adapted_params:
                adapted_params["response_style"] = lang_adaptations.get("response_style", "neutral")
            
            # Adapt formality
            adapted_params["formality_level"] = cultural_context.formality_level
            
            # Add cultural context metadata
            adapted_params["cultural_metadata"] = {
                "language": language,
                "communication_style": cultural_context.communication_style,
                "cultural_sensitivities": cultural_context.cultural_sensitivities
            }
        
        return adapted_params
    
    async def create_response_message(
        self,
        workflow_result: WorkflowResult,
        cultural_context: CulturalContext
    ) -> str:
        """Create culturally appropriate response message"""
        
        language = cultural_context.language
        status = workflow_result.status
        
        # Get base message templates
        templates = self._get_message_templates(language)
        
        # Select appropriate template based on status
        if status.value == "completed":
            if workflow_result.failed_actions == 0:
                template = templates["success"]
            else:
                template = templates["partial_success"]
        elif status.value == "failed":
            template = templates["failure"]
        elif status.value == "rolled_back":
            template = templates["rollback"]
        else:
            template = templates["processing"]
        
        # Customize message based on cultural context
        message = self._customize_message(template, workflow_result, cultural_context)
        
        return message
    
    async def adapt_response(
        self,
        workflow_result: WorkflowResult,
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """Create cultural adaptations for response"""
        
        adaptations = {
            "language": cultural_context.language,
            "communication_style": cultural_context.communication_style,
            "formality_level": cultural_context.formality_level
        }
        
        # Add language-specific adaptations
        if cultural_context.language == "hi":
            adaptations.update({
                "greeting_style": "respectful",
                "address_form": "formal",
                "response_tone": "warm"
            })
        elif cultural_context.language == "en":
            adaptations.update({
                "greeting_style": "friendly",
                "address_form": "casual",
                "response_tone": "supportive"
            })
        
        # Add cultural sensitivities
        if cultural_context.cultural_sensitivities:
            adaptations["cultural_considerations"] = cultural_context.cultural_sensitivities
        
        return adaptations
    
    def _initialize_language_patterns(self) -> Dict[str, str]:
        """Initialize language detection patterns"""
        return {
            "en": r"[a-zA-Z\s]+",
            "hi": r"[\u0900-\u097F\s]+",  # Devanagari script
            "es": r"[a-zA-ZñÑáéíóúüÁÉÍÓÚÜ\s]+",
            "fr": r"[a-zA-ZàâäéèêëîïôöùûüÿÀÂÄÉÈÊËÎÏÔÖÙÛÜŸ\s]+",
            "de": r"[a-zA-ZäöüßÄÖÜ\s]+"
        }
    
    def _initialize_cultural_adaptations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cultural adaptation settings"""
        return {
            "en": {
                "response_style": "direct",
                "greeting_style": "casual",
                "formality_default": "moderate",
                "cultural_values": ["individuality", "directness", "efficiency"]
            },
            "hi": {
                "response_style": "respectful",
                "greeting_style": "formal",
                "formality_default": "high",
                "cultural_values": ["respect", "family", "harmony", "tradition"]
            },
            "es": {
                "response_style": "warm",
                "greeting_style": "friendly",
                "formality_default": "moderate",
                "cultural_values": ["family", "warmth", "community"]
            }
        }
    
    def _initialize_text_normalizers(self) -> Dict[str, Any]:
        """Initialize text normalization functions"""
        
        def default_normalizer(text: str) -> str:
            # Basic normalization
            text = re.sub(r'\s+', ' ', text.strip())
            text = re.sub(r'[^\w\s.,!?-]', '', text)
            return text
        
        def hindi_normalizer(text: str) -> str:
            # Hindi-specific normalization
            text = default_normalizer(text)
            # Add Hindi-specific rules here
            return text
        
        return {
            "default": default_normalizer,
            "en": default_normalizer,
            "hi": hindi_normalizer
        }
    
    async def _detect_language(self, text: str) -> str:
        """Detect language from text input"""
        # Simple pattern-based detection
        # In production, this would use a proper language detection library
        
        for lang, pattern in self.language_detection_patterns.items():
            if re.search(pattern, text):
                # Calculate match percentage
                matches = len(re.findall(pattern, text))
                total_chars = len(text.replace(' ', ''))
                if total_chars > 0 and matches / total_chars > 0.5:
                    return lang
        
        return "en"  # Default to English
    
    def _infer_cultural_region(self, language: str) -> str:
        """Infer cultural region from language"""
        region_mapping = {
            "en": "global",
            "hi": "india_north",  # Hindi - North India
            "ta": "india_south",  # Tamil - South India
            "te": "india_south",  # Telugu - South India  
            "kn": "india_south",  # Kannada - South India
            "ml": "india_south",  # Malayalam - South India
            "mr": "india_west",   # Marathi - West India
            "gu": "india_west",   # Gujarati - West India
            "bn": "india_east",   # Bengali - East India
            "or": "india_east",   # Odia - East India
            "as": "india_northeast",  # Assamese - Northeast India
            "pa": "india_north",  # Punjabi - North India
            "ur": "india_north",  # Urdu - North India
            "es": "latin_america",
            "fr": "europe",
            "de": "europe",
            "ar": "middle_east",
            "ja": "east_asia",
            "ko": "east_asia",
            "zh": "east_asia"
        }
        return region_mapping.get(language, "global")
    
    def _infer_communication_style(self, language: str, cultural_region: str) -> str:
        """Infer communication style from language and region"""
        if language == "hi" or cultural_region == "south_asia":
            return "respectful"
        elif language == "en" and cultural_region == "global":
            return "direct"
        elif language == "es":
            return "warm"
        else:
            return "neutral"
    
    def _infer_formality_level(self, language: str, cultural_region: str) -> str:
        """Infer formality level from language and region"""
        if language == "hi" or cultural_region == "south_asia":
            return "high"
        elif language == "de":
            return "high"
        elif language == "en":
            return "moderate"
        else:
            return "moderate"
    
    def _get_cultural_sensitivities(self, language: str, cultural_region: str) -> List[str]:
        """Get cultural sensitivities for the region"""
        sensitivity_mapping = {
            ("hi", "india_north"): ["family_values", "religious_respect", "elder_respect", "caste_sensitivity"],
            ("hi", "india_central"): ["family_values", "religious_respect", "elder_respect", "traditional_values"],
            ("ta", "india_south"): ["family_values", "educational_respect", "cultural_pride", "language_pride"],
            ("te", "india_south"): ["family_values", "hospitality", "cultural_traditions", "respect_for_elders"],
            ("mr", "india_west"): ["family_values", "business_ethics", "festival_importance", "community_bonds"],
            ("gu", "india_west"): ["family_values", "business_values", "vegetarianism", "community_service"],
            ("bn", "india_east"): ["intellectual_respect", "artistic_appreciation", "family_values", "cultural_heritage"],
            ("as", "india_northeast"): ["nature_respect", "tribal_sensitivity", "community_harmony", "simplicity"],
            ("en", "global"): ["privacy", "personal_space"],
            ("es", "latin_america"): ["family_importance", "personal_relationships"],
            ("ar", "middle_east"): ["religious_considerations", "family_honor"],
            ("hi", "south_asia"): ["family_values", "religious_respect", "elder_respect"]
        }
        
        key = (language, cultural_region)
        return sensitivity_mapping.get(key, ["general_respect"])
    
    def _get_default_date_format(self, cultural_region: str) -> str:
        """Get default date format for cultural region"""
        format_mapping = {
            "global": "MM/DD/YYYY",
            "europe": "DD/MM/YYYY",
            "south_asia": "DD/MM/YYYY",
            "east_asia": "YYYY/MM/DD"
        }
        return format_mapping.get(cultural_region, "MM/DD/YYYY")
    
    def _apply_formal_adaptations(self, text: str, language: str) -> str:
        """Apply formal language adaptations"""
        if language == "hi":
            # Add Hindi formal adaptations
            pass
        elif language == "en":
            # Add English formal adaptations
            text = text.replace("hey", "hello")
            text = text.replace("gonna", "going to")
            text = text.replace("wanna", "want to")
        
        return text
    
    def _adapt_text_content(
        self, 
        content: str, 
        lang_adaptations: Dict[str, Any], 
        cultural_context: CulturalContext
    ) -> str:
        """Adapt text content based on cultural context"""
        
        adapted_content = content
        
        # Apply cultural value adaptations
        cultural_values = lang_adaptations.get("cultural_values", [])
        
        if "respect" in cultural_values:
            # Add respectful language patterns
            pass
        
        if "family" in cultural_values:
            # Consider family context in content
            pass
        
        return adapted_content
    
    def _get_message_templates(self, language: str) -> Dict[str, str]:
        """Get response message templates for language"""
        
        templates = {
            "en": {
                "success": "I've successfully completed your request. Everything went smoothly!",
                "partial_success": "I've completed most of your request, though there were some minor issues.",
                "failure": "I apologize, but I encountered some difficulties processing your request.",
                "rollback": "I had to undo some changes due to an issue, but your data is safe.",
                "processing": "I'm currently working on your request. Please wait a moment."
            },
            "hi": {
                "success": "मैंने आपका अनुरोध सफलतापूर्वक पूरा कर दिया है। सब कुछ ठीक से हुआ है!",
                "partial_success": "मैंने आपका अधिकांश अनुरोध पूरा कर दिया है, हालांकि कुछ छोटी समस्याएं थीं।",
                "failure": "मुझे खेद है, लेकिन आपका अनुरोध प्रोसेस करने में कुछ कठिनाइयों का सामना करना पड़ा।",
                "rollback": "एक समस्या के कारण मुझे कुछ बदलावों को पूर्ववत करना पड़ा, लेकिन आपका डेटा सुरक्षित है।",
                "processing": "मैं वर्तमान में आपके अनुरोध पर काम कर रहा हूं। कृपया थोड़ा इंतज़ार करें।"
            }
        }
        
        return templates.get(language, templates["en"])
    
    def _customize_message(
        self, 
        template: str, 
        workflow_result: WorkflowResult, 
        cultural_context: CulturalContext
    ) -> str:
        """Customize message template based on context"""
        
        message = template
        
        # Add specific details based on formality level
        if cultural_context.formality_level == "high":
            if cultural_context.language == "en":
                message = f"Dear user, {message.lower()}"
            elif cultural_context.language == "hi":
                message = f"आदरणीय उपयोगकर्ता, {message}"
        
        # Add timing information
        if workflow_result.total_execution_time_ms > 0:
            time_seconds = workflow_result.total_execution_time_ms / 1000
            if cultural_context.language == "en":
                message += f" (Completed in {time_seconds:.1f} seconds)"
            elif cultural_context.language == "hi":
                message += f" ({time_seconds:.1f} सेकंड में पूरा हुआ)"
        
        return message
    
    @property
    def supported_regions(self) -> List[str]:
        """Get list of supported cultural regions"""
        return [
            "north_america",
            "europe", 
            "india_north",
            "india_south", 
            "india_west",
            "india_east",
            "india_northeast",
            "india_central",
            "south_asia",
            "east_asia",
            "middle_east",
            "latin_america",
            "africa",
            "oceania"
        ]
    
    def _get_cultural_defaults(self, region: str) -> Dict[str, Any]:
        """Get cultural defaults for a specific region"""
        defaults = {
            "north_america": {
                "communication_style": "direct",
                "formality_level": "medium",
                "date_format": "MM/DD/YYYY",
                "time_format": "12h",
                "currency": "USD",
                "language": "en"
            },
            "europe": {
                "communication_style": "diplomatic", 
                "formality_level": "high",
                "date_format": "DD/MM/YYYY",
                "time_format": "24h",
                "currency": "EUR",
                "language": "en"
            },
            "india_north": {
                "communication_style": "respectful",
                "formality_level": "high",
                "date_format": "DD/MM/YYYY",
                "time_format": "12h",
                "currency": "INR",
                "language": "hi",
                "cultural_values": ["family", "respect", "tradition", "hierarchy"],
                "festivals": ["diwali", "holi", "karva_chauth", "dussehra"]
            },
            "india_south": {
                "communication_style": "respectful",
                "formality_level": "high", 
                "date_format": "DD/MM/YYYY",
                "time_format": "12h",
                "currency": "INR",
                "language": "ta",  # Tamil as primary, but supports multiple
                "cultural_values": ["family", "education", "tradition", "spirituality"],
                "festivals": ["pongal", "onam", "diwali", "navratri"]
            },
            "india_west": {
                "communication_style": "business_friendly",
                "formality_level": "medium",
                "date_format": "DD/MM/YYYY", 
                "time_format": "12h",
                "currency": "INR",
                "language": "mr",  # Marathi/Gujarati
                "cultural_values": ["entrepreneurship", "family", "festivals", "trade"],
                "festivals": ["ganesh_chaturthi", "navratri", "diwali", "gudi_padwa"]
            },
            "india_east": {
                "communication_style": "intellectual",
                "formality_level": "high",
                "date_format": "DD/MM/YYYY",
                "time_format": "12h", 
                "currency": "INR",
                "language": "bn",  # Bengali
                "cultural_values": ["literature", "arts", "family", "intellect"],
                "festivals": ["durga_puja", "kali_puja", "poila_boishakh", "diwali"]
            },
            "india_northeast": {
                "communication_style": "warm",
                "formality_level": "medium",
                "date_format": "DD/MM/YYYY",
                "time_format": "12h",
                "currency": "INR", 
                "language": "as",  # Assamese
                "cultural_values": ["nature", "community", "simplicity", "harmony"],
                "festivals": ["bihu", "durga_puja", "kali_puja", "christmas"]
            },
            "india_central": {
                "communication_style": "traditional",
                "formality_level": "high",
                "date_format": "DD/MM/YYYY",
                "time_format": "12h",
                "currency": "INR",
                "language": "hi",
                "cultural_values": ["tradition", "spirituality", "family", "agriculture"],
                "festivals": ["diwali", "holi", "navratri", "dussehra"]
            },
            "south_asia": {
                "communication_style": "respectful",
                "formality_level": "high", 
                "date_format": "DD/MM/YYYY",
                "time_format": "12h",
                "currency": "INR",
                "language": "hi"
            },
            "east_asia": {
                "communication_style": "indirect",
                "formality_level": "high",
                "date_format": "YYYY/MM/DD", 
                "time_format": "24h",
                "currency": "JPY",
                "language": "ja"
            },
            "middle_east": {
                "communication_style": "respectful",
                "formality_level": "high",
                "date_format": "DD/MM/YYYY",
                "time_format": "12h", 
                "currency": "AED",
                "language": "ar"
            },
            "latin_america": {
                "communication_style": "warm",
                "formality_level": "medium",
                "date_format": "DD/MM/YYYY",
                "time_format": "12h",
                "currency": "USD",
                "language": "es"
            },
            "africa": {
                "communication_style": "respectful",
                "formality_level": "medium", 
                "date_format": "DD/MM/YYYY",
                "time_format": "24h",
                "currency": "USD",
                "language": "en"
            },
            "oceania": {
                "communication_style": "casual",
                "formality_level": "low",
                "date_format": "DD/MM/YYYY", 
                "time_format": "12h",
                "currency": "AUD",
                "language": "en"
            }
        }
        
        return defaults.get(region, defaults["north_america"])
