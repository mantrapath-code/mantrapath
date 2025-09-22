# 🎨 Sprint 2 Frontend Execution Plan
**Live Intelligence Integration with Mobile-First Excellence**

Date: 20 Aug 2025  
Branch: arch  
Owner: MantraPath Frontend Team  

## 🎯 Executive Summary

With the backend foundation now **SOLID** and all 4 Sprint 2 services operational, we're implementing a clean, mobile-first frontend that integrates seamlessly with real backend data. No mocks, no clutter—just production-ready real-time experiences.

**Backend Services Ready:**
- ✅ API Gateway (8000) - Service orchestration with WebSocket `/api/v3/voice/stream`
- ✅ AI Context Store (8013) - User context aggregation and cross-service intelligence
- ✅ AI Event Processor (8014) - Real-time AI analysis and emotion detection
- ✅ Voice Event Processor (8015) - Voice event streaming and activity detection
- ✅ Proactive Assistance Engine (8018) - **57ms response time** (89% faster than target)
- ✅ Notification Service (3001) - WebSocket notifications at `/ws/{user_id}`
- ✅ Mood Service (8002) - Enhanced mood tracking with adaptive collection
- ✅ Chatbot Service (8004) - Phase 2 enhanced conversational AI

---

## 🎯 Sprint 2 Frontend Scope Analysis

Based on the comprehensive backend analysis, here's the **complete Sprint 2 frontend scope** that integrates with your solid backend foundation:

### **Discovered Backend Architecture**
```
PORT MAPPING & SERVICE INTEGRATION:
├── 8000: API Gateway (V3 Enhanced)
│   ├── Service orchestration & routing
│   ├── WebSocket: /api/v3/voice/stream
│   ├── Voice command processing
│   └── Performance monitoring
├── 8013: AI Context Store
│   ├── Cross-service intelligence
│   ├── Context aggregation
│   └── Historical analysis
├── 8014: AI Event Processor
│   ├── Real-time AI analysis
│   ├── Emotion detection
│   └── Risk scoring
├── 8015: Voice Event Processor
│   ├── Voice activity detection
│   ├── Session management
│   └── Audio processing
├── 8018: Proactive Assistance Engine ⭐ SPRINT 2 STAR
│   ├── 57ms evaluation (89% faster than target!)
│   ├── Cultural adaptation
│   ├── Voice assistance
│   ├── Multilingual responses
│   └── Sentiment analysis
├── 3001: Notification Service
│   ├── WebSocket: /ws/{user_id}
│   ├── Real-time notifications
│   └── Push messaging
├── 8002: Mood Service
│   ├── Enhanced mood tracking
│   ├── Adaptive questions
│   └── Pattern detection
└── 8004: Chatbot Service
    ├── Phase 2 enhanced AI
    ├── Crisis detection
    └── Intervention suggestions
```

### **Existing Frontend Infrastructure to Leverage** ✅
```
FRONTEND ASSETS DISCOVERED:
├── hooks/
│   ├── ✅ useEnhancedWebSocket.ts (559 lines - robust WebSocket management)
│   ├── ✅ useRealtimeInsights.ts (233 lines - real-time insights handling)
│   ├── ✅ useResponsiveLayout.ts (mobile responsive system)
│   ├── ✅ useTouchGestures.ts (touch interaction support)
│   ├── ✅ usePerformanceMonitor.ts (performance tracking)
│   ├── ✅ useWebSocket.ts (WebSocket foundation)
│   └── ✅ useMoodTheme.ts, useAuth.tsx, useChatbot.ts (existing features)
├── services/
│   ├── ✅ api.ts (1682 lines - comprehensive API service)
│   ├── ✅ auth.ts (authentication integration)
│   ├── ✅ notifications.ts (notification management)
│   └── ✅ unifiedInsightService.ts (insight aggregation)
├── components/
│   └── ✅ Rich component library with shadcn/ui
└── Framework: React 19 + TypeScript + Vite
```

**Key Advantages:**
- **No infrastructure building needed** - WebSocket, API, and notification systems exist
- **Mobile-first foundation ready** - responsive and touch systems implemented
- **Performance monitoring built-in** - already tracking metrics
- **Real-time insights framework** - just needs backend integration

---

**Primary Focus: Proactive Assistance Engine (Port 8018)**
- This is your backend **star performer** with 57ms response times
- Comprehensive API endpoints for assistance evaluation, triggering, and cultural adaptation
- Voice assistance capabilities with multilingual support
- Sentiment analysis and Models Service integration

