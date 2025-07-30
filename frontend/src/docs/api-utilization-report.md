# MantraPath Backend API Routes Utilization Report

**Generated on:** 2025-01-21  
**Frontend Framework:** React + TypeScript  
**Backend Architecture:** Microservices (API Gateway Pattern)

## Executive Summary

This report analyzes the integration between the MantraPath frontend and backend API routes. Out of **176 total backend routes** across 8 microservices, we have **implemented frontend integration for 47 routes (26.7%)** with **129 routes (73.3%) remaining unutilized**.

### Service-by-Service Integration Status

| Service | Total Routes | Integrated | Unutilized | Integration % |
|---------|-------------|------------|------------|---------------|
| Auth Service | 24 | 6 | 18 | 25.0% |
| Profile Service | 12 | 4 | 8 | 33.3% |
| Mood Service | 50 | 8 | 42 | 16.0% |
| Chatbot Service | 17 | 6 | 11 | 35.3% |
| Content Service | 14 | 7 | 7 | 50.0% |
| Community Service | 37 | 15 | 22 | 40.5% |
| Notification Service | 6 | 3 | 3 | 50.0% |
| Media Service | 16 | 3 | 13 | 18.8% |
| **TOTAL** | **176** | **52** | **124** | **29.5%** |

---

## Detailed Integration Analysis

### 🔐 Auth Service (6/24 integrated - 25.0%)

#### ✅ **INTEGRATED ROUTES**
```typescript
// Core authentication flows
POST /register           ✓ authApi.register()
POST /login             ✓ authApi.login()
POST /logout            ✓ authApi.logout()
POST /refresh-token     ✓ authApi.refreshToken()
GET /me                 ✓ authApi.getMe()
POST /validate          ✓ Used internally for token validation
```

#### ❌ **UNUTILIZED ROUTES (18)**
```typescript
// Session management
POST /logout-all                    // Logout from all devices
POST /revoke-token                  // Revoke refresh token
POST /verify                        // Verify user account

// User management
GET /users/{user_id}                // Get user by ID
PUT /users/{user_id}                // Update user by ID
POST /change-password               // Change user password
GET /status                         // Get user status

// Password reset flow
POST /password-reset/request        // Request password reset
POST /password-reset/confirm        // Confirm password reset

// Admin functionality
GET /admin/users                    // List all users (admin)
POST /admin/users                   // Create new user (admin)
GET /admin/roles                    // List all roles (admin)
POST /admin/roles                   // Create new role (admin)
POST /admin/users/{user_id}/activate      // Activate user
POST /admin/users/{user_id}/deactivate    // Deactivate user
POST /admin/users/{user_id}/roles/{role_name}    // Assign role
DELETE /admin/users/{user_id}/roles/{role_name}  // Remove role

// Health monitoring
GET /health/detailed                // Detailed health information
GET /health/live                    // Liveness probe
GET /health/ready                   // Readiness probe
```

**Priority Recommendations:**
1. **HIGH**: Implement password reset flow for production readiness
2. **MEDIUM**: Add user profile management (change password, account settings)
3. **LOW**: Admin panel for user management (future feature)

---

### 👤 Profile Service (4/12 integrated - 33.3%)

#### ✅ **INTEGRATED ROUTES**
```typescript
GET /api/profiles/me               ✓ profileApi.getProfile()
PATCH /api/profiles/               ✓ profileApi.updateProfile()
GET /api/preferences/              ✓ profileApi.getPreferences()
PATCH /api/preferences/            ✓ profileApi.updatePreferences()
```

#### ❌ **UNUTILIZED ROUTES (8)**
```typescript
// Profile management
GET /api/profiles/                 // List profiles (search/discovery)
POST /api/profiles/                // Create new profile
DELETE /api/profiles/              // Delete profile
GET /api/profiles/{profile_id}     // Get profile by ID
GET /api/profiles/search           // Search profiles

// Granular preferences
GET /api/preferences/privacy       // Get privacy preferences
PATCH /api/preferences/privacy     // Update privacy preferences
GET /api/preferences/theme         // Get theme preferences
PATCH /api/preferences/theme       // Update theme preferences
```

