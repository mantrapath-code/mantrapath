import { useState } from "react"
import { motion } from "framer-motion"
import { 
  Brain, 
  MessageCircle, 
  Heart,
  Database,
  Cpu,
  Languages,
  ArrowRight,
  TrendingUp,
  Users,
  Sparkles,
  Activity,
  FileText,
  BarChart3,
  Zap
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Import service dashboards
import { ModelsServiceDashboard } from "./models"
import { AIContextStoreDashboard } from "./context"
import { MemoryServiceDashboard } from "./memory"
import { ChatServiceDashboard } from "./chat"
import { EnhancedMoodServiceDashboard } from "./enhanced-mood"

interface ServiceInfo {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  port: number
  status: 'active' | 'inactive' | 'pending'
  version: string
  features: string[]
  color: string
  metrics?: {
    requests_24h?: number
    avg_response_time?: number
    uptime?: number
    error_rate?: number
  }
}

const services: ServiceInfo[] = [
  {
    id: "models",
    name: "AI Models Service",
    description: "Manage and optimize AI models for STT, TTS, and NLP processing",
    icon: <Cpu className="h-6 w-6" />,
    port: 8081,
    status: 'active',
    version: "v1.2.0",
    features: ["Model Download", "Performance Optimization", "Real-time Inference", "Model Analytics"],
    color: "from-blue-500 to-cyan-500",
    metrics: {
      requests_24h: 1247,
      avg_response_time: 185,
      uptime: 99.8,
      error_rate: 0.2
    }
  },
  {
    id: "context",
    name: "AI Context Store",
    description: "Intelligent context aggregation and user behavior analysis",
    icon: <Database className="h-6 w-6" />,
    port: 8013,
    status: 'active',
    version: "v2.1.1",
    features: ["Context Aggregation", "Behavior Analysis", "Real-time Updates", "Smart Recommendations"],
    color: "from-green-500 to-emerald-500",
    metrics: {
      requests_24h: 892,
      avg_response_time: 125,
      uptime: 99.9,
      error_rate: 0.1
    }
  },
  {
    id: "memory",
    name: "Memory Service",
    description: "Behavioral pattern analysis and long-term memory management",
    icon: <Brain className="h-6 w-6" />,
    port: 8017,
    status: 'active',
    version: "v1.8.3",
    features: ["Pattern Recognition", "Memory Indexing", "Behavioral Analytics", "Trend Analysis"],
    color: "from-purple-500 to-violet-500",
    metrics: {
      requests_24h: 634,
      avg_response_time: 210,
      uptime: 99.7,
      error_rate: 0.3
    }
  },
  {
    id: "chat",
    name: "Chat Assistant",
    description: "Advanced conversational AI with emotion detection and mood tracking",
    icon: <MessageCircle className="h-6 w-6" />,
    port: 8004,
    status: 'active',
    version: "v3.0.2",
    features: ["Emotion Detection", "Mood Tracking", "Voice Integration", "Personalized Responses"],
    color: "from-pink-500 to-rose-500",
    metrics: {
      requests_24h: 2156,
      avg_response_time: 340,
      uptime: 99.5,
      error_rate: 0.4
    }
  },
  {
    id: "mood",
    name: "Enhanced Mood Service",
    description: "Advanced mood tracking with AI-powered emotional intelligence",
    icon: <Heart className="h-6 w-6" />,
    port: 8003,
    status: 'active',
    version: "v2.3.0",
    features: ["Emotion AI", "Weather Forecasting", "Mood Analytics", "Personalized Insights"],
    color: "from-orange-500 to-red-500",
    metrics: {
      requests_24h: 1098,
      avg_response_time: 165,
      uptime: 99.6,
      error_rate: 0.2
    }
  }
]

export function ServiceHub() {
  const [selectedService, setSelectedService] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState("overview")

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'inactive': return 'bg-red-500'
      case 'pending': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const renderServiceDashboard = () => {
    switch (selectedService) {
      case 'models':
        return <ModelsServiceDashboard />
      case 'context':
        return <AIContextStoreDashboard />
      case 'memory':
        return <MemoryServiceDashboard />
      case 'chat':
        return <ChatServiceDashboard />
      case 'mood':
        return <EnhancedMoodServiceDashboard />
      default:
        return null
    }
  }

  if (selectedService) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-neutral-1 to-neutral-3">
        <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b">
          <div className="px-6 py-4">
            <Button 
              variant="outline" 
              onClick={() => setSelectedService(null)}
              className="mb-2"
            >
              ← Back to Service Hub
            </Button>
          </div>
        </div>
        {renderServiceDashboard()}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-1 to-neutral-3 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-4">
          MantraPath Service Hub
        </h1>
        <p className="text-lg text-neutral-11 max-w-2xl mx-auto">
          Explore and manage your AI-powered services for emotional wellbeing, 
          conversation, and personal growth
        </p>
      </motion.div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* System Status Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-l-4 border-l-blue-500">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-blue-600" />
                  System Health Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {services.filter(s => s.status === 'active').length}/{services.length}
                    </p>
                    <p className="text-sm text-neutral-11">Services Online</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {services.reduce((acc, s) => acc + (s.metrics?.requests_24h || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-neutral-11">Requests (24h)</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {(services.reduce((acc, s) => acc + (s.metrics?.avg_response_time || 0), 0) / services.length).toFixed(0)}ms
                    </p>
                    <p className="text-sm text-neutral-11">Avg Response</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {(services.reduce((acc, s) => acc + (s.metrics?.uptime || 0), 0) / services.length).toFixed(1)}%
                    </p>
                    <p className="text-sm text-neutral-11">Uptime</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Featured Services */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-2xl font-bold mb-4">Featured Services</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {services.slice(0, 3).map((service, index) => (
                <motion.div
                  key={service.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Card className="h-full hover:shadow-lg transition-all duration-300 cursor-pointer group"
                        onClick={() => setSelectedService(service.id)}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${service.color} text-white`}>
                          {service.icon}
                        </div>
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(service.status)}`}></div>
                          <Badge variant="outline">{service.version}</Badge>
                        </div>
                      </div>
                      <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                        {service.name}
                      </CardTitle>
                      <CardDescription>{service.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex flex-wrap gap-1 mb-3">
                        {service.features.slice(0, 2).map((feature, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {feature}
                          </Badge>
                        ))}
                      </div>
                      <Button variant="ghost" size="sm" className="w-full justify-between group-hover:bg-blue-50">
                        Explore Service
                        <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedService('chat')}>
                <CardContent className="p-4 text-center">
                  <MessageCircle className="h-8 w-8 text-pink-600 mx-auto mb-2" />
                  <h3 className="font-semibold">Start Chat</h3>
                  <p className="text-sm text-neutral-11">Begin a conversation</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedService('mood')}>
                <CardContent className="p-4 text-center">
                  <Heart className="h-8 w-8 text-red-600 mx-auto mb-2" />
                  <h3 className="font-semibold">Track Mood</h3>
                  <p className="text-sm text-neutral-11">Log your feelings</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedService('context')}>
                <CardContent className="p-4 text-center">
                  <Database className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <h3 className="font-semibold">View Context</h3>
                  <p className="text-sm text-neutral-11">Check your insights</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedService('memory')}>
                <CardContent className="p-4 text-center">
                  <Brain className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                  <h3 className="font-semibold">View Patterns</h3>
                  <p className="text-sm text-neutral-11">See behavioral insights</p>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        </TabsContent>

        <TabsContent value="services" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {services.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className="h-full hover:shadow-xl transition-all duration-300 cursor-pointer group"
                      onClick={() => setSelectedService(service.id)}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`p-3 rounded-xl bg-gradient-to-r ${service.color} text-white`}>
                          {service.icon}
                        </div>
                        <div>
                          <CardTitle className="group-hover:text-blue-600 transition-colors">
                            {service.name}
                          </CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline">{service.version}</Badge>
                            <div className="flex items-center gap-1">
                              <div className={`w-2 h-2 rounded-full ${getStatusColor(service.status)}`}></div>
                              <span className="text-xs text-neutral-11 capitalize">{service.status}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </div>
                    <CardDescription className="mt-2">{service.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium mb-2">Key Features</p>
                        <div className="flex flex-wrap gap-1">
                          {service.features.map((feature, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {service.metrics && (
                        <div>
                          <p className="text-sm font-medium mb-2">Performance Metrics</p>
                          <div className="grid grid-cols-2 gap-3 text-sm">
                            <div className="flex justify-between">
                              <span className="text-neutral-11">Requests (24h):</span>
                              <span className="font-semibold">{service.metrics.requests_24h?.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-neutral-11">Response Time:</span>
                              <span className="font-semibold">{service.metrics.avg_response_time}ms</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-neutral-11">Uptime:</span>
                              <span className="font-semibold text-green-600">{service.metrics.uptime}%</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-neutral-11">Error Rate:</span>
                              <span className="font-semibold text-red-600">{service.metrics.error_rate}%</span>
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between pt-2 border-t">
                        <span className="text-sm text-neutral-11">Port: {service.port}</span>
                        <div className="flex items-center gap-1">
                          <Zap className="h-3 w-3 text-green-500" />
                          <span className="text-xs text-green-600 font-medium">Optimized</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Service Analytics Dashboard
              </CardTitle>
              <CardDescription>
                Comprehensive analytics and insights across all MantraPath services
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Sparkles className="h-16 w-16 text-blue-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Advanced Analytics Coming Soon</h3>
                <p className="text-neutral-11 max-w-md mx-auto">
                  We're building comprehensive analytics to help you understand service performance, 
                  user engagement, and system health across all MantraPath services.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}