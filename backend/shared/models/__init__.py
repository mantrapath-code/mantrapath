"""
Shared models for MantraPath backend services.
"""
import importlib.util
import os

# Import all models from the standalone models.py file using absolute path
shared_dir = os.path.dirname(os.path.dirname(__file__))
models_file = os.path.join(shared_dir, 'models.py')

spec = importlib.util.spec_from_file_location("shared_models", models_file)
if spec is None or spec.loader is None:
    raise ImportError("Could not load shared models")

shared_models_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared_models_module)

# Import all models from shared_models_module
User = shared_models_module.User
UserProfile = shared_models_module.UserProfile
UserLanguagePreference = shared_models_module.UserLanguagePreference
MoodEntry = shared_models_module.MoodEntry
JournalEntry = shared_models_module.JournalEntry
ChatSession = shared_models_module.ChatSession
ChatMessage = shared_models_module.ChatMessage
CommunityForum = shared_models_module.CommunityForum
ForumThread = shared_models_module.ForumThread
ThreadReply = shared_models_module.ThreadReply
Notification = shared_models_module.Notification
ScheduledNotification = shared_models_module.ScheduledNotification
ForumMembership = shared_models_module.ForumMembership
Like = shared_models_module.Like
Content = shared_models_module.Content
Affirmation = shared_models_module.Affirmation
CommunityEvent = shared_models_module.CommunityEvent
Challenge = shared_models_module.Challenge
ChallengeInvitation = shared_models_module.ChallengeInvitation
ChallengeLeaderboard = shared_models_module.ChallengeLeaderboard
ChallengeProgress = shared_models_module.ChallengeProgress
ChallengeParticipant = shared_models_module.ChallengeParticipant
ChallengeComment = shared_models_module.ChallengeComment
EventParticipant = shared_models_module.EventParticipant
EventComment = shared_models_module.EventComment
EmotionalWeatherForecast = shared_models_module.EmotionalWeatherForecast
CelebrationMoment = shared_models_module.CelebrationMoment
AdaptiveQuestion = shared_models_module.AdaptiveQuestion
EnvironmentalData = shared_models_module.EnvironmentalData
Base = shared_models_module.Base

from .assistance import (
    AssistanceEvaluation,
    InterventionAnalysis,
    TimingEvaluation,
    CulturalEvaluation,
    AssistanceDecision,
    AssistanceContent,
    UserAssistanceNeeds,
    HealthStatus,
    IntegrationStatus,
    ServiceMetrics,
    CulturalProfile,
    AssistanceType,
    UrgencyLevel
)

__all__ = [
    'Base',
    'User',
    'UserProfile', 
    'UserLanguagePreference',
    'MoodEntry',
    'JournalEntry',
    'ChatSession',
    'ChatMessage',
    'CommunityForum',
    'ForumThread',
    'ThreadReply',
    'Notification',
    'ScheduledNotification',
    'ForumMembership',
    'Like',
    'Content',
    'Affirmation',
    'CommunityEvent',
    'Challenge',
    'ChallengeInvitation',
    'ChallengeLeaderboard',
    'ChallengeProgress',
    'ChallengeParticipant',
    'ChallengeComment',
    'EventParticipant',
    'EventComment',
    'EmotionalWeatherForecast',
    'CelebrationMoment',
    'AdaptiveQuestion',
    'EnvironmentalData',
    'AssistanceEvaluation',
    'InterventionAnalysis', 
    'TimingEvaluation',
    'CulturalEvaluation',
    'AssistanceDecision',
    'AssistanceContent',
    'UserAssistanceNeeds',
    'HealthStatus',
    'IntegrationStatus',
    'ServiceMetrics',
    'CulturalProfile',
    'AssistanceType',
    'UrgencyLevel'
]
