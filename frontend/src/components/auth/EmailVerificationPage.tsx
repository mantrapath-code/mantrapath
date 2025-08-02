import { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle, XCircle, Envelope } from '@phosphor-icons/react'
import { toast } from 'sonner'

export function EmailVerificationPage() {
  const { verifyEmail } = useAuth()
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleVerification = async () => {
      const urlParams = new URLSearchParams(window.location.search)
      const token = urlParams.get('token')
      
      if (!token) {
        setStatus('error')
        setMessage('Invalid or missing verification token')
        return
      }

      try {
        const result = await verifyEmail(token)
        setStatus('success')
        setMessage(result.message)
        toast.success('Email verified successfully!')
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          window.location.href = '/'
        }, 3000)
      } catch (error: any) {
        setStatus('error')
        setMessage(error.message || 'Verification failed')
        toast.error('Email verification failed')
      }
    }

    handleVerification()
  }, [verifyEmail])

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="text-center">
          <CardHeader>
            <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center">
              {status === 'verifying' && (
                <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              )}
              {status === 'success' && (
                <div className="bg-green-100 w-full h-full rounded-full flex items-center justify-center">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              )}
              {status === 'error' && (
                <div className="bg-red-100 w-full h-full rounded-full flex items-center justify-center">
                  <XCircle className="w-8 h-8 text-red-600" />
                </div>
              )}
            </div>
            
            <CardTitle>
              {status === 'verifying' && 'Verifying Your Email'}
              {status === 'success' && 'Email Verified!'}
              {status === 'error' && 'Verification Failed'}
            </CardTitle>
            
            <CardDescription>
              {status === 'verifying' && 'Please wait while we verify your email address...'}
              {status === 'success' && 'Your email has been successfully verified. You can now log in to your account.'}
              {status === 'error' && message}
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            {status === 'success' && (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  You will be redirected to the login page in a few seconds.
                </p>
                <Button className="w-full" onClick={() => window.location.href = '/'}>
                  Continue to Login
                </Button>
              </div>
            )}
            
            {status === 'error' && (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Please try registering again or contact support if the problem persists.
                </p>
                <Button className="w-full" onClick={() => window.location.href = '/'}>
                  Back to Login
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