**Priority Recommendations:**
1. **HIGH**: Implement theme preferences for mood-based theming
2. **MEDIUM**: Privacy settings for community interaction
3. **LOW**: Profile discovery features

---

### 😊 Mood Service (8/50 integrated - 16.0%)

#### ✅ **INTEGRATED ROUTES**
```typescript
GET /api/v1/mood/                   ✓ moodApi.getMoodEntries()
POST /api/v1/mood/                  ✓ moodApi.createMoodEntry()
GET /api/v1/mood/analytics/summary  ✓ moodApi.getMoodAnalytics()
GET /api/v1/insights/               ✓ moodApi.getInsights()
POST /api/v1/insights/generate      ✓ moodApi.generateInsights()
GET /api/v1/analytics/overview      ✓ moodApi.getAnalyticsOverview()
GET /api/v1/analytics/trends        ✓ moodApi.getTrends()
GET /api/v1/analytics/health-score  ✓ moodApi.getHealthScore()
```

#### ❌ **UNUTILIZED ROUTES (42)**
```typescript
// Individual mood entry management
GET /api/v1/mood/{mood_id}          // Get specific mood entry
PUT /api/v1/mood/{mood_id}          // Update mood entry
DELETE /api/v1/mood/{mood_id}       // Delete mood entry
POST /api/v1/mood/bulk              // Bulk mood operations
GET /api/v1/mood/context-tags/popular     // Popular context tags
GET /api/v1/mood/prediction/next    // Predict next mood

// Journal system (CRITICAL MISSING)
GET /api/v1/journal/                // Get journal entries
POST /api/v1/journal/               // Create journal entry
GET /api/v1/journal/{entry_id}      // Get specific journal entry
PUT /api/v1/journal/{entry_id}      // Update journal entry
DELETE /api/v1/journal/{entry_id}   // Delete journal entry
POST /api/v1/journal/bulk           // Bulk journal operations
GET /api/v1/journal/search/         // Search journal entries
POST /api/v1/journal/{entry_id}/reanalyze    // Reanalyze entry
GET /api/v1/journal/analytics/sentiment      // Sentiment analysis
GET /api/v1/journal/analytics/themes         // Theme analysis

// Habits tracking (CRITICAL MISSING)
GET /api/v1/habits/                 // Get habits
POST /api/v1/habits/                // Create habit
GET /api/v1/habits/{habit_id}       // Get specific habit
PUT /api/v1/habits/{habit_id}       // Update habit
DELETE /api/v1/habits/{habit_id}    // Delete habit
POST /api/v1/habits/{habit_id}/pause      // Pause habit
POST /api/v1/habits/{habit_id}/resume     // Resume habit
GET /api/v1/habits/{habit_id}/streak      // Get habit streak
GET /api/v1/habits/{habit_id}/analytics   // Habit analytics
GET /api/v1/habits/analytics/overview     // Habits overview
GET /api/v1/habits/streaks/leaderboard    // Streaks leaderboard
GET /api/v1/habits/{habit_id}/events      // Get habit events
POST /api/v1/habits/{habit_id}/events     // Create habit event
PUT /api/v1/habits/{habit_id}/events/{event_id}     // Update habit event
DELETE /api/v1/habits/{habit_id}/events/{event_id}  // Delete habit event

// Advanced insights
GET /api/v1/insights/{insight_id}   // Get specific insight
PUT /api/v1/insights/{insight_id}   // Update insight
DELETE /api/v1/insights/{insight_id} // Delete insight
GET /api/v1/insights/search/        // Search insights
GET /api/v1/insights/recent/unread  // Get recent unread insights
POST /api/v1/insights/mark-all-read // Mark all insights as read
POST /api/v1/insights/{insight_id}/mark-read     // Mark insight as read
POST /api/v1/insights/{insight_id}/feedback      // Provide insight feedback
GET /api/v1/insights/types/{insight_type}        // Get insights by type
GET /api/v1/insights/categories/popular          // Popular insight categories
GET /api/v1/insights/analytics/summary           // Insights analytics summary

// Advanced analytics (PRIORITY)
GET /api/v1/analytics/correlations  // Correlation analysis
GET /api/v1/analytics/patterns/weekly        // Weekly patterns ✓ PLANNED
GET /api/v1/analytics/patterns/seasonal      // Seasonal patterns
GET /api/v1/analytics/insights/triggers      // Mood triggers analysis
GET /api/v1/analytics/insights/boosters      // Mood boosters analysis
GET /api/v1/analytics/habits/impact          // Habits impact analysis
GET /api/v1/analytics/journal/sentiment-trends     // Journal sentiment trends
GET /api/v1/analytics/predictions/mood       // Mood predictions
GET /api/v1/analytics/predictions/habits/{habit_id}  // Habit predictions
GET /api/v1/analytics/export                 // Export analytics data
POST /api/v1/analytics/refresh               // Refresh analytics data
```

