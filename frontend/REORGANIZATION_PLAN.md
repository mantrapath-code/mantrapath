# Frontend Structure Reorganization Plan

## Current Issues Identified
1. **Mock Data Scattered**: Mock data is embedded throughout components and API service
2. **Inconsistent Error Handling**: Different components handle errors differently
3. **Mixed Responsibilities**: Components handle both UI and data logic
4. **GDPR/Privacy Concerns**: No centralized privacy controls
5. **Subscription Logic**: Feature access not properly managed
6. **Large Files**: Some components are too large and complex

## Proposed New Structure

```
frontend/src/
├── components/
│   ├── auth/                     # Authentication components
│   ├── common/                   # Shared UI components
│   ├── community/                # Community features
│   ├── dashboard/                # Dashboard components
│   ├── journal/                  # Journal components
│   ├── mood/                     # Mood tracking components
│   ├── notifications/            # Notification components
│   ├── profile/                  # User profile components
│   ├── subscription/             # NEW: Subscription management
│   ├── privacy/                  # NEW: Privacy controls
│   └── ui/                       # Base UI components
├── services/
│   ├── api/                      # NEW: Organized API services
│   │   ├── auth.ts              # Authentication API
│   │   ├── community.ts         # Community API
│   │   ├── mood.ts              # Mood tracking API
│   │   ├── journal.ts           # Journal API
│   │   ├── notifications.ts     # Notification API
│   │   └── index.ts             # Main API service
│   ├── data/                     # NEW: Data management
│   │   ├── mockData.ts          # Centralized mock data
│   │   ├── offline.ts           # Offline data management
│   │   └── sync.ts              # Data synchronization
│   ├── privacy/                  # NEW: Privacy services
│   │   ├── gdpr.ts              # GDPR compliance
│   │   ├── dataExport.ts        # Data export functionality
│   │   └── consent.ts           # Consent management
│   ├── subscription/             # NEW: Subscription services
│   │   ├── tiers.ts             # Subscription tiers
│   │   ├── features.ts          # Feature access control
│   │   └── billing.ts           # Billing integration
│   ├── notifications.ts          # Enhanced notification service
│   └── dataManager.ts           # Data management service
├── hooks/
│   ├── auth/                     # Authentication hooks
│   ├── data/                     # Data management hooks
│   ├── privacy/                  # Privacy-related hooks
│   └── subscription/             # Subscription hooks
├── utils/
│   ├── errorHandling.ts          # Enhanced error handling
│   ├── validation.ts             # Form validation
│   ├── formatting.ts             # Data formatting
│   ├── privacy.ts                # Privacy utilities
│   └── accessibility.ts          # Accessibility helpers
├── types/
│   ├── api.ts                    # API type definitions
│   ├── user.ts                   # User-related types
│   ├── privacy.ts                # Privacy-related types
│   └── subscription.ts           # Subscription types
├── config/
│   ├── features.ts               # Feature flags
│   ├── privacy.ts                # Privacy settings
│   └── subscription.ts           # Subscription configuration
└── constants/
    ├── privacy.ts                # Privacy constants
    ├── features.ts               # Feature constants
    └── subscription.ts           # Subscription constants
```

## Implementation Steps

### Phase 1: Core Infrastructure (Priority: High)
1. ✅ Create enhanced error handling system
2. ✅ Create centralized notification service
3. ✅ Create data manager service
4. 🔄 Organize API services by feature
5. 🔄 Create privacy management system
6. 🔄 Create subscription management system

### Phase 2: Data Management (Priority: High)
1. 🔄 Extract mock data to centralized service
2. 🔄 Implement offline data management
3. 🔄 Create data synchronization system
4. 🔄 Implement GDPR compliance features

### Phase 3: Component Optimization (Priority: Medium)
1. 🔄 Break down large components
2. 🔄 Implement feature access controls
3. 🔄 Add privacy controls to all components
4. 🔄 Improve accessibility

### Phase 4: Advanced Features (Priority: Low)
1. 🔄 Advanced analytics with privacy controls
2. 🔄 Data export functionality
3. 🔄 Advanced subscription features
4. 🔄 Performance optimization

## GDPR Compliance Features

### Data Rights Implementation
- **Right to Access**: User can view all their data
- **Right to Rectification**: User can edit their data
- **Right to Erasure**: User can delete their data
- **Right to Portability**: User can export their data
- **Right to Restrict Processing**: User can limit data usage

### Privacy Controls
- **Data Minimization**: Only collect necessary data
- **Purpose Limitation**: Clear purpose for each data point
- **Consent Management**: Granular consent for different features
- **Data Retention**: Automatic data cleanup after retention period

### Subscription Tiers

#### Free Tier
- Basic mood tracking (10 entries/month)
- Simple analytics
- Community access (read-only)
- Basic privacy controls

#### Premium Tier ($9.99/month)
- Unlimited mood tracking
- Advanced analytics
- Full community access
- Export data
- Priority support
- Enhanced privacy controls

#### Pro Tier ($19.99/month)
- All Premium features
- Team collaboration
- Advanced ML insights
- Custom reports
- API access
- Maximum privacy controls

## Migration Strategy

### Week 1: Foundation
- Implement new error handling across auth components
- Create privacy service foundation
- Set up subscription service structure

### Week 2: Data Organization
- Extract mock data to centralized service
- Implement offline capabilities
- Create privacy consent system

### Week 3: Component Updates
- Update community components with new error handling
- Add subscription controls to features
- Implement privacy controls

### Week 4: Testing & Polish
- Comprehensive testing of new structure
- Performance optimization
- Documentation updates

## Benefits of New Structure

1. **Maintainability**: Clear separation of concerns
2. **Scalability**: Easy to add new features
3. **Privacy**: Built-in GDPR compliance
4. **User Experience**: Consistent error handling and notifications
5. **Business Model**: Clear subscription tiers with feature controls
6. **Development Speed**: Reusable components and services
7. **Security**: Centralized data management with privacy controls
