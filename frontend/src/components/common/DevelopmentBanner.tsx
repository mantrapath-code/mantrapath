import { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { X, Info, CheckCircle } from '@phosphor-icons/react'
import { apiService } from '@/services/api'

export function DevelopmentBanner() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'available' | 'unavailable'>('checking')
  const [isDismissed, setIsDismissed] = useState(false)

  useEffect(() => {
    const checkBackend = async () => {
      try {
        await apiService.healthCheck()
        setBackendStatus('available')
      } catch (error) {
        setBackendStatus('unavailable')
      }
    }

    checkBackend()
    
    // Check periodically in case backend comes online
    const interval = setInterval(checkBackend, 30000) // Every 30 seconds
    
    return () => clearInterval(interval)
  }, [])

  if (isDismissed || backendStatus === 'checking') {
    return null
  }

  return (
    <div className="relative">
      {backendStatus === 'unavailable' && (
        <Alert className="border-amber-200 bg-amber-50 text-amber-800 mb-4">
          <Info className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <div className="flex-1">
              <strong>Backend Unavailable:</strong> Cannot connect to MantraPath services.
              <br />
              <span className="text-sm">
                Please ensure backend services are running: <code className="bg-amber-100 px-1 rounded">./start.sh</code>
                <br />
                Check network connection and verify services are accessible.
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsDismissed(true)}
              className="ml-4 h-auto p-1"
            >
              <X className="h-4 w-4" />
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {backendStatus === 'available' && (
        <Alert className="border-green-200 bg-green-50 text-green-800 mb-4">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <div>
              <strong>Backend Connected:</strong> All features are fully functional.
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsDismissed(true)}
              className="ml-4 h-auto p-1"
            >
              <X className="h-4 w-4" />
            </Button>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}