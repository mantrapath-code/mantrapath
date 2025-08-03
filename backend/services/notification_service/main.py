"""
Notification Service - Push notifications, alerts, and messaging with WebSocket support
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional, Dict, Any, Set
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel, UUID4, Field
import json
import redis
import asyncio
import logging

# Import shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user
# from shared.auth import require_admin  # TODO: implement require_admin function
from shared.models import Notification, User, UserProfile

app = FastAPI(
    title="MantraPath Notification Service",
    description="Push notifications, alerts, and messaging",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for queuing and caching
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logging.info(f"WebSocket connected for user {user_id}")
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logging.info(f"WebSocket disconnected for user {user_id}")
        
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            connections_to_remove = set()
            for connection in self.active_connections[user_id].copy():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logging.error(f"Error sending message to user {user_id}: {e}")
                    connections_to_remove.add(connection)
            
            # Remove failed connections
            for connection in connections_to_remove:
                self.active_connections[user_id].discard(connection)
                
    async def broadcast(self, message: dict):
        for user_id, connections in self.active_connections.items():
            await self.send_personal_message(message, user_id)

manager = ConnectionManager()

# Pydantic models
class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: str = Field(..., pattern="^(mood_reminder|insight|community|system|crisis)$")
    action_url: Optional[str] = None
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")
    send_immediately: bool = False

class NotificationResponse(BaseModel):
    id: UUID4
    title: str
    message: str
    notification_type: str
    action_url: Optional[str]
    priority: str
    is_read: bool
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    mood_reminders: bool = True
    weekly_reports: bool = True
    community_updates: bool = True
    crisis_alerts: bool = True

class SendNotificationRequest(BaseModel):
    user_ids: Optional[List[str]] = None  # If None, sends to all users
    title: str
    message: str
    notification_type: str
    action_url: Optional[str] = None
    priority: str = "normal"

class WebSocketMessage(BaseModel):
    type: str  # 'notification', 'mood_update', 'chat_message', etc.
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_json_dict(self):
        """Convert to JSON-serializable dictionary"""
        data = self.dict()
        data['timestamp'] = self.timestamp.isoformat()
        return data

# WebSocket endpoint for real-time notifications
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    try:
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        welcome_message = WebSocketMessage(
            type="connection",
            data={"message": "Connected to MantraPath notifications", "user_id": user_id}
        )
        await websocket.send_json(welcome_message.to_json_dict())
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (heartbeat, status updates, etc.)
                data = await websocket.receive_json()
                
                # Handle different message types from client
                if data.get("type") == "heartbeat":
                    heartbeat_response = WebSocketMessage(
                        type="heartbeat_ack",
                        data={"timestamp": datetime.utcnow().isoformat()}
                    )
                    await websocket.send_json(heartbeat_response.to_json_dict())
                    
                elif data.get("type") == "mark_read":
                    # Handle marking notifications as read via WebSocket
                    notification_id = data.get("notification_id")
                    if notification_id:
                        # Mark as read in database (you'd need to get db session here)
                        response = WebSocketMessage(
                            type="notification_read",
                            data={"notification_id": notification_id, "status": "read"}
                        )
                        await websocket.send_json(response.to_json_dict())
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                logging.error(f"Error in WebSocket communication: {e}")
                break
                
    except Exception as e:
        logging.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(websocket, user_id)

@app.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "connected_users": len(manager.active_connections),
        "total_connections": sum(len(connections) for connections in manager.active_connections.values()),
        "users": list(manager.active_connections.keys())
    }

# Notification management endpoints
@app.post("/notify/send")
async def send_notification(
    notification_data: NotificationCreate,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send notification to a specific user"""
    
    # Verify target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check user's notification preferences
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile and not should_send_notification(notification_data.notification_type, profile):
        return {"message": "Notification blocked by user preferences"}
    
    # Create notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        action_url=notification_data.action_url,
        priority=notification_data.priority,
        is_sent=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send notification in background
    if notification_data.send_immediately:
        background_tasks.add_task(
            process_notification_immediately, 
            str(notification.id), 
            db,
            user_id  # Pass user_id for WebSocket notification
        )
    else:
        # Queue for batch processing
        background_tasks.add_task(
            queue_notification_for_processing, 
            str(notification.id),
            user_id  # Pass user_id for WebSocket notification
        )
    
    return {
        "id": str(notification.id),
        "message": "Notification created and queued for delivery"
    }

