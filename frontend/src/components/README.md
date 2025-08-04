# MantraPath Frontend Components

**Version:** 2.0.0  
**Last Updated:** August 4, 2025  
**Status:** Production Ready - Mock-Free & Unified

## Overview

This directory contains all reusable UI components for the MantraPath frontend application. All components are built with React, TypeScript, and Tailwind CSS, following modern design patterns and accessibility standards.

## 🏗️ Architecture Principles

### ✅ **Mock-Free Components**
- **Real Data Only** - All components consume real backend data
- **No Sample Data** - Removed all hardcoded mock data and fallback content
- **Proper Loading States** - Components show loading indicators while fetching data
- **Error Handling** - Clean error states instead of mock fallbacks

### 🎯 **Unified Patterns**
- **Consistent Structure** - Standardized component organization and exports
- **Naming Conventions** - Clear, descriptive component and prop names
- **Type Safety** - Comprehensive TypeScript interfaces and props
- **Accessibility** - WCAG compliant with proper ARIA attributes

## 📁 Component Organization

```
components/
├── auth/                    # Authentication & User Management
│   ├── AuthScreen.tsx      # Main authentication interface
│   ├── EmailVerification.tsx # Email verification component
│   └── index.ts            # Barrel exports
├── chatbot/                # AI Chatbot Interface
│   ├── ChatBot.tsx         # Main chatbot component
│   └── index.ts            # Barrel exports
├── common/                 # Shared Utility Components
│   ├── BreathingExercise.tsx # Guided breathing component
│   ├── DevelopmentBanner.tsx # Development environment banner
│   └── index.ts            # Barrel exports
├── community/              # Community & Social Features
│   ├── CommunityFeed.tsx   # Main community feed
│   ├── EnhancedCommunitySection.tsx # Enhanced community interface
│   ├── EnhancedChallengeCard.tsx # Challenge cards
│   ├── EnhancedEventCard.tsx # Event cards
│   └── index.ts            # Barrel exports
├── dashboard/              # Analytics & Dashboard
│   ├── WellnessDashboard.tsx # Main wellness dashboard
│   ├── CrisisPredictionDashboard.tsx # Crisis prediction interface
│   └── index.ts            # Barrel exports
├── journal/                # Journaling & Mood Tracking
│   ├── JournalSection.tsx  # Main journaling interface
│   └── index.ts            # Barrel exports
├── notifications/          # Notification System
│   ├── RealTimeNotifications.tsx # Real-time notification display
│   ├── EnhancedNotificationContainer.tsx # Enhanced notifications
│   ├── SmartNotificationScheduler.tsx # Notification scheduling
│   └── index.ts            # Barrel exports
├── profile/                # User Profile Management
│   ├── ProfileDropdown.tsx # Profile dropdown menu
│   ├── ProfileDashboard.tsx # User profile dashboard
│   └── index.ts            # Barrel exports
├── ui/                     # Base UI Components (shadcn/ui)
│   ├── button.tsx          # Button component
│   ├── card.tsx            # Card component
│   ├── input.tsx           # Input component
│   └── [...50+ components] # Complete UI component library
└── index.ts                # Main component exports
```

## 🧩 Component Categories

### 🔐 Authentication Components (`auth/`)

**Purpose:** Handle user authentication, registration, and account management.

**Key Components:**
- `AuthScreen` - Complete authentication interface with login/register
- `EmailVerification` - Email verification flow component

**Features:**
- JWT token management
- Form validation and error handling
- Responsive design for mobile and desktop
- Accessibility compliant

### 🤖 Chatbot Components (`chatbot/`)

**Purpose:** AI-powered conversational interface for user support and guidance.

**Key Components:**
- `ChatBot` - Main chatbot interface with conversation management

**Features:**
- Real-time conversation with AI backend
- Context-aware responses
- Mood and wellness integration
- Expandable/collapsible interface

### 🔧 Common Components (`common/`)

**Purpose:** Shared utility components used across multiple features.

**Key Components:**
- `BreathingExercise` - Guided breathing exercise with visual cues
- `DevelopmentBanner` - Development environment indicator

**Features:**
- Reusable across different sections
- Lightweight and performant
- Consistent styling and behavior

### 👥 Community Components (`community/`)

**Purpose:** Social features including forums, events, challenges, and community interaction.