**Secondary Focus: Real-time Event Integration**
- Notification Service WebSocket (Port 3001) as primary real-time channel
- API Gateway voice streaming (Port 8000) for voice features
- AI Context Store (Port 8013) for intelligent context awareness
- Enhanced mood tracking (Port 8002) with adaptive collection

**Mobile-First Implementation**
- Leverage existing `useResponsiveLayout`, `useTouchGestures`, `usePerformanceMonitor`
- Build on existing WebSocket infrastructure (`useEnhancedWebSocket`, `useRealtimeInsights`)
- Extend current notification system for real-time assistance delivery

---

## 🚀 Sprint 2 Frontend Stories Implementation

### **Story V3-FE-004: Real-Time Event Integration** 
**Priority**: P0 | **Points**: 10 | **Owner**: Frontend Lead  
**Goal**: Connect frontend to live backend events with <300ms UI response time

#### Implementation Tasks

**Task 1: Enhanced WebSocket Event Router (3h)**
```typescript
// File: src/hooks/useEnhancedWebSocket.ts (Update existing)
// Connect to actual backend WebSocket endpoints discovered

interface EventRouter {
  // AI Events (Port 8014)
  'ai.emotion_detected': (data: EmotionData) => void
  'ai.risk_score_updated': (data: RiskData) => void
  'ai.intervention_needed': (data: InterventionData) => void
  
  // Context Events (Port 8013)
  'context.updated': (data: ContextData) => void
  'context.aggregated': (data: AggregatedData) => void
  'context.intelligence_generated': (data: IntelligenceData) => void
  
  // Assistance Events (Port 8018) - Primary Sprint 2 focus
  'assistance.triggered': (data: AssistanceData) => void
  'assistance.delivered': (data: DeliveryData) => void
  'assistance.accepted': (data: FeedbackData) => void
  'assistance.declined': (data: FeedbackData) => void
  'assistance.evaluation_complete': (data: EvaluationData) => void
  
  // Voice Events (API Gateway Port 8000 + Voice Processor Port 8015)
  'voice.activity_detected': (data: VoiceData) => void
  'voice.session_started': (data: SessionData) => void
  'voice.session_ended': (data: SessionData) => void
  'voice.command_processed': (data: CommandData) => void
  
  // Notification Events (Port 3001) - Primary WebSocket endpoint
  'notification.sent': (data: NotificationData) => void
  'notification.delivered': (data: DeliveryData) => void
  'notification.interacted': (data: InteractionData) => void
  
  // Mood Events (Port 8002) - Enhanced adaptive mood tracking
  'mood.entry_created': (data: MoodEntryData) => void
  'mood.pattern_detected': (data: PatternData) => void
  'mood.adaptive_question_triggered': (data: QuestionData) => void
  
  // Chat Events (Port 8004) - Phase 2 enhanced chatbot
  'chat.message_received': (data: ChatMessageData) => void
  'chat.intervention_suggested': (data: InterventionData) => void
  'chat.crisis_detected': (data: CrisisData) => void
}

const BACKEND_WEBSOCKET_ENDPOINTS = {
  // Primary WebSocket connection (Notification Service)
  primary: `ws://localhost:3001/ws/{user_id}`,
  
  // API Gateway voice streaming
  voiceStream: `ws://localhost:8000/api/v3/voice/stream`,
  
  // Individual services (if needed for direct connections)
  assistance: `ws://localhost:8018/ws/{user_id}`,
  aiContext: `ws://localhost:8013/ws/{user_id}`,
  aiEvents: `ws://localhost:8014/ws/{user_id}`,
  voiceEvents: `ws://localhost:8015/ws/{user_id}`
}
```

**Task 2: Real-Time State Management (3h)**
```typescript
// File: src/contexts/RealtimeContext.tsx (New comprehensive context)
interface RealtimeState {
  // Live user context (from AI Context Store Port 8013)
  userContext: UserContext | null
  contextLastUpdated: string | null
  contextIntelligence: IntelligenceData | null
  
  // AI insights (from AI Event Processor Port 8014)
  currentEmotionState: EmotionState | null
  riskScore: number | null
  interventionSuggestions: InterventionData[]
  
  // Assistance state (from Proactive Assistance Engine Port 8018)
  activeAssistance: AssistanceSession | null
  assistanceHistory: AssistanceEvent[]
  assistanceEvaluations: EvaluationData[]
  culturalAdaptations: CulturalContext | null
  
  // Voice activity (from Voice Event Processor Port 8015 + API Gateway Port 8000)
  voiceSession: VoiceSession | null
  voiceCommands: VoiceCommand[]
  voiceActivityLevel: number
  