**Priority Recommendations:**
1. **CRITICAL**: Implement journal system (currently using mock data)
2. **CRITICAL**: Implement habits tracking system
3. **HIGH**: Weekly patterns for mood pattern notifications
4. **HIGH**: Mood correlations and triggers analysis
5. **MEDIUM**: Individual mood entry management
6. **MEDIUM**: Advanced insights management

---

### 🤖 Chatbot Service (6/17 integrated - 35.3%)

#### ✅ **INTEGRATED ROUTES**
```typescript
POST /api/chatbot/chat              ✓ chatbotApi.sendMessage()
POST /api/chatbot/enhanced/chat     ✓ chatbotApi.enhancedChat()
GET /api/chatbot/chat/session       ✓ chatbotApi.getSession()
POST /api/chatbot/chat/session      ✓ chatbotApi.createSession()
GET /api/chatbot/chat/history       ✓ chatbotApi.getChatHistory()
GET /api/chatbot/chat/suggestions   ✓ chatbotApi.getSuggestions()
```

#### ❌ **UNUTILIZED ROUTES (11)**
```typescript
// Advanced chat features
POST /api/chatbot/enhanced/chat/enhanced    // Advanced enhanced chat
POST /api/chatbot/chat/upload               // Upload file for chat context

// Chat management
GET /api/chatbot/chat/sessions              // Get all chat sessions
GET /api/chatbot/chat/conversations         // Get conversations
POST /api/chatbot/chat/feedback             // Provide chat feedback

// Analytics
GET /api/chatbot/analytics                  // Chatbot analytics
GET /api/chatbot/chat/analytics             // Chat analytics
GET /api/chatbot/enhanced/chat/analytics    // Enhanced chat analytics

// Health monitoring
GET /health/detailed                        // Detailed health information
GET /health/phase2                          // Phase 2 health check
GET /api/chatbot/health                     // Chatbot specific health
```

**Priority Recommendations:**
1. **HIGH**: Implement file upload for chat context (images, documents)
2. **MEDIUM**: Chat feedback system for improving AI responses
3. **MEDIUM**: Chat analytics for usage insights
4. **LOW**: Multiple chat sessions management

---

### 📝 Content Service (7/14 integrated - 50.0%)

#### ✅ **INTEGRATED ROUTES**
```typescript
GET /content/{id}                   ✓ contentApi.getContent()
GET /content/feed                   ✓ contentApi.getContentFeed()
GET /content/search                 ✓ contentApi.searchContent()
GET /affirmations                   ✓ contentApi.getAffirmations()
GET /affirmations/random            ✓ contentApi.getRandomAffirmation()
POST /bookmark/{content_id}         ✓ contentApi.bookmarkContent()
GET /bookmarks                      ✓ contentApi.getBookmarks()
```

