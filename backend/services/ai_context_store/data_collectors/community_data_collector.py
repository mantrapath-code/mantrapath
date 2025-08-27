"""
Community Data Collector for AI Context Store
Collects community activity data to build user context
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)

class CommunityDataCollector:
    """Collects community activity data for context building"""
    
    def __init__(self):
        self.community_service_url = "http://community-service:8006"
        self.timeout = 30
        
    async def collect_user_community_data(self, user_id: str, jwt_token: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Collect community activity data for a user
        
        Args:
            user_id: User ID to collect data for
            jwt_token: Authentication token
            days_back: How many days back to collect data
            
        Returns:
            Dictionary containing community context data
        """
        try:
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            
            community_data = {}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get user's posts
                try:
                    posts_response = await client.get(
                        f"{self.community_service_url}/api/v1/posts",
                        headers=headers,
                        params={"author_id": user_id, "limit": 50}
                    )
                    if posts_response.status_code == 200:
                        community_data["posts"] = posts_response.json()
                except Exception as e:
                    logger.warning(f"Failed to fetch posts: {e}")
                    community_data["posts"] = []
                
                # Get user's comments  
                try:
                    comments_response = await client.get(
                        f"{self.community_service_url}/api/v1/comments",
                        headers=headers,
                        params={"author_id": user_id, "limit": 50}
                    )
                    if comments_response.status_code == 200:
                        community_data["comments"] = comments_response.json()
                except Exception as e:
                    logger.warning(f"Failed to fetch comments: {e}")
                    community_data["comments"] = []
                
                # Get user's forum activity
                try:
                    forum_response = await client.get(
                        f"{self.community_service_url}/api/v1/forum/user-activity",
                        headers=headers
                    )
                    if forum_response.status_code == 200:
                        community_data["forum_activity"] = forum_response.json()
                except Exception as e:
                    logger.warning(f"Failed to fetch forum activity: {e}")
                    community_data["forum_activity"] = {}
                
                return self._process_community_data(community_data)
                    
        except Exception as e:
            logger.warning(f"Error collecting community data for user {user_id}: {e}")
            return {}
    
    def _process_community_data(self, community_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw community data into context format"""
        posts = community_data.get("posts", [])
        comments = community_data.get("comments", [])
        forum_activity = community_data.get("forum_activity", {})
        
        # Calculate engagement metrics
        total_posts = len(posts)
        total_comments = len(comments)
        
        # Recent activity (last 7 days)
        recent_cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent_posts = [p for p in posts if p.get('created_at', '') > recent_cutoff]
        recent_comments = [c for c in comments if c.get('created_at', '') > recent_cutoff]
        
        # Extract topics and interests
        all_content = []
        for post in posts:
            all_content.append(post.get('content', '') + ' ' + post.get('title', ''))
        for comment in comments:
            all_content.append(comment.get('content', ''))
        
        topics = self._extract_topics(' '.join(all_content))
        
        # Calculate engagement patterns
        engagement_patterns = self._analyze_engagement_patterns(posts, comments)
        
        # Support patterns (helping others)
        support_given = self._analyze_support_patterns(comments)
        
        return {
            "total_posts": total_posts,
            "total_comments": total_comments,
            "recent_posts": len(recent_posts),
            "recent_comments": len(recent_comments),
            "engagement_score": self._calculate_engagement_score(posts, comments),
            "common_topics": topics,
            "engagement_patterns": engagement_patterns,
            "support_given": support_given,
            "forum_activity": forum_activity,
            "community_standing": self._assess_community_standing(posts, comments),
            "last_active": self._get_last_activity_date(posts, comments),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from community content"""
        if not content:
            return []
        
        # Topic keywords related to mental health and wellness
        topic_keywords = {
            'anxiety': ['anxiety', 'anxious', 'worry', 'worried', 'nervous'],
            'depression': ['depression', 'depressed', 'sad', 'sadness', 'down'],
            'stress': ['stress', 'stressed', 'pressure', 'overwhelmed'],
            'mindfulness': ['mindfulness', 'meditation', 'mindful', 'breathing'],
            'relationships': ['relationship', 'partner', 'family', 'friends', 'social'],
            'work': ['work', 'job', 'career', 'workplace', 'boss'],
            'sleep': ['sleep', 'insomnia', 'tired', 'exhausted', 'rest'],
            'therapy': ['therapy', 'therapist', 'counseling', 'treatment'],
            'exercise': ['exercise', 'workout', 'fitness', 'running', 'gym'],
            'mood': ['mood', 'feeling', 'emotions', 'emotional']
        }
        
        content_lower = content.lower()
        found_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def _analyze_engagement_patterns(self, posts: List[Dict], comments: List[Dict]) -> Dict[str, Any]:
        """Analyze user's engagement patterns"""
        if not posts and not comments:
            return {}
        
        # Time-based patterns
        all_activities = []
        for post in posts:
            if post.get('created_at'):
                all_activities.append(post['created_at'])
        for comment in comments:
            if comment.get('created_at'):
                all_activities.append(comment['created_at'])
        
        if not all_activities:
            return {}
        
        # Find most active time
        activity_by_hour = {}
        for activity in all_activities:
            try:
                hour = datetime.fromisoformat(activity.replace('Z', '+00:00')).hour
                activity_by_hour[hour] = activity_by_hour.get(hour, 0) + 1
            except:
                continue
        
        most_active_hour = max(activity_by_hour, key=activity_by_hour.get) if activity_by_hour else None
        
        return {
            "posts_vs_comments_ratio": total_posts / (total_posts + total_comments) if (total_posts + total_comments) > 0 else 0,
            "most_active_hour": most_active_hour,
            "activity_frequency": len(all_activities) / 30,  # activities per day over last 30 days
            "engagement_consistency": self._calculate_consistency(all_activities)
        }
    
    def _analyze_support_patterns(self, comments: List[Dict]) -> Dict[str, Any]:
        """Analyze how much support the user provides to others"""
        if not comments:
            return {"support_score": 0, "supportive_responses": 0}
        
        supportive_keywords = ['hope', 'support', 'help', 'understand', 'sorry', 'here for you', 'better', 'care', 'love', 'strong', 'brave', 'proud']
        
        supportive_count = 0
        total_words = 0
        
        for comment in comments:
            content = comment.get('content', '').lower()
            total_words += len(content.split())
            if any(keyword in content for keyword in supportive_keywords):
                supportive_count += 1
        
        return {
            "support_score": supportive_count / len(comments) if comments else 0,
            "supportive_responses": supportive_count,
            "avg_comment_length": total_words / len(comments) if comments else 0
        }
    
    def _calculate_engagement_score(self, posts: List[Dict], comments: List[Dict]) -> float:
        """Calculate overall engagement score"""
        post_score = len(posts) * 2  # Posts are weighted more
        comment_score = len(comments) * 1
        
        # Factor in likes/reactions if available
        total_likes = 0
        for post in posts:
            total_likes += post.get('likes_count', 0)
        for comment in comments:
            total_likes += comment.get('likes_count', 0)
        
        like_score = min(total_likes * 0.1, 10)  # Cap at 10 points
        
        return min(post_score + comment_score + like_score, 100)  # Cap at 100
    
    def _assess_community_standing(self, posts: List[Dict], comments: List[Dict]) -> str:
        """Assess user's standing in the community"""
        engagement_score = self._calculate_engagement_score(posts, comments)
        
        if engagement_score >= 50:
            return "highly_active"
        elif engagement_score >= 20:
            return "moderately_active"
        elif engagement_score >= 5:
            return "occasionally_active"
        else:
            return "new_or_inactive"
    
    def _get_last_activity_date(self, posts: List[Dict], comments: List[Dict]) -> Optional[str]:
        """Get the date of last community activity"""
        all_dates = []
        
        for post in posts:
            if post.get('created_at'):
                all_dates.append(post['created_at'])
        for comment in comments:
            if comment.get('created_at'):
                all_dates.append(comment['created_at'])
        
        return max(all_dates) if all_dates else None
    
    def _calculate_consistency(self, activities: List[str]) -> float:
        """Calculate consistency of community engagement"""
        if len(activities) < 2:
            return 0.0
        
        try:
            dates = [datetime.fromisoformat(activity.replace('Z', '+00:00')).date() for activity in activities]
            unique_dates = list(set(dates))
            
            # Calculate days between first and last activity
            if len(unique_dates) < 2:
                return 1.0
            
            date_range = (max(unique_dates) - min(unique_dates)).days
            if date_range == 0:
                return 1.0
            
            # Consistency is the ratio of active days to total days in range
            return len(unique_dates) / (date_range + 1)
        except:
            return 0.0