**Key Components:**
- `CommunityFeed` - Main community activity feed with real-time updates
- `EnhancedCommunitySection` - Comprehensive community interface
- `EnhancedChallengeCard` - Interactive challenge cards
- `EnhancedEventCard` - Event display and interaction cards

**Features:**
- Real-time community updates via WebSocket
- Forum threads and discussions
- Event and challenge management
- User engagement tracking
- Community scoring and achievements

### 📊 Dashboard Components (`dashboard/`)

**Purpose:** Analytics, insights, and data visualization for user wellness tracking.

**Key Components:**
- `WellnessDashboard` - Main wellness analytics dashboard
- `CrisisPredictionDashboard` - Mental health crisis prediction interface

**Features:**
- Real-time analytics from wellness service
- Interactive charts and visualizations
- Personalized insights and recommendations
- Crisis intervention alerts

### 📔 Journal Components (`journal/`)

**Purpose:** Personal journaling and mood tracking functionality.

**Key Components:**
- `JournalSection` - Complete journaling interface with mood tracking

**Features:**
- Rich text journaling
- Mood and wellness tracking
- Sentiment analysis integration
- Personal insights and patterns

### 🔔 Notification Components (`notifications/`)

**Purpose:** Real-time notification system and user alerts.

**Key Components:**
- `RealTimeNotifications` - Live notification display
- `EnhancedNotificationContainer` - Advanced notification management
- `SmartNotificationScheduler` - Intelligent notification scheduling

**Features:**
- WebSocket-based real-time notifications
- Smart scheduling based on user patterns
- Customizable notification preferences
- Engagement tracking and optimization

### 👤 Profile Components (`profile/`)

**Purpose:** User profile management and account settings.

**Key Components:**
- `ProfileDropdown` - User profile dropdown menu
- `ProfileDashboard` - Comprehensive profile management interface

**Features:**
- User profile editing
- Account settings management
- Privacy and security controls
- Activity history and statistics

### 🎨 UI Components (`ui/`)

**Purpose:** Base design system components built on shadcn/ui.

**Key Components:**
- 50+ base UI components including buttons, cards, inputs, dialogs, etc.
- Consistent design tokens and theming
- Accessibility compliant
- Mobile responsive

## 🎯 Component Standards

### TypeScript Implementation
```typescript
// Component interface example
interface ComponentProps {
  title: string
  onAction: (data: ActionData) => void
  className?: string
  children?: React.ReactNode
}

// Component implementation
export function Component({ title, onAction, className, children }: ComponentProps) {
  // Component logic
}
```

### Naming Conventions
- **Components:** PascalCase (e.g., `CommunityFeed`)
- **Props:** camelCase (e.g., `onItemClick`)
- **Files:** PascalCase matching component name (e.g., `CommunityFeed.tsx`)
- **Enhanced Components:** Use "Enhanced" prefix for improved versions

### File Structure
```typescript
// Component file structure
import { dependencies } from 'libraries'
import { localDependencies } from '@/local'

// Interfaces and types
interface ComponentProps {
  // Props definition
}

// Main component
export function Component(props: ComponentProps) {
  // Component implementation
}

// Default export if needed
export default Component
```

### Export Patterns
```typescript
// index.ts barrel exports
export { ComponentName } from './ComponentName'
export { AnotherComponent } from './AnotherComponent'
export type { ComponentProps } from './ComponentName'
```

## 🔌 Data Integration

### API Integration
All components follow consistent patterns for backend integration:

```typescript
// Hook-based data fetching
const { data, loading, error } = useCustomHook()

// Error handling
if (error) {
  return <ErrorState message={error} />
}

// Loading states
if (loading) {
  return <LoadingSpinner />
}

// Render with real data
return <ComponentContent data={data} />
```

### WebSocket Integration
Real-time components use WebSocket connections:

```typescript
const { isConnected, lastMessage } = useWebSocket()

// Connection status handling
if (!isConnected) {
  return <OfflineIndicator />
}

// Real-time data updates
useEffect(() => {
  if (lastMessage) {
    handleRealtimeUpdate(lastMessage)
  }
}, [lastMessage])
```

## 🎨 Styling Guidelines

### Tailwind CSS Classes
- **Consistent Spacing** - Use Tailwind spacing scale (p-4, m-2, etc.)
- **Responsive Design** - Mobile-first approach (sm:, md:, lg: breakpoints)
- **Color System** - Use semantic color names (primary, secondary, accent)
- **Component Variants** - Consistent styling patterns across similar components