#### ❌ **UNUTILIZED ROUTES (7)**
```typescript
// Content management
PUT /content/{id}                   // Update content by ID
DELETE /content/{id}                // Delete content by ID
GET /content/category/{category}    // Get content by category

// Affirmations management
POST /affirmations                  // Create affirmation
GET /affirmations/analytics         // Affirmations analytics

// Bookmarks management
DELETE /bookmark/{content_id}       // Remove bookmark

// Challenges system (IMPORTANT)
GET /challenge/active               // Get active challenges
GET /challenge/{id}/status          // Get challenge status
POST /challenge/{id}/complete-step  // Complete challenge step
POST /challenge/{id}/complete-day   // Complete challenge day

// User management
DELETE /user/{user_id}/delete       // Delete user data
```

**Priority Recommendations:**
1. **HIGH**: Implement challenges system (mentioned in community requirements)
2. **MEDIUM**: Bookmark removal functionality
3. **MEDIUM**: Content categorization
4. **LOW**: Content management (admin features)

---

### 👥 Community Service (15/37 integrated - 40.5%)

#### ✅ **INTEGRATED ROUTES**
```typescript
// Forums management
GET /forums                         ✓ communityApi.getForums()
POST /forums                        ✓ communityApi.createForum()
GET /forums/{forum_id}              ✓ communityApi.getForum()
PUT /forums/{forum_id}              ✓ communityApi.updateForum()
DELETE /forums/{forum_id}           ✓ communityApi.deleteForum()

// Forum membership
POST /forums/{forum_id}/join        ✓ communityApi.joinForum()
DELETE /forums/{forum_id}/leave     ✓ communityApi.leaveForum()
GET /forums/{forum_id}/members      ✓ communityApi.getForumMembers()

// Threads & Posts
GET /forums/{forum_id}/threads      ✓ communityApi.getForumThreads()
POST /forums/thread                 ✓ communityApi.createThread()
GET /forums/thread/{thread_id}      ✓ communityApi.getThread()
POST /forums/thread/{thread_id}/reply     ✓ communityApi.replyToThread()

// Interactions
POST /forums/like                   ✓ communityApi.likeContent()
GET /forums/like/{content_type}/{content_id}    ✓ communityApi.getLikeStatus()
DELETE /forums/like/{content_type}/{content_id} ✓ communityApi.removeLike()
```

#### ❌ **UNUTILIZED ROUTES (22)**
```typescript
// Thread management
PUT /forums/thread/{thread_id}              // Update thread
DELETE /forums/thread/{thread_id}           // Delete thread
POST /forums/thread/{thread_id}/view        // Track thread view
GET /forums/thread/{thread_id}/view-stats   // Get thread view stats

// Comments system
POST /forums/comment                        // Add comment

// Search & Discovery
GET /forums/search                          // Search community content
GET /forums/analytics                       // Forums analytics

// Forum features
POST /forums/{forum_id}/invite              // Invite to forum
POST /forums/join/{invite_code}             // Join via invite code

// Events & Challenges (IMPLEMENTED IN UI BUT NOT CONNECTED)
GET /forums/events                          // Get community events ⚠️
POST /forums/events                         // Create community event ⚠️
GET /forums/challenges                      // Get community challenges ⚠️
POST /forums/challenges                     // Create community challenge ⚠️

// Tags & Categories
GET /forums/tags                            // Get available tags
POST /forums/tags                           // Create new tag
GET /forums/{forum_id}/tags/{tag_id}        // Get tagged content

// Media & Attachments
POST /forums/media                          // Upload media
GET /forums/media/{content_type}/{content_id}    // Get media attachments

// User Management
GET /users/forums                           // Get user's forums
GET /users/{user_id}/activity               // Get user activity
GET /forums/users/{user_id}/reputation      // Get user reputation
DELETE /user/{user_id}/delete               // Delete user data

// Moderation & Reporting
POST /forums/report                         // Report content
POST /forums/report/enhanced                // Enhanced reporting
GET /forums/reports                         // Get reports (moderators)
POST /forums/moderation/action              // Take moderation action
GET /forums/moderation/dashboard            // Moderation dashboard

// Support & Guidelines
GET /forums/guidelines                      // Community guidelines
GET /forums/support                         // Get support resources
GET /forums/support/{content_type}/{content_id}      // Content-specific support
GET /forums/support/{content_type}/{content_id}/user // User-specific support

// Volunteer System
POST /forums/volunteer/apply                // Apply to be volunteer
POST /forums/volunteer/approve/{application_id}      // Approve volunteer application
```

