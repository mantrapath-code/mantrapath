"""
Community Feed Endpoints - Unified feed system
"""
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from shared.database import get_db
from shared.auth import get_current_user
from shared.user_display import get_user_display_name
from shared.models import (
    User, Challenge, CommunityEvent, CommunityForum, ForumThread, 
    ThreadReply, ChallengeComment, EventComment, ChallengeProgress,
    ChallengeParticipant, EventParticipant, ForumMembership, Like
)

logger = logging.getLogger(__name__)

def get_community_feed(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    types: str = Query("thread,challenge,event", description="Comma-separated content types"),
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, all"),
    sort_by: str = Query("recent", description="Sort by: recent, popular, trending"),
    limit: int = Query(20, le=50)
):
    """Get unified community feed with filtering"""
    try:
        user_id = current_user.get('user_id')
        feed_items = []
        
        # Parse filters
        content_types = [t.strip() for t in types.split(',')]
        
        # Calculate time filter
        time_filter = None
        if time_range != 'all':
            days = {'1d': 1, '7d': 7, '30d': 30}.get(time_range, 7)
            time_filter = datetime.utcnow() - timedelta(days=days)
        
        # Get threads
        if 'thread' in content_types:
            threads_query = db.query(ForumThread).join(CommunityForum)
            if time_filter:
                threads_query = threads_query.filter(ForumThread.created_at >= time_filter)
            
            threads = threads_query.order_by(desc(ForumThread.created_at)).limit(limit).all()
            
            for thread in threads:
                # Get engagement metrics
                like_count = db.query(Like).filter(
                    Like.content_type == 'thread',
                    Like.content_id == thread.id
                ).count()
                
                comment_count = db.query(ThreadReply).filter(
                    ThreadReply.thread_id == thread.id
                ).count()
                
                is_liked = db.query(Like).filter(
                    Like.user_id == user_id,
                    Like.content_type == 'thread',
                    Like.content_id == thread.id
                ).first() is not None
                
                # Get forum info
                forum = db.query(CommunityForum).filter(
                    CommunityForum.id == thread.forum_id
                ).first()
                
                feed_items.append({
                    'id': thread.id,
                    'type': 'thread',
                    'title': thread.title,
                    'content': thread.content,
                    'author': {
                        'id': thread.author_id,
                        'name': get_user_display_name({'id': thread.author_id})
                    },
                    'created_at': thread.created_at.isoformat(),
                    'engagement': {
                        'likes': like_count,
                        'comments': comment_count
                    },
                    'category': forum.category if forum else 'general',
                    'is_liked': is_liked,
                    'metadata': {
                        'forum_id': thread.forum_id,
                        'forum_name': forum.name if forum else 'Unknown'
                    }
                })
        
        # Get challenges
        if 'challenge' in content_types:
            challenges_query = db.query(Challenge)
            if time_filter:
                challenges_query = challenges_query.filter(Challenge.created_at >= time_filter)
            
            challenges = challenges_query.order_by(desc(Challenge.created_at)).limit(limit).all()
            
            for challenge in challenges:
                participant_count = db.query(ChallengeParticipant).filter(
                    ChallengeParticipant.challenge_id == challenge.id
                ).count()
                
                comment_count = db.query(ChallengeComment).filter(
                    ChallengeComment.challenge_id == challenge.id
                ).count()
                
                feed_items.append({
                    'id': challenge.id,
                    'type': 'challenge',
                    'title': challenge.title,
                    'content': challenge.description,
                    'author': {
                        'id': challenge.created_by,
                        'name': get_user_display_name({'id': challenge.created_by})
                    },
                    'created_at': challenge.created_at.isoformat(),
                    'engagement': {
                        'likes': 0,  # Could implement challenge likes
                        'comments': comment_count,
                        'participants': participant_count
                    },
                    'category': challenge.category,
                    'is_liked': False,
                    'metadata': {
                        'duration_days': challenge.duration_days,
                        'end_date': challenge.end_date.isoformat() if challenge.end_date else None
                    }
                })
        
        # Get events
        if 'event' in content_types:
            events_query = db.query(CommunityEvent)
            if time_filter:
                events_query = events_query.filter(CommunityEvent.created_at >= time_filter)
            
            events = events_query.order_by(desc(CommunityEvent.created_at)).limit(limit).all()
            
            for event in events:
                participant_count = db.query(EventParticipant).filter(
                    EventParticipant.event_id == event.id
                ).count()
                
                comment_count = db.query(EventComment).filter(
                    EventComment.event_id == event.id
                ).count()
                
                feed_items.append({
                    'id': event.id,
                    'type': 'event',
                    'title': event.title,
                    'content': event.description,
                    'author': {
                        'id': event.created_by,
                        'name': get_user_display_name({'id': event.created_by})
                    },
                    'created_at': event.created_at.isoformat(),
                    'engagement': {
                        'likes': 0,  # Could implement event likes
                        'comments': comment_count,
                        'participants': participant_count
                    },
                    'category': 'events',
                    'is_liked': False,
                    'metadata': {
                        'start_time': event.start_time.isoformat(),
                        'end_time': event.end_time.isoformat(),
                        'is_virtual': event.is_virtual
                    }
                })
        
        # Sort feed items
        if sort_by == 'popular':
            feed_items.sort(key=lambda x: x['engagement']['likes'] + x['engagement']['comments'], reverse=True)
        elif sort_by == 'trending':
            # Simple trending algorithm based on recent engagement
            for item in feed_items:
                hours_old = (datetime.utcnow() - datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))).total_seconds() / 3600
                engagement_score = item['engagement']['likes'] + item['engagement']['comments']
                item['trending_score'] = engagement_score / max(hours_old, 1)
            feed_items.sort(key=lambda x: x.get('trending_score', 0), reverse=True)
        else:  # recent
            feed_items.sort(key=lambda x: x['created_at'], reverse=True)
        
        return feed_items[:limit]
        
    except Exception as e:
        logger.error(f"Error getting community feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get community feed")

