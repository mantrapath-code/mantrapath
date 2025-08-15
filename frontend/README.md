# MantraPath Frontend

**Version:** 2.1.0  
**Last Updated:** August 13, 2025  
**Status:** Production Ready - Clean Architecture & Scalable Design

## Overview

The MantraPath frontend is a modern, React-based web application built with TypeScript, Vite, and Tailwind CSS. This application provides a comprehensive mental wellness platform with real-time features, community interaction,- **Automation Ready** - CI/CD friendly structure with proper build processes

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`
4. Build for production: `npm run build`

### Code Quality Standards
- Run `npm run lint` before committing
- Follow TypeScript strict mode guidelines
- Write self-documenting code with proper naming
- Test components in isolation before integration

### Adding New Features
1. Create feature branch from `main`
2. Add components in appropriate domain directory
3. Include proper TypeScript interfaces
4. Update index.ts exports for new components
5. Follow existing patterns for API integration

## 📞 Supporturnaling, and AI-powered insights. The codebase has been thoroughly cleaned and optimized for scalability.

## 🎯 Key Features

### ✅ **Clean Architecture**
- **100% Real Backend Integration** - No mock data, sample data, or fallback logic
- **Zero Code Duplication** - Consolidated utilities, types, and components
- **Unified Component Structure** - Consistent patterns across all components
- **Type-Safe Implementation** - Comprehensive TypeScript with zero redundant types

### 🏗️ **Scalable Design Patterns**
- **Domain-Driven Organization** - Components grouped by business features
- **Atomic Design Principles** - Reusable components from atoms to organisms
- **Service Layer Architecture** - Centralized API management with consistent patterns
- **Custom Hook Strategy** - Business logic encapsulated in reusable hooks

### 🔧 **Core Technologies**
- **React 18** with hooks and functional components
- **TypeScript** for type safety and developer experience
- **Vite** for fast development and optimized builds
- **Tailwind CSS** with shadcn/ui components
- **Framer Motion** for smooth animations
- **WebSocket** for real-time features

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/           # Feature-based component organization
│   │   ├── auth/            # Authentication & user management
│   │   │   ├── AuthScreen.tsx
│   │   │   ├── EmailVerification.tsx
│   │   │   └── index.ts
│   │   ├── chatbot/         # AI chatbot interface
│   │   │   ├── ChatBot.tsx
│   │   │   └── index.ts
│   │   ├── common/          # Shared utility components
│   │   │   ├── BreathingExercise.tsx
│   │   │   ├── DevelopmentBanner.tsx
│   │   │   └── index.ts
│   │   ├── community/       # Social features & forums
│   │   │   ├── CommunityFeed.tsx
│   │   │   ├── EnhancedCommunitySection.tsx
│   │   │   ├── EnhancedChallengeCard.tsx
│   │   │   ├── EnhancedEventCard.tsx
│   │   │   └── index.ts
│   │   ├── dashboard/       # Analytics & insights
│   │   │   ├── WellnessDashboard.tsx
│   │   │   ├── CrisisPredictionDashboard.tsx
│   │   │   └── index.ts
│   │   ├── journal/         # Journaling & mood tracking
│   │   │   ├── JournalSection.tsx
│   │   │   └── index.ts
│   │   ├── notifications/   # Real-time notification system
│   │   │   ├── RealTimeNotifications.tsx
│   │   │   ├── EnhancedNotificationContainer.tsx
│   │   │   ├── SmartNotificationScheduler.tsx
│   │   │   └── index.ts
│   │   ├── profile/         # User profile management
│   │   │   ├── ProfileDashboard.tsx
│   │   │   ├── ProfileDropdown.tsx
│   │   │   ├── ProfileEditor.tsx
│   │   │   ├── ProfileAvatar.tsx
│   │   │   └── index.ts
│   │   ├── ui/              # Base design system (50+ components)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── [...50+ components]
│   │   │   └── index.ts
│   │   └── index.ts         # Centralized exports
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.tsx      # Authentication management
│   │   ├── useWellness.ts   # Wellness data & analytics
│   │   ├── useJournal.ts    # Journal entries management
│   │   ├── useCommunity.ts  # Community features
│   │   ├── useWebSocket.ts  # Real-time connections
│   │   └── [10+ hooks]      # Domain-specific business logic
│   ├── pages/               # Top-level page components
│   │   ├── InsightsPage.tsx
│   │   └── AchievementsPage.tsx
│   ├── services/            # API service layer
│   │   ├── api.ts           # Core API client & endpoints
│   │   ├── auth.ts          # Authentication service
│   │   ├── notifications.ts # Notification service
│   │   └── unifiedInsightService.ts # Analytics service
│   ├── types/               # TypeScript definitions
│   │   └── index.ts         # Centralized type exports
│   ├── utils/               # Utility functions
│   │   ├── timeUtils.ts     # Time formatting (consolidated)
│   │   ├── errorHandling.ts # Error management
│   │   ├── userDisplay.ts   # User data utilities
│   │   └── [5+ utilities]   # Helper functions
│   ├── styles/              # Global styles & themes
│   │   ├── theme.css        # Theme definitions
│   │   └── notifications.css # Notification styles
│   ├── lib/                 # Core utilities
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Application entry point
│   ├── index.css            # Base styles
│   └── main.css             # Primary stylesheet
├── public/                  # Static assets
├── package.json             # Dependencies & scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend services running (see backend setup guide)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mantrapath/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript checks
```