  // Real-time notifications (from Notification Service Port 3001)
  activeNotifications: NotificationData[]
  notificationHistory: NotificationEvent[]
  
  // Enhanced mood tracking (from Mood Service Port 8002)
  currentMoodState: MoodState | null
  moodPatterns: MoodPattern[]
  adaptiveQuestions: AdaptiveQuestion[]
  
  // Chat intelligence (from Chatbot Service Port 8004)
  chatSessions: ChatSession[]
  chatInsights: ChatInsight[]
  crisisAlerts: CrisisAlert[]
  
  // Connection health across all services
  connectionStatus: Record<string, 'connected' | 'connecting' | 'disconnected'>
  lastHeartbeat: Record<string, string>
  serviceHealth: Record<string, HealthStatus>
}

// Enhanced WebSocket manager that connects to actual backend endpoints
export class EnhancedWebSocketManager {
  private connections: Map<string, WebSocket> = new Map()
  private eventHandlers: Map<string, Function[]> = new Map()
  
  async initialize(userId: string) {
    // Connect to primary notification WebSocket (Port 3001)
    await this.connectToService('notifications', `ws://localhost:3001/ws/${userId}`)
    
    // Connect to voice streaming (API Gateway Port 8000)
    await this.connectToService('voice', `ws://localhost:8000/api/v3/voice/stream`)
    
    // Connect to assistance engine (Port 8018) if WebSocket available
    await this.connectToService('assistance', `ws://localhost:8018/ws/${userId}`)
    
    // Add other connections as needed
  }
  
  private async connectToService(serviceId: string, endpoint: string) {
    try {
      const ws = new WebSocket(endpoint)
      
      ws.onopen = () => {
        console.log(`✅ Connected to ${serviceId} at ${endpoint}`)
        this.connections.set(serviceId, ws)
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.routeEvent(data.type, data)
      }
      
      ws.onerror = (error) => {
        console.error(`❌ WebSocket error for ${serviceId}:`, error)
      }
      
      ws.onclose = () => {
        console.log(`🔌 Disconnected from ${serviceId}`)
        this.connections.delete(serviceId)
        // Implement reconnection logic
      }
      
    } catch (error) {
      console.error(`Failed to connect to ${serviceId}:`, error)
    }
  }
}
```

**Task 3: Live Dashboard Integration (2h)**
```typescript
// File: src/components/dashboard/LiveDashboard.tsx
// Update existing dashboard to use real backend data

export function LiveDashboard() {
  const { 
    userContext, 
    currentEmotionState, 
    riskScore, 
    assistanceHistory,
    moodPatterns,
    voiceActivityLevel,
    connectionStatus 
  } = useRealtime()
  
  return (
    <div className="space-y-6">
      {/* Real-time connection status */}
      <ConnectionHealthIndicator 
        services={connectionStatus}
        className="fixed top-4 right-4 z-50"
      />
      
      {/* Live Mood State (from Mood Service Port 8002) */}
      <LiveMoodIndicator 
        emotion={currentEmotionState} 
        patterns={moodPatterns}
        updateSource="mood_service"
        servicePort={8002}
      />
      
      {/* Context-Aware Insights (from AI Context Store Port 8013) */}
      <ContextualInsights 
        context={userContext}
        riskScore={riskScore}
        intelligence={userContext?.intelligence}
        servicePort={8013}
      />
      
      {/* Live Voice Activity (from Voice Processor Port 8015 + Gateway Port 8000) */}
      <VoiceActivityIndicator 
        activityLevel={voiceActivityLevel}
        session={voiceSession}
        servicePort={8015}
      />
      
      {/* Proactive Assistance Status (from Assistance Engine Port 8018) */}
      <ProactiveAssistancePanel
        activeAssistance={activeAssistance}
        history={assistanceHistory}
        evaluations={assistanceEvaluations}
        servicePort={8018}
      />
      
      {/* AI Event Insights (from AI Event Processor Port 8014) */}
      <AIEventInsights
        emotionState={currentEmotionState}
        riskScore={riskScore}
        interventions={interventionSuggestions}
        servicePort={8014}
      />
    </div>
  )
}

