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
from shared.auth import get_current_user, require_admin
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
    notification_type: str = Field(..., regex="^(mood_reminder|insight|community|system|crisis)$")
    action_url: Optional[str] = None
    priority: str = Field("normal", regex="^(low|normal|high|urgent)$")
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
        await websocket.send_json(welcome_message.dict())
        
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
                    await websocket.send_json(heartbeat_response.dict())
                    
                elif data.get("type") == "mark_read":
                    # Handle marking notifications as read via WebSocket
                    notification_id = data.get("notification_id")
                    if notification_id:
                        # Mark as read in database (you'd need to get db session here)
                        response = WebSocketMessage(
                            type="notification_read",
                            data={"notification_id": notification_id, "status": "read"}
                        )
                        await websocket.send_json(response.dict())
                        
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
    current_user: Dict[str, Any] = Depends(require_admin)
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
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark notification as read"""
    
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
    
    # Send real-time update via WebSocket
    asyncio.create_task(
        manager.send_personal_message(
            {
                "type": "notification_read",
                "data": {
                    "notification_id": str(notification_id),
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            current_user["user_id"]
        )
    )
    
    return {"message": "Notification marked as read"}

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
        email_notifications=profile.email_notifications,
        push_notifications=profile.push_notifications,
        mood_reminders=profile.mood_reminders,
        weekly_reports=profile.weekly_reports,
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
            id=uuid.uuid4(),
            user_id=current_user["user_id"]
        )
        db.add(profile)
    
    # Update preferences
    profile.email_notifications = preferences.email_notifications
    profile.push_notifications = preferences.push_notifications
    profile.mood_reminders = preferences.mood_reminders
    profile.weekly_reports = preferences.weekly_reports
    
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
        "mood_reminder": profile.mood_reminders,
        "insight": profile.push_notifications,
        "community": True,  # Always allow community notifications
        "system": profile.push_notifications,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)