"""
🚨 Early Warning System - Phase 2A: Proactive Mental Health Intelligence

Real-time monitoring and intelligent alerting system that:
- Continuously monitors user mental health indicators
- Triggers intelligent alerts based on crisis predictions
- Manages escalation protocols and intervention recommendations
- Integrates with notification system for immediate response

This system transforms crisis prediction into actionable, life-saving interventions.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import asyncio
import os
from enum import Enum
from collections import deque
import redis
import uuid

# Import our crisis predictor
from .crisis_predictor import CrisisPredictionSystem

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels for crisis warnings"""
    CRITICAL = "CRITICAL"     # Immediate intervention required
    HIGH = "HIGH"             # Professional support recommended within hours
    MEDIUM = "MEDIUM"         # Increased monitoring and support
    LOW = "LOW"               # Routine check-in
    INFO = "INFO"             # Wellness information

class InterventionType(Enum):
    """Types of interventions that can be triggered"""
    CRISIS_HOTLINE = "crisis_hotline"
    EMERGENCY_CONTACT = "emergency_contact"
    PROFESSIONAL_REFERRAL = "professional_referral"
    PEER_SUPPORT = "peer_support"
    THERAPEUTIC_ACTIVITY = "therapeutic_activity"
    WELLNESS_CHECK = "wellness_check"
    BREATHING_EXERCISE = "breathing_exercise"