def get_user_community_score(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate user's community engagement score"""
    try:
        user_id = current_user.get('user_id')
        
        # Participation score (0-25)
        forums_joined = db.query(ForumMembership).filter(
            ForumMembership.user_id == user_id,
            ForumMembership.is_active == True
        ).count()
        
        challenges_joined = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.user_id == user_id
        ).count()
        
        events_joined = db.query(EventParticipant).filter(
            EventParticipant.user_id == user_id
        ).count()
        
        participation_score = min(25, (forums_joined * 3) + (challenges_joined * 2) + (events_joined * 2))
        
        # Engagement score (0-25)
        threads_created = db.query(ForumThread).filter(
            ForumThread.author_id == user_id
        ).count()
        
        replies_posted = db.query(ThreadReply).filter(
            ThreadReply.author_id == user_id
        ).count()
        
        likes_given = db.query(Like).filter(
            Like.user_id == user_id
        ).count()
        
        engagement_score = min(25, (threads_created * 3) + (replies_posted * 2) + (likes_given * 1))
        
        # Helpfulness score (0-25) - based on likes received
        likes_received = db.query(Like).join(ForumThread, Like.content_id == ForumThread.id).filter(
            ForumThread.author_id == user_id,
            Like.content_type == 'thread'
        ).count()
        
        reply_likes = db.query(Like).join(ThreadReply, Like.content_id == ThreadReply.id).filter(
            ThreadReply.author_id == user_id,
            Like.content_type == 'reply'
        ).count()
        
        helpfulness_score = min(25, (likes_received * 2) + (reply_likes * 2))
        
        # Consistency score (0-25) - based on recent activity
        recent_activity = db.query(ForumThread).filter(
            ForumThread.author_id == user_id,
            ForumThread.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        recent_replies = db.query(ThreadReply).filter(
            ThreadReply.author_id == user_id,
            ThreadReply.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        consistency_score = min(25, (recent_activity * 3) + (recent_replies * 2))
        
        # Calculate total score
        total_score = participation_score + engagement_score + helpfulness_score + consistency_score
        
        # Determine level
        if total_score >= 80:
            level = "Community Champion"
            next_threshold = 100
        elif total_score >= 60:
            level = "Active Member"
            next_threshold = 80
        elif total_score >= 40:
            level = "Regular Contributor"
            next_threshold = 60
        elif total_score >= 20:
            level = "Community Member"
            next_threshold = 40
        else:
            level = "New Member"
            next_threshold = 20
        
        return {
            'total_score': total_score,
            'breakdown': {
                'participation': participation_score,
                'engagement': engagement_score,
                'helpfulness': helpfulness_score,
                'consistency': consistency_score
            },
            'level': level,
            'next_level_threshold': next_threshold
        }
        
    except Exception as e:
        logger.error(f"Error calculating community score: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate community score")