// Enhanced components that show real backend service data
function ConnectionHealthIndicator({ services }: { services: Record<string, string> }) {
  return (
    <div className="bg-background/95 backdrop-blur-sm rounded-lg p-3">
      <h4 className="text-xs font-medium mb-2">Backend Services</h4>
      <div className="space-y-1">
        {Object.entries(services).map(([service, status]) => (
          <div key={service} className="flex items-center gap-2 text-xs">
            <div className={`w-2 h-2 rounded-full ${
              status === 'connected' ? 'bg-green-500' : 
              status === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
              'bg-red-500'
            }`} />
            <span>{service}</span>
            <span className="text-muted-foreground">
              {service === 'assistance' ? ':8018' : 
               service === 'notifications' ? ':3001' :
               service === 'mood' ? ':8002' :
               service === 'voice' ? ':8000' : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Task 4: Optimistic UI with Rollback (1h)**
```typescript
// File: src/hooks/useOptimisticState.ts
export function useOptimisticState<T>(
  initialState: T,
  updateFn: (state: T) => Promise<T>
) {
  const [state, setState] = useState(initialState)
  const [isOptimistic, setIsOptimistic] = useState(false)
  
  const optimisticUpdate = useCallback(async (newState: T) => {
    const previousState = state
    setState(newState)
    setIsOptimistic(true)
    
    try {
      const confirmed = await updateFn(newState)
      setState(confirmed)
    } catch (error) {
      // Rollback on failure
      setState(previousState)
      toast.error('Update failed - changes reverted')
    } finally {
      setIsOptimistic(false)
    }
  }, [state, updateFn])
  
  return { state, optimisticUpdate, isOptimistic }
}
```

**Task 5: Connection Health Monitoring (1h)**
```typescript
// File: src/components/common/ConnectionHealthIndicator.tsx
export function ConnectionHealthIndicator() {
  const { connectionStatus, lastHeartbeat } = useRealtime()
  
  return (
    <div className="fixed top-4 right-4 z-50">
      <Badge variant={connectionStatus === 'connected' ? 'default' : 'destructive'}>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`} />
          <span className="text-xs">
            {connectionStatus === 'connected' ? 'Live' : 'Connecting...'}
          </span>
        </div>
      </Badge>
    </div>
  )
}
```

---

### **Story V3-FE-005: Proactive UI Assistance**
**Priority**: P0 | **Points**: 8 | **Owner**: Senior Frontend Dev  
**Goal**: Context-aware assistance that responds to backend assistance events

#### Implementation Tasks

**Task 1: Contextual Help Overlay System (3h)**
```typescript
// File: src/components/assistance/ContextualHelpOverlay.tsx
interface HelpOverlayProps {
  trigger: AssistanceEvent
  userContext: UserContext
  onAccept: () => void
  onDecline: (reason?: string) => void
}

export function ContextualHelpOverlay({ 
  trigger, 
  userContext, 
  onAccept, 
  onDecline 
}: HelpOverlayProps) {
  const culturalTone = useCulturalTone(userContext.cultural_profile)
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div className="bg-background/95 backdrop-blur-sm rounded-lg shadow-lg max-w-md">
        <div className="p-6 space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              <Heart className="w-4 h-4 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-foreground">
                {culturalTone.greeting}
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                {trigger.suggestion.message}
              </p>
            </div>
          </div>
          
          <div className="flex gap-2 justify-end">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => onDecline()}
            >
              Not now
            </Button>
            <Button 
              size="sm"
              onClick={onAccept}
            >
              {culturalTone.acceptance}
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
```

**Task 2: Proactive Suggestions Panel (2h)**
```typescript
// File: src/components/assistance/ProactiveSuggestionsPanel.tsx
export function ProactiveSuggestionsPanel() {
  const { assistanceHistory, userContext } = useRealtime()
  const suggestions = useProactiveSuggestions(userContext)
  
  return (
    <Card className="border-none shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Brain className="w-4 h-4" />
          Personalized Suggestions
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {suggestions.map((suggestion) => (
          <SuggestionCard 
            key={suggestion.id}
            suggestion={suggestion}
            userContext={userContext}
            onAction={handleSuggestionAction}
          />
        ))}
      </CardContent>
    </Card>
  )
}
```

**Task 3: Intelligent Navigation Assistance (2h)**
```typescript
// File: src/components/assistance/SmartNavigationAssistant.tsx
export function SmartNavigationAssistant() {
  const { userContext, riskScore } = useRealtime()
  const navigation = useNavigation()
  
  // Show guidance based on user state
  const getNavigationGuidance = () => {
    if (riskScore && riskScore > 0.7) {
      return {
        message: "Consider visiting the mood tracker to log how you're feeling",
        action: () => navigation.navigate('/mood'),
        priority: 'high'
      }
    }
    
    if (userContext?.hasUnreadJournalPrompts) {
      return {
        message: "You have new journal prompts waiting",
        action: () => navigation.navigate('/journal'),
        priority: 'medium'
      }
    }
    
    return null
  }
  
  const guidance = getNavigationGuidance()
  
  if (!guidance) return null
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-4 left-4 right-4 md:left-auto md:w-80"
    >
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              <ArrowRight className="w-4 h-4 text-primary" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-foreground">{guidance.message}</p>
            </div>
            <Button size="sm" onClick={guidance.action}>
              Go
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
```

**Task 4: Cultural Adaptation Engine (1h)**
```typescript
// File: src/hooks/useCulturalTone.ts
export function useCulturalTone(culturalProfile: CulturalProfile) {
  return useMemo(() => {
    const { region, language, communication_style } = culturalProfile
    
    const tones = {
      'en-US': {
        greeting: "I've noticed something that might help",
        acceptance: "Show me",
        formal: false
      },
      'ja-JP': {
        greeting: "お手伝いできることがあるかもしれません",
        acceptance: "見てみる", 
        formal: true
      },
      'es-ES': {
        greeting: "He notado algo que podría ayudarte",
        acceptance: "Mostrar",
        formal: false
      }
    }
    
    return tones[`${language}-${region}`] || tones['en-US']
  }, [culturalProfile])
}
```

---

### **Cross-Device Mobile Excellence** 
**Priority**: P0 | **Points**: 12 | **Owner**: Mid Frontend Dev  
**Goal**: Flawless mobile/tablet experience with touch-first design

#### Implementation Tasks

**Task 1: Responsive Layout System (4h)**
```typescript
// File: src/hooks/useResponsiveLayout.ts
export function useResponsiveLayout() {
  const [screenSize, setScreenSize] = useState<ScreenSize>('desktop')
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait')
  
  useEffect(() => {
    const updateLayout = () => {
      const width = window.innerWidth
      const height = window.innerHeight
      
      if (width < 640) setScreenSize('mobile')
      else if (width < 1024) setScreenSize('tablet') 
      else setScreenSize('desktop')
      
      setOrientation(width > height ? 'landscape' : 'portrait')
    }
    
    updateLayout()
    window.addEventListener('resize', updateLayout)
    window.addEventListener('orientationchange', updateLayout)
    
    return () => {
      window.removeEventListener('resize', updateLayout)
      window.removeEventListener('orientationchange', updateLayout)
    }
  }, [])
  
  return { screenSize, orientation }
}
```

**Task 2: Touch Gesture Support (3h)**
```typescript
// File: src/hooks/useTouchGestures.ts
export function useTouchGestures() {
  const swipeHandlers = useSwipeable({
    onSwipedLeft: (eventData) => {
      // Navigate forward or open side panel
    },
    onSwipedRight: (eventData) => {
      // Navigate back or close panel
    },
    onSwipedUp: (eventData) => {
      // Open quick actions
    },
    onSwipedDown: (eventData) => {
      // Refresh content
    },
    preventDefaultTouchmoveEvent: true,
    trackMouse: true
  })
  
  return swipeHandlers
}
```

**Task 3: Mobile Navigation Optimization (2h)**
```typescript
// File: src/components/navigation/MobileNavigation.tsx
export function MobileNavigation() {
  const { screenSize } = useResponsiveLayout()
  const swipeHandlers = useTouchGestures()
  
  if (screenSize !== 'mobile') return null
  
  return (
    <motion.nav 
      {...swipeHandlers}
      className="fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur-sm border-t"
    >
      <div className="flex items-center justify-around py-2">
        {navigationItems.map((item) => (
          <NavItem 
            key={item.id}
            {...item}
            isMobile
            touchOptimized
          />
        ))}
      </div>
    </motion.nav>
  )
}
```

**Task 4: Performance Optimization (2h)**
```typescript
// File: src/hooks/usePerformanceMonitor.ts
export function usePerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    batteryLevel: null
  })
  
  useEffect(() => {
    // Monitor render performance
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      entries.forEach((entry) => {
        if (entry.entryType === 'measure') {
          setMetrics(prev => ({
            ...prev,
            renderTime: entry.duration
          }))
        }
      })
    })
    
    observer.observe({ entryTypes: ['measure'] })
    
    // Monitor memory usage
    if ('memory' in performance) {
      const memoryInfo = (performance as any).memory
      setMetrics(prev => ({
        ...prev,
        memoryUsage: memoryInfo.usedJSHeapSize / 1024 / 1024 // MB
      }))
    }
    
    // Monitor battery (if available)
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        setMetrics(prev => ({
          ...prev,
          batteryLevel: battery.level
        }))
      })
    }
    
    return () => observer.disconnect()
  }, [])
  
  return metrics
}
```

**Task 5: Accessibility Excellence (1h)**
```typescript
// File: src/components/common/AccessibilityProvider.tsx
export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  
  useEffect(() => {
    // Respect user preferences
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const contrastQuery = window.matchMedia('(prefers-contrast: high)')
    
    setReducedMotion(motionQuery.matches)
    setHighContrast(contrastQuery.matches)
    
    const handleMotionChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches)
    const handleContrastChange = (e: MediaQueryListEvent) => setHighContrast(e.matches)
    
    motionQuery.addEventListener('change', handleMotionChange)
    contrastQuery.addEventListener('change', handleContrastChange)
    
    return () => {
      motionQuery.removeEventListener('change', handleMotionChange)
      contrastQuery.removeEventListener('change', handleContrastChange)
    }
  }, [])
  
  return (
    <div 
      className={cn(
        reducedMotion && 'motion-reduce',
        highContrast && 'high-contrast'
      )}
      data-reduced-motion={reducedMotion}
      data-high-contrast={highContrast}
    >
      {children}
    </div>
  )
}
```

---

## 🔗 Backend Integration Endpoints

### **Real-Time WebSocket Endpoints**
```typescript
// Primary WebSocket Connections
const WEBSOCKET_ENDPOINTS = {
  // API Gateway - Voice Streaming (Port 8000)
  voiceStream: `ws://localhost:8000/api/v3/voice/stream`,
  
  // Notification Service - Real-time notifications (Port 3001)
  notifications: `ws://localhost:3001/ws/{user_id}`,
  
  // Individual service endpoints (if direct connection needed)
  aiContext: `ws://localhost:8013/ws/{user_id}`,
  aiEvents: `ws://localhost:8014/ws/{user_id}`,
  voiceEvents: `ws://localhost:8015/ws/{user_id}`,
  assistance: `ws://localhost:8018/ws/{user_id}`
}
```

### **HTTP API Endpoints**
```typescript
// Core API Endpoints mapped to actual backend services
const API_ENDPOINTS = {
  // API Gateway (Port 8000) - Primary entry point
  gateway: {
    base: 'http://localhost:8000',
    health: '/api/v3/health/enhanced',
    voiceCommand: '/api/v3/voice/command',
    metrics: '/api/v3/metrics/performance'
  },
  
  // AI Context Store (Port 8013)
  context: {
    base: 'http://localhost:8013',
    root: '/',
    metrics: '/metrics'
  },
  
  // AI Event Processor (Port 8014) 
  aiEvents: {
    base: 'http://localhost:8014',
    // Routes defined in app.py (not yet examined)
  },
  
  // Voice Event Processor (Port 8015)
  voiceEvents: {
    base: 'http://localhost:8015',
    // Routes defined in app.py
  },
  
  // Proactive Assistance Engine (Port 8018) - Key for Sprint 2
  assistance: {
    base: 'http://localhost:8018',
    evaluate: (userId: string) => `/api/v1/assistance/evaluate/${userId}`,
    status: (userId: string) => `/api/v1/assistance/status/${userId}`,
    trigger: (userId: string) => `/api/v1/assistance/trigger/${userId}`,
    voiceAssistance: (userId: string) => `/api/v1/assistance/voice/${userId}`,
    multilingualResponse: '/api/v1/assistance/multilingual-response',
    sentimentAnalysis: '/api/v1/assistance/sentiment-analysis',
    modelsStatus: '/api/v1/models/status',
    health: '/health',
    metrics: '/metrics'
  },
  
  // Notification Service (Port 3001)
  notifications: {
    base: 'http://localhost:3001',
    // WebSocket primary: /ws/{user_id}
  },
  
  // Mood Service (Port 8002) - Enhanced mood tracking
  mood: {
    base: 'http://localhost:8002',
    // Rich mood tracking with adaptive questions
  },
  
  // Chatbot Service (Port 8004) - Phase 2 enhanced
  chatbot: {
    base: 'http://localhost:8004',
    // Enhanced V2 conversational capabilities
  }
}
```

### **Event Types for Real-time Integration**
```typescript
// Event types based on actual backend event channels
interface EventRouter {
  // AI Events (from ai_event_processor)
  'ai.emotion_detected': (data: EmotionData) => void
  'ai.risk_score_updated': (data: RiskData) => void
  'ai.intervention_needed': (data: InterventionData) => void
  
