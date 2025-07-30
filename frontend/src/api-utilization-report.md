# MantraPath API Utilization Report

This document provides a comprehensive analysis of backend API route utilization in the MantraPath frontend application.

## Executive Summary

**Total Backend Routes**: 176 routes across 8 microservices  
**Currently Utilized**: 47 routes (26.7%)  
**Unutilized**: 129 routes (73.3%)  

## Service-by-Service Analysis

### 🔐 Auth Service (24 routes)
**Utilized**: 6/24 routes (25%)

#### ✅ Currently Used:
- `POST /register` - User registration
- `POST /login` - User login  
- `POST /logout` - User logout
- `POST /refresh-token` - Token refresh
- `GET /me` - Get current user
- `POST /validate` - Token validation

#### ❌ Not Utilized:
- `POST /logout-all` - Logout from all devices
- `POST /revoke-token` - Revoke refresh token
- `POST /verify` - Verify user account
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user by ID
- `POST /change-password` - Change password
- `GET /status` - User status
- `POST /password-reset/request` - Request password reset
- `POST /password-reset/confirm` - Confirm password reset
- All admin endpoints (9 routes)
- Health check endpoints (4 routes)

### 👤 Profile Service (12 routes)
**Utilized**: 4/12 routes (33%)

#### ✅ Currently Used:
- `GET /api/profiles/me` - Get current profile
- `PATCH /api/profiles/` - Update profile
- `GET /api/preferences/` - Get preferences
- `PATCH /api/preferences/` - Update preferences

#### ❌ Not Utilized:
- `GET /api/profiles/` - List profiles
- `POST /api/profiles/` - Create profile
- `DELETE /api/profiles/` - Delete profile
- `GET /api/profiles/{profile_id}` - Get profile by ID
- `GET /api/profiles/search` - Search profiles
- Privacy preferences endpoints (2 routes)
- Theme preferences endpoints (2 routes)
- Health check endpoints (4 routes)

### 😊 Mood Service (50 routes)
**Utilized**: 8/50 routes (16%)

#### ✅ Currently Used:
- `GET /api/v1/mood/` - Get mood entries
- `POST /api/v1/mood/` - Create mood entry
- `GET /api/v1/mood/analytics/summary` - Mood analytics
- `GET /api/v1/insights/` - Get insights
- `POST /api/v1/insights/generate` - Generate insights
- `GET /api/v1/analytics/overview` - Analytics overview
- `GET /api/v1/analytics/trends` - Trend analysis
- `GET /api/v1/analytics/health-score` - Health score

#### ❌ Not Utilized:
- Individual mood entry operations (3 routes)
- Bulk mood operations
- Context tags and predictions (2 routes)
- Journal management (10 routes)
- Habits tracking (14 routes)
- Advanced insights operations (11 routes)
- Advanced analytics (11 routes)
- Health check endpoint

### 🤖 Chatbot Service (17 routes)
**Utilized**: 6/17 routes (35%)

#### ✅ Currently Used:
- `POST /api/chatbot/chat` - Send chat message
- `POST /api/chatbot/enhanced/chat` - Enhanced chat
- `GET /api/chatbot/chat/session` - Get session
- `POST /api/chatbot/chat/session` - Create session
- `GET /api/chatbot/chat/history` - Chat history
- `GET /api/chatbot/chat/suggestions` - Get suggestions

#### ❌ Not Utilized:
- `POST /api/chatbot/enhanced/chat/enhanced` - Advanced enhanced chat
- `POST /api/chatbot/chat/upload` - File upload for chat
- `GET /api/chatbot/chat/sessions` - Get all sessions
- `GET /api/chatbot/chat/conversations` - Get conversations
- `POST /api/chatbot/chat/feedback` - Chat feedback
- Analytics endpoints (3 routes)
- Health check endpoints (4 routes)

### 📝 Content Service (14 routes)
**Utilized**: 7/14 routes (50%)

#### ✅ Currently Used:
- `GET /content/{id}` - Get content by ID
- `GET /content/feed` - Content feed
- `GET /content/search` - Search content
- `GET /affirmations` - Get affirmations
- `GET /affirmations/random` - Random affirmation
- `POST /bookmark/{content_id}` - Bookmark content
- `GET /bookmarks` - Get bookmarks

#### ❌ Not Utilized:
- `PUT /content/{id}` - Update content
- `DELETE /content/{id}` - Delete content
- `GET /content/category/{category}` - Content by category
- `POST /affirmations` - Create affirmation
- `GET /affirmations/analytics` - Affirmations analytics
- `DELETE /bookmark/{content_id}` - Remove bookmark
- Challenge endpoints (3 routes)
- `DELETE /user/{user_id}/delete` - Delete user data
- `GET /health` - Health check

### 👥 Community Service (37 routes)
**Utilized**: 15/37 routes (41%)