**Priority Recommendations:**
1. **CRITICAL**: Connect events and challenges API (UI implemented but not connected)
2. **HIGH**: Implement comments system for threads
3. **HIGH**: Thread view tracking and statistics
4. **HIGH**: Search functionality
5. **MEDIUM**: User activity and reputation tracking
6. **MEDIUM**: Content reporting and moderation
7. **LOW**: Advanced moderation dashboard

---

### 🔔 Notification Service (3/6 integrated - 50.0%)

#### ✅ **INTEGRATED ROUTES**
```typescript
POST /notify/send                   ✓ notificationApi.sendNotification()
GET /notify/recent                  ✓ notificationApi.getRecentNotifications()
GET /notify/preferences             ✓ notificationApi.getPreferences()
```

#### ❌ **UNUTILIZED ROUTES (3)**
```typescript
POST /notify/schedule               // Schedule notification
PUT /notify/preferences             // Update notification preferences ⚠️
DELETE /user/{user_id}/delete       // Delete user notification data
```

**Priority Recommendations:**
1. **HIGH**: Implement notification preferences update (method mismatch - API uses PUT, frontend might expect PATCH)
2. **MEDIUM**: Scheduled notifications for mood pattern alerts
3. **LOW**: User data deletion (admin feature)

---

### 📁 Media Service (3/16 integrated - 18.8%)

#### ✅ **INTEGRATED ROUTES**
```typescript
POST /api/v1/media/upload           ✓ communityApi.uploadMedia()
GET /api/v1/media/{media_id}        ✓ Used for media details
GET /api/v1/media/{media_id}/file   ✓ Used for media file access
```

#### ❌ **UNUTILIZED ROUTES (13)**
```typescript
// Media management
GET /api/v1/media/                  // Get media list
PUT /api/v1/media/{media_id}        // Update media
DELETE /api/v1/media/{media_id}     // Delete media
GET /api/v1/media/{media_id}/preview      // Get media preview
GET /api/v1/media/{media_id}/thumbnail    // Get media thumbnail

// Media interactions
POST /api/v1/media/{media_id}/like        // Like media
DELETE /api/v1/media/{media_id}/like      // Remove like
GET /api/v1/media/{media_id}/like-status  // Get like status
POST /api/v1/media/{media_id}/view        // Track media view
GET /api/v1/media/{media_id}/reactions    // Get media reactions
POST /api/v1/media/{media_id}/reactions   // Add reaction
DELETE /api/v1/media/{media_id}/reactions/{reaction_id}  // Remove reaction

// Moderation
GET /api/v1/media/pending                 // Get pending media (for approval)
GET /api/v1/media/admin/pending           // Get admin pending queue
POST /api/v1/media/{media_id}/moderate    // Moderate media content

// User management
DELETE /api/v1/media/user/{user_id}/delete     // Delete user media data
```

**Priority Recommendations:**
1. **HIGH**: Media moderation system (mentioned in requirements)
2. **MEDIUM**: Media interactions (likes, reactions) for community posts
3. **MEDIUM**: Media gallery and management
4. **LOW**: Advanced media analytics

---

## Frontend Components Analysis

### Current Implementation Status

#### ✅ **Fully Integrated Components**
- `EnhancedCommunitySection` - Full community forum functionality
- `ChatBot` - Basic chat functionality with session management
- `MoodTracker` - Basic mood logging
- API utilities in `/lib/api.ts` - Comprehensive API wrapper

#### ⚠️ **Partially Integrated Components**
- `JournalSection` - Using mock data, needs journal API integration
- `WellnessDashboard` - Using mock data, needs analytics APIs
- `MoodInsights` - Basic implementation, needs advanced analytics
- Authentication - Basic flow, missing password reset and admin features

#### ❌ **Missing Components**
- Habits tracking system
- Advanced mood analytics and correlations
- Media gallery and moderation
- Notification center
- User preferences/settings panel
- Admin dashboard for moderation

---

