import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Home, 
  TrendingUp, 
  Brain, 
  Trophy, 
  BookOpen, 
  Users, 
  MessageCircle,
  Bell,
  Settings,
  User,
  LogOut,
  Menu,
  X,
  Heart,
  Mic,
  Cpu
} from "lucide-react"
import { 
  Sidebar, 
  SidebarHeader, 
  SidebarContent, 
  SidebarFooter, 
  SidebarItem, 
  SidebarGroup, 
  SidebarToggle 
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { RealTimeNotifications } from "@/components/notifications"
import { useAuth } from "@/hooks/useAuth"
import { useDeviceCapabilities } from "@/hooks/useDeviceCapabilities"

interface SidebarLayoutProps {
  children: React.ReactNode
  activeTab: string
  onTabChange: (tab: string) => void
  onShowChat: () => void
  onShowProfile: () => void
  isConnected?: boolean
  isOfflineMode?: boolean
}

export function SidebarLayout({
  children,
  activeTab,
  onTabChange,
  onShowChat,
  onShowProfile,
  isConnected = false,
  isOfflineMode = false
}: SidebarLayoutProps) {
  const { user, logout } = useAuth()
  const deviceCapabilities = useDeviceCapabilities()
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)

  const navigationItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: <Home size={20} />,
      group: "main"
    },
    {
      id: "insights",
      label: "Insights",
      icon: <TrendingUp size={20} />,
      group: "main"
    },
    {
      id: "services",
      label: "Service Hub",
      icon: <Cpu size={20} />,
      group: "main",
      badge: "AI"
    },
    {
      id: "crisis",
      label: "Crisis Monitor",
      icon: <Brain size={20} />,
      group: "main",
      badge: "AI"
    },
    {
      id: "achievements",
      label: "Achievements",
      icon: <Trophy size={20} />,
      group: "wellness"
    },
    {
      id: "mood",
      label: "Mood Tracker",
      icon: <Heart size={20} />,
      group: "wellness",
      badge: "NEW"
    },
    {
      id: "journal",
      label: "Journal",
      icon: <BookOpen size={20} />,
      group: "wellness"
    },
    {
      id: "voice-testing",
      label: "Voice Testing",
      icon: <Mic size={20} />,
      group: "wellness",
      badge: "TEST"
    },
    {
      id: "community",
      label: "Community",
      icon: <Users size={20} />,
      group: "social"
    }
  ]

  const mainItems = navigationItems.filter(item => item.group === "main")
  const wellnessItems = navigationItems.filter(item => item.group === "wellness")
  const socialItems = navigationItems.filter(item => item.group === "social")

  const SidebarContentComponent = () => (
    <>
      <SidebarHeader>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 mood-ring flex items-center justify-center rounded-lg">
            <span className="text-white font-bold text-sm">M</span>
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg font-bold text-foreground truncate">MantraPath</h1>
            <p className="text-xs text-muted-foreground truncate">
              Welcome, {user?.username}!
            </p>
          </div>
        </div>
        <SidebarToggle />
      </SidebarHeader>

      <SidebarContent>
        <div className="space-y-6">
          {/* Main Navigation */}
          <SidebarGroup title="Main">
            {mainItems.map((item) => (
              <SidebarItem
                key={item.id}
                icon={item.icon}
                label={item.label}
                isActive={activeTab === item.id}
                badge={item.badge}
                onClick={() => {
                  onTabChange(item.id)
                  if (deviceCapabilities.isMobile) {
                    setIsMobileSidebarOpen(false)
                  }
                }}
              />
            ))}
          </SidebarGroup>

          {/* Wellness Tools */}
          <SidebarGroup title="Wellness">
            {wellnessItems.map((item) => (
              <SidebarItem
                key={item.id}
                icon={item.icon}
                label={item.label}
                isActive={activeTab === item.id}
                onClick={() => {
                  onTabChange(item.id)
                  if (deviceCapabilities.isMobile) {
                    setIsMobileSidebarOpen(false)
                  }
                }}
              />
            ))}
          </SidebarGroup>

          {/* Social */}
          <SidebarGroup title="Social">
            {socialItems.map((item) => (
              <SidebarItem
                key={item.id}
                icon={item.icon}
                label={item.label}
                isActive={activeTab === item.id}
                onClick={() => {
                  onTabChange(item.id)
                  if (deviceCapabilities.isMobile) {
                    setIsMobileSidebarOpen(false)
                  }
                }}
              />
            ))}
          </SidebarGroup>

          {/* AI Assistant */}
          <SidebarGroup title="Assistant">
            <SidebarItem
              icon={<MessageCircle size={20} />}
              label="AI Chat"
              onClick={() => {
                onShowChat()
                if (deviceCapabilities.isMobile) {
                  setIsMobileSidebarOpen(false)
                }
              }}
            />
          </SidebarGroup>
        </div>
      </SidebarContent>

      <SidebarFooter>
        <div className="space-y-3">
          {/* Connection Status */}
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-muted/50">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : isOfflineMode ? 'bg-gray-500' : 'bg-red-500'
            }`} />
            <span className="text-xs text-muted-foreground flex-1">
              {isConnected ? 'Connected' : isOfflineMode ? 'Offline' : 'Disconnected'}
            </span>
          </div>

          {/* User Profile */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start gap-3 h-auto p-3">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={''} />
                  <AvatarFallback>
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 text-left min-w-0">
                  <div className="text-sm font-medium truncate">
                    {user?.username || 'User'}
                  </div>
                  <div className="text-xs text-muted-foreground truncate">
                    {user?.email || 'user@example.com'}
                  </div>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem onClick={onShowProfile}>
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-red-600">
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </SidebarFooter>
    </>
  )

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar */}
      {!deviceCapabilities.isMobile && (
        <Sidebar defaultCollapsed={false}>
          <SidebarContentComponent />
        </Sidebar>
      )}

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isMobileSidebarOpen && deviceCapabilities.isMobile && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
              onClick={() => setIsMobileSidebarOpen(false)}
            />
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              className="fixed inset-y-0 left-0 w-80 bg-background border-r z-50 lg:hidden"
            >
              <Sidebar defaultCollapsed={false}>
                <SidebarContentComponent />
              </Sidebar>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        {deviceCapabilities.isMobile && (
          <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-30">
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMobileSidebarOpen(true)}
                >
                  <Menu size={20} />
                </Button>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 mood-ring flex items-center justify-center rounded-lg">
                    <span className="text-white font-bold text-sm">M</span>
                  </div>
                  <h1 className="text-lg font-bold">MantraPath</h1>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <RealTimeNotifications />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onShowChat}
                >
                  <MessageCircle size={20} />
                </Button>
              </div>
            </div>
          </header>
        )}

        {/* Desktop Header */}
        {!deviceCapabilities.isMobile && (
          <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-30">
            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-4">
                <h2 className="text-xl font-semibold capitalize">
                  {navigationItems.find(item => item.id === activeTab)?.label || 'Dashboard'}
                </h2>
                {!isOfflineMode && (
                  <Badge variant="outline" className="text-xs">
                    <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-yellow-500'}`} />
                    {isConnected ? 'Live' : 'Connecting...'}
                  </Badge>
                )}
              </div>
              
              <div className="flex items-center gap-3">
                <RealTimeNotifications />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onShowChat}
                >
                  <MessageCircle size={16} className="mr-2" />
                  AI Assistant
                </Button>
              </div>
            </div>
          </header>
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto px-4 py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}