#### ✅ Currently Used:
- `GET /forums` - Get forums
- `POST /forums` - Create forum
- `GET /forums/{forum_id}` - Get forum
- `POST /forums/{forum_id}/join` - Join forum
- `DELETE /forums/{forum_id}/leave` - Leave forum
- `GET /forums/{forum_id}/threads` - Get threads
- `POST /forums/thread` - Create thread
- `POST /forums/thread/{thread_id}/reply` - Reply to thread
- `POST /forums/like` - Like content
- `DELETE /forums/like/{content_type}/{content_id}` - Remove like
- `GET /forums/events` - Get events
- `POST /forums/events` - Create event
- `GET /forums/challenges` - Get challenges
- `POST /forums/challenges` - Create challenge
- `GET /forums/search` - Search community

#### ❌ Not Utilized:
- Forum management (2 routes)
- Forum membership (2 routes)
- Thread management (4 routes)
- Thread views and stats (2 routes)
- Comments (1 route)
- Like status check (1 route)
- Moderation and reporting (4 routes)
- Support and guidelines (3 routes)
- Event/challenge joining (4 routes - **PRIORITY**)
- Tags and categories (3 routes)
- Media attachments (2 routes)
- User management (3 routes)
- Volunteer system (2 routes)
- Health check (1 route)

### 🔔 Notification Service (6 routes)
**Utilized**: 4/6 routes (67%)

#### ✅ Currently Used:
- `POST /notify/send` - Send notification
- `GET /notify/recent` - Get recent notifications
- `GET /notify/preferences` - Get preferences
- `PUT /notify/preferences` - Update preferences

#### ❌ Not Utilized:
- `POST /notify/schedule` - Schedule notification
- `DELETE /user/{user_id}/delete` - Delete user data
- Health check endpoints (2 routes)

### 📁 Media Service (16 routes)
**Utilized**: 1/16 routes (6%)

#### ✅ Currently Used:
- `POST /api/v1/media/upload` - Upload media

#### ❌ Not Utilized:
- Media management (7 routes)
- Media interactions (5 routes)
- Moderation (2 routes)
- User management (1 route)
- Health checks (2 routes)

## Priority Implementation Recommendations

### High Priority (Essential Features)
1. **Event/Challenge Participation** - Community Service
   - `POST /forums/events/{event_id}/join`
   - `DELETE /forums/events/{event_id}/leave` 
   - `POST /forums/challenges/{challenge_id}/join`
   - `DELETE /forums/challenges/{challenge_id}/leave`

2. **Password Management** - Auth Service
   - `POST /change-password`
   - `POST /password-reset/request`
   - `POST /password-reset/confirm`

3. **Enhanced Mood Tracking** - Mood Service
   - `GET /api/v1/mood/{mood_id}` - Individual mood details
   - `PUT /api/v1/mood/{mood_id}` - Update mood entries
   - `DELETE /api/v1/mood/{mood_id}` - Delete mood entries

### Medium Priority (User Experience Enhancement)
1. **Journal Functionality** - Mood Service
   - Complete journal management system (10 routes)
   - Sentiment analysis and search capabilities

2. **Media Management** - Media Service  
   - Complete media interaction system (15 routes)
   - Essential for rich community posts

3. **Thread Management** - Community Service
   - Thread views, updates, and detailed management

### Low Priority (Advanced Features)
1. **Habits Tracking** - Mood Service (14 routes)
2. **Advanced Analytics** - Mood Service (11 routes)
3. **Admin Functionality** - Auth Service (9 routes)
4. **Moderation Tools** - Community Service (4 routes)

## Technical Debt Analysis

### Areas of Concern:
1. **Media Service Underutilization**: Only 6% usage despite being critical for community engagement
2. **Mood Service Complex Features**: Advanced analytics and habits tracking not implemented
3. **Missing Error Handling**: Many API calls lack comprehensive error handling
4. **Authentication Gaps**: Password reset and account verification not implemented

### Recommendations:
1. Implement event/challenge participation immediately
2. Add comprehensive error boundary components
3. Create a media management interface
4. Implement journal functionality for better user engagement
5. Add password reset flow for better UX

## Backend Compatibility Notes

The current implementation is compatible with the documented backend APIs with the following considerations:

### ✅ Properly Implemented:
- All API calls use correct HTTP methods
- Request/response patterns match OpenAPI specifications  
- Authentication headers are properly included
- Error handling follows standard patterns

### ⚠️ Needs Attention:
- Event/challenge participation endpoints are called but may not exist in current backend
- Some mock data structures may not match exact backend schemas
- File upload handling needs FormData header management

### 🔧 Backend Route Validation Required:
These endpoints are used in frontend but need backend verification:
- `POST /forums/events/{event_id}/join`
- `DELETE /forums/events/{event_id}/leave`
- `POST /forums/challenges/{challenge_id}/join` 
- `DELETE /forums/challenges/{challenge_id}/leave`

## Conclusion

The MantraPath frontend demonstrates good API integration patterns but has significant room for feature expansion. The 73.3% of unutilized routes represent opportunities for enhanced functionality, particularly in areas like journal management, habits tracking, and advanced analytics.

The immediate priority should be completing the community events and challenges functionality, followed by implementing password management and enhanced mood tracking features.