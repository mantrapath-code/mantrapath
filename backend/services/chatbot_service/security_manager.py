"""
Security Manager for MantraPath Chatbot

Comprehensive security validation, input sanitization, and content filtering
for safe, therapeutic conversations with robust threat detection.

Author: MantraPath Development Team
Version: 3.0.0
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import asyncio

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Comprehensive security manager for conversation safety
    """
    
    def __init__(self):
        # Threat detection patterns
        self.threat_patterns = {
            "self_harm": [
                r"\bkill\s+(myself|me)\b", r"\bsuicide\b", r"\bend\s+it\s+all\b",
                r"\bcut\s+(myself|me)\b", r"\bhurt\s+(myself|me)\b"
            ],
            "harmful_content": [
                r"\b(bomb|explosive|weapon)\b", r"\b(drug|illegal)\s+making\b",
                r"\bhack\b.*\binto\b", r"\bsteal\b.*\bpassword\b"
            ],
            "inappropriate": [
                r"\bsex(ual)?\b.*\bexplicit\b", r"\bpornography\b",
                r"\binappropriate\b.*\bcontent\b"
            ]
        }
        
        # Content filtering rules
        self.content_filters = {
            "profanity": ["fuck", "shit", "damn", "hell"],  # Basic filter
            "spam_indicators": ["click here", "free money", "urgent response"],
            "injection_attempts": ["<script>", "javascript:", "eval(", "exec("]
        }
        
        # Crisis intervention keywords (higher sensitivity)
        self.crisis_keywords = [
            "suicide", "kill myself", "end it all", "can't go on", "hopeless",
            "worthless", "better off dead", "no point", "give up"
        ]
        
        logger.info("SecurityManager initialized with comprehensive threat detection")
    
    async def validate_input(self, user_input: str, user_profile: Dict) -> Dict[str, Any]:
        """
        Comprehensive input validation and security analysis
        
        Args:
            user_input: User's message content
            user_profile: User profile for context-aware validation
            
        Returns:
            Validation result with safety assessment and recommendations
        """
        validation_start = datetime.utcnow()
        
        # Basic input sanitization
        sanitized_input = self._sanitize_input(user_input)
        
        # Threat detection analysis
        threat_analysis = await self._detect_threats(sanitized_input)
        
        # Crisis detection (high priority)
        crisis_analysis = self._detect_crisis_indicators(sanitized_input)
        
        # Content appropriateness check
        content_analysis = self._analyze_content_appropriateness(sanitized_input)
        
        # Generate security score
        security_score = self._calculate_security_score(
            threat_analysis, crisis_analysis, content_analysis
        )
        
        # Determine validation result
        is_safe = security_score["overall_safety"] >= 0.7
        requires_intervention = crisis_analysis["crisis_detected"] or security_score["threat_level"] > 0.6
        
        validation_result = {
            "is_safe": is_safe,
            "requires_intervention": requires_intervention,
            "security_score": security_score,
            "threat_analysis": threat_analysis,
            "crisis_analysis": crisis_analysis,
            "content_analysis": content_analysis,
            "sanitized_input": sanitized_input,
            "validation_level": "comprehensive",
            "processing_time": (datetime.utcnow() - validation_start).total_seconds(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log security events
        if requires_intervention:
            await self._log_security_event(user_profile.get("user_id"), validation_result)
        
        return validation_result
    
    def _sanitize_input(self, user_input: str) -> str:
        """
        Basic input sanitization while preserving conversational context
        """
        if not user_input:
            return ""
        
        # Remove potential injection attempts
        sanitized = user_input
        for injection in self.content_filters["injection_attempts"]:
            sanitized = sanitized.replace(injection, "[FILTERED]")
        
        # Clean excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized.strip())
        
        # Limit length (prevent abuse)
        if len(sanitized) > 2000:
            sanitized = sanitized[:2000] + "... [MESSAGE TRUNCATED]"
        
        return sanitized
    
    async def _detect_threats(self, user_input: str) -> Dict[str, Any]:
        """
        Advanced threat detection using pattern matching and context analysis
        """
        threat_scores = {}
        detected_threats = []
        
        user_input_lower = user_input.lower()
        
        # Check each threat category
        for threat_type, patterns in self.threat_patterns.items():
            threat_score = 0.0
            
            for pattern in patterns:
                matches = re.findall(pattern, user_input_lower, re.IGNORECASE)
                if matches:
                    threat_score += 0.3 * len(matches)
                    detected_threats.append({
                        "type": threat_type,
                        "pattern": pattern,
                        "matches": matches,
                        "severity": "high" if threat_type == "self_harm" else "medium"
                    })
            
            threat_scores[threat_type] = min(threat_score, 1.0)
        
        return {
            "threat_scores": threat_scores,
            "detected_threats": detected_threats,
            "max_threat_level": max(threat_scores.values()) if threat_scores else 0.0,
            "threat_categories": list(threat_scores.keys())
        }
    
    def _detect_crisis_indicators(self, user_input: str) -> Dict[str, Any]:
        """
        Specialized crisis detection with high sensitivity
        """
        user_input_lower = user_input.lower()
        
        # Direct crisis keyword matching
        crisis_matches = []
        crisis_score = 0.0
        
        for keyword in self.crisis_keywords:
            if keyword in user_input_lower:
                crisis_matches.append(keyword)
                crisis_score += 0.2
        
        # Contextual crisis indicators
        crisis_phrases = [
            "can't take it anymore", "nothing matters", "no way out",
            "everyone would be better", "tired of living", "no hope left"
        ]
        
        for phrase in crisis_phrases:
            if phrase in user_input_lower:
                crisis_matches.append(phrase)
                crisis_score += 0.3
        
        # Emotional intensity indicators
        intense_emotions = ["overwhelmed", "desperate", "trapped", "unbearable"]
        emotional_intensity = sum(1 for emotion in intense_emotions if emotion in user_input_lower)
        
        crisis_detected = crisis_score > 0.4 or len(crisis_matches) >= 2
        urgency_level = min(crisis_score * 5, 5.0)  # Scale to 1-5
        
        return {
            "crisis_detected": crisis_detected,
            "crisis_score": min(crisis_score, 1.0),
            "urgency_level": urgency_level,
            "crisis_indicators": crisis_matches,
            "emotional_intensity": emotional_intensity,
            "intervention_required": crisis_detected or urgency_level >= 4.0
        }
    
    def _analyze_content_appropriateness(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze content appropriateness for therapeutic context
        """
        user_input_lower = user_input.lower()
        
        # Check for inappropriate content
        inappropriate_score = 0.0
        inappropriate_elements = []
        
        for category, terms in self.content_filters.items():
            if category == "injection_attempts":
                continue  # Already handled in sanitization
            
            for term in terms:
                if term in user_input_lower:
                    inappropriate_elements.append({"category": category, "term": term})
                    inappropriate_score += 0.1
        
        # Professional boundary assessment
        boundary_violations = self._assess_boundary_violations(user_input_lower)
        
        # Content complexity (for age-appropriate responses)
        complexity_score = self._assess_content_complexity(user_input)
        
        return {
            "inappropriate_score": min(inappropriate_score, 1.0),
            "inappropriate_elements": inappropriate_elements,
            "boundary_violations": boundary_violations,
            "content_complexity": complexity_score,
            "is_appropriate": inappropriate_score < 0.3 and not boundary_violations,
            "requires_content_filter": inappropriate_score > 0.2
        }
    
    def _assess_boundary_violations(self, user_input_lower: str) -> List[str]:
        """
        Assess professional boundary violations
        """
        violations = []
        
        boundary_indicators = {
            "personal_requests": ["what's your name", "where do you live", "are you single"],
            "inappropriate_intimacy": ["love you", "attracted to", "date me"],
            "role_confusion": ["be my friend", "personal relationship", "outside therapy"]
        }
        
        for violation_type, indicators in boundary_indicators.items():
            for indicator in indicators:
                if indicator in user_input_lower:
                    violations.append(violation_type)
                    break
        
        return violations
    
    def _assess_content_complexity(self, user_input: str) -> Dict[str, Any]:
        """
        Assess content complexity for appropriate response tailoring
        """
        words = user_input.split()
        sentences = user_input.split('.')
        
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
        
        complexity_level = "simple"
        if avg_word_length > 6 or avg_sentence_length > 20:
            complexity_level = "complex"
        elif avg_word_length > 4 or avg_sentence_length > 12:
            complexity_level = "moderate"
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "complexity_level": complexity_level
        }
    
    def _calculate_security_score(
        self, 
        threat_analysis: Dict, 
        crisis_analysis: Dict, 
        content_analysis: Dict
    ) -> Dict[str, float]:
        """
        Calculate comprehensive security scoring
        """
        # Threat level calculation
        threat_level = threat_analysis["max_threat_level"]
        
        # Crisis risk calculation
        crisis_risk = crisis_analysis["crisis_score"]
        
        # Content appropriateness
        content_risk = content_analysis["inappropriate_score"]
        
        # Overall safety calculation (weighted)
        overall_safety = 1.0 - (
            (threat_level * 0.4) + 
            (crisis_risk * 0.4) + 
            (content_risk * 0.2)
        )
        
        return {
            "overall_safety": max(overall_safety, 0.0),
            "threat_level": threat_level,
            "crisis_risk": crisis_risk,
            "content_risk": content_risk,
            "safety_category": self._categorize_safety(overall_safety)
        }
    
    def _categorize_safety(self, safety_score: float) -> str:
        """
        Categorize safety level based on score
        """
        if safety_score >= 0.9:
            return "very_safe"
        elif safety_score >= 0.7:
            return "safe"
        elif safety_score >= 0.5:
            return "moderate_risk"
        elif safety_score >= 0.3:
            return "high_risk"
        else:
            return "critical_risk"
    
    async def _log_security_event(self, user_id: str, validation_result: Dict):
        """
        Log security events for monitoring and analysis
        """
        try:
            security_event = {
                "user_id": user_id,
                "event_type": "security_validation",
                "requires_intervention": validation_result["requires_intervention"],
                "security_score": validation_result["security_score"],
                "crisis_detected": validation_result["crisis_analysis"]["crisis_detected"],
                "threat_level": validation_result["threat_analysis"]["max_threat_level"],
                "timestamp": validation_result["timestamp"]
            }
            
            # In production, this would write to a secure audit log
            logger.warning(f"Security event logged: {security_event}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")

class InputValidator:
    """
    Input validation for data integrity and format checking
    """
    
    def __init__(self):
        logger.info("InputValidator initialized")
    
    def validate_message_format(self, user_input: str) -> Dict[str, Any]:
        """
        Validate message format and basic constraints
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for empty input
        if not user_input or not user_input.strip():
            validation_result["is_valid"] = False
            validation_result["errors"].append("Empty message not allowed")
        
        # Check length constraints
        if len(user_input) > 2000:
            validation_result["warnings"].append("Message exceeds recommended length")
        
        # Check for valid characters (allow most Unicode)
        if re.search(r'[^\w\s\.,!?;:()\-\'"@#$%&*+=<>/\\|`~\[\]{}^]', user_input):
            validation_result["warnings"].append("Message contains unusual characters")
        
        return validation_result
    
    def validate_user_context(self, user_profile: Dict) -> Dict[str, Any]:
        """
        Validate user context and profile data
        """
        required_fields = ["user_id"]
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "data_quality": "good"
        }
        
        for field in required_fields:
            if field not in user_profile:
                validation_result["is_valid"] = False
                validation_result["missing_fields"].append(field)
        
        return validation_result
