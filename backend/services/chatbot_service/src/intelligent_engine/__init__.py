"""
Intelligent Engine Module for MantraPath Chatbot Service

This module contains the core intelligence components for the mood-aware,
behavior-adaptive chatbot system that integrates with all MantraPath services.

Components:
    - MoodAwareResponder: Core mood-aware response generation
    - ServiceIntegrator: Multi-service data integration
    - ContextAnalyzer: User context analysis and processing
    - ResponseGenerator: Intelligent response generation engine
    
Author: MantraPath Development Team
Version: 1.0.0
"""

from .mood_aware_responder import MoodAwareResponder
from .service_integrator import ServiceIntegrator
from .context_analyzer import ContextAnalyzer
from .response_generator import ResponseGenerator

__all__ = [
    'MoodAwareResponder',
    'ServiceIntegrator', 
    'ContextAnalyzer',
    'ResponseGenerator'
]

# Version information
__version__ = '1.0.0'
__author__ = 'MantraPath Development Team'