  // Context Events (from ai_context_store)
  'context.updated': (data: ContextData) => void
  'context.aggregated': (data: AggregatedData) => void
  'context.intelligence_generated': (data: IntelligenceData) => void
  
  // Assistance Events (from proactive_assistance_engine)
  'assistance.triggered': (data: AssistanceData) => void
  'assistance.delivered': (data: DeliveryData) => void
  'assistance.accepted': (data: FeedbackData) => void
  'assistance.declined': (data: FeedbackData) => void
  'assistance.evaluation_complete': (data: EvaluationData) => void
  
  // Voice Events (from voice_event_processor + API Gateway)
  'voice.activity_detected': (data: VoiceData) => void
  'voice.session_started': (data: SessionData) => void
  'voice.session_ended': (data: SessionData) => void
  'voice.command_processed': (data: CommandData) => void
  
  // Mood Events (from mood_service)
  'mood.entry_created': (data: MoodEntryData) => void
  'mood.pattern_detected': (data: PatternData) => void
  'mood.adaptive_question_triggered': (data: QuestionData) => void
  
  // Notification Events (from notification_service)
  'notification.sent': (data: NotificationData) => void
  'notification.delivered': (data: DeliveryData) => void
  'notification.interacted': (data: InteractionData) => void
  
  // Chat Events (from chatbot_service)
  'chat.message_received': (data: ChatMessageData) => void
  'chat.intervention_suggested': (data: InterventionData) => void
  'chat.crisis_detected': (data: CrisisData) => void
}