class EarlyWarningSystem:
    """
    🚨 Real-time Early Warning System for Mental Health Crises
    
    Monitors user data streams and triggers intelligent alerts when crisis
    prediction models indicate elevated risk. Manages escalation protocols
    and coordinates intervention responses.
    """
    
    def __init__(self):
        self.system_version = "2.0.0-warning"
        self.crisis_predictor = CrisisPredictionSystem()
        
        # Alert configuration
        self.alert_thresholds = {
            AlertLevel.CRITICAL: 0.85,
            AlertLevel.HIGH: 0.70,
            AlertLevel.MEDIUM: 0.50,
            AlertLevel.LOW: 0.30
        }
        
        # Monitoring intervals (minutes)
        self.monitoring_intervals = {
            AlertLevel.CRITICAL: 15,   # Every 15 minutes
            AlertLevel.HIGH: 60,       # Every hour
            AlertLevel.MEDIUM: 240,    # Every 4 hours
            AlertLevel.LOW: 720,       # Every 12 hours
            AlertLevel.INFO: 1440      # Daily
        }
        
        # Alert history and state management
        self.active_alerts = {}  # user_id -> alert_info
        self.alert_history = deque(maxlen=1000)
        self.user_alert_counts = {}  # user_id -> alert_count_by_level
        
        # Intervention tracking
        self.intervention_outcomes = {}
        self.escalation_rules = self._initialize_escalation_rules()
        
        # Redis for real-time communication
        try:
            self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
            self.redis_available = True
        except Exception as e:
            logger.warning(f"Redis not available for early warning system: {e}")
            self.redis_available = False
        
        # External service URLs
        self.notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8007")
        self.crisis_hotline_number = os.getenv("CRISIS_HOTLINE_NUMBER", "988")  # US Suicide & Crisis Lifeline
        
        logger.info("Early Warning System initialized successfully")
    
    async def monitor_user_risk(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 Main monitoring function - analyzes user data and triggers alerts if needed
        
        Args:
            user_id: Unique user identifier
            user_data: Current user data for analysis
        
        Returns:
            Monitoring result with any alerts triggered
        """
        try:
            # Get crisis prediction
            crisis_prediction = self.crisis_predictor.predict_crisis_risk(user_data)
            
            crisis_probability = crisis_prediction.get("crisis_probability", 0)
            current_alert_level = self._determine_alert_level(crisis_probability)
            
            # Check if alert should be triggered
            should_alert, alert_reason = self._should_trigger_alert(
                user_id, current_alert_level, crisis_prediction
            )
            
            monitoring_result = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "crisis_probability": crisis_probability,
                "alert_level": current_alert_level.value,
                "monitoring_active": True,
                "alert_triggered": should_alert,
                "next_check_in": self._calculate_next_check_time(current_alert_level).isoformat()
            }
            
            if should_alert:
                # Trigger alert workflow
                alert_response = await self._trigger_alert_workflow(
                    user_id, current_alert_level, crisis_prediction, alert_reason
                )
                monitoring_result.update(alert_response)
                
                logger.info(f"Alert triggered for user {user_id}: {current_alert_level.value} - {alert_reason}")
            else:
                # Update monitoring status without alert
                await self._update_monitoring_status(user_id, current_alert_level, crisis_prediction)
                
                logger.debug(f"Monitoring updated for user {user_id}: {current_alert_level.value} (no alert)")
            
            return monitoring_result
            
        except Exception as e:
            logger.error(f"Error in user risk monitoring for {user_id}: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "monitoring_active": False,
                "alert_triggered": False
            }
    
    async def _trigger_alert_workflow(
        self, 
        user_id: str, 
        alert_level: AlertLevel, 
        crisis_prediction: Dict, 
        reason: str
    ) -> Dict[str, Any]:
        """Comprehensive alert workflow with multiple intervention pathways"""
        
        alert_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Create alert record
        alert_info = {
            "alert_id": alert_id,
            "user_id": user_id,
            "alert_level": alert_level.value,
            "crisis_probability": crisis_prediction.get("crisis_probability", 0),
            "reason": reason,
            "timestamp": timestamp.isoformat(),
            "interventions_triggered": [],
            "status": "active"
        }
        
        # Determine appropriate interventions
        interventions = self._select_interventions(alert_level, crisis_prediction)
        
        # Execute interventions
        intervention_results = []
        for intervention_type in interventions:
            try:
                result = await self._execute_intervention(
                    user_id, intervention_type, alert_info, crisis_prediction
                )
                intervention_results.append(result)
                alert_info["interventions_triggered"].append(intervention_type.value)
                
            except Exception as e:
                logger.error(f"Failed to execute intervention {intervention_type.value}: {e}")
                intervention_results.append({
                    "type": intervention_type.value,
                    "success": False,
                    "error": str(e)
                })
        
        # Store alert in active alerts
        self.active_alerts[user_id] = alert_info
        self.alert_history.append(alert_info)
        
        # Update alert counts
        if user_id not in self.user_alert_counts:
            self.user_alert_counts[user_id] = {level.value: 0 for level in AlertLevel}
        self.user_alert_counts[user_id][alert_level.value] += 1
        
        # Broadcast alert via Redis for real-time systems
        if self.redis_available:
            await self._broadcast_alert(alert_info)
        
        return {
            "alert_id": alert_id,
            "alert_level": alert_level.value,
            "interventions_executed": len(intervention_results),
            "intervention_results": intervention_results,
            "next_escalation_check": self._calculate_escalation_time(alert_level).isoformat(),
            "alert_active": True
        }
    
    def _select_interventions(self, alert_level: AlertLevel, crisis_prediction: Dict) -> List[InterventionType]:
        """Select appropriate interventions based on alert level and risk factors"""
        
        interventions = []
        crisis_prob = crisis_prediction.get("crisis_probability", 0)
        urgency = crisis_prediction.get("urgency_level", "ROUTINE")
        
        if alert_level == AlertLevel.CRITICAL:
            # Immediate, multi-pronged response
            interventions.extend([
                InterventionType.CRISIS_HOTLINE,
                InterventionType.EMERGENCY_CONTACT,
                InterventionType.PROFESSIONAL_REFERRAL
            ])
            
        elif alert_level == AlertLevel.HIGH:
            # Professional support with peer backup
            interventions.extend([
                InterventionType.PROFESSIONAL_REFERRAL,
                InterventionType.PEER_SUPPORT,
                InterventionType.WELLNESS_CHECK
            ])
            
        elif alert_level == AlertLevel.MEDIUM:
            # Supportive interventions
            interventions.extend([
                InterventionType.PEER_SUPPORT,
                InterventionType.THERAPEUTIC_ACTIVITY,
                InterventionType.WELLNESS_CHECK
            ])
            
        elif alert_level == AlertLevel.LOW:
            # Gentle check-ins
            interventions.extend([
                InterventionType.WELLNESS_CHECK,
                InterventionType.BREATHING_EXERCISE
            ])
        
        return interventions
    
    async def _execute_intervention(
        self, 
        user_id: str, 
        intervention_type: InterventionType, 
        alert_info: Dict, 
        crisis_prediction: Dict
    ) -> Dict[str, Any]:
        """Execute specific intervention based on type"""
        
        try:
            if intervention_type == InterventionType.CRISIS_HOTLINE:
                return await self._trigger_crisis_hotline_alert(user_id, alert_info)
                
            elif intervention_type == InterventionType.EMERGENCY_CONTACT:
                return await self._notify_emergency_contacts(user_id, alert_info)
                
            elif intervention_type == InterventionType.PROFESSIONAL_REFERRAL:
                return await self._send_professional_referral(user_id, crisis_prediction)
                
            elif intervention_type == InterventionType.PEER_SUPPORT:
                return await self._activate_peer_support(user_id, alert_info)
                
            elif intervention_type == InterventionType.THERAPEUTIC_ACTIVITY:
                return await self._suggest_therapeutic_activities(user_id, crisis_prediction)
                
            elif intervention_type == InterventionType.WELLNESS_CHECK:
                return await self._send_wellness_check_notification(user_id, alert_info)
                
            elif intervention_type == InterventionType.BREATHING_EXERCISE:
                return await self._guide_breathing_exercise(user_id)
                
            else:
                return {
                    "type": intervention_type.value,
                    "success": False,
                    "error": "Unknown intervention type"
                }
                
        except Exception as e:
            logger.error(f"Intervention execution error ({intervention_type.value}): {e}")
            return {
                "type": intervention_type.value,
                "success": False,
                "error": str(e)
            }
    
    async def _trigger_crisis_hotline_alert(self, user_id: str, alert_info: Dict) -> Dict[str, Any]:
        """Send immediate crisis hotline information and alert"""
        
        # Create urgent notification with crisis resources
        notification_data = {
            "title": "🚨 Immediate Support Available",
            "message": f"If you're in crisis, help is available 24/7. Call {self.crisis_hotline_number} (Suicide & Crisis Lifeline) or text 'HELLO' to 741741 (Crisis Text Line). You are not alone.",
            "notification_type": "crisis_alert",
            "priority": "urgent",
            "action_url": f"tel:{self.crisis_hotline_number}",
            "send_immediately": True
        }
        
        # Send via notification service
        success = await self._send_notification(user_id, notification_data)
        
        # Log crisis intervention
        logger.critical(f"Crisis hotline alert sent to user {user_id} - Alert ID: {alert_info['alert_id']}")
        
        return {
            "type": InterventionType.CRISIS_HOTLINE.value,
            "success": success,
            "message": "Crisis hotline information sent",
            "resources_provided": ["988 Suicide & Crisis Lifeline", "Crisis Text Line"]
        }
    
    async def _send_wellness_check_notification(self, user_id: str, alert_info: Dict) -> Dict[str, Any]:
        """Send personalized wellness check notification"""
        
        alert_level = alert_info.get("alert_level", "MEDIUM")
        
        if alert_level == "HIGH":
            message = "We've noticed some patterns in your recent entries that suggest you might benefit from extra support. How are you feeling right now?"
        elif alert_level == "MEDIUM":
            message = "Just checking in - your wellbeing matters to us. Would you like to share how you're doing today?"
        else:
            message = "Time for a gentle check-in. How has your mood been lately?"
        
        notification_data = {
            "title": "💜 Wellness Check-in",
            "message": message,
            "notification_type": "wellness_check",
            "priority": "high" if alert_level in ["CRITICAL", "HIGH"] else "normal",
            "action_url": "/mood-entry",
            "send_immediately": True
        }
        
        success = await self._send_notification(user_id, notification_data)
        
        return {
            "type": InterventionType.WELLNESS_CHECK.value,
            "success": success,
            "message": "Wellness check notification sent"
        }
    
    async def _send_notification(self, user_id: str, notification_data: Dict) -> bool:
        """Send notification via notification service"""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.notification_service_url}/notify/send-notification/{user_id}",
                    json=notification_data,
                    headers={"Content-Type": "application/json"}
                )
                
                return response.status_code in [200, 201]
                
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
            return False
    
    async def _broadcast_alert(self, alert_info: Dict):
        """Broadcast alert via Redis for real-time monitoring systems"""
        try:
            if self.redis_available:
                channel = f"mental_health_alerts"
                message = json.dumps({
                    "type": "crisis_alert",
                    "alert_info": alert_info,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                self.redis_client.publish(channel, message)
                
        except Exception as e:
            logger.error(f"Failed to broadcast alert: {e}")
    
    def _determine_alert_level(self, crisis_probability: float) -> AlertLevel:
        """Determine alert level based on crisis probability"""
        
        if crisis_probability >= self.alert_thresholds[AlertLevel.CRITICAL]:
            return AlertLevel.CRITICAL
        elif crisis_probability >= self.alert_thresholds[AlertLevel.HIGH]:
            return AlertLevel.HIGH
        elif crisis_probability >= self.alert_thresholds[AlertLevel.MEDIUM]:
            return AlertLevel.MEDIUM
        elif crisis_probability >= self.alert_thresholds[AlertLevel.LOW]:
            return AlertLevel.LOW
        else:
            return AlertLevel.INFO
    
    def _should_trigger_alert(
        self, 
        user_id: str, 
        current_level: AlertLevel, 
        crisis_prediction: Dict
    ) -> Tuple[bool, str]:
        """Determine if an alert should be triggered based on various factors"""
        
        # Check if user already has active alert
        existing_alert = self.active_alerts.get(user_id)
        if existing_alert:
            existing_level = AlertLevel(existing_alert["alert_level"])
            
            # Escalate if risk level increased significantly
            if current_level.value in ["CRITICAL", "HIGH"] and existing_level.value not in ["CRITICAL", "HIGH"]:
                return True, f"Escalation from {existing_level.value} to {current_level.value}"
            
            # Don't duplicate alerts of same level within threshold time
            last_alert_time = datetime.fromisoformat(existing_alert["timestamp"])
            time_since_alert = datetime.utcnow() - last_alert_time
            min_interval = timedelta(minutes=self.monitoring_intervals[current_level])
            
            if time_since_alert < min_interval:
                return False, "Within minimum alert interval"
        
        # Trigger alert for elevated risk levels
        if current_level in [AlertLevel.CRITICAL, AlertLevel.HIGH]:
            return True, f"High risk detected: {current_level.value}"
        
        # Trigger for medium risk if it's a new concern
        if current_level == AlertLevel.MEDIUM and not existing_alert:
            return True, "New medium risk concern identified"
        
        return False, "No alert criteria met"
    
    def _calculate_next_check_time(self, alert_level: AlertLevel) -> datetime:
        """Calculate when next monitoring check should occur"""
        interval_minutes = self.monitoring_intervals[alert_level]
        return datetime.utcnow() + timedelta(minutes=interval_minutes)
    
    def _calculate_escalation_time(self, alert_level: AlertLevel) -> datetime:
        """Calculate when to check for escalation if no response"""
        escalation_times = {
            AlertLevel.CRITICAL: 30,   # 30 minutes
            AlertLevel.HIGH: 120,      # 2 hours
            AlertLevel.MEDIUM: 360,    # 6 hours
            AlertLevel.LOW: 720        # 12 hours
        }
        
        minutes = escalation_times.get(alert_level, 720)
        return datetime.utcnow() + timedelta(minutes=minutes)
    
    async def _update_monitoring_status(self, user_id: str, alert_level: AlertLevel, crisis_prediction: Dict):
        """Update monitoring status without triggering alert"""
        
        # Store current status in Redis for real-time monitoring
        if self.redis_available:
            try:
                status_key = f"user_monitoring:{user_id}"
                status_data = {
                    "alert_level": alert_level.value,
                    "crisis_probability": crisis_prediction.get("crisis_probability", 0),
                    "last_updated": datetime.utcnow().isoformat(),
                    "next_check": self._calculate_next_check_time(alert_level).isoformat()
                }
                
                # Store with expiration
                expiry_seconds = self.monitoring_intervals[alert_level] * 60 * 2  # 2x check interval
                self.redis_client.setex(status_key, expiry_seconds, json.dumps(status_data))
                
            except Exception as e:
                logger.error(f"Failed to update monitoring status for {user_id}: {e}")
    
    def _initialize_escalation_rules(self) -> Dict:
        """Initialize escalation rules for different scenarios"""
        return {
            "no_response_critical": {
                "time_limit_minutes": 60,
                "action": "emergency_contact"
            },
            "no_response_high": {
                "time_limit_minutes": 240,
                "action": "professional_referral"
            },
            "repeated_alerts": {
                "threshold": 3,
                "time_window_hours": 24,
                "action": "intensive_support"
            }
        }
    
    async def get_user_alert_status(self, user_id: str) -> Dict[str, Any]:
        """Get current alert status for a user"""
        
        active_alert = self.active_alerts.get(user_id)
        alert_counts = self.user_alert_counts.get(user_id, {})
        
        # Get current monitoring status from Redis
        current_status = {}
        if self.redis_available:
            try:
                status_key = f"user_monitoring:{user_id}"
                status_data = self.redis_client.get(status_key)
                if status_data:
                    current_status = json.loads(status_data)
            except Exception as e:
                logger.error(f"Failed to get monitoring status for {user_id}: {e}")
        
        return {
            "user_id": user_id,
            "has_active_alert": bool(active_alert),
            "active_alert": active_alert,
            "alert_counts": alert_counts,
            "current_monitoring": current_status,
            "system_version": self.system_version
        }
    
    async def resolve_alert(self, user_id: str, resolution_reason: str = "Resolved") -> Dict[str, Any]:
        """Manually resolve an active alert"""
        
        if user_id not in self.active_alerts:
            return {
                "success": False,
                "message": "No active alert found for user"
            }
        
        alert_info = self.active_alerts[user_id]
        alert_info["status"] = "resolved"
        alert_info["resolution_time"] = datetime.utcnow().isoformat()
        alert_info["resolution_reason"] = resolution_reason
        
        # Move to history and remove from active
        del self.active_alerts[user_id]
        
        # Clean up Redis monitoring status
        if self.redis_available:
            try:
                status_key = f"user_monitoring:{user_id}"
                self.redis_client.delete(status_key)
            except Exception as e:
                logger.error(f"Failed to clean up monitoring status for {user_id}: {e}")
        
        logger.info(f"Alert resolved for user {user_id}: {resolution_reason}")
        
        return {
            "success": True,
            "message": "Alert resolved successfully",
            "alert_id": alert_info["alert_id"],
            "resolution_time": alert_info["resolution_time"]
        }

# Additional helper methods for specific interventions would be implemented here...
# This represents the core Early Warning System architecture for Phase 2A
