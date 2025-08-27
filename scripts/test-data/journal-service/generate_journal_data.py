#!/usr/bin/env python3
"""
Journal Service Test Data Generator
Creates realistic journal entries for testing insights and correlations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from auth_helper import get_authenticated_session

class JournalDataGenerator:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        
        # Journal entry templates by mood category
        self.journal_templates = {
            "high_mood": [
                "Had an amazing day! Everything went smoothly and I felt really productive. Spent time {activity} which always makes me feel great.",
                "Feeling fantastic today. {activity} really helped boost my energy. Grateful for {gratitude}.",
                "What a wonderful day! Successfully completed {achievement} and feeling really accomplished.",
                "Great mood today! {activity} with friends was exactly what I needed. Looking forward to tomorrow.",
                "Feeling energized and positive. {activity} this morning set a great tone for the day."
            ],
            "medium_mood": [
                "Decent day overall. Had some ups and downs but managed to {activity}. Feeling okay about progress.",
                "Average day today. {activity} helped maintain balance. Some challenges but nothing too overwhelming.",
                "Feeling neutral but stable. {activity} was relaxing and helped me stay centered.",
                "Okay day, not great but not bad either. {activity} provided some good moments.",
                "Mixed feelings today. {activity} was helpful but still feeling a bit {emotion}."
            ],
            "low_mood": [
                "Struggling a bit today. Tried {activity} to lift my spirits but still feeling {emotion}.",
                "Difficult day. Finding it hard to stay motivated. {activity} helped a little but mood still low.",
                "Not feeling great today. {emotion} is weighing on me. {activity} provided brief relief.",
                "Challenging day emotionally. {activity} was somewhat helpful but still processing {emotion}.",
                "Tough day. Feeling {emotion}. Hoping {activity} tomorrow will help improve things."
            ]
        }
        
        # Activity options
        self.activities = [
            "exercising", "reading", "meditating", "walking", "cooking", "listening to music",
            "spending time in nature", "talking with friends", "working on hobbies", "journaling",
            "practicing yoga", "watching movies", "playing games", "learning something new"
        ]
        
        # Emotions for different moods
        self.emotions = {
            "high": ["excited", "grateful", "accomplished", "energized", "optimistic"],
            "medium": ["neutral", "contemplative", "steady", "balanced", "content"],
            "low": ["anxious", "overwhelmed", "tired", "frustrated", "uncertain"]
        }
        
        # Gratitude items
        self.gratitude_items = [
            "good health", "supportive friends", "family time", "work opportunities",
            "beautiful weather", "peaceful moments", "personal growth", "new experiences"
        ]
        
        # Achievements
        self.achievements = [
            "a work project", "exercise goals", "learning objectives", "personal tasks",
            "creative projects", "social connections", "health improvements", "skill development"
        ]
    
    def get_mood_category(self, mood_score: int) -> str:
        """Categorize mood score for appropriate journal content"""
        if mood_score >= 7:
            return "high_mood"
        elif mood_score >= 4:
            return "medium_mood"
        else:
            return "low_mood"
    
    def generate_journal_content(self, mood_score: int) -> str:
        """Generate journal content based on mood score"""
        category = self.get_mood_category(mood_score)
        template = random.choice(self.journal_templates[category])
        
        # Replace placeholders with random content
        content = template.format(
            activity=random.choice(self.activities),
            emotion=random.choice(self.emotions[category.replace("_mood", "")]),
            gratitude=random.choice(self.gratitude_items),
            achievement=random.choice(self.achievements)
        )
        
        return content
    
    def create_journal_entry(self, content: str, date: datetime, mood_before: int = None, mood_after: int = None):
        """Create a single journal entry"""
        try:
            journal_data = {
                "content": content,
                "mood_before": mood_before,
                "mood_after": mood_after,
                "tags": self.generate_tags(content),
                "timestamp": date.isoformat()
            }
            
            response = self.auth.make_request(
                "POST",
                "/api/v1/journal/",
                json=journal_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created journal entry on {date.strftime('%Y-%m-%d')}")
                return response.json()
            else:
                print(f"❌ Failed to create journal entry: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating journal entry: {e}")
            return None
    
    def generate_tags(self, content: str) -> list:
        """Generate relevant tags for journal content"""
        tags = []
        
        # Activity-based tags
        for activity in self.activities:
            if activity in content.lower():
                tags.append(activity.replace(" ", "_"))
        
        # Emotion-based tags
        all_emotions = []
        for emotion_list in self.emotions.values():
            all_emotions.extend(emotion_list)
        
        for emotion in all_emotions:
            if emotion in content.lower():
                tags.append(emotion)
        
        # General tags based on keywords
        if any(word in content.lower() for word in ["work", "project", "job"]):
            tags.append("work")
        if any(word in content.lower() for word in ["friend", "social", "people"]):
            tags.append("social")
        if any(word in content.lower() for word in ["exercise", "gym", "workout"]):
            tags.append("fitness")
        if any(word in content.lower() for word in ["grateful", "thankful", "appreciate"]):
            tags.append("gratitude")
        
        return list(set(tags))[:5]  # Limit to 5 unique tags
    
    def generate_entries_with_mood_correlation(self, days: int = 30):
        """Generate journal entries that correlate with mood scores"""
        print(f"\n📝 Generating {days} days of mood-correlated journal entries...")
        
        base_date = datetime.now() - timedelta(days=days)
        created_count = 0
        
        for day in range(days):
            # Generate 1-2 entries per day
            entries_per_day = random.randint(1, 2)
            
            for entry in range(entries_per_day):
                # Generate mood scores for before/after
                mood_before = random.randint(3, 8)
                
                # Journal writing often helps mood slightly
                mood_after = min(10, mood_before + random.randint(0, 2))
                
                # Generate content based on the average mood
                avg_mood = (mood_before + mood_after) // 2
                content = self.generate_journal_content(avg_mood)
                
                entry_time = base_date + timedelta(
                    days=day,
                    hours=random.randint(18, 22),  # Evening entries
                    minutes=random.randint(0, 59)
                )
                
                if self.create_journal_entry(content, entry_time, mood_before, mood_after):
                    created_count += 1
        
        print(f"✅ Created {created_count} mood-correlated journal entries")
    
    def generate_themed_entries(self, theme: str = "gratitude", entries: int = 10):
        """Generate journal entries around a specific theme"""
        print(f"\n🎯 Generating {entries} {theme}-themed journal entries...")
        
        theme_templates = {
            "gratitude": [
                "Today I'm grateful for {gratitude}. It really made me appreciate {activity}.",
                "Feeling thankful for {gratitude}. Spent time {activity} and felt blessed.",
                "Grateful moment: {gratitude}. {activity} reminded me of life's good things."
            ],
            "growth": [
                "Learned something new today through {activity}. Growth feels good even when challenging.",
                "Personal development moment: {activity} taught me about {emotion}.",
                "Growing through {activity}. Each challenge is an opportunity to improve."
            ],
            "reflection": [
                "Reflecting on {activity} today. It made me feel {emotion} about my progress.",
                "Taking time to think about {activity}. Feeling {emotion} about the journey.",
                "Contemplative mood after {activity}. Processing feelings of {emotion}."
            ]
        }
        
        if theme not in theme_templates:
            print(f"❌ Unknown theme: {theme}")
            return
        
        base_date = datetime.now() - timedelta(days=entries)
        created_count = 0
        
        for day in range(entries):
            template = random.choice(theme_templates[theme])
            content = template.format(
                activity=random.choice(self.activities),
                emotion=random.choice(self.emotions["medium"]),
                gratitude=random.choice(self.gratitude_items)
            )
            
            entry_date = base_date + timedelta(days=day)
            mood_before = random.randint(5, 8)
            mood_after = min(10, mood_before + 1)
            
            if self.create_journal_entry(content, entry_date, mood_before, mood_after):
                created_count += 1
        
        print(f"✅ Created {created_count} {theme}-themed journal entries")

def main():
    """Main function to run journal data generation"""
    print("🚀 Starting Journal Service Test Data Generation...")
    
    try:
        # Get authenticated session
        auth = get_authenticated_session("primary")
        generator = JournalDataGenerator(auth)
        
        # Generate different types of test data
        print("\n" + "="*50)
        print("Choose journal data generation option:")
        print("1. Mood-correlated entries (30 days)")
        print("2. Gratitude-themed entries (10 entries)")
        print("3. Growth-themed entries (10 entries)")
        print("4. Reflection-themed entries (10 entries)")
        print("5. Comprehensive journal data (all types)")
        print("="*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            generator.generate_entries_with_mood_correlation(30)
        elif choice == "2":
            generator.generate_themed_entries("gratitude", 10)
        elif choice == "3":
            generator.generate_themed_entries("growth", 10)
        elif choice == "4":
            generator.generate_themed_entries("reflection", 10)
        elif choice == "5":
            print("🎯 Generating comprehensive journal data...")
            generator.generate_entries_with_mood_correlation(25)
            generator.generate_themed_entries("gratitude", 7)
            generator.generate_themed_entries("growth", 7)
            generator.generate_themed_entries("reflection", 6)
        else:
            print("❌ Invalid choice")
            return
        
        print("\n🎉 Journal test data generation completed!")
        
    except Exception as e:
        print(f"❌ Error in journal data generation: {e}")

if __name__ == "__main__":
    main()