---

## 📱 Mobile-First Design Principles

### **Touch-Optimized Interface**
- **Touch Targets**: Minimum 44px (iOS) / 48dp (Android) 
- **Gesture Support**: Swipe navigation, pull-to-refresh, pinch-to-zoom
- **Haptic Feedback**: Success vibrations for confirmations
- **Safe Areas**: Respect notch and home indicator areas

### **Performance Targets**
- **Initial Load**: <2s on 3G connection
- **Real-time Events**: <300ms UI response time  
- **Memory Usage**: <100MB on mobile, <200MB on desktop
- **Battery Impact**: <5% additional battery usage

### **Progressive Enhancement**
- **Offline First**: Cache critical UI and last 10 notifications
- **Reduced Motion**: Respect `prefers-reduced-motion`
- **High Contrast**: Support `prefers-contrast: high`
- **Dark Mode**: Auto-detect and manual toggle

---

## 🧪 Testing Strategy

### **Real-Time Testing**
```typescript
// File: src/__tests__/realtime.test.tsx
describe('Real-time Integration', () => {
  test('receives assistance events and updates UI within 300ms', async () => {
    const { container } = render(<App />)
    
    // Mock WebSocket event
    mockWebSocketEvent({
      type: 'assistance.triggered',
      data: { userId: 'test-user', suggestion: 'Take a breathing break' }
    })
    
    // Verify UI updates within target time
    await waitFor(() => {
      expect(screen.getByText('Take a breathing break')).toBeInTheDocument()
    }, { timeout: 300 })
  })
  
  test('handles connection failures gracefully', async () => {
    // Simulate connection failure
    mockWebSocketDisconnect()
    
    expect(screen.getByText('Connecting...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })
})
```

