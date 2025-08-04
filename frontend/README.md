# MantraPath Frontend

**Version:** 2.0.0  
**Last Updated:** August 4, 2025  
**Status:** Production Ready - Mock-Free & Unified

## Overview

The MantraPath frontend is a modern, React-based web application built with TypeScript, Vite, and Tailwind CSS. This application provides a comprehensive mental wellness platform with real-time features, community interaction, journaling, and AI-powered insights.

## 🎯 Key Features

### ✅ **Mock-Free Architecture**
- **100% Real Backend Integration** - No mock data, sample data, or fallback logic
- **Live API Connections** - All data comes from authenticated backend services
- **Real-time Updates** - WebSocket integration for live community and notification features
- **Proper Error Handling** - Clean error states instead of fallback mock data

### 🏗️ **Unified Code Architecture**
- **Consistent Patterns** - Standardized component structure and naming conventions
- **Clean Component Hierarchy** - Well-organized component architecture
- **Unified Service Layer** - Centralized API management with consistent patterns
- **Type Safety** - Comprehensive TypeScript implementation

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
│   ├── components/           # Reusable UI components
│   │   ├── auth/            # Authentication components
│   │   ├── chatbot/         # AI chatbot interface
│   │   ├── common/          # Shared utility components
│   │   ├── community/       # Community features
│   │   ├── dashboard/       # Dashboard and analytics
│   │   ├── journal/         # Journaling components
│   │   ├── notifications/   # Notification system
│   │   ├── profile/         # User profile management
│   │   └── ui/              # Base UI components (shadcn/ui)
│   ├── hooks/               # Custom React hooks
│   ├── pages/               # Top-level page components
│   ├── services/            # API service layer
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   └── styles/              # Global styles and themes
├── public/                  # Static assets
├── docs/                    # Documentation
└── dist/                    # Production build output
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

### Component Organization
- **Atomic Design** - Components organized by complexity and reusability
- **Feature-Based** - Components grouped by business domain
- **Consistent Exports** - Standardized index.ts files for clean imports

### State Management
- **React Hooks** - useState, useEffect, useCallback for local state
- **Custom Hooks** - Domain-specific hooks for data fetching and business logic
- **Context Providers** - For shared state (auth, theme, websocket)

### Data Fetching
- **Service Layer** - Centralized API calls through service classes
- **Custom Hooks** - Domain-specific hooks that encapsulate data fetching logic
- **Error Handling** - Consistent error states and user feedback
- **Loading States** - Proper loading indicators throughout the app

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

### Code Standards
- **TypeScript First** - All components and utilities are strongly typed
- **Functional Components** - React hooks pattern throughout
- **ESLint + Prettier** - Consistent code formatting and linting
- **Component Documentation** - JSDoc comments for complex components

### Naming Conventions
- **Components** - PascalCase (e.g., `CommunityFeed.tsx`)
- **Hooks** - camelCase with 'use' prefix (e.g., `useWellness.ts`)
- **Services** - camelCase with descriptive names (e.g., `apiService.ts`)
- **Types** - PascalCase interfaces (e.g., `interface UserProfile`)

### File Organization
- **Single Responsibility** - One component per file
- **Barrel Exports** - index.ts files for clean imports
- **Co-location** - Related files grouped together
- **Consistent Structure** - Standardized file and folder patterns

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

## 🔄 Recent Changes (v2.0.0)

### ✅ **Completed Improvements**
- **Removed All Mock Data** - 100% real backend integration
- **Unified Architecture** - Consistent patterns throughout codebase
- **Obsolete Code Cleanup** - Removed deprecated mood service components
- **Enhanced Error Handling** - Proper error states instead of fallbacks
- **Improved Performance** - Optimized bundle size and loading
- **Better TypeScript** - Enhanced type safety and developer experience

### 🗑️ **Removed**
- Mock data generators and sample data functions
- Fallback logic for offline scenarios
- Obsolete mood service components (15 files, 282KB)
- Deprecated hooks and utilities
- Inconsistent naming patterns

### 🔧 **Refactored**
- Component naming standardization
- Service layer unification
- Hook consolidation and cleanup
- Error handling patterns
- Loading state management

## 📞 Support

For technical support or questions:
- **Documentation** - Check component and API documentation
- **Issues** - Create GitHub issues for bugs or feature requests
- **Development** - Follow coding standards and contribution guidelines

---

**Built with ❤️ for mental wellness and community support**
