#!/usr/bin/env python3
"""
Mood Service Test Data Generator
Creates realistic mood entries with various patterns for testing insights
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from auth_helper import get_authenticated_session

class MoodDataGenerator:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        
        # Mood patterns for realistic data
        self.mood_patterns = {
            "stable": [7, 7, 6, 8, 7, 7, 6],  # Stable week
            "improving": [4, 5, 6, 7, 8, 8, 9],  # Getting better
            "declining": [8, 7, 6, 5, 4, 5, 4],  # Getting worse
            "volatile": [3, 8, 4, 9, 2, 7, 5],  # Up and down
            "weekend_boost": [6, 6, 7, 7, 8, 9, 8]  # Better on weekends
        }
        
        self.energy_levels = [3, 4, 5, 6, 7, 8, 9]
        self.stress_levels = [1, 2, 3, 4, 5, 6, 7]
        
        # Contexts for mood entries
        self.contexts = [
            {"activity": "work", "location": "office", "weather": "sunny"},
            {"activity": "exercise", "location": "gym", "weather": "cloudy"},
            {"activity": "socializing", "location": "restaurant", "weather": "rainy"},
            {"activity": "reading", "location": "home", "weather": "sunny"},
            {"activity": "walking", "location": "park", "weather": "clear"},
            {"activity": "meditation", "location": "home", "weather": "overcast"},
            {"activity": "working", "location": "office", "weather": "sunny"}
        ]
    
    def create_mood_entry(self, mood_score: int, date: datetime, context: dict = None):
        """Create a single mood entry"""
        try:
            mood_data = {
                "mood_score": mood_score,
                "energy_level": random.choice(self.energy_levels),
                "stress_level": random.choice(self.stress_levels),
                "notes": f"Feeling {self._mood_description(mood_score)} today",
                "context": context or random.choice(self.contexts),
                "timestamp": date.isoformat()
            }
            
            response = self.auth.make_request(
                "POST",
                "/api/v1/mood/",
                json=mood_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created mood entry: {mood_score}/10 on {date.strftime('%Y-%m-%d')}")
                return response.json()
            else:
                print(f"❌ Failed to create mood entry: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating mood entry: {e}")
            return None
    
    def _mood_description(self, score: int) -> str:
        """Convert mood score to description"""
        if score >= 9: return "amazing"
        elif score >= 7: return "good"
        elif score >= 5: return "okay"
        elif score >= 3: return "low"
        else: return "very low"
    
    def generate_pattern_data(self, pattern_name: str, weeks: int = 4):
        """Generate mood data following a specific pattern"""
        if pattern_name not in self.mood_patterns:
            print(f"❌ Unknown pattern: {pattern_name}")
            return
        
        pattern = self.mood_patterns[pattern_name]
        base_date = datetime.now() - timedelta(weeks=weeks)
        
        print(f"\n📊 Generating {weeks} weeks of '{pattern_name}' mood data...")
        
        created_count = 0
        for week in range(weeks):
            for day, mood_score in enumerate(pattern):
                # Add some randomness to make it realistic
                actual_score = max(1, min(10, mood_score + random.randint(-1, 1)))
                
                entry_date = base_date + timedelta(weeks=week, days=day)
                
                if self.create_mood_entry(actual_score, entry_date):
                    created_count += 1
        
        print(f"✅ Created {created_count} mood entries for '{pattern_name}' pattern")
    
    def generate_diverse_data(self, days: int = 30):
        """Generate diverse mood data for the last N days"""
        print(f"\n📊 Generating diverse mood data for last {days} days...")
        
        base_date = datetime.now() - timedelta(days=days)
        created_count = 0
        
        for day in range(days):
            # Create 1-3 entries per day with some variety
            entries_per_day = random.randint(1, 3)
            
            for entry in range(entries_per_day):
                # Generate realistic mood scores with some patterns
                if day % 7 in [5, 6]:  # Weekends tend to be better
                    mood_score = random.randint(6, 9)
                elif day % 7 == 0:  # Mondays can be tough
                    mood_score = random.randint(3, 7)
                else:  # Regular weekdays
                    mood_score = random.randint(4, 8)
                
                entry_time = base_date + timedelta(
                    days=day, 
                    hours=random.randint(8, 20),
                    minutes=random.randint(0, 59)
                )
                
                if self.create_mood_entry(mood_score, entry_time):
                    created_count += 1
        
        print(f"✅ Created {created_count} diverse mood entries")
    
    def generate_streak_data(self, streak_length: int = 7, mood_range: tuple = (7, 9)):
        """Generate data for a good mood streak"""
        print(f"\n🔥 Generating {streak_length}-day mood streak data...")
        
        base_date = datetime.now() - timedelta(days=streak_length + 5)
        created_count = 0
        
        for day in range(streak_length):
            mood_score = random.randint(mood_range[0], mood_range[1])
            entry_date = base_date + timedelta(days=day)
            
            if self.create_mood_entry(mood_score, entry_date):
                created_count += 1
        
        print(f"✅ Created {created_count} entries for mood streak")

def main():
    """Main function to run mood data generation"""
    print("🚀 Starting Mood Service Test Data Generation...")
    
    try:
        # Get authenticated session
        auth = get_authenticated_session("primary")
        generator = MoodDataGenerator(auth)
        
        # Generate different types of test data
        print("\n" + "="*50)
        print("Choose data generation option:")
        print("1. Diverse realistic data (30 days)")
        print("2. Stable mood pattern (4 weeks)")
        print("3. Improving mood pattern (4 weeks)")
        print("4. Weekend boost pattern (4 weeks)")
        print("5. Mood streak data (7 days)")
        print("6. All patterns (comprehensive)")
        print("="*50)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            generator.generate_diverse_data(30)
        elif choice == "2":
            generator.generate_pattern_data("stable", 4)
        elif choice == "3":
            generator.generate_pattern_data("improving", 4)
        elif choice == "4":
            generator.generate_pattern_data("weekend_boost", 4)
        elif choice == "5":
            generator.generate_streak_data(7, (7, 9))
        elif choice == "6":
            print("🎯 Generating comprehensive test data...")
            generator.generate_diverse_data(45)
            generator.generate_pattern_data("improving", 2)
            generator.generate_streak_data(5, (8, 10))
        else:
            print("❌ Invalid choice")
            return
        
        print("\n🎉 Mood test data generation completed!")
        
    except Exception as e:
        print(f"❌ Error in mood data generation: {e}")

if __name__ == "__main__":
    main()