## Critical Missing Integrations

### 1. **Journal System** (CRITICAL)
- **Backend**: 10 journal routes available
- **Frontend**: Using mock data
- **Impact**: Core feature not functional
- **Effort**: 2-3 days

### 2. **Habits Tracking** (CRITICAL)
- **Backend**: 14 habit routes available
- **Frontend**: Not implemented
- **Impact**: Key wellness feature missing
- **Effort**: 3-4 days

### 3. **Advanced Mood Analytics** (HIGH)
- **Backend**: 15+ analytics routes available
- **Frontend**: Basic implementation only
- **Impact**: Intelligent insights not available
- **Effort**: 2-3 days

### 4. **Events & Challenges Connection** (HIGH)
- **Backend**: Routes implemented
- **Frontend**: UI implemented but not connected
- **Impact**: Community features incomplete
- **Effort**: 1 day

### 5. **Media Moderation** (HIGH)
- **Backend**: Full moderation system available
- **Frontend**: Basic upload only
- **Impact**: Content safety not implemented
- **Effort**: 2 days

---

## Implementation Priority Matrix

### **Phase 1: Core Functionality (Week 1)**
1. Connect community events/challenges APIs
2. Implement journal system backend integration
3. Fix notification preferences update method
4. Add mood pattern notifications backend connection

### **Phase 2: Enhanced Features (Week 2)**
1. Implement habits tracking system
2. Add advanced mood analytics (correlations, patterns)
3. Implement media moderation workflow
4. Add thread comments and search

### **Phase 3: Advanced Features (Week 3-4)**
1. User activity tracking and reputation
2. Advanced insights management
3. Content management and categorization
4. Scheduled notifications

### **Phase 4: Admin & Moderation (Future)**
1. Admin dashboard for user management
2. Advanced moderation tools
3. System analytics and monitoring
4. Volunteer management system

---

## Route Integration Recommendations

### Immediate Actions (Next Sprint)
```typescript
// 1. Connect existing UI components to backend
- Community events API integration
- Community challenges API integration  
- Journal system implementation
- Notification preferences fix

// 2. Critical missing features
- Habits tracking system
- Advanced mood analytics
- Media moderation system
```

### Short-term (1-2 months)
```typescript
// 3. Enhanced user experience
- User activity tracking
- Content search and discovery
- Advanced insights management
- Thread comments system
```

### Long-term (3+ months)
```typescript
// 4. Administrative features
- User management dashboard
- Content moderation dashboard
- System analytics
- Volunteer management
```

---

## Technical Debt & Considerations

### API Configuration
- **Environment Variables**: Need proper environment configuration for different deployments
- **Error Handling**: Implement consistent error handling across all API calls
- **Loading States**: Add proper loading states for all async operations
- **Caching**: Implement client-side caching for frequently accessed data

### Authentication & Security
- **Token Management**: Implement proper token refresh logic
- **Role-based Access**: Implement role-based UI components
- **Route Protection**: Add protected routes for admin features

### Performance
- **Pagination**: Implement pagination for list endpoints
- **Infinite Scroll**: For community feeds and timelines
- **Data Optimization**: Optimize data fetching patterns

### User Experience
- **Offline Support**: Add offline capabilities for core features
- **Real-time Updates**: Implement WebSocket connections for live updates
- **Progressive Enhancement**: Ensure core functionality works without JavaScript

---

## Conclusion

The MantraPath frontend has a solid foundation with **29.5% API integration coverage**. The **Community Service leads with 40.5% integration**, followed by **Content Service at 50%**. However, critical features like the **journal system, habits tracking, and advanced analytics remain unutilized**, representing significant missed opportunities for user engagement and value delivery.

**Immediate priority should be given to:**
1. **Journal API integration** (replacing mock data)
2. **Habits tracking implementation** (core wellness feature)
3. **Community events/challenges connection** (UI ready, needs backend)
4. **Advanced mood analytics** (leveraging existing 42 unutilized routes)

With focused development effort, the application could achieve **60-70% API utilization** within 2-4 weeks, significantly enhancing the user experience and feature completeness.