### Theme Integration
Components support dynamic theming:
```typescript
// Theme-aware styling
const themeClasses = {
  primary: 'bg-primary text-primary-foreground',
  secondary: 'bg-secondary text-secondary-foreground',
  accent: 'bg-accent text-accent-foreground'
}
```

### Accessibility Standards
- **ARIA Labels** - Proper labeling for screen readers
- **Keyboard Navigation** - Tab order and keyboard shortcuts
- **Color Contrast** - WCAG AA compliant color combinations
- **Focus Management** - Visible focus indicators

## 🧪 Testing Patterns

### Component Testing
```typescript
// Example test structure
describe('ComponentName', () => {
  it('renders with required props', () => {
    // Test implementation
  })

  it('handles user interactions', () => {
    // Interaction testing
  })

  it('displays error states correctly', () => {
    // Error state testing
  })
})
```

### Accessibility Testing
- **Screen Reader Testing** - Verify screen reader compatibility
- **Keyboard Testing** - Ensure keyboard navigation works
- **Color Contrast** - Verify contrast ratios meet standards

## 🚀 Performance Optimization

### Code Splitting
```typescript
// Lazy loading for large components
const LargeComponent = lazy(() => import('./LargeComponent'))

// Usage with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <LargeComponent />
</Suspense>
```

### Memoization
```typescript
// Memoize expensive computations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data)
}, [data])

// Memoize callback functions
const handleClick = useCallback((id: string) => {
  onItemClick(id)
}, [onItemClick])
```

## 📱 Responsive Design

### Breakpoint Strategy
- **Mobile First** - Base styles for mobile devices
- **Progressive Enhancement** - Add features for larger screens
- **Flexible Layouts** - Use CSS Grid and Flexbox for responsive layouts

### Mobile Optimization
- **Touch Targets** - Minimum 44px touch targets
- **Gesture Support** - Swipe and touch gesture handling
- **Performance** - Optimized for mobile performance

## 🔄 Recent Changes (v2.0.0)

### ✅ **Improvements Made**
- **Removed Mock Data** - All components now use real backend data
- **Unified Naming** - Consistent component and prop naming conventions
- **Enhanced TypeScript** - Improved type safety and interfaces
- **Better Error Handling** - Proper error states replace mock fallbacks
- **Performance Optimization** - Reduced bundle size and improved loading

### 🗑️ **Removed**
- **Mood Service Components** - Deprecated mood tracking components (15 files)
- **Sample Data Functions** - Removed all mock data generators
- **Fallback Logic** - Removed mock data fallbacks
- **Inconsistent Patterns** - Unified component structure

### 🔧 **Refactored**
- **Component Organization** - Better file structure and exports
- **Prop Interfaces** - Consistent prop naming and typing
- **State Management** - Unified state management patterns
- **Styling Patterns** - Consistent Tailwind CSS usage

## 📚 Usage Examples

### Basic Component Usage
```typescript
import { CommunityFeed } from '@/components/community'

function App() {
  return (
    <div className="container mx-auto p-4">
      <CommunityFeed />
    </div>
  )
}
```

### Component with Props
```typescript
import { ChatBot } from '@/components/chatbot'

function Dashboard() {
  return (
    <ChatBot
      className="fixed bottom-4 right-4"
      onMessageSent={(message) => console.log('Message sent:', message)}
    />
  )
}
```

### Advanced Integration
```typescript
import { WellnessDashboard } from '@/components/dashboard'
import { useAuth } from '@/hooks/useAuth'

function WellnessPage() {
  const { user } = useAuth()
  
  if (!user) {
    return <div>Please log in to view your wellness dashboard.</div>
  }
  
  return (
    <div className="min-h-screen bg-background">
      <WellnessDashboard />
    </div>
  )
}
```

## 📞 Component Support

### Development Guidelines
- Follow TypeScript-first approach
- Use consistent naming conventions
- Implement proper error handling
- Include accessibility features
- Write comprehensive prop interfaces

### Contributing
- Create components in appropriate directories
- Follow existing patterns and conventions
- Include proper TypeScript types
- Add index.ts exports for new components
- Update documentation for new features

---

**All components are production-ready and follow modern React patterns for optimal performance and user experience.**
