"""
Context Models for MantraPath API Gateway V3
Data models for AI and cultural context
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class AIContext(BaseModel):
    """AI context data model"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context_data: Dict[str, Any] = {}
    
    def to_header(self) -> str:
        """Convert to header string"""
        return f"user_id={self.user_id or ''};session_id={self.session_id or ''}"


class CulturalContext(BaseModel):
    """Cultural context data model"""
    language: Optional[str] = None
    region: Optional[str] = None
    cultural_preferences: Dict[str, Any] = {}
    
    def to_header(self) -> str:
        """Convert to header string"""
        return f"lang={self.language or ''};region={self.region or ''}"