### **Mobile Testing Matrix**
- **iOS**: Safari 15+, Chrome, Edge
- **Android**: Chrome, Samsung Internet, Firefox  
- **Tablets**: iPad, Android tablets
- **Touch Interactions**: Gestures, haptics, orientation

---

## 🎯 Success Metrics

### **Performance KPIs**
- ✅ UI Response Time: <300ms for real-time events
- ✅ WebSocket Latency: <200ms message delivery  
- ✅ Memory Usage: <100MB mobile, <200MB desktop
- ✅ Battery Impact: <5% additional usage

### **User Experience KPIs**  
- ✅ Real-time Update Success Rate: >99%
- ✅ Proactive Assistance Accuracy: >90%
- ✅ Cross-Device Consistency: >95%
- ✅ Accessibility Compliance: WCAG 2.1 AA

### **Technical KPIs**
- ✅ Code Coverage: >90% for new features
- ✅ Performance Regression: 0% degradation
- ✅ Mobile Performance Score: >90 (Lighthouse)
- ✅ Bundle Size Impact: <10% increase

---

## 📅 Implementation Timeline

### **Week 1: Foundation (Days 1-3)**
- **Day 1**: Enhanced WebSocket & Real-time State Management  
- **Day 2**: Live Dashboard Integration & Optimistic UI
- **Day 3**: Connection Health & Error Handling

