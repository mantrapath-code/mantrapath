import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ChatCircle, X } from "@phosphor-icons/react"
import { MoodTracker } from "@/components/MoodTracker"
import { JournalSection } from "@/components/JournalSection"
import { ChatBot } from "@/components/ChatBot"
import { EnhancedCommunitySection } from "@/components/EnhancedCommunitySection"
import { WellnessDashboard } from "@/components/WellnessDashboard"
import { CrisisPredictionDashboard } from "@/components/CrisisPredictionDashboard"
import { MoodPatternNotifications } from "@/components/MoodPatternNotifications"
import { RealTimeNotifications } from "@/components/RealTimeNotifications"
import { AuthScreen } from "@/components/AuthScreen"
import { EmailVerification } from "@/components/EmailVerification"
import { DevelopmentBanner } from "@/components/DevelopmentBanner"
import { ProfileDropdown, ProfileDashboard } from "@/components/profile"
import { AuthProvider, useAuth } from "@/hooks/useAuth"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { useWebSocket } from "@/hooks/useWebSocket"
import { motion, AnimatePresence } from "framer-motion"
import { Toaster } from "@/components/ui/sonner"
// Import localStorage utilities for debugging
import "@/utils/localStorage"
// Import notification styles
import "./styles/notifications.css"

function AppContent() {
  const { user, logout, isAuthenticated, loading } = useAuth()
  const [activeTab, setActiveTab] = useState("dashboard")
  const [showChat, setShowChat] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [showEmailVerification, setShowEmailVerification] = useState(false)
  
  // Initialize mood-based theme system
  const { currentTheme } = useMoodBasedTheme()
  
  // Initialize WebSocket connection for real-time features
  const { isConnected, connectionError } = useWebSocket()
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Check for email verification token in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const verificationToken = urlParams.get('token')
    
    if (verificationToken) {
      setShowEmailVerification(true)
    }
  }, [])

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
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-10 h-10 mood-ring flex items-center justify-center">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">MantraPath</h1>
                <p className="text-sm text-muted-foreground">Welcome back, {user?.username}!</p>
              </div>
            </motion.div>
            
            <div className="flex items-center gap-3">
              <RealTimeNotifications />
              
              <Button
                onClick={() => setShowChat(!showChat)}
                className="lg:hidden"
                size="sm"
                variant={showChat ? "secondary" : "default"}
              >
                <ChatCircle size={16} />
              </Button>
              
              <ProfileDropdown
                user={user!}
                onProfileView={() => setShowProfile(true)}
                onProfileEdit={() => {
                  setShowProfile(true)
                  // Could set a specific tab here for editing
                }}
                onSettings={() => {
                  setShowProfile(true)
                  // Could set a specific tab here for settings
                }}
                onLogout={logout}
              />
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-4 py-6">
        <DevelopmentBanner />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid grid-cols-5 w-full mb-6">
                <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                <TabsTrigger value="crisis">Crisis Monitor</TabsTrigger>
                <TabsTrigger value="mood">Mood</TabsTrigger>
                <TabsTrigger value="journal">Journal</TabsTrigger>
                <TabsTrigger value="community">Community</TabsTrigger>
              </TabsList>
              
              <TabsContent value="dashboard" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <WellnessDashboard />
                </motion.div>
              </TabsContent>
              
              <TabsContent value="crisis" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <CrisisPredictionDashboard />
                </motion.div>
              </TabsContent>
              
              <TabsContent value="mood" className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <MoodTracker />
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
          {!isMobile && (
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
        {isMobile && showChat && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
              onClick={() => setShowChat(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-4 z-50 lg:hidden rounded-lg overflow-hidden"
            >
              <div className="relative h-full bg-background rounded-lg">
                <Button
                  onClick={() => setShowChat(false)}
                  className="absolute top-4 right-4 z-10"
                  size="sm"
                  variant="ghost"
                >
                  <X size={16} />
                </Button>
                <div className="h-full p-4 pt-16">
                  <ChatBot className="h-full" />
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
      
      {/* Floating chat button for mobile */}
      {isMobile && !showChat && (
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          className="fixed bottom-6 right-6 z-30 lg:hidden"
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
      
      <footer className="border-t bg-card/50 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>MantraPath - Supporting your mental wellness journey, one step at a time. 💜</p>
            <p className="mt-2">Remember: This app complements but doesn't replace professional mental health support.</p>
          </div>
        </div>
      </footer>
      
      {/* Mood Pattern Notifications - Global component */}
      <MoodPatternNotifications />
      
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
      <AppContent />
    </AuthProvider>
  )
}

export default App