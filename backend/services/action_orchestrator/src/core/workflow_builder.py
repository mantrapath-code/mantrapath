"""
Workflow Builder
Constructs cross-service workflows based on voice intents and cultural context
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4, UUID

from ..models import (
    VoiceIntent, ActionWorkflow, WorkflowStep, ServiceAction,
    IntentType, WorkflowStatus, CulturalContext
)

logger = logging.getLogger(__name__)


class WorkflowBuilder:
    """
    Builds cross-service workflows based on voice intents
    
    Creates structured workflows with proper step ordering,
    dependencies, and rollback actions
    """
    
    def __init__(self):
        # Service endpoint configurations
        self.service_endpoints = self._initialize_service_endpoints()
        
        # Workflow templates for different intent types
        self.workflow_templates = self._initialize_workflow_templates()
        
        # Action dependencies mapping
        self.action_dependencies = self._initialize_action_dependencies()
        
        logger.info("Workflow Builder initialized")
    
    async def build_workflow(
        self,
        intent: VoiceIntent,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionWorkflow:
        """
        Build workflow based on voice intent and context
        
        Returns a complete ActionWorkflow with steps, actions, and rollback plans
        """
        try:
            # Get workflow template for intent type
            template = self.workflow_templates.get(
                intent.intent_type,
                self.workflow_templates[IntentType.UNKNOWN]
            )
            
            # Build workflow steps
            steps = await self._build_workflow_steps(intent, template, context)
            
            # Build rollback steps
            rollback_steps = await self._build_rollback_steps(steps)
            
            # Create workflow
            workflow = ActionWorkflow(
                intent=intent,
                steps=steps,
                status=WorkflowStatus.PENDING,
                rollback_steps=rollback_steps,
                cultural_context=intent.cultural_context
            )
            
            logger.info(f"Built workflow with {len(steps)} steps for intent {intent.intent_type}")
            return workflow
            
        except Exception as e:
            logger.error(f"Workflow building failed: {str(e)}", exc_info=True)
            
            # Create minimal fallback workflow
            fallback_workflow = await self._create_fallback_workflow(intent)
            return fallback_workflow
    
    async def _build_workflow_steps(
        self,
        intent: VoiceIntent,
        template: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[WorkflowStep]:
        """Build workflow steps from template and intent"""
        
        steps = []
        step_templates = template.get("steps", [])
        
        for step_template in step_templates:
            # Build actions for this step
            actions = await self._build_step_actions(
                intent, step_template, context
            )
            
            # Create workflow step
            step = WorkflowStep(
                actions=actions,
                parallel_execution=step_template.get("parallel_execution", False),
                success_condition=step_template.get("success_condition"),
                failure_handling=step_template.get("failure_handling", "continue")
            )
            
            steps.append(step)
        
        return steps
    
    async def _build_step_actions(
        self,
        intent: VoiceIntent,
        step_template: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ServiceAction]:
        """Build actions for a workflow step"""
        
        actions = []
        action_templates = step_template.get("actions", [])
        
        for action_template in action_templates:
            # Extract base action info
            service_name = action_template["service"]
            action_type = action_template["action_type"]
            
            # Build parameters from intent and template
            parameters = await self._build_action_parameters(
                intent, action_template, context
            )
            
            # Get cultural adaptations
            cultural_adaptations = await self._get_cultural_adaptations(
                action_template, intent.cultural_context
            )
            
            # Build rollback action if specified
            rollback_action = None
            if "rollback" in action_template:
                rollback_action = action_template["rollback"]
            
            # Get dependencies
            dependencies = self._resolve_action_dependencies(
                action_template.get("dependencies", [])
            )
            
            # Create service action
            action = ServiceAction(
                service_name=service_name,
                action_type=action_type,
                parameters=parameters,
                cultural_adaptations=cultural_adaptations,
                timeout_seconds=action_template.get("timeout", 30),
                retry_count=action_template.get("retry_count", 3),
                rollback_action=rollback_action,
                dependencies=dependencies
            )
            
            actions.append(action)
        
        return actions
    
    async def _build_action_parameters(
        self,
        intent: VoiceIntent,
        action_template: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build action parameters from intent and template"""
        
        parameters = {}
        
        # Start with template default parameters
        parameters.update(action_template.get("default_parameters", {}))
        
        # Add intent-specific parameters
        if intent.parameters:
            # Map intent parameters to action parameters
            parameter_mapping = action_template.get("parameter_mapping", {})
            for intent_param, intent_value in intent.parameters.items():
                if intent_param in parameter_mapping:
                    action_param = parameter_mapping[intent_param]
                    parameters[action_param] = intent_value
                else:
                    # Direct mapping if no specific mapping defined
                    parameters[intent_param] = intent_value
        
        # Add context parameters
        if context:
            context_mapping = action_template.get("context_mapping", {})
            for context_key, context_value in context.items():
                if context_key in context_mapping:
                    action_param = context_mapping[context_key]
                    parameters[action_param] = context_value
        
        # Add standard parameters
        parameters["user_id"] = str(intent.user_id)
        if intent.session_id:
            parameters["session_id"] = str(intent.session_id)
        
        # Add cultural context
        parameters["language"] = intent.cultural_context.language
        parameters["cultural_region"] = intent.cultural_context.cultural_region
        
        return parameters
    
    async def _get_cultural_adaptations(
        self,
        action_template: Dict[str, Any],
        cultural_context: Any
    ) -> Dict[str, Any]:
        """Get cultural adaptations for action"""
        
        adaptations = {}
        
        # Get template-defined adaptations
        template_adaptations = action_template.get("cultural_adaptations", {})
        language = cultural_context.language
        
        if language in template_adaptations:
            adaptations.update(template_adaptations[language])
        
        # Add general cultural adaptations
        adaptations["language"] = language
        adaptations["formality_level"] = cultural_context.formality_level
        adaptations["communication_style"] = cultural_context.communication_style
        
        return adaptations
    
    def _resolve_action_dependencies(self, dependency_names: List[str]) -> List[Any]:
        """Resolve action dependencies to action IDs"""
        # This would resolve symbolic dependency names to actual action IDs
        # For now, return empty list as dependencies are resolved at runtime
        return []
    
    async def _build_rollback_steps(
        self, 
        forward_steps: List[WorkflowStep]
    ) -> List[WorkflowStep]:
        """Build rollback steps for workflow"""
        
        rollback_steps = []
        
        # Create rollback steps in reverse order
        for step in reversed(forward_steps):
            rollback_actions = []
            
            for action in reversed(step.actions):
                if action.rollback_action:
                    # Create rollback action
                    rollback_service_action = ServiceAction(
                        service_name=action.service_name,
                        action_type=action.rollback_action["action_type"],
                        parameters=action.rollback_action.get("parameters", {}),
                        cultural_adaptations=action.cultural_adaptations,
                        timeout_seconds=action.rollback_action.get("timeout", 30),
                        retry_count=action.rollback_action.get("retry_count", 2)
                    )
                    rollback_actions.append(rollback_service_action)
            
            if rollback_actions:
                rollback_step = WorkflowStep(
                    actions=rollback_actions,
                    parallel_execution=False,  # Rollbacks should be sequential
                    failure_handling="continue"  # Continue rollback even if some fail
                )
                rollback_steps.append(rollback_step)
        
        return rollback_steps
    
    async def _create_fallback_workflow(self, intent: VoiceIntent) -> ActionWorkflow:
        """Create minimal fallback workflow for error cases"""
        
        # Create a simple acknowledgment action
        fallback_action = ServiceAction(
            service_name="chatbot_service",
            action_type="send_response",
            parameters={
                "message": "I understand your request but need more information to help you.",
                "user_id": str(intent.user_id),
                "language": intent.cultural_context.language
            },
            cultural_adaptations={
                "language": intent.cultural_context.language,
                "formality_level": intent.cultural_context.formality_level
            }
        )
        
        fallback_step = WorkflowStep(
            actions=[fallback_action],
            parallel_execution=False,
            failure_handling="continue"
        )
        
        return ActionWorkflow(
            intent=intent,
            steps=[fallback_step],
            status=WorkflowStatus.PENDING,
            cultural_context=intent.cultural_context
        )
    
    def _initialize_service_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Initialize service endpoint configurations"""
        return {
            "mood_service": {
                "base_url": "http://mood-service:8003",
                "timeout": 30,
                "retry_count": 3
            },
            "journal_service": {
                "base_url": "http://journal-service:8004",
                "timeout": 45,
                "retry_count": 3
            },
            "chatbot_service": {
                "base_url": "http://chatbot-service:8008",
                "timeout": 30,
                "retry_count": 2
            },
            "profile_service": {
                "base_url": "http://profile-service:8002",
                "timeout": 20,
                "retry_count": 3
            },
            "community_service": {
                "base_url": "http://community-service:8006",
                "timeout": 30,
                "retry_count": 2
            },
            "analytics_service": {
                "base_url": "http://ml-service:8010",
                "timeout": 60,
                "retry_count": 2
            }
        }
    
    def _initialize_workflow_templates(self) -> Dict[IntentType, Dict[str, Any]]:
        """Initialize workflow templates for different intent types"""
        return {
            IntentType.MOOD_TRACKING: {
                "description": "Track user mood and update analytics",
                "steps": [
                    {
                        "name": "validate_mood_data",
                        "parallel_execution": False,
                        "actions": [
                            {
                                "service": "mood_service",
                                "action_type": "validate_mood_entry",
                                "parameter_mapping": {
                                    "mood_value": "mood_score",
                                    "emotion_type": "primary_emotion",
                                    "intensity": "emotion_intensity"
                                },
                                "timeout": 15,
                                "dependencies": []
                            }
                        ]
                    },
                    {
                        "name": "save_and_analyze",
                        "parallel_execution": True,
                        "actions": [
                            {
                                "service": "mood_service",
                                "action_type": "save_mood_entry",
                                "parameter_mapping": {
                                    "mood_value": "mood_score",
                                    "emotion_type": "primary_emotion"
                                },
                                "rollback": {
                                    "action_type": "delete_mood_entry",
                                    "parameters": {"entry_id": "${saved_entry_id}"}
                                },
                                "timeout": 20
                            },
                            {
                                "service": "analytics_service",
                                "action_type": "update_mood_analytics",
                                "parameter_mapping": {
                                    "mood_value": "mood_score"
                                },
                                "timeout": 30
                            }
                        ]
                    }
                ]
            },
            
            IntentType.JOURNAL_ENTRY: {
                "description": "Create and analyze journal entry",
                "steps": [
                    {
                        "name": "process_journal_content",
                        "parallel_execution": False,
                        "actions": [
                            {
                                "service": "journal_service",
                                "action_type": "create_journal_entry",
                                "parameter_mapping": {
                                    "content": "journal_content",
                                    "privacy_level": "privacy_setting"
                                },
                                "rollback": {
                                    "action_type": "delete_journal_entry",
                                    "parameters": {"entry_id": "${created_entry_id}"}
                                },
                                "timeout": 30
                            }
                        ]
                    },
                    {
                        "name": "analyze_and_respond",
                        "parallel_execution": True,
                        "actions": [
                            {
                                "service": "analytics_service",
                                "action_type": "analyze_journal_sentiment",
                                "parameter_mapping": {
                                    "content": "journal_content"
                                },
                                "timeout": 45
                            },
                            {
                                "service": "chatbot_service",
                                "action_type": "generate_journal_response",
                                "parameter_mapping": {
                                    "content": "journal_content"
                                },
                                "cultural_adaptations": {
                                    "en": {"response_style": "supportive"},
                                    "hi": {"response_style": "respectful"}
                                },
                                "timeout": 25
                            }
                        ]
                    }
                ]
            },
            
            IntentType.CHAT_CONVERSATION: {
                "description": "Handle chat conversation",
                "steps": [
                    {
                        "name": "process_chat_message",
                        "parallel_execution": False,
                        "actions": [
                            {
                                "service": "chatbot_service",
                                "action_type": "process_message",
                                "parameter_mapping": {
                                    "content": "processed_text"
                                },
                                "cultural_adaptations": {
                                    "en": {"tone": "friendly"},
                                    "hi": {"tone": "respectful"}
                                },
                                "timeout": 30
                            }
                        ]
                    }
                ]
            },
            
            IntentType.ANALYTICS_QUERY: {
                "description": "Retrieve analytics data",
                "steps": [
                    {
                        "name": "fetch_analytics",
                        "parallel_execution": True,
                        "actions": [
                            {
                                "service": "analytics_service",
                                "action_type": "get_user_analytics",
                                "parameter_mapping": {
                                    "time_range": "analysis_period",
                                    "metric_type": "data_type"
                                },
                                "timeout": 45
                            },
                            {
                                "service": "mood_service",
                                "action_type": "get_mood_trends",
                                "parameter_mapping": {
                                    "time_range": "analysis_period"
                                },
                                "timeout": 30
                            }
                        ]
                    }
                ]
            },
            
            IntentType.UNKNOWN: {
                "description": "Fallback workflow for unknown intents",
                "steps": [
                    {
                        "name": "clarification_request",
                        "parallel_execution": False,
                        "actions": [
                            {
                                "service": "chatbot_service",
                                "action_type": "request_clarification",
                                "default_parameters": {
                                    "message": "I'm not sure I understood. Could you please rephrase?"
                                },
                                "cultural_adaptations": {
                                    "hi": {"message": "मुझे यकीन नहीं है कि मैं समझ गया। क्या आप कृपया दोबारा कह सकते हैं?"}
                                },
                                "timeout": 15
                            }
                        ]
                    }
                ]
            }
        }
    
    def _initialize_action_dependencies(self) -> Dict[str, List[str]]:
        """Initialize action dependency mappings"""
        return {
            "save_mood_entry": ["validate_mood_data"],
            "update_mood_analytics": ["save_mood_entry"],
            "analyze_journal_sentiment": ["create_journal_entry"],
            "generate_journal_response": ["create_journal_entry"]
        }
