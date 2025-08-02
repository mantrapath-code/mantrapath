#!/usr/bin/env python3
"""
Test Script for Enhanced Chatbot Context Engine
Demonstrates the new personalized AI capabilities
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from shared.database import get_db, engine
from shared.models import User, UserProfile, MoodEntry, JournalEntry, ChatSession, Base

# Import the new context engine
from services.chatbot_service.context_engine import UserContextEngine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

class ContextEngineTest:
    def __init__(self):
        self.context_engine = UserContextEngine()
    
    async def create_test_user_data(self, db: Session):
        """Create comprehensive test data for a user"""
        
        # Create test user
        test_user = User(
            id="test-user-123",
            email="test@mantrapath.com",
            username="testuser",
            password_hash="dummy_hash",
            first_name="Alice",
            last_name="Johnson",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        
        # Create user profile
        test_profile = UserProfile(
            user_id="test-user-123",
            bio="Mental wellness enthusiast",
            timezone="America/New_York",
            notifications_enabled=True,
            daily_reminder_enabled=True,
            theme_preference="dark"
        )
        
        # Create mood entries showing a declining trend
        mood_entries = []
        for i in range(20):
            days_ago = i
            # Simulate declining mood over time
            mood_score = max(1, 4 - (i * 0.15))  # Start at 4, decline to ~1
            
            mood_entry = MoodEntry(
                user_id="test-user-123",
                mood_score=int(mood_score),
                energy_level=max(1, int(mood_score)),
                stress_level=min(5, int(6 - mood_score)),
                notes=f"Day {i} mood entry",
                context_tags=["work", "anxiety"] if i > 10 else ["family", "social"],
                created_at=datetime.utcnow() - timedelta(days=days_ago)
            )
            mood_entries.append(mood_entry)
        
        # Create journal entries
        journal_entries = []
        journal_content = [
            "Today I felt overwhelmed at work. The project deadlines are piling up.",
            "Grateful for my morning walk. Nature always helps me feel centered.",
            "Had a difficult conversation with my manager. Feeling uncertain about my role.",
            "Meditation session was particularly calming today. Need to do this more often.",
            "Struggled with anxiety again. The breathing exercises from the app helped.",
            "Family dinner was nice. Reminded me what's really important in life.",
            "Work stress is affecting my sleep. Need to find better coping strategies.",
            "Journaling is becoming a helpful habit. Writing helps me process emotions."
        ]
        
        for i, content in enumerate(journal_content):
            journal_entry = JournalEntry(
                user_id="test-user-123",
                title=f"Journal Entry {i+1}",
                content=content,
                mood_before=2 + i % 3,
                mood_after=3 + i % 3,
                sentiment_score=0.3 if "difficult" in content or "anxiety" in content else 0.7,
                themes=["work", "anxiety"] if "work" in content else ["gratitude", "self-care"],
                word_count=len(content.split()),
                created_at=datetime.utcnow() - timedelta(days=i*2)
            )
            journal_entries.append(journal_entry)
        
        # Create chat session
        chat_session = ChatSession(
            user_id="test-user-123",
            title="Recent Chat",
            session_type="support",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        # Add all to database
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.id == "test-user-123").first()
            if existing_user:
                print("Test user already exists, skipping creation")
                return
            
            db.add(test_user)
            db.add(test_profile)
            db.add_all(mood_entries)
            db.add_all(journal_entries)
            db.add(chat_session)
            db.commit()
            
            print("✅ Test user data created successfully")
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.rollback()
    
    async def test_context_engine(self, db: Session):
        """Test the context engine with the test user"""
        
        print("\n🧠 Testing Enhanced Context Engine...")
        print("=" * 50)
        
        try:
            # Get user context
            start_time = datetime.utcnow()
            context = await self.context_engine.get_user_context("test-user-123", db)
            end_time = datetime.utcnow()
            
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            print(f"⏱️ Context retrieved in {processing_time:.2f}ms")
            print(f"📊 Context version: {context.context_version}")
            print(f"🔄 Last updated: {context.last_updated}")
            
            # Display profile information
            print(f"\n👤 Profile Information:")
            print(f"   Name: {context.profile.get('first_name')} {context.profile.get('last_name')}")
            print(f"   Account age: {context.profile.get('account_age_days')} days")
            print(f"   Timezone: {context.profile.get('timezone')}")
            print(f"   Privacy mode: {context.profile.get('privacy_mode')}")
            
            # Display mood patterns
            print(f"\n😊 Mood Patterns:")
            print(f"   Trend: {context.mood_patterns.get('trend')}")
            print(f"   Average mood: {context.mood_patterns.get('average_mood'):.2f}")
            print(f"   Recent average: {context.mood_patterns.get('recent_average'):.2f}")
            print(f"   Stability: {context.mood_patterns.get('stability')}")
            print(f"   Total entries: {context.mood_patterns.get('total_entries')}")
            print(f"   Common triggers: {context.mood_patterns.get('common_triggers')}")
            
            # Display writing style
            print(f"\n✍️ Writing Style:")
            print(f"   Total journal entries: {context.writing_style.get('total_entries')}")
            print(f"   Average word count: {context.writing_style.get('avg_word_count'):.0f}")
            print(f"   Average sentiment: {context.writing_style.get('avg_sentiment'):.2f}")
            print(f"   Common themes: {context.writing_style.get('common_themes')}")
            print(f"   Writing frequency: {context.writing_style.get('writing_frequency')} entries/month")
            
            # Display community behavior
            print(f"\n👥 Community Behavior:")
            print(f"   Engagement level: {context.community_behavior.get('engagement_level')}")
            print(f"   Forums joined: {context.community_behavior.get('forums_joined')}")
            print(f"   Total posts: {context.community_behavior.get('total_posts')}")
            
            # Display conversation insights
            print(f"\n💬 Conversation History:")
            print(f"   Total sessions: {context.conversation_history.get('total_sessions')}")
            print(f"   Recent topics: {context.conversation_history.get('recent_topics')}")
            
            # Display current state
            print(f"\n📈 Current State:")
            print(f"   Current mood score: {context.current_state.get('current_mood_score')}")
            print(f"   Overall state: {context.current_state.get('overall_state')}")
            print(f"   Engagement recency: {context.current_state.get('engagement_recency')}")
            print(f"   Days since last mood entry: {context.current_state.get('days_since_mood_entry')}")
            
            # Display communication preferences
            print(f"\n🗣️ Communication Preferences:")
            prefs = context.communication_preferences
            print(f"   Empathy level: {prefs.get('empathy_level'):.2f}")
            print(f"   Directness level: {prefs.get('directness_level'):.2f}")
            print(f"   Encouragement style: {prefs.get('encouragement_style')}")
            print(f"   Response length: {prefs.get('response_length')}")
            print(f"   Crisis sensitivity: {prefs.get('crisis_sensitivity')}")
            
            print(f"\n✅ Context engine test completed successfully!")
            
            return context
            
        except Exception as e:
            print(f"❌ Context engine test failed: {e}")
            raise
    
    async def test_personalized_responses(self, context):
        """Test personalized response generation"""
        
        print(f"\n🤖 Testing Personalized Response Generation...")
        print("=" * 50)
        
        # Import the response generator from enhanced_main
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'chatbot_service'))
        from enhanced_main import ContextualResponseGenerator
        
        response_generator = ContextualResponseGenerator()
        
        test_inputs = [
            "Hello, how are you?",
            "I'm feeling really anxious about work today",
            "I've been struggling lately and need some support",
            "How can I improve my mood?",
            "I want to hurt myself"
        ]
        
        for i, user_input in enumerate(test_inputs):
            print(f"\n📝 Test {i+1}: '{user_input}'")
            
            try:
                response_data = await response_generator.generate_personalized_response(
                    user_input, context
                )
                
                print(f"   🤖 Response: {response_data['response'][:200]}...")
                print(f"   📊 Personalization score: {response_data['personalization_score']:.2f}")
                print(f"   🎯 User state: {response_data['user_state']}")
                print(f"   💡 Message type: {response_data['message_type']}")
                
            except Exception as e:
                print(f"   ❌ Error generating response: {e}")
    
    async def run_full_test(self):
        """Run the complete test suite"""
        
        print("🚀 Starting Enhanced Chatbot Context Engine Test")
        print("=" * 60)
        
        # Get database session
        db = next(get_db())
        
        try:
            # Create test data
            await self.create_test_user_data(db)
            
            # Test context engine
            context = await self.test_context_engine(db)
            
            # Test personalized responses
            await self.test_personalized_responses(context)
            
            print(f"\n🎉 All tests completed successfully!")
            print("=" * 60)
            print("The enhanced chatbot is ready for personalized interactions!")
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            raise
        finally:
            db.close()

async def main():
    """Main test function"""
    tester = ContextEngineTest()
    await tester.run_full_test()

if __name__ == "__main__":
    print("MantraPath Enhanced AI - Context Engine Test")
    print("This script demonstrates the new personalized chatbot capabilities")
    print()
    
    asyncio.run(main())
