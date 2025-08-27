#!/usr/bin/env python3
"""
Community Service Test Data Generator
Creates realistic community posts, comments, and interactions for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from auth_helper import get_authenticated_session

class CommunityDataGenerator:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        
        # Available forums (get these dynamically in a real implementation)
        self.forums = [
            {"id": "9406512c-7357-4d3d-b9e7-8e17aeb4c3b5", "name": "Mental Health Support"},
            {"id": "8f179914-4080-454a-8e49-bc40a898ec0b", "name": "General Discussion"},
            {"id": "becb404a-57df-4350-8e52-f5dd8e7f5752", "name": "Challenge Support"},
            {"id": "71812c09-7305-457a-b667-b62fb8f47495", "name": "Mindfulness & Meditation"}
        ]
        
        # Post titles by category
        self.post_titles = {
            "motivation": [
                "Daily motivation boost! 🌟",
                "Small wins that made my day",
                "Finding strength in routine",
                "Progress isn't always linear",
                "Celebrating today's achievements"
            ],
            "support": [
                "Looking for encouragement today",
                "Sharing my struggles and hopes", 
                "How do you cope with difficult times?",
                "Grateful for this community",
                "We're in this together 💚"
            ],
            "gratitude": [
                "Today I'm grateful for...",
                "Appreciation post ✨",
                "Finding joy in simple moments",
                "Blessed and thankful",
                "What are you grateful for?"
            ],
            "tips": [
                "Life hack that changed my perspective",
                "Sharing what works for me",
                "Quick tip for better days",
                "Mental health strategy that helps",
                "Pro tip from my journey"
            ],
            "milestone": [
                "Milestone Monday celebration! 🎉",
                "Personal record achieved!",
                "Big win to share",
                "Goal reached after months of work",
                "Progress update - feeling proud!"
            ]
        }
        
        # Post content templates by category
        self.post_templates = {
            "motivation": [
                "Just wanted to share that I've been feeling more positive lately! 🌟 {activity} has really helped me stay motivated.",
                "Small wins matter! Today I managed to {achievement} and it feels great. Keep pushing forward everyone! 💪",
                "Reminder: Progress isn't always linear. {activity} taught me that it's okay to have ups and downs.",
                "Finding strength in {activity}. Anyone else have activities that instantly boost their mood?",
                "Celebrating {achievement} today! Sometimes the smallest steps make the biggest difference."
            ],
            "support": [
                "Going through a tough time and could use some encouragement. {activity} helps a bit but still struggling.",
                "Has anyone else found {activity} helpful during difficult periods? Looking for new strategies.",
                "Feeling {emotion} today. Grateful for this supportive community. You all make a difference.",
                "Rough day but trying to stay hopeful. {activity} provided some relief. How do you cope?",
                "Sending love to anyone else having a challenging time. We're in this together. 💚"
            ],
            "gratitude": [
                "Grateful for {gratitude} today. {activity} reminded me of life's simple pleasures. ✨",
                "Appreciation post: Thank you to everyone who shares their journey here. {activity} feels more meaningful with community support.",
                "Today I'm thankful for {gratitude}. {activity} helped me recognize all the good in my life.",
                "Feeling blessed after {activity}. What are you grateful for today?",
                "Grateful moment: {gratitude}. This community always reminds me of the positive things."
            ],
            "tips": [
                "Life hack: {activity} has been a game-changer for my mental health. Highly recommend trying it!",
                "Pro tip: When feeling {emotion}, try {activity}. It's made a huge difference for me.",
                "Sharing what works: {activity} + {secondary_activity} = instant mood boost for me. Worth trying!",
                "Found that {activity} works better when done consistently. Anyone else notice this?",
                "Quick tip: {activity} for just 10 minutes can completely shift your day. Give it a try!"
            ],
            "milestone": [
                "Milestone Monday! Just completed {achievement} and feeling incredibly proud! 🎉",
                "Personal record: {number} days of consistent {activity}! The journey continues.",
                "Big win today: {achievement}! Thank you to this community for the constant inspiration.",
                "Celebrating {achievement} after weeks of {activity}. Persistence pays off!",
                "Reached a goal I set months ago: {achievement}. {activity} was key to getting here."
            ]
        }
        
        # Comment templates for interactions
        self.comment_templates = [
            "This is so inspiring! Thank you for sharing 💚",
            "I really needed to read this today. Thank you!",
            "Love this! {activity} has helped me too.",
            "So proud of your progress! Keep it up! 🌟",
            "This resonates with me. Thanks for the reminder.",
            "Sending you positive vibes! You've got this! ✨",
            "Great advice! I'm going to try {activity}.",
            "Your journey is inspiring. Thank you for being vulnerable.",
            "This made my day! Community support is everything.",
            "So relatable. We're all in this together! 💪"
        ]
        
        # Activities and contexts
        self.activities = [
            "meditation", "journaling", "exercise", "reading", "walking in nature",
            "yoga", "deep breathing", "listening to music", "creative writing",
            "painting", "cooking", "gardening", "volunteering", "learning new skills"
        ]
        
        self.achievements = [
            "30 days of consistent meditation", "first 5K run", "reading 10 books this year",
            "writing in my journal daily", "completing a creative project", "learning a new skill",
            "maintaining work-life balance", "practicing self-compassion", "setting healthy boundaries"
        ]
        
        self.gratitude_items = [
            "supportive friends", "family time", "good health", "peaceful moments",
            "nature's beauty", "learning opportunities", "this community", "personal growth"
        ]
        
        self.emotions = [
            "overwhelmed", "anxious", "uncertain", "hopeful", "grateful",
            "excited", "contemplative", "energized", "peaceful"
        ]
    
    def create_community_post(self, category: str, date: datetime):
        """Create a community post"""
        try:
            template = random.choice(self.post_templates[category])
            
            # Select random forum and title
            forum = random.choice(self.forums)
            title = random.choice(self.post_titles.get(category, self.post_titles["motivation"]))
            
            # Fill in template variables
            content = template.format(
                activity=random.choice(self.activities),
                secondary_activity=random.choice(self.activities),
                achievement=random.choice(self.achievements),
                gratitude=random.choice(self.gratitude_items),
                emotion=random.choice(self.emotions),
                number=random.randint(5, 100)
            )
            
            post_data = {
                "forum_id": forum["id"],
                "title": title,
                "content": content,
                "category": category,
                "tags": self.generate_tags(content, category),
                "is_anonymous": random.choice([True, False]),
                "timestamp": date.isoformat()
            }
            
            response = self.auth.make_request(
                "POST",
                "/forums/thread",
                json=post_data
            )
            
            if response.status_code in [200, 201]:
                post_id = response.json().get("id")
                print(f"✅ Created {category} post '{title}' in {forum['name']} on {date.strftime('%Y-%m-%d')}")
                return post_id
            else:
                print(f"❌ Failed to create post: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating post: {e}")
            return None
    
    def create_comment(self, post_id: str, date: datetime):
        """Create a comment on a post"""
        try:
            template = random.choice(self.comment_templates)
            content = template.format(activity=random.choice(self.activities))
            
            comment_data = {
                "content": content,
                "post_id": post_id,
                "timestamp": date.isoformat()
            }
            
            response = self.auth.make_request(
                "POST",
                f"/forums/thread/{post_id}/reply",
                json=comment_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created comment on post {post_id}")
                return response.json()
            else:
                print(f"❌ Failed to create comment: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating comment: {e}")
            return None
    
    def add_reaction(self, post_id: str, reaction_type: str = "like"):
        """Add a reaction to a post"""
        try:
            response = self.auth.make_request(
                "POST",
                "/forums/like",
                json={"type": reaction_type, "thread_id": post_id}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Added {reaction_type} to post {post_id}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error adding reaction: {e}")
            return False
    
    def generate_tags(self, content: str, category: str) -> list:
        """Generate relevant tags for community content"""
        tags = [category]
        
        # Activity-based tags
        for activity in self.activities:
            if activity in content.lower():
                tags.append(activity.replace(" ", "_"))
        
        # Emotion-based tags
        for emotion in self.emotions:
            if emotion in content.lower():
                tags.append(emotion)
        
        # General tags
        if any(word in content.lower() for word in ["grateful", "thankful", "appreciation"]):
            tags.append("gratitude")
        if any(word in content.lower() for word in ["goal", "milestone", "achievement"]):
            tags.append("achievement")
        if any(word in content.lower() for word in ["support", "help", "encourage"]):
            tags.append("support")
        
        return list(set(tags))[:5]
    
    def generate_community_activity(self, days: int = 30):
        """Generate diverse community activity over specified days"""
        print(f"\n👥 Generating {days} days of community activity...")
        
        base_date = datetime.now() - timedelta(days=days)
        created_posts = []
        
        for day in range(days):
            # Generate 1-3 posts per day
            posts_per_day = random.randint(1, 3)
            
            for post_num in range(posts_per_day):
                category = random.choice(list(self.post_templates.keys()))
                
                post_time = base_date + timedelta(
                    days=day,
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                
                post_id = self.create_community_post(category, post_time)
                if post_id:
                    created_posts.append(post_id)
                    
                    # Add some comments and reactions
                    if random.random() < 0.7:  # 70% chance of comments
                        comment_time = post_time + timedelta(
                            hours=random.randint(1, 12)
                        )
                        self.create_comment(post_id, comment_time)
                    
                    if random.random() < 0.8:  # 80% chance of reactions
                        reaction = random.choice(["like", "heart", "support"])
                        self.add_reaction(post_id, reaction)
        
        print(f"✅ Created {len(created_posts)} community posts with interactions")
        
        # Generate challenges (3-5 challenges total)
        print(f"\n🏆 Generating challenges...")
        created_challenges = []
        for i in range(random.randint(3, 5)):
            challenge_id = self.create_challenge()
            if challenge_id:
                created_challenges.append(challenge_id)
        
        # Generate events (2-4 events total)
        print(f"\n📅 Generating events...")
        created_events = []
        for i in range(random.randint(2, 4)):
            event_id = self.create_event()
            if event_id:
                created_events.append(event_id)
        
        print(f"🎯 Total created: {len(created_posts)} posts, {len(created_challenges)} challenges, {len(created_events)} events")
        return created_posts, created_challenges, created_events
    
    def create_challenge(self):
        """Create a community challenge"""
        try:
            challenge_templates = [
                {
                    "title": "30-Day Mindfulness Challenge",
                    "description": "Join us for 30 days of daily mindfulness practice. Each day we'll focus on a different aspect of mindfulness.",
                    "type": "mindfulness",
                    "duration_days": 30,
                    "difficulty": "beginner"
                },
                {
                    "title": "Weekly Gratitude Practice",
                    "description": "Share three things you're grateful for every day this week. Let's build a habit of gratitude together!",
                    "type": "gratitude",
                    "duration_days": 7,
                    "difficulty": "beginner"
                },
                {
                    "title": "Digital Detox Weekend",
                    "description": "Take a break from social media and digital distractions for the weekend. Focus on real-world connections.",
                    "type": "wellness",
                    "duration_days": 2,
                    "difficulty": "intermediate"
                },
                {
                    "title": "Morning Routine Mastery",
                    "description": "Establish a consistent morning routine that sets you up for success. Share your progress and tips!",
                    "type": "habits",
                    "duration_days": 21,
                    "difficulty": "intermediate"
                },
                {
                    "title": "Acts of Kindness Challenge",
                    "description": "Perform one act of kindness each day. Small gestures can make a big difference!",
                    "type": "community",
                    "duration_days": 14,
                    "difficulty": "beginner"
                }
            ]
            
            challenge_data = random.choice(challenge_templates)
            
            # Add dynamic dates
            start_date = datetime.now() + timedelta(days=random.randint(1, 7))
            end_date = start_date + timedelta(days=challenge_data["duration_days"])
            
            challenge_data.update({
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "max_participants": random.randint(50, 200),
                "is_active": True
            })
            
            response = self.auth.make_request(
                "POST",
                "/forums/challenges",
                json=challenge_data
            )
            
            if response.status_code in [200, 201]:
                challenge_id = response.json().get("id")
                print(f"✅ Created challenge: {challenge_data['title']}")
                return challenge_id
            else:
                print(f"❌ Failed to create challenge: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating challenge: {e}")
            return None
    
    def create_event(self):
        """Create a community event"""
        try:
            event_templates = [
                {
                    "title": "Weekly Meditation Circle",
                    "description": "Join us for a guided meditation session. All levels welcome! Bring your own cushion or chair.",
                    "type": "meditation",
                    "location": "Community Center - Room A",
                    "is_virtual": False
                },
                {
                    "title": "Mental Health First Aid Workshop",
                    "description": "Learn how to provide initial support to someone experiencing mental health challenges.",
                    "type": "workshop",
                    "location": "Online via Zoom",
                    "is_virtual": True
                },
                {
                    "title": "Nature Walk & Mindfulness",
                    "description": "Combine gentle exercise with mindfulness practice in beautiful natural surroundings.",
                    "type": "outdoor",
                    "location": "City Park - Main Entrance",
                    "is_virtual": False
                },
                {
                    "title": "Stress Management Webinar",
                    "description": "Expert-led session on practical stress management techniques for daily life.",
                    "type": "webinar",
                    "location": "Online Event",
                    "is_virtual": True
                },
                {
                    "title": "Community Support Group",
                    "description": "Safe space to share experiences and support each other. Facilitated by trained counselors.",
                    "type": "support",
                    "location": "Community Center - Quiet Room",
                    "is_virtual": False
                }
            ]
            
            event_data = random.choice(event_templates)
            
            # Add dynamic dates and times
            event_date = datetime.now() + timedelta(days=random.randint(7, 30))
            start_hour = random.randint(9, 19)
            duration_minutes = random.choice([60, 90, 120])
            start_time = event_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            event_data.update({
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "max_participants": random.randint(20, 100),
                "is_virtual": random.choice([True, False])
            })
            
            # Remove the old fields that don't match the API
            event_data.pop("date", None)
            event_data.pop("time", None)
            event_data.pop("duration_minutes", None)
            event_data.pop("registration_required", None)
            
            response = self.auth.make_request(
                "POST",
                "/forums/events",
                json=event_data
            )
            
            if response.status_code in [200, 201]:
                event_id = response.json().get("id")
                print(f"✅ Created event: {event_data['title']}")
                return event_id
            else:
                print(f"❌ Failed to create event: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return None
    
    def generate_themed_discussion(self, theme: str = "mental_health_awareness"):
        """Generate a themed discussion thread"""
        print(f"\n💬 Generating {theme} discussion thread...")
        
        theme_posts = {
            "mental_health_awareness": [
                "Mental Health Awareness Week: What's one thing that has helped your mental health journey?",
                "Reminder: It's okay to not be okay. Seeking help is a sign of strength, not weakness.",
                "Let's share resources! What books, apps, or practices have supported your mental health?"
            ],
            "motivation_monday": [
                "Motivation Monday: What's keeping you motivated this week?",
                "Monday reset: Share one goal you're working toward this week!",
                "New week, new opportunities. What's your intention for this Monday?"
            ],
            "wellness_wednesday": [
                "Wellness Wednesday: What does self-care look like for you today?",
                "Midweek check-in: How are you taking care of yourself this week?",
                "Wellness tip Wednesday: Share your favorite way to recharge!"
            ]
        }
        
        if theme not in theme_posts:
            print(f"❌ Unknown theme: {theme}")
            return
        
        base_time = datetime.now() - timedelta(hours=2)
        
        for i, content in enumerate(theme_posts[theme]):
            post_time = base_time + timedelta(minutes=i * 30)
            
            post_data = {
                "content": content,
                "category": "discussion",
                "tags": [theme, "community", "discussion"],
                "is_pinned": i == 0,  # Pin the first post
                "timestamp": post_time.isoformat()
            }
            
            response = self.auth.make_request(
                "POST",
                "/api/v1/community/posts",
                json=post_data
            )
            
            if response.status_code in [200, 201]:
                post_id = response.json().get("id")
                print(f"✅ Created {theme} discussion post")
                
                # Add some engagement
                for j in range(random.randint(2, 5)):
                    comment_time = post_time + timedelta(minutes=j * 15)
                    self.create_comment(post_id, comment_time)

def main():
    """Main function to run community data generation"""
    print("🚀 Starting Community Service Test Data Generation...")
    
    try:
        # Get authenticated session
        auth = get_authenticated_session("primary")
        generator = CommunityDataGenerator(auth)
        
        # Generate different types of test data
        print("\n" + "="*50)
        print("Choose community data generation option:")
        print("1. General community activity (30 days)")
        print("2. Mental health awareness discussion")
        print("3. Motivation Monday thread")
        print("4. Wellness Wednesday thread")
        print("5. Comprehensive community data (all types)")
        print("="*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            generator.generate_community_activity(30)
        elif choice == "2":
            generator.generate_themed_discussion("mental_health_awareness")
        elif choice == "3":
            generator.generate_themed_discussion("motivation_monday")
        elif choice == "4":
            generator.generate_themed_discussion("wellness_wednesday")
        elif choice == "5":
            print("🎯 Generating comprehensive community data...")
            generator.generate_community_activity(20)
            generator.generate_themed_discussion("mental_health_awareness")
            generator.generate_themed_discussion("motivation_monday")
        else:
            print("❌ Invalid choice")
            return
        
        print("\n🎉 Community test data generation completed!")
        
    except Exception as e:
        print(f"❌ Error in community data generation: {e}")

if __name__ == "__main__":
    main()
