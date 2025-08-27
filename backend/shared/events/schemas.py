"""
Shared event payload schemas for MantraPath V3
Single source of truth for event contracts used across services.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Core assistance events
class AssistanceInterventionNeeded(BaseModel):
    user_id: str
    risk_level: str
    recommended_actions: List[str]
    reason: str
    ts: datetime

class AssistanceTriggered(BaseModel):
    user_id: str
    assistance_type: Optional[str] = None
    channel: Optional[str] = None
    ts: datetime

class AssistanceDelivered(BaseModel):
    user_id: str
    assistance_type: Optional[str] = None
    status: str
    ts: datetime

class AssistanceUserResponse(BaseModel):
    user_id: str
    assistance_type: Optional[str] = None
    response: str  # "accepted" | "declined"
    feedback: Optional[str] = None
    ts: datetime

# Upstream event examples
class ContextUpdated(BaseModel):
    user_id: str
    fields_changed: List[str]
    ts: datetime

class AIEmotionDetected(BaseModel):
    user_id: str
    emotion: str
    score: float
    ts: datetime

class VoiceActivityDetected(BaseModel):
    user_id: str
    activity: str
    details: Dict[str, Any] = Field(default_factory=dict)
    ts: datetime
