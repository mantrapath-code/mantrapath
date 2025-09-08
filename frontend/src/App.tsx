import { useState, useEffect, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { X } from "@phosphor-icons/react"
import { JournalSection } from "@/components/journal"
import { ChatBot } from "@/components/chatbot"
import { EnhancedCommunitySection } from "@/components/community"
import { WellnessDashboard } from "@/components/dashboard"
import { CrisisDetectionDashboard } from "@/components/crisis"
import { AuthScreen } from "@/components/auth"
import { EmailVerification } from "@/components/auth"
import { DevelopmentBanner } from "@/components/common"
import { ProfileDashboard } from "@/components/profile"
import { EnhancedInsightsPage } from "@/pages/EnhancedInsightsPage"
import { AchievementsPage } from "@/pages/AchievementsPage"
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
  
  // Enhanced device capabilities
  const deviceCapabilities = useDeviceCapabilities()
  
  // Initialize mood-based theme system
  const { currentTheme } = useMoodBasedTheme()
  
  // Initialize robust WebSocket connection for real-time features
  const { isConnected, connectionError, connectionStats } = useRobustWebSocket(user?.id, {
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    heartbeatInterval: 30000,
    enableHeartbeat: true
  })
  
  // Fallback mode when WebSocket is not available
  const isOfflineMode = !import.meta.env.VITE_WS_URL && !isConnected
  
  // Performance monitoring
  const { metrics, alerts, getPerformanceScore } = usePerformanceMonitor()
  
  // Memoize performance score to prevent excessive re-calculations
  const performanceScore = useMemo(() => getPerformanceScore(metrics), [getPerformanceScore, metrics])

  // Check for email verification token in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const verificationToken = urlParams.get('token')
    
    if (verificationToken) {
      setShowEmailVerification(true)
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
            <WellnessDashboard />
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
      default:
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <WellnessDashboard />
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
        
        {/* Offline Mode Notice */}
        {isOfflineMode && (
          <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span className="text-sm text-blue-800 dark:text-blue-200">
                Offline Mode: Real-time features are disabled. Set VITE_WS_URL environment variable to enable WebSocket connections.
              </span>
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
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {renderContent()}
          </div>
          
          {/* Desktop chatbot sidebar */}
          {!deviceCapabilities.isMobile && (
            <div className="lg:col-span-1">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="sticky top-32"
              >
                <ChatBot />
              </motion.div>
            </div>
          )}
        </div>
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

      {/* Mobile chatbot overlay */}
      <AnimatePresence>
        {showChat && deviceCapabilities.isMobile && (
          <motion.div
            initial={{ opacity: 0, y: 300 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 300 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end lg:hidden"
            onClick={() => setShowChat(false)}
          >
            <motion.div
              initial={{ opacity: 0, y: 300 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 300 }}
              className="bg-background rounded-t-lg w-full max-h-[80vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-4 border-b">
                <h3 className="text-lg font-semibold">AI Assistant</h3>
                <Button
                  onClick={() => setShowChat(false)}
                  size="sm"
                  variant="ghost"
                >
                  <X size={20} />
                </Button>
              </div>
              <div className="p-4">
                <ChatBot />
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