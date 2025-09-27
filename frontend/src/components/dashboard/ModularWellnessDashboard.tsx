import { motion } from "framer-motion"
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
        // TODO: Start voice recording
        toast.info('Voice recording feature coming soon!')
        break
      case 'journal':
        onNavigate('journal')
        toast.success('Opening journal...')
        break
      case 'chat':
        // TODO: Focus on chatbot or open chat
        toast.success('AI companion is available on the right sidebar!')
        break
      default:
        toast.info(`${actionType} feature coming soon!`)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Hero Section - Wellness Overview */}
      <WellnessOverviewCard />
      
      {/* Quick Actions */}
      <QuickActionsGrid onActionClick={handleQuickAction} />
      
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Goals and Current Mood */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CurrentMoodCard onNavigate={onNavigate} />
            <KeyStatsPanel />
          </div>
          
          {/* Goals take full width */}
          <GoalsAndAchievements onNavigate={onNavigate} />
        </div>
        
        {/* Right Column - Could add more widgets here */}
        <div className="space-y-6">
          {/* Placeholder for additional widgets */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="p-6 rounded-lg bg-gradient-to-br from-primary/5 to-secondary/5 border border-dashed border-primary/20 text-center"
          >
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              Coming Soon
            </h3>
            <p className="text-xs text-muted-foreground">
              More wellness insights and personalized recommendations will appear here
            </p>
          </motion.div>
        </div>
      </div>
      
      {/* Footer note about modular design */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-center py-4"
      >
        <p className="text-xs text-muted-foreground">
          ✨ This dashboard is now fully modular and optimized for better performance
        </p>
      </motion.div>
    </div>
  )
}