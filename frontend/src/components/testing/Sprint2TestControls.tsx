/**
 * Sprint 2 Test Controls - Development helper for testing real-time features
 */

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Brain, Heart, Play, TestTube, Users } from '@phosphor-icons/react'
import { useAuth } from '@/hooks/useAuth'
import { sprint2ApiService } from '@/services/sprint2-api'
import { toast } from 'sonner'

export function Sprint2TestControls() {
  const [isLoading, setIsLoading] = useState(false)
  const [lastResponse, setLastResponse] = useState<any>(null)
  const { user } = useAuth()

  const testScenarios = [
    { 
      id: 'wellness_check', 
      name: 'Wellness Check', 
      description: 'Test proactive wellness check assistance',
      icon: Heart,
      color: 'text-green-600'
    },
    { 
      id: 'mood_support', 
      name: 'Mood Support', 
      description: 'Test mood-based assistance trigger',
      icon: Brain,
      color: 'text-blue-600'
    },
    { 
      id: 'crisis_prevention', 
      name: 'Crisis Prevention', 
      description: 'Test high-priority assistance',
      icon: TestTube,
      color: 'text-red-600'
    },
    { 
      id: 'social_connection', 
      name: 'Social Connection', 
      description: 'Test community engagement prompt',
      icon: Users,
      color: 'text-purple-600'
    }
  ]

  const handleTriggerAssistance = async (scenarioId: string) => {
    if (!user) {
      toast.error('Please login first')
      return
    }

    setIsLoading(true)
    try {
      const response = await sprint2ApiService.triggerAssistance(user.id, {
        assistance_type: scenarioId,
        priority: scenarioId === 'crisis_prevention' ? 'high' : 'medium',
        test_mode: true
      })
      
      setLastResponse(response)
      toast.success(`✨ ${scenarioId} assistance triggered!`)
      
      // Also evaluate to get more data
      const evaluation = await sprint2ApiService.evaluateAssistance(user.id, {
        context: `test_scenario_${scenarioId}`
      })
      
      console.log('Assistance evaluation:', evaluation)
      
    } catch (error) {
      console.error('Failed to trigger assistance:', error)
      toast.error('Failed to trigger assistance')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestServiceConnection = async () => {
    if (!user) {
      toast.error('Please login first')
      return
    }

    setIsLoading(true)
    try {
      const results = await Promise.allSettled([
        sprint2ApiService.evaluateAssistance(user.id),
        sprint2ApiService.getAssistanceStatus(user.id),
        sprint2ApiService.getContextRoot(),
        sprint2ApiService.getModelsStatus()
      ])
      
      const [evaluation, status, context, models] = results
      
      console.log('Service test results:', { evaluation, status, context, models })
      
      const successCount = results.filter(r => r.status === 'fulfilled').length
      toast.success(`${successCount}/4 services responding`)
      
    } catch (error) {
      console.error('Service test failed:', error)
      toast.error('Service connection test failed')
    } finally {
      setIsLoading(false)
    }
  }

  if (!user) {
    return (
      <Card className="border-yellow-200 bg-yellow-50">
        <CardContent className="pt-6">
          <p className="text-center text-yellow-800">
            Please login to test Sprint 2 features
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-purple-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-purple-800">
          <TestTube size={20} />
          Sprint 2 Test Controls
          <Badge variant="outline" className="ml-auto">Development</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        
        {/* Service Connection Test */}
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
          <div>
            <h4 className="font-medium">Service Health Check</h4>
            <p className="text-sm text-gray-600">Test all Sprint 2 backend services</p>
          </div>
          <Button 
            onClick={handleTestServiceConnection}
            disabled={isLoading}
            size="sm"
            variant="outline"
          >
            <Play size={14} className="mr-1" />
            Test Services
          </Button>
        </div>

        {/* Assistance Triggers */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-800">Trigger Proactive Assistance</h4>
          <div className="grid grid-cols-1 gap-3">
            {testScenarios.map((scenario) => {
              const IconComponent = scenario.icon
              return (
                <div 
                  key={scenario.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <IconComponent className={scenario.color} size={20} />
                    <div>
                      <div className="font-medium text-sm">{scenario.name}</div>
                      <div className="text-xs text-gray-600">{scenario.description}</div>
                    </div>
                  </div>
                  <Button
                    onClick={() => handleTriggerAssistance(scenario.id)}
                    disabled={isLoading}
                    size="sm"
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Play size={12} className="mr-1" />
                    Trigger
                  </Button>
                </div>
              )
            })}
          </div>
        </div>

        {/* Last Response */}
        {lastResponse && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <h4 className="font-medium text-green-800 mb-2">Last Response</h4>
            <pre className="text-xs text-green-700 overflow-auto max-h-32">
              {JSON.stringify(lastResponse, null, 2)}
            </pre>
          </div>
        )}

        <div className="text-xs text-gray-500 border-t pt-3">
          💡 Use these controls to test real-time assistance features during development. 
          Triggered events should appear in the Proactive Assistance Panel.
        </div>
      </CardContent>
    </Card>
  )
}
