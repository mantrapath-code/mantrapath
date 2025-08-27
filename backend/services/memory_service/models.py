"""
Memory Service Database Models
Enhanced models for comprehensive user interaction tracking
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

Base = declarative_base()

class UserInteraction(Base):
    """Enhanced user interaction model for comprehensive tracking"""
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(100), nullable=False)  # mood, chat, journal, community
    interaction_data = Column(JSON, nullable=False)
    cultural_context = Column(JSON, nullable=True)
    source_service = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    session_id = Column(String(255), nullable=True, index=True)
    metadata = Column(JSON, nullable=True)
    processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    patterns = relationship("MoodPattern", back_populates="interactions")
    insights = relationship("BehavioralInsight", back_populates="interaction")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_user_type_timestamp', 'user_id', 'interaction_type', 'timestamp'),
        Index('idx_source_timestamp', 'source_service', 'timestamp'),
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
    )

class MoodPattern(Base):
    """Mood pattern tracking for behavioral analysis"""
    __tablename__ = 'mood_patterns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    pattern_type = Column(String(100), nullable=False)  # trend, cycle, anomaly
    pattern_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    interaction_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Foreign key to interactions
    primary_interaction_id = Column(Integer, ForeignKey('user_interactions.id'), nullable=True)
    
    # Relationships
    interactions = relationship("UserInteraction", back_populates="patterns")
    insights = relationship("BehavioralInsight", back_populates="pattern")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_pattern_active', 'user_id', 'pattern_type', 'is_active'),
        Index('idx_user_confidence', 'user_id', 'confidence_score'),
        Index('idx_date_range', 'start_date', 'end_date'),
    )

class BehavioralInsight(Base):
    """Behavioral insights generated from user interactions"""
    __tablename__ = 'behavioral_insights'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False)  # recommendation, warning, celebration
    insight_data = Column(JSON, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    recommendations = Column(JSON, nullable=True)
    is_acted_upon = Column(Boolean, default=False)
    feedback_score = Column(Float, nullable=True)
    generated_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Foreign keys
    interaction_id = Column(Integer, ForeignKey('user_interactions.id'), nullable=True)
    pattern_id = Column(Integer, ForeignKey('mood_patterns.id'), nullable=True)
    
    # Relationships
    interaction = relationship("UserInteraction", back_populates="insights")
    pattern = relationship("MoodPattern", back_populates="insights")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_insight_type', 'user_id', 'insight_type'),
        Index('idx_user_accuracy', 'user_id', 'accuracy_score'),
        Index('idx_generated_expires', 'generated_at', 'expires_at'),
        Index('idx_acted_upon', 'is_acted_upon'),
    )

class MemorySession(Base):
    """Memory sessions for grouping related interactions"""
    __tablename__ = 'memory_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_type = Column(String(100), nullable=False)  # daily, chat, journal, mood_tracking
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    interaction_count = Column(Integer, default=0)
    session_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_user_session_type', 'user_id', 'session_type'),
        Index('idx_session_active', 'is_active', 'start_time'),
        Index('idx_session_time_range', 'start_time', 'end_time'),
    )

class MemoryAggregation(Base):
    """Aggregated memory data for performance optimization"""
    __tablename__ = 'memory_aggregations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    aggregation_type = Column(String(100), nullable=False)  # daily, weekly, monthly
    aggregation_date = Column(DateTime(timezone=True), nullable=False)
    total_interactions = Column(Integer, default=0)
    interaction_breakdown = Column(JSON, nullable=True)
    mood_summary = Column(JSON, nullable=True)
    activity_summary = Column(JSON, nullable=True)
    insights_count = Column(Integer, default=0)
    patterns_count = Column(Integer, default=0)
    last_calculated = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_user_aggregation_date', 'user_id', 'aggregation_type', 'aggregation_date'),
        Index('idx_aggregation_calculated', 'last_calculated'),
    )

class UserMemoryProfile(Base):
    """User memory profile for personalized tracking"""
    __tablename__ = 'user_memory_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    profile_data = Column(JSON, nullable=False)
    preferences = Column(JSON, nullable=True)
    privacy_settings = Column(JSON, nullable=True)
    retention_period_days = Column(Integer, default=365)
    last_interaction = Column(DateTime(timezone=True), nullable=True)
    total_interactions = Column(Integer, default=0)
    memory_score = Column(Float, nullable=True)  # Overall memory engagement score
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_user_active', 'is_active', 'last_interaction'),
        Index('idx_memory_score', 'memory_score'),
    )

class InteractionEmotion(Base):
    """Emotion tracking for interactions"""
    __tablename__ = 'interaction_emotions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interaction_id = Column(Integer, ForeignKey('user_interactions.id'), nullable=False)
    emotion_name = Column(String(100), nullable=False)
    emotion_intensity = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence_score = Column(Float, nullable=False)
    detected_by = Column(String(100), nullable=False)  # service that detected emotion
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationship
    interaction = relationship("UserInteraction")
    
    # Indexes
    __table_args__ = (
        Index('idx_interaction_emotion', 'interaction_id', 'emotion_name'),
        Index('idx_emotion_intensity', 'emotion_name', 'emotion_intensity'),
    )

class MemoryCache(Base):
    """Cache table for frequently accessed memory data"""
    __tablename__ = 'memory_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    cache_data = Column(JSON, nullable=False)
    cache_type = Column(String(100), nullable=False)  # recent_interactions, patterns, insights
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_cache_expires', 'expires_at'),
        Index('idx_user_cache_type', 'user_id', 'cache_type'),
    )

# Database initialization function
def create_memory_tables(engine):
    """Create all memory service tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Memory Service tables created successfully")

def get_memory_table_info():
    """Get information about memory service tables"""
    tables = Base.metadata.tables
    table_info = {}
    
    for table_name, table in tables.items():
        columns = [{"name": col.name, "type": str(col.type)} for col in table.columns]
        indexes = [idx.name for idx in table.indexes]
        
        table_info[table_name] = {
            "columns": columns,
            "indexes": indexes,
            "column_count": len(columns)
        }
    
    return table_info

if __name__ == "__main__":
    # Display table information
    info = get_memory_table_info()
    print("Memory Service Database Schema:")
    for table_name, details in info.items():
        print(f"\n📋 Table: {table_name}")
        print(f"   Columns: {details['column_count']}")
        print(f"   Indexes: {len(details['indexes'])}")
        for col in details['columns'][:5]:  # Show first 5 columns
            print(f"   - {col['name']}: {col['type']}")
        if details['column_count'] > 5:
            print(f"   ... and {details['column_count'] - 5} more columns")
