import { useState, useEffect, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { X } from "@phosphor-icons/react"
import { JournalSection } from "@/components/journal"
import { MinimizableChatBot } from "@/components/chatbot"
import { EnhancedCommunitySection } from "@/components/community"
import { ModularWellnessDashboard } from "@/components/dashboard"
import { CrisisDetectionDashboard } from "@/components/crisis"
import { AuthScreen } from "@/components/auth"
import { EmailVerification } from "@/components/auth"
import { DevelopmentBanner } from "@/components/common"
import { ProfileDashboard } from "@/components/profile"
import { EnhancedInsightsPage } from "@/pages/EnhancedInsightsPage"
import { AchievementsPage } from "@/pages/AchievementsPage"
import { MoodTestPage } from "@/pages/MoodTestPage"
import { OptimizedMoodPage } from "@/pages/OptimizedMoodPage"
import VoiceTestingPage from "@/pages/VoiceTestingPageIndic"
import { ProactiveAssistancePanel } from "@/components/assistance"
import { SidebarLayout } from "@/components/layout/SidebarLayout"
import { AuthProvider, useAuth } from "@/hooks/useAuth"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { useRobustWebSocket } from "@/hooks/useRobustWebSocket"
import { RealtimeProvider } from "@/contexts/RealtimeContext"
import { useDeviceCapabilities } from "@/hooks/useDeviceCapabilities"
import { usePerformanceMonitor } from "@/hooks/usePerformanceMonitor"
import { motion, AnimatePresence } from "framer-motion"
import { Toaster } from "@/components/ui/sonner"
import { toast } from "sonner"
// Import localStorage utilities for debugging
import "@/utils/localStorage"
// Import voice permissions for voice features
import "@/utils/voicePermissions"
// Import health check for development
import "@/utils/healthCheck"
// Import notification styles
import "./styles/notifications.css"

function AppContent() {
  const { user, logout, isAuthenticated, loading } = useAuth()
  const [activeTab, setActiveTab] = useState("dashboard")
  const [showChat, setShowChat] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [showEmailVerification, setShowEmailVerification] = useState(false)
  
  // Check for verification token in URL on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get('token')
    if (token) {
      setShowEmailVerification(true)
    }
  }, [])
  
  // Enhanced device capabilities
  const deviceCapabilities = useDeviceCapabilities()
  
  // Initialize mood-based theme system
  const { currentTheme } = useMoodBasedTheme()
  
  // Initialize robust WebSocket connection for real-time features
  const { isConnected, connectionError, connectionStats, hasAttemptedConnection, reconnectAll } = useRobustWebSocket(user?.id, {
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    heartbeatInterval: 30000,
    enableHeartbeat: true
  })
  
  // Improved offline / realtime status logic:
  // Original logic only flagged offline when VITE_WS_URL was unset. That hid real connection issues for other devices.
  // Now: if we attempted to connect and are still not connected after a grace period, mark realtime offline even if VITE_WS_URL is set.
  const [graceExpired, setGraceExpired] = useState(false)
  useEffect(() => {
    if (!hasAttemptedConnection) return
    const t = setTimeout(() => setGraceExpired(true), 5000)
    return () => clearTimeout(t)
  }, [hasAttemptedConnection])
  const isOfflineMode = (graceExpired && hasAttemptedConnection && !isConnected)
  
  // Performance monitoring
  const { metrics, alerts, getPerformanceScore } = usePerformanceMonitor()
  
  // Memoize performance score to prevent excessive re-calculations
  const performanceScore = useMemo(() => getPerformanceScore(metrics), [getPerformanceScore, metrics])

  // Check for email verification token in URL or verification result
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const verificationToken = urlParams.get('token')
    const currentPath = window.location.pathname
    
    // Handle direct token verification (legacy)
    if (verificationToken) {
      setShowEmailVerification(true)
    }
    
    // Handle verification success/failure redirects from auth service
    if (currentPath.includes('verification-success')) {
      const status = urlParams.get('status')
      if (status === 'already_verified') {
        toast.success('Email already verified! You can now log in.')
      } else {
        toast.success('Email verified successfully! You can now log in.')
      }
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname)
    } else if (currentPath.includes('verification-failed')) {
      const error = urlParams.get('error')
      if (error === 'token_expired') {
        toast.error('Verification link has expired. Please register again.')
      } else if (error === 'invalid_token') {
        toast.error('Invalid verification link. Please try again.')
      } else {
        toast.error('Email verification failed. Please try again.')
      }
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [])

  // Check for force logout parameter
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('logout') === 'true') {
      console.log('🔧 Force logout requested')
      logout()
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [logout])

  const handleCloseEmailVerification = () => {
    setShowEmailVerification(false)
    // Clear the token from URL
    const url = new URL(window.location.href)
    url.searchParams.delete('token')
    window.history.replaceState({}, document.title, url.pathname)
  }

  const handleLoginRedirect = () => {
    setShowEmailVerification(false)
    // Clear the token from URL and show auth screen
    const url = new URL(window.location.href)
    url.searchParams.delete('token')
    window.history.replaceState({}, document.title, url.pathname)
    // Force re-authentication check
    window.location.reload()
  }

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 mood-ring mx-auto mb-4 flex items-center justify-center">
            <span className="text-white font-bold text-2xl">M</span>
          </div>
          <p className="text-muted-foreground">Loading MantraPath...</p>
        </div>
      </div>
    )
  }

  // Show auth screen if not authenticated
  if (!isAuthenticated) {
    return (
      <>
        <AuthScreen />
        {showEmailVerification && (
          <EmailVerification
            onClose={handleCloseEmailVerification}
            onLoginRedirect={handleLoginRedirect}
          />
        )}
      </>
    )
  }
  
  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <ModularWellnessDashboard onNavigate={setActiveTab} />
          </motion.div>
        )
      case "insights":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <EnhancedInsightsPage />
          </motion.div>
        )
      case "crisis":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <CrisisDetectionDashboard />
          </motion.div>
        )
      case "achievements":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <AchievementsPage />
          </motion.div>
        )
      case "mood-test":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <MoodTestPage />
          </motion.div>
        )
      case "mood":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <OptimizedMoodPage />
          </motion.div>
        )
      case "journal":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <JournalSection />
          </motion.div>
        )
      case "community":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <EnhancedCommunitySection />
          </motion.div>
        )
      case "voice-testing":
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <VoiceTestingPage />
          </motion.div>
        )
      default:
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <ModularWellnessDashboard onNavigate={setActiveTab} />
          </motion.div>
        )
    }
  }

  return (
    <>
      <SidebarLayout
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onShowChat={() => setShowChat(true)}
        onShowProfile={() => setShowProfile(true)}
        isConnected={isConnected}
        isOfflineMode={isOfflineMode}
      >
        <DevelopmentBanner />
        {import.meta.env.DEV && (
          <div className="mb-4 p-2 rounded border text-xs bg-gray-50 dark:bg-gray-900">
            <div className="flex flex-wrap gap-4">
              <span>WS Status: {isConnected ? '✅ Connected' : '❌ Not Connected'}</span>
              <span>Configured VITE_WS_URL: {String(import.meta.env.VITE_WS_URL || 'AUTO')}</span>
              <span>Total Connections: {connectionStats.totalConnections}</span>
              <span>Healthy: {connectionStats.healthyConnections}</span>
              <span>Failed: {connectionStats.failedConnections}</span>
              <span>Attempted: {hasAttemptedConnection ? 'Yes' : 'No'}</span>
              {connectionError && <span className="text-red-600">Err: {connectionError}</span>}
            </div>
          </div>
        )}
        
        {/* Offline Mode Notice */}
        {isOfflineMode && (
          <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-950 border border-amber-300 dark:border-amber-800 rounded-lg">
            <div className="flex items-start gap-3">
              <div className="mt-1 w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
              <div className="text-sm text-amber-800 dark:text-amber-200 space-y-1">
                <p className="font-medium">Real-time connection unavailable</p>
                {connectionError ? (
                  <p className="text-xs opacity-90">{connectionError}</p>
                ) : (
                  <p className="text-xs opacity-90">Attempting to establish WebSocket connection failed. Background features continue using REST.</p>
                )}
                <div className="flex gap-2 pt-1">
                  <Button size="sm" variant="outline" onClick={() => reconnectAll()}>Retry</Button>
                  <Button size="sm" variant="ghost" onClick={() => window.location.reload()}>Reload</Button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Performance Status Bar */}
        {alerts.length > 0 && (
          <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm text-yellow-800 dark:text-yellow-200">
                Performance Alert: {alerts[0].message}
              </span>
              <span className="text-xs text-yellow-600 dark:text-yellow-400">
                Score: {performanceScore}/100
              </span>
            </div>
          </div>
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            {renderContent()}
          </div>
          
          {/* Desktop chatbot sidebar */}
          {!deviceCapabilities.isMobile && (
            <div className="lg:col-span-1">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="sticky top-0"
              >
                <MinimizableChatBot />
              </motion.div>
            </div>
          )}
        </div>
        
        {/* Mobile minimizable chatbot - always rendered */}
        {deviceCapabilities.isMobile && <MinimizableChatBot />}
      </SidebarLayout>
        
      {/* Profile Dashboard Modal */}
      <AnimatePresence>
        {showProfile && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowProfile(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-background rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <ProfileDashboard onClose={() => setShowProfile(false)} />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>


      
      {/* Sprint 2: Proactive Assistance Panel */}
      <ProactiveAssistancePanel />
      
      <Toaster 
        position="top-right"
        expand={false}
        richColors
        closeButton
      />
    </>
  )
}

function App() {
  return (
    <AuthProvider>
      <RealtimeProvider>
        <AppContent />
      </RealtimeProvider>
    </AuthProvider>
  )
}

export default App