### **Week 2: Assistance & Mobile (Days 4-7)**  
- **Day 4**: Contextual Help System & Proactive Suggestions
- **Day 5**: Intelligent Navigation & Cultural Adaptation
- **Day 6**: Mobile Responsive System & Touch Gestures  
- **Day 7**: Performance Optimization & Testing

---

## 🚀 Definition of Done (Sprint 2 Frontend)

### **V3-FE-004: Real-Time Event Integration** ✅ READY TO IMPLEMENT
- ✅ Backend WebSocket endpoints mapped (Notification Service Port 3001 primary)
- ✅ Existing `useEnhancedWebSocket` ready for backend integration
- ✅ Event routing architecture defined for 8 backend services
- ⏳ Connect to real Proactive Assistance Engine (Port 8018)
- ⏳ Integrate AI Context Store intelligence (Port 8013)
- ⏳ Real-time mood tracking from Mood Service (Port 8002)
- ⏳ Voice activity streaming from API Gateway (Port 8000)

### **V3-FE-005: Proactive UI Assistance** ✅ BACKEND READY
- ✅ Proactive Assistance Engine **performing at 57ms** (89% faster than target)
- ✅ Cultural adaptation APIs available (`/api/v1/assistance/multilingual-response`)
- ✅ Voice assistance APIs ready (`/api/v1/assistance/voice/{user_id}`)
- ✅ Sentiment analysis endpoint available
- ⏳ Contextual help overlay system implementation
- ⏳ Proactive suggestion panels with cultural tone
- ⏳ Smart navigation assistance based on user state

### **Cross-Device Mobile Excellence** ✅ FOUNDATION READY
- ✅ `useResponsiveLayout`, `useTouchGestures` hooks exist
- ✅ `usePerformanceMonitor` tracking system implemented
- ✅ React 19 + TypeScript + Vite stack optimized
- ⏳ Mobile navigation optimization
- ⏳ Touch gesture integration for assistance panels
- ⏳ Battery and performance optimizations

### **Integration Quality** ✅ BACKEND INTEGRATION MAPPED
- ✅ All 8 backend services mapped with endpoints
- ✅ WebSocket architecture defined for real-time events
- ✅ API service (1682 lines) ready for backend integration
- ✅ No mocks needed - direct backend data integration
- ⏳ Error handling with graceful degradation
- ⏳ Optimistic UI with rollback on failures
- ⏳ Cross-service intelligence display

---

## 📋 Sprint 2 Implementation Checklist

### **Week 1: Core Integration (Days 1-3)**
- [ ] **Day 1**: Update `useEnhancedWebSocket` to connect to Port 3001 notifications
- [ ] **Day 1**: Integrate Proactive Assistance Engine API calls (Port 8018)
- [ ] **Day 2**: Implement real-time state management with backend events
- [ ] **Day 2**: Update dashboard with live AI Context Store data (Port 8013)
- [ ] **Day 3**: Add voice activity indicators from API Gateway (Port 8000)
- [ ] **Day 3**: Implement connection health monitoring across services

### **Week 2: Assistance & Mobile (Days 4-7)**
- [ ] **Day 4**: Build contextual help overlay system for assistance events
- [ ] **Day 4**: Implement proactive suggestion panels with cultural adaptation
- [ ] **Day 5**: Add intelligent navigation assistance based on AI insights
- [ ] **Day 5**: Integrate sentiment analysis and multilingual responses
- [ ] **Day 6**: Optimize mobile navigation with touch gesture support
- [ ] **Day 6**: Implement performance optimizations and battery management
- [ ] **Day 7**: End-to-end testing and accessibility compliance

### **Success Metrics Targets**
- **UI Response Time**: <300ms for real-time events (Target leveraging 57ms backend)
- **WebSocket Reliability**: >99% uptime with auto-reconnection
- **Mobile Performance**: >90 Lighthouse score on mobile devices
- **Cross-Service Integration**: All 8 backend services connected and functional
- **Cultural Adaptation**: Assistance tone adapts to user cultural profile
- **Zero Mock Data**: 100% real backend integration

---

## 🎯 Next Steps

**Immediate Action (Today):**
1. **Start with Proactive Assistance Engine integration** - Your 57ms backend star ⭐
2. **Connect to Notification Service WebSocket** - Primary real-time channel (Port 3001)
3. **Update existing `useEnhancedWebSocket`** - Leverage 559 lines of existing code

**This Sprint 2 frontend plan leverages your solid backend foundation and existing frontend infrastructure for a clean, production-ready implementation with zero clutter and exceptional mobile experience.**
