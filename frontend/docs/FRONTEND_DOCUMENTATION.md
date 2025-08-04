# MantraPath Frontend Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Directory Structure](#directory-structure)
4. [Component Architecture](#component-architecture)
5. [Configuration Files](#configuration-files)
6. [Development Workflow](#development-workflow)
7. [Styling System](#styling-system)
8. [State Management](#state-management)
9. [API Integration](#api-integration)
10. [Performance Optimization](#performance-optimization)
11. [Security Considerations](#security-considerations)
12. [Best Practices](#best-practices)

---

## Project Overview

**MantraPath** is a holistic wellness platform frontend application built with modern React and TypeScript technologies. The application provides a comprehensive mental health and wellness dashboard with features including mood tracking, journaling, community interactions, chatbot assistance, and personalized insights.

### Key Features
- **Mood Tracking & Analytics**: Advanced mood pattern recognition and visualization
- **Journal Management**: Personal journaling with mood correlation
- **Community Platform**: User interactions, discussions, and support groups
- **AI Chatbot**: Intelligent wellness assistant (Mitra)
- **Real-time Notifications**: Live updates and wellness reminders
- **Personalized Dashboard**: Customizable wellness metrics and insights
- **Profile Management**: User settings and wellness preferences
- **Crisis Prediction**: Advanced analytics for mental health crisis prevention

---

## Technology Stack

### Core Technologies
- **React 19.0.0**: Latest React with concurrent features
- **TypeScript 5.7.2**: Strict type safety and modern JavaScript features
- **Vite 6.3.5**: Fast build tool and development server
- **Tailwind CSS 4.0.17**: Utility-first CSS framework

### UI Framework & Components
- **Radix UI**: Comprehensive primitive component library
- **Lucide React**: Icon library for modern UI
- **Phosphor Icons**: Additional icon set for enhanced UX
- **Framer Motion 12.6.2**: Advanced animations and gestures

### Data Visualization
- **Recharts 2.15.1**: Chart library for mood analytics
- **D3.js 7.9.0**: Advanced data visualization capabilities

### Form Management
- **React Hook Form 7.54.2**: Performant form handling
- **Zod 3.24.2**: Schema validation

---

## Directory Structure

```
frontend/
├── public/                          # Static assets
├── src/                            # Source code
│   ├── components/                 # React components
│   │   ├── auth/                  # Authentication components
│   │   ├── chatbot/               # AI chatbot interface
│   │   ├── common/                # Shared components
│   │   ├── community/             # Community features
│   │   ├── dashboard/             # Dashboard components
│   │   ├── journal/               # Journaling interface
│   │   ├── mood/                  # Mood tracking components
│   │   ├── notifications/         # Notification system
│   │   ├── profile/               # User profile management
│   │   └── ui/                    # Base UI components (Radix-based)
│   ├── hooks/                     # Custom React hooks
│   ├── pages/                     # Page-level components
│   ├── services/                  # API service layers
│   ├── styles/                    # Global styles and themes
│   ├── types/                     # TypeScript type definitions
│   ├── utils/                     # Utility functions
│   ├── App.tsx                    # Main application component
│   ├── main.tsx                   # Application entry point
│   └── index.css                  # Base styles
├── package.json                   # Dependencies and scripts
├── tailwind.config.js             # Tailwind CSS configuration
├── tsconfig.json                  # TypeScript configuration
└── vite.config.ts                 # Vite build configuration
```

### Component Organization Principles

#### Feature-Based Structure
Components are organized by feature domains:
- **auth/**: Login, registration, verification components
- **mood/**: Mood tracking, analytics, pattern recognition
- **journal/**: Personal journaling and mood correlation
- **community/**: Social features, discussions, support groups
- **dashboard/**: Main dashboard and wellness metrics
- **chatbot/**: AI assistant interface and conversation management
- **notifications/**: Real-time notifications and alert system
- **profile/**: User settings, preferences, and profile management

---

## Component Architecture

### Component Hierarchy

```
App.tsx (Root)
├── AuthProvider (Context)
├── ThemeProvider (Context)
├── ErrorBoundary
├── DevelopmentBanner
├── AuthScreen (Conditional)
├── MainApplication
│   ├── ProfileDropdown
│   ├── Tabs Navigation
│   │   ├── WellnessDashboard
│   │   ├── MoodTracker
│   │   ├── JournalSection
│   │   ├── EnhancedCommunitySection
│   │   ├── InsightsPage
│   │   ├── WeatherPage
│   │   └── AchievementsPage
│   ├── FloatingChatBot
│   ├── RealTimeNotifications
│   └── MoodPatternNotifications
```

### Component Design Patterns

#### 1. Compound Components
Used extensively with Radix UI for complex interactive elements:
```typescript
<Tabs defaultValue="dashboard">
  <TabsList>
    <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
    <TabsTrigger value="mood">Mood</TabsTrigger>
  </TabsList>
  <TabsContent value="dashboard">
    <WellnessDashboard />
  </TabsContent>
</Tabs>
```

#### 2. Custom Hooks Pattern
Encapsulating business logic and state management:
- `useAuth()`: Authentication state and methods
- `useMoodBasedTheme()`: Dynamic theming based on mood
- `useWebSocket()`: Real-time connection management

#### 3. Component Structure Best Practices
```typescript
interface ComponentProps {
  /** Description of the prop */
  propName: PropType
}

export const ComponentName: React.FC<ComponentProps> = ({
  propName,
  ...restProps
}) => {
  // Hooks (useState, useEffect, custom hooks)
  // Event handlers
  // Computed values
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="component-styles"
      {...restProps}
    >
      {/* Component JSX */}
    </motion.div>
  )
}
```

---

## Configuration Files

### 1. Vite Configuration (`vite.config.ts`)

```typescript
export default defineConfig({
  plugins: [
    react(),           // React support with SWC
    tailwindcss(),     // Tailwind CSS integration
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')  // Path aliasing
    }
  },
  server: {
    port: 5173,                    // Development server port
    host: '0.0.0.0',              // Allow external access
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Backend API proxy
        changeOrigin: true,
        secure: false
      }
    }
  }
})
```

### 2. TypeScript Configuration (`tsconfig.json`)

Key configuration highlights:
- **Strict Mode**: Maximum type safety
- **Path Mapping**: Absolute imports support with `@/*`
- **Modern JavaScript**: ES2020+ features
- **Unused Code Detection**: Clean code enforcement

### 3. Tailwind CSS Configuration (`tailwind.config.js`)

Extended with custom design tokens:
- Custom color palette for wellness theme
- Animation utilities
- Container queries plugin
- Responsive design utilities

---

## Development Workflow

### Getting Started

1. **Environment Setup**
   ```bash
   npm install        # Install dependencies
   npm run dev        # Start development server
   ```

2. **Development Commands**
   ```bash
   npm run lint       # Code linting
   npm run build      # Production build
   npm run preview    # Preview production build
   ```

### Development Guidelines

#### 1. Code Organization
- One component per file
- Feature-based directory structure
- Consistent naming conventions (PascalCase for components)
- Index files for clean imports

#### 2. Import Conventions
```typescript
// External libraries
import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

// Internal components (absolute imports)
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'

// Types and interfaces
import type { User, MoodData } from '@/types'
```

---

## Styling System

### Design System Architecture

#### 1. Tailwind Integration
- Utility-first CSS approach
- Custom color palette for wellness theme
- Responsive design utilities
- Animation and transition classes

#### 2. Component-Specific Styles
```typescript
<div className="
  bg-white dark:bg-gray-900 
  rounded-lg shadow-sm 
  p-6 space-y-4
  transform transition-all duration-200
  hover:shadow-md hover:scale-105
">
```

#### 3. Theme System
- Dynamic theming with `useMoodBasedTheme`
- Dark mode support with `next-themes`
- Mood-based color adaptations
- Responsive breakpoint strategies

---

## State Management

### State Architecture

#### 1. Local Component State
For simple, component-specific state:
```typescript
const [isOpen, setIsOpen] = useState(false)
const [formData, setFormData] = useState<FormData>({})
```

#### 2. Context API
For app-wide state (authentication, theme):
```typescript
const AuthContext = createContext<AuthContextType>()

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  
  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
```

#### 3. Custom Hooks
For shared stateful logic:
```typescript
export const useMoodData = () => {
  const [moodData, setMoodData] = useState<MoodEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const fetchMoodData = useCallback(async () => {
    try {
      setLoading(true)
      const data = await moodService.getUserMoodData()
      setMoodData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { moodData, loading, error, refetch: fetchMoodData }
}
```

---

## API Integration

### Service Layer Architecture

#### Base API Client
```typescript
class ApiClient {
  private baseURL: string
  private token: string | null
  
  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.token = localStorage.getItem('authToken')
  }
  
  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
      ...options.headers
    }
    
    const response = await fetch(url, {
      ...options,
      headers
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    
    return response.json()
  }
}
```

#### Service Implementations
```typescript
export const moodService = {
  async getMoodEntries(userId: string): Promise<MoodEntry[]> {
    return apiClient.request(`/mood/entries/${userId}`)
  },
  
  async createMoodEntry(entry: CreateMoodEntryRequest): Promise<MoodEntry> {
    return apiClient.request('/mood/entries', {
      method: 'POST',
      body: JSON.stringify(entry)
    })
  }
}
```

### Real-time Integration

#### WebSocket Connection
```typescript
export const useWebSocket = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  
  useEffect(() => {
    const ws = new WebSocket(import.meta.env.VITE_WS_URL)
    
    ws.onopen = () => setIsConnected(true)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleRealtimeUpdate(data)
    }
    
    setSocket(ws)
    return () => ws.close()
  }, [])
  
  return { socket, isConnected }
}
```

---

## Performance Optimization

### Code Splitting

#### Route-based Splitting
```typescript
import { lazy, Suspense } from 'react'

const MoodDashboard = lazy(() => import('@/components/mood/MoodDashboard'))

const App = () => (
  <Suspense fallback={<LoadingSpinner />}>
    <Routes>
      <Route path="/mood" element={<MoodDashboard />} />
    </Routes>
  </Suspense>
)
```

### Memoization Strategies

#### Component Memoization
```typescript
const MoodCard = React.memo<MoodCardProps>(({ mood, onUpdate }) => {
  const handleUpdate = useCallback(() => {
    onUpdate(mood.id)
  }, [mood.id, onUpdate])
  
  return (
    <Card className="mood-card">
      <MoodDisplay mood={mood} />
      <Button onClick={handleUpdate}>Update</Button>
    </Card>
  )
})
```

---

## Security Considerations

### Authentication Security

#### Token Management
```typescript
class TokenManager {
  private static readonly TOKEN_KEY = 'authToken'
  
  static setTokens(accessToken: string, refreshToken: string) {
    localStorage.setItem(this.TOKEN_KEY, accessToken)
    localStorage.setItem('refreshToken', refreshToken)
  }
  
  static getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY)
  }
  
  static clearTokens() {
    localStorage.removeItem(this.TOKEN_KEY)
    localStorage.removeItem('refreshToken')
  }
}
```

### Input Validation & Sanitization

#### Form Validation with Zod
```typescript
import { z } from 'zod'

const moodEntrySchema = z.object({
  mood: z.number().min(1).max(10),
  notes: z.string().max(1000).optional(),
  date: z.date(),
  tags: z.array(z.string()).max(10)
})

type MoodEntryFormData = z.infer<typeof moodEntrySchema>
```

---

## Best Practices

### Code Quality

1. **TypeScript Usage**
   - Strict type checking enabled
   - Proper interface definitions
   - Generic type usage for reusable components

2. **Component Design**
   - Single responsibility principle
   - Proper prop drilling vs context usage
   - Consistent error handling patterns

3. **Performance**
   - Lazy loading for large components
   - Memoization for expensive calculations
   - Proper dependency arrays in hooks

4. **Accessibility**
   - Semantic HTML usage
   - ARIA labels and roles
   - Keyboard navigation support
   - Screen reader compatibility

### Testing Strategy

1. **Unit Testing**
   - Component testing with React Testing Library
   - Hook testing with custom test utilities
   - Service layer testing with mocked API calls

2. **Integration Testing**
   - User flow testing
   - API integration testing
   - Cross-component interaction testing

3. **E2E Testing**
   - Critical user journeys
   - Authentication flows
   - Data persistence verification

### Deployment

1. **Build Optimization**
   - Bundle size analysis
   - Code splitting strategies
   - Asset optimization

2. **Environment Configuration**
   - Environment-specific builds
   - Feature flag management
   - API endpoint configuration

3. **Monitoring**
   - Error tracking integration
   - Performance monitoring
   - User analytics

---

## Troubleshooting

### Common Issues

1. **Build Errors**
   - TypeScript type errors
   - Missing dependencies
   - Import path issues

2. **Runtime Errors**
   - API connection failures
   - Authentication token expiry
   - WebSocket connection issues

3. **Performance Issues**
   - Large bundle sizes
   - Slow component rendering
   - Memory leaks in useEffect

### Debug Tools

- React Developer Tools
- Vite build analyzer
- TypeScript compiler diagnostics
- Browser dev tools profiling

---

## Contributing

### Code Standards
- Follow ESLint configuration
- Use Prettier for code formatting
- Write meaningful commit messages
- Include proper TypeScript types

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation if needed
4. Submit PR with detailed description
5. Code review and approval process

---

This documentation provides a comprehensive guide to the MantraPath frontend codebase, covering all aspects from basic setup to advanced optimization techniques. It serves as both a reference for existing developers and an onboarding guide for new team members.
