import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ChatCircle } from "@phosphor-icons/react"
import { MoodTracker } from "@/components/MoodTracker"
import { JournalSection } from "@/components/JournalSection"
import { ChatBot } from "@/components/ChatBot"
import { CommunitySection } from "@/components/CommunitySection"
import { WellnessDashboard } from "@/components/WellnessDashboard"
import { motion } from "framer-motion"

function App() {
  const [activeTab, setActiveTab] = useState("dashboard")
  const [showChat, setShowChat] = useState(false)
  
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
                <p className="text-sm text-muted-foreground">Your wellness companion</p>
              </div>
            </motion.div>
            
            <Button
              onClick={() => setShowChat(!showChat)}
              className="md:hidden"
              size="sm"
            >
              <ChatCircle size={16} />
            </Button>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid grid-cols-4 w-full mb-6">
                <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
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
                  <CommunitySection />
                </motion.div>
              </TabsContent>
            </Tabs>
          </div>
          
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className={`sticky top-24 ${showChat || window.innerWidth >= 1024 ? 'block' : 'hidden'}`}
            >
              <ChatBot />
            </motion.div>
          </div>
        </div>
      </div>
      
      <footer className="border-t bg-card/50 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>MantraPath - Supporting your mental wellness journey, one step at a time. 💜</p>
            <p className="mt-2">Remember: This app complements but doesn't replace professional mental health support.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App