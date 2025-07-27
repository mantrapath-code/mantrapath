"""
Notification Service - Push notifications, alerts, and messaging
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel, UUID4, Field
import json
import redis
import asyncio

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
            db
        )
    else:
        # Queue for batch processing
        background_tasks.add_task(
            queue_notification_for_processing, 
            str(notification.id)
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
    for notification_id in notification_ids:
        background_tasks.add_task(
            queue_notification_for_processing, 
            notification_id
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

async def process_notification_immediately(notification_id: str, db: Session):
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

async def queue_notification_for_processing(notification_id: str):
    """Queue notification for batch processing"""
    
    queue_data = {
        "notification_id": notification_id,
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
        "queue_size": redis_client.llen("notification_queue")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)