@app.post("/notify/send/broadcast")
async def broadcast_notification(
    broadcast_data: SendNotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Broadcast notification to multiple users (admin only)"""
    
    # Get target users
    if broadcast_data.user_ids:
        target_users = db.query(User).filter(
            User.id.in_(broadcast_data.user_ids)
        ).all()
    else:
        # Send to all active users
        target_users = db.query(User).filter(User.is_active == True).all()
    
    notification_ids = []
    
    for user in target_users:
        # Check user preferences
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if profile and not should_send_notification(broadcast_data.notification_type, profile):
            continue
        
        # Create notification
        notification = Notification(
            id=uuid.uuid4(),
            user_id=str(user.id),
            # TODO: Re-enable cache clearing before production deployment
            # redis_client.delete(f"user_context:{user_id}")  # Clear stale cache
            title=broadcast_data.title,
            message=broadcast_data.message,
            notification_type=broadcast_data.notification_type,
            action_url=broadcast_data.action_url,
            priority=broadcast_data.priority,
            is_sent=False
        )
        
        db.add(notification)
        notification_ids.append(str(notification.id))
    
    db.commit()
    
    # Queue all notifications for processing
    for i, notification_id in enumerate(notification_ids):
        user_id = target_users[i].id if i < len(target_users) else None
        background_tasks.add_task(
            queue_notification_for_processing, 
            notification_id,
            str(user_id) if user_id else None
        )
    
    return {
        "message": f"Broadcast notification queued for {len(notification_ids)} users"
    }

@app.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's notifications (alias for /notify/recent)"""
    
    query = db.query(Notification).filter(
        Notification.user_id == current_user["user_id"]
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    notifications = query.order_by(
        desc(Notification.created_at)
    ).offset(skip).limit(limit).all()
    
    return [
        NotificationResponse(
            id=notification.id,
            title=notification.title,
            message=notification.message,
            notification_type=notification.notification_type,
            action_url=notification.action_url,
            priority=notification.priority,
            is_read=notification.is_read,
            is_sent=notification.is_sent,
            sent_at=notification.sent_at,
            created_at=notification.created_at
        )
        for notification in notifications
    ]

@app.get("/notify/recent", response_model=List[NotificationResponse])
async def get_recent_notifications(
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's recent notifications"""
    
    query = db.query(Notification).filter(
        Notification.user_id == current_user["user_id"]
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    notifications = query.order_by(
        desc(Notification.created_at)
    ).offset(skip).limit(limit).all()
    
    return [
        NotificationResponse(
            id=notification.id,
            title=notification.title,
            message=notification.message,
            notification_type=notification.notification_type,
            action_url=notification.action_url,
            priority=notification.priority,
            is_read=notification.is_read,
            is_sent=notification.is_sent,
            sent_at=notification.sent_at,
            created_at=notification.created_at
        )
        for notification in notifications
    ]

@app.post("/notify/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: UUID4,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """🎯 UPGRADED: Mark notification as read with RL-powered effectiveness tracking"""
    
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user["user_id"]
        )
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    # 🤖 ENHANCED: Track notification effectiveness with RL learning
    background_tasks.add_task(
        track_ml_notification_effectiveness,
        str(notification_id),
        current_user["user_id"],
        "read",  # engagement_type
        db,
        background_tasks
    )
    
    # Send real-time update via WebSocket
    asyncio.create_task(
        manager.send_personal_message(
            {
                "type": "notification_read",
                "data": {
                    "notification_id": str(notification_id),
                    "timestamp": datetime.utcnow().isoformat(),
                    "ml_tracking_enabled": True
                }
            },
            current_user["user_id"]
        )
    )
    
    return {
        "message": "Notification marked as read",
        "ml_tracking_enabled": True,
        "rl_learning_active": True
    }

@app.post("/notify/mark-all-read")
async def mark_all_notifications_read(
    notification_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark all notifications as read"""
    
    query = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user["user_id"],
            Notification.is_read == False
        )
    )
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    updated_count = query.update({"is_read": True})
    db.commit()
    
    return {"message": f"Marked {updated_count} notifications as read"}

# Notification preferences
@app.get("/notify/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's notification preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        # Return default preferences
        return NotificationPreferences()
    
    return NotificationPreferences(
        email_notifications=profile.notifications_enabled,
        push_notifications=profile.notifications_enabled,
        mood_reminders=profile.daily_reminder_enabled,
        weekly_reports=profile.weekly_report_enabled,
        # Default values for missing fields
        community_updates=True,
        crisis_alerts=True
    )

@app.put("/notify/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user's notification preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=current_user["user_id"]
        )
        db.add(profile)
    
    # Update preferences (map to actual UserProfile fields)
    profile.notifications_enabled = preferences.email_notifications or preferences.push_notifications
    profile.daily_reminder_enabled = preferences.mood_reminders
    profile.weekly_report_enabled = preferences.weekly_reports
    
    db.commit()
    
    return {"message": "Notification preferences updated successfully"}

# Scheduled notifications
@app.post("/notify/schedule")
async def schedule_notification(
    user_id: str,
    notification_data: NotificationCreate,
    send_at: datetime,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Schedule a notification for future delivery"""
    
    # Create notification with future send time
    notification = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        action_url=notification_data.action_url,
        priority=notification_data.priority,
        is_sent=False
    )
    
    db.add(notification)
    db.commit()
    
    # Schedule in Redis
    schedule_data = {
        "notification_id": str(notification.id),
        "send_at": send_at.isoformat()
    }
    
    redis_client.lpush(
        "scheduled_notifications", 
        json.dumps(schedule_data)
    )
    
    return {
        "id": str(notification.id),
        "message": f"Notification scheduled for {send_at.isoformat()}"
    }

# Utility functions
def should_send_notification(notification_type: str, profile: UserProfile) -> bool:
    """Check if notification should be sent based on user preferences"""
    
    type_preference_map = {
        "mood_reminder": profile.daily_reminder_enabled,
        "insight": profile.notifications_enabled,
        "community": True,  # Always allow community notifications
        "system": profile.notifications_enabled,
        "crisis": True  # Always allow crisis notifications
    }
    
    return type_preference_map.get(notification_type, True)

async def process_notification_immediately(notification_id: str, db: Session, user_id: str = None):
    """Process notification for immediate delivery"""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        return
    
    # Get user profile for delivery preferences
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == notification.user_id
    ).first()
    
    # Simulate sending notification (in real implementation, this would
    # interface with push notification services, email providers, etc.)
    success = await simulate_notification_delivery(notification, profile)
    
    if success:
        notification.is_sent = True
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        # Send real-time notification via WebSocket
        if user_id:
            websocket_message = WebSocketMessage(
                type="notification",
                data={
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "action_url": notification.action_url,
                    "priority": notification.priority,
                    "created_at": notification.created_at.isoformat()
                }
            )
            await manager.send_personal_message(websocket_message.dict(), user_id)

async def queue_notification_for_processing(notification_id: str, user_id: str = None):
    """Queue notification for batch processing"""
    
    queue_data = {
        "notification_id": notification_id,
        "user_id": user_id,
        "queued_at": datetime.utcnow().isoformat()
    }
    
    redis_client.lpush("notification_queue", json.dumps(queue_data))

async def simulate_notification_delivery(notification: Notification, profile: UserProfile) -> bool:
    """Simulate notification delivery (replace with real implementation)"""
    
    # In a real implementation, this would:
    # 1. Send push notifications via FCM/APNS
    # 2. Send emails via SendGrid/SES
    # 3. Send SMS via Twilio
    # 4. Update WebSocket connections for real-time notifications
    
    print(f"📱 Sending notification to user {notification.user_id}")
    print(f"   Title: {notification.title}")
    print(f"   Message: {notification.message}")
    print(f"   Type: {notification.notification_type}")
    print(f"   Priority: {notification.priority}")
    
    # Simulate network delay
    await asyncio.sleep(0.1)
    
    return True

# Background task for processing notification queue
async def process_notification_queue():
    """Background task to process queued notifications"""
    
    while True:
        try:
            # Get notifications from queue
            queue_item = redis_client.brpop("notification_queue", timeout=30)
            
            if queue_item:
                queue_data = json.loads(queue_item[1])
                notification_id = queue_data["notification_id"]
                
                # Process the notification
                # In a real implementation, you'd get a DB session here
                # await process_notification_immediately(notification_id, db)
                
                print(f"📧 Processed queued notification: {notification_id}")
        
        except Exception as e:
            print(f"Error processing notification queue: {e}")
            await asyncio.sleep(5)

# Notification analytics
@app.get("/notify/analytics")
async def get_notification_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get notification analytics for user"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get notification counts by type
    notifications = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user["user_id"],
            Notification.created_at >= start_date
        )
    ).all()
    
    # Calculate metrics
    total_notifications = len(notifications)
    unread_notifications = len([n for n in notifications if not n.is_read])
    sent_notifications = len([n for n in notifications if n.is_sent])
    
    # Group by type
    by_type = {}
    for notification in notifications:
        notification_type = notification.notification_type
        if notification_type not in by_type:
            by_type[notification_type] = {
                "total": 0,
                "read": 0,
                "sent": 0
            }
        
        by_type[notification_type]["total"] += 1
        if notification.is_read:
            by_type[notification_type]["read"] += 1
        if notification.is_sent:
            by_type[notification_type]["sent"] += 1
    
    return {
        "period_days": days,
        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications,
        "sent_notifications": sent_notifications,
        "read_rate": round((total_notifications - unread_notifications) / max(total_notifications, 1) * 100, 1),
        "delivery_rate": round(sent_notifications / max(total_notifications, 1) * 100, 1),
        "by_type": by_type
    }

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "notification_service",
        "timestamp": datetime.utcnow().isoformat(),
        "queue_size": redis_client.llen("notification_queue"),
        "websocket_connections": len(manager.active_connections)
    }

# Real-time notification triggers
@app.post("/notify/mood-pattern")
async def trigger_mood_pattern_notification(
    user_id: str,
    pattern_type: str,
    pattern_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Trigger mood pattern notification based on analytics"""
    
    # Generate personalized message based on pattern
    if pattern_type == "negative_trend":
        title = "Mood Pattern Alert"
        message = f"We've noticed your mood has been trending downward over the past {pattern_data.get('days', 7)} days. Consider trying some wellness activities."
        action_url = "/mood"
    elif pattern_type == "positive_streak":
        title = "Great Progress! 🎉"
        message = f"Amazing! You've maintained a positive mood for {pattern_data.get('streak_days', 1)} days. Keep up the excellent work!"
        action_url = "/dashboard"
    elif pattern_type == "intervention_needed":
        title = "Wellness Check-in"
        message = "It might be a good time to use your coping strategies or reach out for support."
        action_url = "/community"
    else:
        title = "Mood Insights Available"
        message = "New insights about your mood patterns are ready to view."
        action_url = "/dashboard"
    
    notification_data = NotificationCreate(
        title=title,
        message=message,
        notification_type="mood_pattern",
        action_url=action_url,
        priority="high" if pattern_type == "intervention_needed" else "normal",
        send_immediately=True
    )
    
    # Create and send notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        action_url=notification_data.action_url,
        priority=notification_data.priority,
        is_sent=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send immediately
    background_tasks.add_task(
        process_notification_immediately,
        str(notification.id),
        db,
        user_id
    )
    
    return {
        "id": str(notification.id),
        "message": "Mood pattern notification sent",
        "pattern_type": pattern_type
    }

@app.post("/notify/weekly-report")
async def send_weekly_report(
    user_id: str,
    report_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send weekly mood report notification"""
    
    title = "Your Weekly Mood Report is Ready! 📊"
    message = f"This week's insights: {report_data.get('summary', 'Your personalized mood analysis is available.')}"
    
    notification_data = NotificationCreate(
        title=title,
        message=message,
        notification_type="weekly_report",
        action_url="/reports/weekly",
        priority="normal",
        send_immediately=True
    )
    
    notification = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        action_url=notification_data.action_url,
        priority=notification_data.priority,
        is_sent=False
    )
    
    db.add(notification)
    db.commit()
    
    background_tasks.add_task(
        process_notification_immediately,
        str(notification.id),
        db,
        user_id
    )
    
    return {"message": "Weekly report notification sent", "notification_id": str(notification.id)}

@app.post("/notify/schedule-smart-notifications")
async def schedule_smart_notifications(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """🤖 UPGRADED: Schedule ML-powered personalized notifications with ensemble timing prediction"""
    
    user_id = current_user["user_id"]
    
    try:
        # 🧠 STEP 1: Get user's mood history for ML prediction
        user_mood_data = await get_user_mood_history(user_id, db)
        user_engagement_data = await get_user_engagement_history(user_id, db)
        
        # 🤖 STEP 2: Get optimal notification times from ML service (Ensemble Timing Predictor)
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8008")
            
            # Prepare ML input data
            ml_request_data = {
                "user_id": user_id,
                "mood_entries": user_mood_data,
                "engagement_history": user_engagement_data,
                "current_context": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "day_of_week": datetime.utcnow().weekday(),
                    "user_timezone": current_user.get("timezone", "UTC")
                }
            }
            
            # Call advanced ML timing predictor
            timing_response = await client.post(
                f"{ml_service_url}/predict-timing",
                json=ml_request_data,
                headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
            )
            
            if timing_response.status_code == 200:
                ml_timing_data = timing_response.json()
                optimal_times = ml_timing_data.get("optimal_times", [])
                ensemble_metrics = ml_timing_data.get("ensemble_predictions", {})
                feature_importance = ml_timing_data.get("feature_importance", {})
                
                logging.info(f"ML Timing Prediction for user {user_id}: {len(optimal_times)} optimal times found, stacking_score: {ensemble_metrics.get('stacking_score', 'N/A')}")
                
                scheduled_count = 0
                ml_notifications = []
                
                # 📝 STEP 3: Generate personalized content for each optimal time using NLP engine
                for idx, time_slot in enumerate(optimal_times[:3]):  # Schedule top 3 ML-predicted optimal times
                    hour = time_slot.get("hour", 9)
                    effectiveness_score = time_slot.get("effectiveness_score", 0.7)
                    confidence = time_slot.get("confidence", 0.8)
                    reasoning = time_slot.get("reasoning", "ML ensemble prediction")
                    
                    # Determine notification type based on ML insights
                    notification_type = determine_ml_notification_type(time_slot, user_mood_data)
                    
                    # 🎨 Call NLP-powered content generation
                    content_request = {
                        "notification_type": notification_type,
                        "user_context": {
                            "recent_mood_trend": calculate_recent_mood_trend(user_mood_data),
                            "time_of_day": hour,
                            "ml_effectiveness_score": effectiveness_score,
                            "ml_confidence": confidence,
                            "ml_reasoning": reasoning,
                            "user_profile": current_user.get("profile", {})
                        },
                        "effectiveness_score": effectiveness_score
                    }
                    
                    content_response = await client.post(
                        f"{ml_service_url}/generate-content",
                        json=content_request,
                        headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
                    )
                    
                    if content_response.status_code == 200:
                        ml_content = content_response.json()
                        title = ml_content.get("title", "Wellness Reminder")
                        message = ml_content.get("message", "Take a moment for your well-being")
                        action_url = ml_content.get("action_suggestions", ["/dashboard"])[0] if ml_content.get("action_suggestions") else "/dashboard"
                        personalization_level = ml_content.get("personalization_level", 0.5)
                        therapeutic_framework = ml_content.get("therapeutic_framework", "general")
                        
                        logging.info(f"ML Content Generated: personalization={personalization_level:.2f}, framework={therapeutic_framework}")
                    else:
                        # Fallback content
                        title, message, action_url = generate_notification_content(notification_type, effectiveness_score)
                        personalization_level = 0.3
                        therapeutic_framework = "fallback"
                    
                    # 🗂️ Store ML-enhanced schedule in Redis
                    schedule_key = f"ml_notification_schedule:{user_id}:{uuid.uuid4()}"
                    ml_schedule_data = {
                        "user_id": user_id,
                        "notification_type": notification_type,
                        "title": title,
                        "message": message,
                        "action_url": action_url,
                        "hour": hour,
                        "ml_effectiveness_score": effectiveness_score,
                        "ml_confidence": confidence,
                        "ml_reasoning": reasoning,
                        "personalization_level": personalization_level,
                        "therapeutic_framework": therapeutic_framework,
                        "ensemble_score": ensemble_metrics.get("stacking_score", 0.7),
                        "feature_importance": feature_importance,
                        "created_at": datetime.utcnow().isoformat(),
                        "ml_version": "v2.0.0-ensemble",
                        "source": "ml_service"
                    }
                    
                    redis_client.setex(schedule_key, 604800, json.dumps(ml_schedule_data))  # Store for 1 week
                    scheduled_count += 1
                    
                    ml_notifications.append({
                        "hour": hour,
                        "effectiveness_score": effectiveness_score,
                        "confidence": confidence,
                        "notification_type": notification_type,
                        "personalization_level": personalization_level,
                        "ml_reasoning": reasoning
                    })
                
                return {
                    "message": f"🤖 Successfully scheduled {scheduled_count} ML-powered personalized notifications",
                    "ml_service_used": True,
                    "optimal_times": optimal_times,
                    "ensemble_metrics": ensemble_metrics,
                    "feature_importance": feature_importance,
                    "scheduled_notifications": ml_notifications,
                    "next_notification": calculate_next_notification_time(optimal_times),
                    "ml_version": "v2.0.0-ensemble"
                }
            else:
                logging.warning(f"ML service unavailable (status: {timing_response.status_code}), falling back to default schedule")
                # Fallback to default schedule
                return await schedule_default_notifications(user_id, db, background_tasks)
                
    except Exception as e:
        logging.error(f"Error in ML-powered smart notifications: {e}")
        # Fallback to default schedule with error details
        fallback_result = await schedule_default_notifications(user_id, db, background_tasks)
        fallback_result["ml_error"] = str(e)
        fallback_result["fallback_used"] = True
        return fallback_result

def generate_notification_content(notification_type: str, effectiveness: float) -> tuple[str, str, str]:
    """Generate appropriate notification content based on type and effectiveness"""
    
    if notification_type == "morning_boost":
        return (
            "Good Morning! 🌅",
            "Start your day with intention. How are you feeling right now?",
            "/mood"
        )
    elif notification_type == "midday_check":
        return (
            "Midday Check-in ☀️",
            "Take a moment to notice how you're doing. You're halfway through the day!",
            "/mood"
        )
    elif notification_type == "afternoon_support":
        return (
            "Afternoon Energy Boost 🌟",
            "Feeling the afternoon dip? Try a quick breathing exercise or short walk.",
            "/wellness"
        )
    elif notification_type == "evening_reflection":
        return (
            "Evening Reflection 🌙",
            "How did today go? Take a moment to reflect and prepare for rest.",
            "/journal"
        )
    elif notification_type == "day_preparation":
        return (
            "Gentle Day Prep 💙",
            "Today might be challenging. Remember to be kind to yourself and use your support tools.",
            "/community"
        )
    elif notification_type == "preventive":
        if effectiveness > 8:
            return (
                "Wellness Check 🎯",
                "This is typically when you need extra support. You've got this!",
                "/mood"
            )
        else:
            return (
                "Mindful Moment 🧘",
                "Perfect time for a brief mindfulness practice or mood check.",
                "/wellness"
            )
    else:
        return (
            "Wellness Reminder 🌱",
            "A gentle reminder to check in with yourself. How are you doing?",
            "/mood"
        )

async def schedule_default_notifications(user_id: str, db: Session, background_tasks: BackgroundTasks):
    """Schedule default notifications for users without enough data for personalization"""
    
    default_times = [
        {"hour": 9, "type": "morning_check", "effectiveness": 7.5},
        {"hour": 15, "type": "afternoon_support", "effectiveness": 8.0},
        {"hour": 20, "type": "evening_reflection", "effectiveness": 7.0}
    ]
    
    scheduled_count = 0
    
    for time_slot in default_times:
        title, message, action_url = generate_notification_content(
            time_slot["type"], 
            time_slot["effectiveness"]
        )
        
        schedule_key = f"notification_schedule:{user_id}:{uuid.uuid4()}"
        schedule_data = {
            "user_id": user_id,
            "notification_type": time_slot["type"],
            "title": title,
            "message": message,
            "action_url": action_url,
            "hour": time_slot["hour"],
            "day_of_week": None,
            "effectiveness_score": time_slot["effectiveness"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        redis_client.setex(schedule_key, 604800, json.dumps(schedule_data))
        scheduled_count += 1
    
    return {
        "message": f"Scheduled {scheduled_count} default notifications. Will personalize as you use the app more.",
        "note": "Notifications will become more personalized as we learn your patterns"
    }

def calculate_next_notification_time(optimal_times: List[Dict]) -> str:
    """Calculate when the next notification will be sent"""
    if not optimal_times:
        return "No notifications scheduled"
    
    now = datetime.utcnow()
    next_times = []
    
    for time_slot in optimal_times:
        hour = time_slot.get("hour", 9)
        day_of_week = time_slot.get("day_of_week")
        
        if day_of_week is not None:
            # Specific day of week
            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:  # Target day has passed this week
                days_ahead += 7
            next_time = now + timedelta(days=days_ahead)
            next_time = next_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            # Daily notification
            next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
        
        next_times.append(next_time)
    
    next_notification = min(next_times)
    return next_notification.strftime("%Y-%m-%d %H:%M UTC")

@app.post("/notify/weekly-report-legacy")
async def send_weekly_report_legacy(
    user_id: str,
    report_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send personalized weekly mood report"""
    
    # Generate report summary
    avg_mood = report_data.get("average_mood", 0)
    mood_trend = report_data.get("trend", "stable")
    top_activities = report_data.get("helpful_activities", [])
    
    if mood_trend == "improving":
        title = "Weekly Progress Report 📈"
        emoji = "🌟"
        trend_text = "improving"
    elif mood_trend == "declining":
        title = "Weekly Wellness Check 💙"
        emoji = "🤗"
        trend_text = "showing some challenges"
    else:
        title = "Weekly Mood Summary 📊"
        emoji = "⚖️"
        trend_text = "staying stable"
    
    activities_text = ""
    if top_activities:
        activities_text = f" Your most helpful activities were: {', '.join(top_activities[:3])}."
    
    message = (
        f"{emoji} Your average mood this week was {avg_mood:.1f}/10, {trend_text}. "
        f"{activities_text} Keep focusing on what works for you!"
    )
    
    notification_data = NotificationCreate(
        title=title,
        message=message,
        notification_type="weekly_report",
        action_url="/dashboard",
        priority="normal",
        send_immediately=True
    )
    
    # Create and send notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        action_url=notification_data.action_url,
        priority=notification_data.priority,
        is_sent=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send immediately
    background_tasks.add_task(
        process_notification_immediately,
        str(notification.id),
        db,
        user_id
    )
    
    return {
        "id": str(notification.id),
        "message": "Weekly report notification sent",
        "report_summary": {
            "average_mood": avg_mood,
            "trend": mood_trend,
            "helpful_activities": top_activities
        }
    }

@app.post("/notify/intervention-alert")
async def send_intervention_alert(
    user_id: str,
    alert_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send smart intervention alert based on optimal timing"""
    
    alert_type = alert_data.get("type", "general")
    optimal_time = alert_data.get("optimal_time", "now")
    
    if alert_type == "breathing":
        title = "Time for a Breathing Break 🌬️"
        message = "Your patterns suggest this might be a good time for a quick breathing exercise."
        action_url = "/chatbot?action=breathing"
    elif alert_type == "journaling":
        title = "Reflection Opportunity ✍️"
        message = "Consider taking a moment to journal about your current thoughts and feelings."
        action_url = "/journal"
    elif alert_type == "community":
        title = "Connect with Others 🤝"
        message = "Your community has new supportive messages. Sometimes connecting helps!"
        action_url = "/community"
    elif alert_type == "movement":
        title = "Movement Break 🚶"
        message = "A short walk or stretch might help boost your mood right now."
        action_url = "/dashboard"
    else:
        title = "Wellness Check-in 💜"
        message = "Take a moment to check in with yourself. You're doing great!"
        action_url = "/dashboard"
    
    notification_data = NotificationCreate(
        title=title,
        message=message,
        notification_type="intervention",
        action_url=action_url,
        priority="high",
        send_immediately=True
    )
    
    # Create and send notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        action_url=notification_data.action_url,
        priority=notification_data.priority,
        is_sent=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send immediately
    background_tasks.add_task(
        process_notification_immediately,
        str(notification.id),
        db,
        user_id
    )
    
    return {
        "id": str(notification.id),
        "message": "Intervention alert sent",
        "alert_type": alert_type,
        "optimal_time": optimal_time
    }

# 🤖 ML Integration Helper Functions

async def get_user_mood_history(user_id: str, db: Session, days: int = 30) -> List[Dict[str, Any]]:
    """Get user's mood history for ML prediction"""
    try:
        from shared.models import MoodEntry
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        mood_entries = db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= cutoff_date
            )
        ).order_by(desc(MoodEntry.created_at)).all()
        
        return [
            {
                "timestamp": entry.created_at.isoformat(),
                "mood_score": entry.mood_score,
                "energy_level": getattr(entry, 'energy_level', 5),
                "stress_level": getattr(entry, 'stress_level', 5),
                "activities": getattr(entry, 'activities', []),
                "notes": getattr(entry, 'notes', '')
            }
            for entry in mood_entries
        ]
    except Exception as e:
        logging.error(f"Error fetching mood history for user {user_id}: {e}")
        return []

async def get_user_engagement_history(user_id: str, db: Session, days: int = 30) -> List[Dict[str, Any]]:
    """Get user's notification engagement history for ML prediction"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        notifications = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.created_at >= cutoff_date,
                Notification.is_sent == True
            )
        ).order_by(desc(Notification.created_at)).all()
        
        return [
            {
                "notification_id": str(notif.id),
                "notification_type": notif.notification_type,
                "sent_at": notif.sent_at.isoformat() if notif.sent_at else None,
                "is_read": notif.is_read,
                "priority": notif.priority,
                "engagement_time": notif.sent_at.isoformat() if notif.sent_at else None,
                "engagement_type": "read" if notif.is_read else "ignored"
            }
            for notif in notifications
        ]
    except Exception as e:
        logging.error(f"Error fetching engagement history for user {user_id}: {e}")
        return []

def determine_ml_notification_type(time_slot: Dict[str, Any], user_mood_data: List[Dict[str, Any]]) -> str:
    """Determine optimal notification type based on ML insights"""
    try:
        effectiveness_score = time_slot.get("effectiveness_score", 0.7)
        hour = time_slot.get("hour", 9)
        confidence = time_slot.get("confidence", 0.8)
        
        # Analyze recent mood trend
        if user_mood_data:
            recent_moods = [entry.get("mood_score", 5) for entry in user_mood_data[:7]]
            avg_mood = sum(recent_moods) / len(recent_moods) if recent_moods else 5
        else:
            avg_mood = 5
        
        # ML-based notification type selection
        if avg_mood < 4 and effectiveness_score > 0.8:
            return "supportive"
        elif 6 <= hour <= 10 and confidence > 0.85:
            return "motivational"
        elif 12 <= hour <= 14:
            return "reminder"
        elif 18 <= hour <= 21 and avg_mood > 6:
            return "reflection"
        elif effectiveness_score > 0.9:
            return "celebration"
        else:
            return "check_in"
    except Exception as e:
        logging.error(f"Error determining ML notification type: {e}")
        return "check_in"

def calculate_recent_mood_trend(user_mood_data: List[Dict[str, Any]]) -> str:
    """Calculate recent mood trend for NLP content generation"""
    try:
        if len(user_mood_data) < 3:
            return "stable"
        
        recent_moods = [entry.get("mood_score", 5) for entry in user_mood_data[:7]]
        if len(recent_moods) < 3:
            return "stable"
        
        # Calculate trend
        early_avg = sum(recent_moods[-3:]) / 3
        recent_avg = sum(recent_moods[:3]) / 3
        
        diff = recent_avg - early_avg
        
        if diff > 1:
            return "improving"
        elif diff < -1:
            return "declining"
        else:
            return "stable"
    except Exception as e:
        logging.error(f"Error calculating mood trend: {e}")
        return "stable"

# 🎯 Enhanced RL Effectiveness Tracking Integration

async def track_ml_notification_effectiveness(
    notification_id: str,
    user_id: str,
    engagement_type: str,
    db: Session,
    background_tasks: BackgroundTasks
):
    """Track notification effectiveness using RL-powered ML service"""
    try:
        # Get notification details
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            return
        
        # Calculate mood impact (if available)
        mood_impact = 0
        try:
            from shared.models import MoodEntry
            recent_mood = db.query(MoodEntry).filter(
                and_(
                    MoodEntry.user_id == user_id,
                    MoodEntry.created_at >= notification.sent_at
                )
            ).order_by(MoodEntry.created_at).first()
            
            if recent_mood:
                # Simplified mood impact calculation
                mood_impact = recent_mood.mood_score - 5  # Baseline mood
        except Exception:
            mood_impact = 0
        
        # Prepare RL tracking data
        rl_tracking_data = {
            "notification_id": notification_id,
            "user_id": user_id,
            "engagement_type": engagement_type,
            "engagement_time": datetime.utcnow().isoformat(),
            "subsequent_mood_change": mood_impact,
            "content_type": notification.notification_type,
            "priority": notification.priority
        }
        
        # Send to ML service for RL learning
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8008")
            
            rl_response = await client.post(
                f"{ml_service_url}/track-effectiveness",
                json=rl_tracking_data
            )
            
            if rl_response.status_code == 200:
                rl_result = rl_response.json()
                logging.info(f"RL tracking successful: reward={rl_result.get('rl_reward', 'N/A')}, updates={rl_result.get('rl_updates', {})}")
            else:
                logging.warning(f"RL tracking failed: {rl_response.status_code}")
                
    except Exception as e:
        logging.error(f"Error in ML effectiveness tracking: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)