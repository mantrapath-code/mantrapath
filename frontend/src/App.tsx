import { useState, useEffect, useRef, useMemo } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ChatCircle, X, List, House, ChartLine, Brain, Trophy, BookOpen, Users } from "@phosphor-icons/react"
import { JournalSection } from "@/components/journal"
import { ChatBot } from "@/components/chatbot"
import { EnhancedCommunitySection } from "@/components/community"
import { WellnessDashboard } from "@/components/dashboard"
import { RealTimeNotifications } from "@/components/notifications"
import { AuthScreen } from "@/components/auth"
import { EmailVerification } from "@/components/auth"
import { DevelopmentBanner } from "@/components/common"
import { ProfileDropdown, ProfileDashboard } from "@/components/profile"
import { EnhancedInsightsPage } from "@/pages/EnhancedInsightsPage"
import { AchievementsPage } from "@/pages/AchievementsPage"
import { ProactiveAssistancePanel } from "@/components/assistance"
import { AuthProvider, useAuth } from "@/hooks/useAuth"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { useEnhancedWebSocket } from "@/hooks/useEnhancedWebSocket"
import { RealtimeProvider } from "@/contexts/RealtimeContext"
import { useDeviceCapabilities } from "@/hooks/useDeviceCapabilities"
import { useResponsiveLayout, useResponsiveNavigation, useResponsiveInteractions } from "@/hooks/useResponsiveLayout"
import { useTouchGestures } from "@/hooks/useTouchGestures"
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
  const [showMobileMenu, setShowMobileMenu] = useState(false)
  
  // Enhanced device capabilities and responsive layout
  const deviceCapabilities = useDeviceCapabilities()
  const { currentLayout, adaptComponent } = useResponsiveLayout()
  const { navigationType, navigationPosition, isSticky, isCollapsible } = useResponsiveNavigation()
  const { isTouchFriendly, hasGestureSupport, hasHoverEffects } = useResponsiveInteractions()
  
  // Initialize mood-based theme system
  const { currentTheme } = useMoodBasedTheme()
  
  // Initialize enhanced WebSocket connection for real-time features (Sprint 2)
  const { isConnected, connectionError, connectionStats } = useEnhancedWebSocket([], {
    maxConnections: 3,
    heartbeatInterval: 30000,
    reconnectStrategy: {
      maxAttempts: 3,
      baseDelay: 2000,
      backoffMultiplier: 1.5
    }
  })
  
  // Fallback mode when WebSocket is not available
  const isOfflineMode = !import.meta.env.VITE_WS_URL && !isConnected
  
  // Performance monitoring
  const { metrics, alerts, getPerformanceScore } = usePerformanceMonitor()
  
  // Memoize performance score to prevent excessive re-calculations
  const performanceScore = useMemo(() => getPerformanceScore(metrics), [getPerformanceScore, metrics])
  
  // Touch gesture support for mobile navigation
  const mobileMenuRef = useRef<HTMLDivElement>(null)
  
  // Memoize gesture handlers to prevent infinite re-renders
  const gestureHandlers = useMemo(() => ({
    onSwipeLeft: () => setShowMobileMenu(false),
    onSwipeRight: () => setShowMobileMenu(true)
  }), [])
  
  const { isTracking: isGestureTracking } = useTouchGestures(mobileMenuRef as React.RefObject<HTMLElement>, gestureHandlers)

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
  
  return (
    <div className="min-h-screen bg-background">
      <header className={`border-b bg-card/50 backdrop-blur-sm ${isSticky ? 'sticky top-0' : ''} z-40`}>
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-10 h-10 mood-ring flex items-center justify-center">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-2xl font-bold text-foreground">MantraPath</h1>
                <p className="text-sm text-muted-foreground">Welcome back, {user?.username}!</p>
              </div>
              <div className="sm:hidden">
                <h1 className="text-xl font-bold text-foreground">MantraPath</h1>
              </div>
            </motion.div>
            
            {/* Mobile Menu Button */}
            {deviceCapabilities.isMobile && (
              <Button
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                size="sm"
                variant="ghost"
                className="lg:hidden"
              >
                <List size={20} />
              </Button>
            )}
            
            {/* Desktop Actions */}
            <div className="hidden lg:flex items-center gap-3">
              <RealTimeNotifications />
              
              {/* Connection Status Indicator */}
              {!isOfflineMode && (
                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-muted/50">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'}`} />
                  <span className="text-xs text-muted-foreground">
                    {isConnected ? 'Live' : 'Connecting...'}
                  </span>
                </div>
              )}
              
              <Button
                onClick={() => setShowChat(!showChat)}
                size="sm"
                variant={showChat ? "secondary" : "default"}
              >
                <ChatCircle size={16} />
              </Button>
              
              <ProfileDropdown
                user={user!}
                onProfileView={() => setShowProfile(true)}
                onProfileEdit={() => setShowProfile(true)}
                onSettings={() => setShowProfile(true)}
                onLogout={logout}
              />
            </div>
            
            {/* Mobile Actions */}
            <div className="flex lg:hidden items-center gap-2">
              <RealTimeNotifications />
              
              {/* Connection Status Indicator */}
              {!isOfflineMode && (
                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-muted/50">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'}`} />
                  <span className="text-xs text-muted-foreground">
                    {isConnected ? 'Live' : 'Connecting...'}
                  </span>
                </div>
              )}
              
              <Button
                onClick={() => setShowChat(!showChat)}
                size="sm"
                variant={showChat ? "secondary" : "default"}
              >
                <ChatCircle size={16} />
              </Button>
              
              <ProfileDropdown
                user={user!}
                onProfileView={() => setShowProfile(true)}
                onProfileEdit={() => setShowProfile(true)}
                onSettings={() => setShowProfile(true)}
                onLogout={logout}
              />
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-4 py-6 min-h-[calc(100vh-200px)]">
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
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pb-8">
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              {/* Mobile Navigation - Bottom Navigation */}
              {deviceCapabilities.isMobile && (
                <div className="fixed bottom-0 left-0 right-0 bg-background border-t z-30 lg:hidden">
                  <div className="flex justify-around items-center py-2">
                    <button
                      onClick={() => setActiveTab("dashboard")}
                      className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                        activeTab === "dashboard" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <House size={20} />
                      <span className="text-xs mt-1">Dashboard</span>
                    </button>
                    <button
                      onClick={() => setActiveTab("insights")}
                      className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                        activeTab === "insights" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <ChartLine size={20} />
                      <span className="text-xs mt-1">Insights</span>
                    </button>
                    <button
                      onClick={() => setActiveTab("crisis")}
                      className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                        activeTab === "crisis" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <Brain size={20} />
                      <span className="text-xs mt-1">Monitor</span>
                    </button>
                    <button
                      onClick={() => setActiveTab("achievements")}
                      className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                        activeTab === "achievements" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <Trophy size={20} />
                      <span className="text-xs mt-1">Goals</span>
                    </button>
                    <button
                      onClick={() => setActiveTab("journal")}
                      className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                        activeTab === "journal" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <BookOpen size={20} />
                      <span className="text-xs mt-1">Journal</span>
                    </button>
                    <button
                      onClick={() => setActiveTab("community")}
                      className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                        activeTab === "community" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <Users size={20} />
                      <span className="text-xs mt-1">Community</span>
                    </button>
                  </div>
                </div>
              )}
              
              {/* Tablet Navigation - Sidebar */}
              {deviceCapabilities.isTablet && (
                <div className="hidden md:block lg:hidden mb-6">
                  <TabsList className="grid grid-cols-3 w-full">
                    <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                    <TabsTrigger value="insights">Insights</TabsTrigger>
                    <TabsTrigger value="achievements">Goals</TabsTrigger>
                  </TabsList>
                  <TabsList className="grid grid-cols-2 w-full mt-2">
                    <TabsTrigger value="journal">Journal</TabsTrigger>
                    <TabsTrigger value="community">Community</TabsTrigger>
                  </TabsList>
                </div>
              )}
              
              {/* Desktop Navigation - Grid Layout */}
              {deviceCapabilities.isDesktop && (
                <div className="hidden lg:block mb-6">
                  <TabsList className="grid grid-cols-5 w-full">
                    <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                    <TabsTrigger value="insights">Insights</TabsTrigger>
                    <TabsTrigger value="achievements">Achievements</TabsTrigger>
                    <TabsTrigger value="journal">Journal</TabsTrigger>
                    <TabsTrigger value="community">Community</TabsTrigger>
                  </TabsList>
                </div>
              )}
              
              <TabsContent value="dashboard" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <WellnessDashboard />
                </motion.div>
              </TabsContent>

              <TabsContent value="insights" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <EnhancedInsightsPage />
                </motion.div>
              </TabsContent>

              <TabsContent value="achievements" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <AchievementsPage />
                </motion.div>
              </TabsContent>
              
              <TabsContent value="journal" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <JournalSection />
                </motion.div>
              </TabsContent>
              
              <TabsContent value="community" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <EnhancedCommunitySection />
                </motion.div>
              </TabsContent>
            </Tabs>
          </div>
          
          {/* Desktop chatbot sidebar */}
          {deviceCapabilities.isDesktop && (
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
      </div>
      
      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {showMobileMenu && deviceCapabilities.isMobile && (
          <motion.div
            initial={{ opacity: 0, x: -300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -300 }}
            className="fixed inset-y-0 left-0 w-80 bg-background border-r z-50 lg:hidden"
            ref={mobileMenuRef}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold">Menu</h2>
                <Button
                  onClick={() => setShowMobileMenu(false)}
                  size="sm"
                  variant="ghost"
                >
                  <X size={20} />
                </Button>
              </div>
              
              <nav className="space-y-4">
                <button
                  onClick={() => {
                    setActiveTab("dashboard")
                    setShowMobileMenu(false)
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    activeTab === "dashboard" ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <House size={20} />
                  <span>Dashboard</span>
                </button>
                
                <button
                  onClick={() => {
                    setActiveTab("insights")
                    setShowMobileMenu(false)
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    activeTab === "insights" ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <ChartLine size={20} />
                  <span>Insights</span>
                </button>
                
                <button
                  onClick={() => {
                    setActiveTab("crisis")
                    setShowMobileMenu(false)
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    activeTab === "crisis" ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <Brain size={20} />
                  <span>Crisis Monitor</span>
                </button>
                
                <button
                  onClick={() => {
                    setActiveTab("achievements")
                    setShowMobileMenu(false)
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    activeTab === "achievements" ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <Trophy size={20} />
                  <span>Achievements</span>
                </button>
                
                <button
                  onClick={() => {
                    setActiveTab("journal")
                    setShowMobileMenu(false)
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    activeTab === "journal" ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <BookOpen size={20} />
                  <span>Journal</span>
                </button>
                
                <button
                  onClick={() => {
                    setActiveTab("community")
                    setShowMobileMenu(false)
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    activeTab === "community" ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <Users size={20} />
                  <span>Community</span>
                </button>
              </nav>
              
              <div className="mt-8 pt-6 border-t">
                <div className="text-sm text-muted-foreground mb-2">Connection Status</div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : isOfflineMode ? 'bg-gray-500' : 'bg-red-500'}`} />
                  <span className="text-sm">
                    {isConnected ? 'Connected' : isOfflineMode ? 'Offline Mode' : 'Disconnected'}
                  </span>
                </div>
                {connectionStats && connectionStats.totalConnections > 0 && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {connectionStats.healthyConnections}/{connectionStats.totalConnections} connections
                  </div>
                )}
                {isOfflineMode && (
                  <div className="text-xs text-muted-foreground mt-1">
                    Real-time features disabled
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
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
      
      {/* Floating chat button for mobile */}
      {deviceCapabilities.isMobile && !showChat && (
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          className="fixed bottom-24 right-6 z-30 lg:hidden"
        >
          <Button
            onClick={() => setShowChat(true)}
            size="lg"
            className="rounded-full w-14 h-14 shadow-lg"
          >
            <ChatCircle size={24} />
          </Button>
        </motion.div>
      )}
      
      {/* Add bottom padding for mobile devices to account for bottom navigation */}
      {deviceCapabilities.isMobile && (
        <div className="h-20 lg:hidden" />
      )}
      
      {/* Sprint 2: Proactive Assistance Panel */}
      <ProactiveAssistancePanel />
      
      <footer className="border-t bg-card/50 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>MantraPath - Supporting your mental wellness journey, one step at a time. 💜</p>
            <p className="mt-2">Remember: This app complements but doesn't replace professional mental health support.</p>
          </div>
        </div>
      </footer>
      
      <Toaster 
        position="top-right"
        expand={false}
        richColors
        closeButton
      />
    </div>
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