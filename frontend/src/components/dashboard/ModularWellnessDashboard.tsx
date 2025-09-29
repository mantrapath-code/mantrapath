import { motion } from "framer-motion"
import { Brain } from "lucide-react"
import { WellnessOverviewCard } from "./WellnessOverviewCard"
import { QuickActionsGrid } from "./QuickActionsGrid"
import { GoalsAndAchievements } from "./GoalsAndAchievements"
import { KeyStatsPanel } from "./KeyStatsPanel"
import { CurrentMoodCard } from "./CurrentMoodCard"
import { toast } from "sonner"

interface ModularWellnessDashboardProps {
  onNavigate?: (tab: string) => void
}

export function ModularWellnessDashboard({ onNavigate }: ModularWellnessDashboardProps) {
  
  const handleQuickAction = (actionType: string) => {
    if (!onNavigate) {
      toast.info(`${actionType} feature coming soon!`)
      return
    }

    switch (actionType) {
      case 'mood':
        onNavigate('mood')
        toast.success('Opening mood tracker...')
        break
      case 'voice':
        onNavigate('voice-testing')
        toast.success('Opening voice testing...')
        break
      case 'journal':
        onNavigate('journal')
        toast.success('Opening journal...')
        break
      case 'chat':
        // Scroll to chat section on desktop or show mobile chat
        const chatElement = document.querySelector('[data-chat-widget]')
        if (chatElement) {
          chatElement.scrollIntoView({ behavior: 'smooth' })
          toast.success('AI chat is now focused!')
        } else {
          toast.success('AI companion is available on the right sidebar!')
        }
        break
      default:
        toast.info(`${actionType} feature coming soon!`)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      {/* Hero Section - Wellness Overview */}
      <WellnessOverviewCard />
      
      {/* Quick Actions */}
      <QuickActionsGrid onActionClick={handleQuickAction} />
      
      {/* Main Content Grid - Improved Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Column - Current Mood and Stats */}
        <div className="xl:col-span-2 space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CurrentMoodCard onNavigate={onNavigate} />
            <KeyStatsPanel />
          </div>
          
          {/* Goals take full width on larger screens */}
          <GoalsAndAchievements onNavigate={onNavigate} />
        </div>
        
        {/* Right Column - Additional insights */}
        <div className="space-y-6">
          {/* Quick Tips Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="p-6 rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/50 dark:to-indigo-950/50 border border-blue-200 dark:border-blue-800"
          >
            <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-3 flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Quick Tips
            </h3>
            <ul className="space-y-2 text-xs text-blue-800 dark:text-blue-200">
              <li>• Track your mood daily for better insights</li>
              <li>• Use voice notes for quick emotional capture</li>
              <li>• Journal regularly to process your thoughts</li>
              <li>• Chat with AI when you need support</li>
            </ul>
          </motion.div>
          
          {/* Coming Soon Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="p-6 rounded-lg bg-gradient-to-br from-primary/5 to-secondary/5 border border-dashed border-primary/20 text-center"
          >
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              Coming Soon
            </h3>
            <p className="text-xs text-muted-foreground">
              Personalized wellness recommendations and advanced analytics
            </p>
          </motion.div>
        </div>
      </div>
      
      {/* Footer note */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-center py-4 border-t border-muted"
      >
        <p className="text-xs text-muted-foreground">
          ✨ Your personalized wellness dashboard
        </p>
      </motion.div>
    </div>
  )
}