## 🔌 Backend Integration

### API Services
The frontend connects to multiple backend services:

- **Authentication Service** - User login/registration, JWT tokens
- **Community Service** - Forums, events, challenges, social features
- **Journal Service** - Personal journaling and mood tracking
- **Wellness Service** - AI insights, analytics, recommendations
- **Notification Service** - Real-time notifications and alerts

### Environment Configuration
```bash
# Required environment variables
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=MantraPath
```

## 🏗️ Architecture Patterns

### 🎯 **Component Organization Strategy**
- **Domain-Driven Design** - Components grouped by business features (auth, community, dashboard)
- **Atomic Design Principles** - UI components range from basic atoms to complex organisms
- **Feature Isolation** - Each domain has its own components, hooks, and logic
- **Consistent Barrel Exports** - Clean import structure with index.ts files

### 🔄 **State Management Architecture**
- **Local State First** - useState/useEffect for component-specific state
- **Custom Hooks** - Domain-specific hooks encapsulate business logic and API calls
- **Context Providers** - Shared state for authentication, theme, and WebSocket connections
- **No External State Libraries** - Leveraging React's built-in state management

### 📊 **Data Flow Patterns**
- **Service Layer** - Centralized API calls through dedicated service classes
- **Hook-Based Data Fetching** - Custom hooks manage loading states, errors, and caching
- **Real-time Updates** - WebSocket integration for live community and notification features
- **Error Boundary Strategy** - Graceful error handling at multiple component levels

### 🎨 **Styling Architecture**
- **Tailwind CSS 4.0** - Utility-first CSS with custom design tokens
- **Component Variants** - CVA (Class Variance Authority) for dynamic styling
- **Theme System** - Mood-based dynamic theming with CSS custom properties
- **Responsive Design** - Mobile-first approach with breakpoint strategy

### 🧩 **Code Organization Principles**
- **Single Responsibility** - Each component has one clear purpose
- **Composition over Inheritance** - Building complex UIs through component composition
- **TypeScript First** - Strict typing with comprehensive interfaces
- **Performance Optimization** - Lazy loading, memoization, and efficient re-renders

## 🎨 UI/UX Features

### Design System
- **shadcn/ui Components** - Modern, accessible component library
- **Tailwind CSS** - Utility-first CSS framework
- **Consistent Theming** - Mood-based dynamic themes
- **Responsive Design** - Mobile-first responsive layouts

### User Experience
- **Real-time Updates** - Live community feed and notifications
- **Smooth Animations** - Framer Motion for enhanced interactions
- **Accessibility** - WCAG compliant components and keyboard navigation
- **Progressive Enhancement** - Graceful degradation for offline scenarios

## 🔧 Development Guidelines

### 📋 **Code Standards**
- **TypeScript First** - All components and utilities are strongly typed with strict configuration
- **Functional Components** - React hooks pattern throughout (no class components)
- **ESLint + Prettier** - Automated code formatting and linting with custom rules
- **Component Documentation** - JSDoc comments for complex components and public APIs

### 📛 **Naming Conventions**
- **Components** - PascalCase (e.g., `CommunityFeed.tsx`, `AuthScreen.tsx`)
- **Hooks** - camelCase with 'use' prefix (e.g., `useWellness.ts`, `useAuth.tsx`)
- **Services** - camelCase with descriptive names (e.g., `apiService.ts`, `authService.ts`)
- **Types/Interfaces** - PascalCase interfaces (e.g., `interface UserProfile`, `type MoodEntry`)
- **Utilities** - camelCase functions (e.g., `formatRelativeTime`, `getDisplayName`)

### 📁 **File Organization Strategy**
- **Single Responsibility** - One primary component/hook/service per file
- **Barrel Exports** - index.ts files in each directory for clean imports
- **Co-location** - Related files (component + styles + tests) grouped together
- **Consistent Structure** - Standardized file and folder patterns across domains

### 🎯 **Component Design Principles**
- **Props Interface First** - Define clear, typed interfaces for all component props
- **Composition over Configuration** - Build complex UIs through component composition
- **Accessibility First** - WCAG compliant with proper ARIA attributes and keyboard navigation
- **Performance Conscious** - Memoization, lazy loading, and efficient re-render strategies

### 🔄 **Data Fetching Patterns**
```typescript
// Standard hook pattern for data fetching
export function useFeatureData() {
  const [data, setData] = useState<FeatureData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const result = await apiService.getFeatureData()
      setData(result)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, refetch: fetchData }
}
```

### 🎨 **Styling Guidelines**
```typescript
// Component with proper styling patterns
interface ComponentProps {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Component({ variant = 'primary', size = 'md', className }: ComponentProps) {
  return (
    <div className={cn(
      'base-styles',
      variant === 'primary' && 'primary-styles',
      variant === 'secondary' && 'secondary-styles',
      size === 'sm' && 'small-styles',
      size === 'lg' && 'large-styles',
      className
    )}>
      {/* Component content */}
    </div>
  )
}
```

