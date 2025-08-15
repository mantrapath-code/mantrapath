"""
Response Models for MantraPath API Gateway V3
Enhanced response data models
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class EnhancedResponse(BaseModel):
    """Enhanced response data model"""
    status: str
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_info: Optional[Dict[str, Any]] = None