## 🧪 Testing & Quality

### Code Quality
- **TypeScript** - Compile-time type checking
- **ESLint** - Static code analysis
- **Build Verification** - Production build testing
- **Performance Monitoring** - Bundle size optimization

### Browser Support
- **Modern Browsers** - Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile Support** - iOS Safari, Android Chrome
- **Progressive Enhancement** - Graceful degradation for older browsers

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Build Output
- **Optimized Bundle** - Minified and tree-shaken JavaScript
- **CSS Optimization** - Purged and compressed stylesheets
- **Asset Optimization** - Optimized images and static assets
- **Source Maps** - For production debugging

### Performance Features
- **Code Splitting** - Dynamic imports for route-based splitting
- **Tree Shaking** - Unused code elimination
- **Asset Optimization** - Compressed images and fonts
- **Caching Strategy** - Optimized cache headers for static assets

## 📚 Additional Resources

### Documentation
- [Component Library](./docs/components.md) - Detailed component documentation
- [API Integration](./docs/api-integration.md) - Backend integration guide
- [Deployment Guide](./docs/deployment.md) - Production deployment instructions

### Development Tools
- [VS Code Extensions](./docs/vscode-setup.md) - Recommended extensions and settings
- [Debugging Guide](./docs/debugging.md) - Frontend debugging best practices

## 🔄 Recent Changes (v2.1.0)

### ✅ **Code Cleanup & Architecture Improvements**
- **Eliminated All Duplicates** - Removed duplicate components, utilities, and type definitions
- **Consolidated Time Utilities** - Merged `timeFormat.ts` and `timeUtils.ts` into single utility
- **Removed Redundant Types** - Eliminated duplicate type definitions and unnecessary re-exports
- **Cleaned Up Auth Components** - Removed unused `EmailVerificationPage` component
- **Removed Test Components** - Eliminated `NotificationSchedulerTest` and other debug components

### 🗑️ **Files Removed**
- `src/App.tsx.corrupted` - Corrupted backup file
- `src/types.ts` - Redundant type re-exports (consolidated to `types/index.ts`)
- `src/utils/timeFormat.ts` - Duplicate time utility (merged into `timeUtils.ts`)
- `src/components/auth/EmailVerificationPage.tsx` - Unused duplicate component
- `src/components/notifications/NotificationSchedulerTest.tsx` - Test component

### 🔧 **Refactored & Optimized**
- **CSS Import Structure** - Removed duplicate Tailwind imports in stylesheets
- **Time Utility Functions** - Enhanced `formatRelativeTime` with better UTC handling
- **Component Exports** - Updated all index.ts files to remove deleted component references
- **Import Statements** - Updated all components to use consolidated utilities

### 📊 **Architecture Enhancements**
- **Domain-Driven Organization** - Better component grouping by business features
- **Type Safety Improvements** - Eliminated duplicate interfaces and improved type consistency
- **Service Layer Consolidation** - Cleaner API service structure
- **Hook Pattern Standardization** - Consistent data fetching patterns across all hooks

### � **Performance Improvements**
- **Reduced Bundle Size** - Eliminated dead code and duplicate utilities
- **Faster Build Times** - Reduced file count and simplified dependency tree
- **Better Tree Shaking** - Improved import structure for optimal bundling
- **Memory Efficiency** - Removed redundant component instances and unused imports

## � Scalability & Future-Proofing

### 🔧 **Component Scalability**
- **Modular Architecture** - Each domain can be developed and scaled independently
- **Reusable UI Library** - 50+ base components provide consistent foundation
- **Plugin-Ready Structure** - Easy addition of new features without architectural changes
- **API-First Design** - Backend-agnostic frontend that adapts to service changes

### 🌐 **Performance Scaling**
- **Code Splitting** - Lazy loading for route-based and component-based splitting
- **Bundle Optimization** - Tree shaking and dynamic imports for optimal loading
- **Caching Strategy** - Smart caching in custom hooks with invalidation patterns
- **Real-time Efficiency** - WebSocket connection pooling and message optimization

### 🔐 **Maintainability Features**
- **Type Safety** - Comprehensive TypeScript prevents runtime errors at scale
- **Testing Strategy** - Component and integration test foundations in place
- **Documentation** - Self-documenting code with comprehensive README files
- **Error Boundaries** - Graceful failure handling prevents cascade failures

### 🚀 **Development Velocity**
- **Hot Reload** - Vite provides instant feedback during development
- **Developer Experience** - Rich TypeScript intellisense and error detection
- **Consistent Patterns** - New developers can quickly understand and contribute
- **Automation Ready** - CI/CD friendly structure with proper build processes

## �📞 Support

For technical support or questions:
- **Documentation** - Check component and API documentation
- **Issues** - Create GitHub issues for bugs or feature requests
- **Development** - Follow coding standards and contribution guidelines

---

**Built with ❤️ for mental wellness and community support**
