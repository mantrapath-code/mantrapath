import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, XCircle, Mail, Loader2 } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { toast } from 'sonner'

interface EmailVerificationProps {
  onClose: () => void
  onLoginRedirect: () => void
}

export function EmailVerification({ onClose, onLoginRedirect }: EmailVerificationProps) {
  const { verifyEmail, resendVerification } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'expired'>('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [resendEmail, setResendEmail] = useState('')
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    // Get token from URL parameters
    const urlParams = new URLSearchParams(window.location.search)
    const tokenFromUrl = urlParams.get('token')
    
    if (!tokenFromUrl) {
      setStatus('error')
      setErrorMessage('Invalid verification link. No token provided.')
      return
    }

    setToken(tokenFromUrl)

    const handleVerification = async () => {
      try {
        const result = await verifyEmail(tokenFromUrl)
        setStatus('success')
        toast.success(result.message)
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          onLoginRedirect()
        }, 3000)
      } catch (error: any) {
        console.error('Email verification failed:', error)
        const errorMsg = error.message || 'Verification failed'
        
        if (errorMsg.includes('expired')) {
          setStatus('expired')
        } else {
          setStatus('error')
        }
        setErrorMessage(errorMsg)
        toast.error(errorMsg)
      }
    }

    handleVerification()
  }, [verifyEmail, onLoginRedirect])

  const handleResendVerification = async () => {
    if (!resendEmail) {
      toast.error('Please enter your email address')
      return
    }

    try {
      const result = await resendVerification(resendEmail)
      toast.success(result.message)
    } catch (error: any) {
      toast.error(error.message || 'Failed to resend verification email')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-md space-y-6 bg-background rounded-lg">
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto mb-4">
              {status === 'loading' && (
                <Loader2 className="h-12 w-12 text-primary animate-spin" />
              )}
              {status === 'success' && (
                <CheckCircle className="h-12 w-12 text-green-600" />
              )}
              {(status === 'error' || status === 'expired') && (
                <XCircle className="h-12 w-12 text-red-600" />
              )}
            </div>
            
            <CardTitle>
              {status === 'loading' && 'Verifying Email...'}
              {status === 'success' && 'Email Verified!'}
              {status === 'error' && 'Verification Failed'}
              {status === 'expired' && 'Link Expired'}
            </CardTitle>
            
            <CardDescription>
              {status === 'loading' && 'Please wait while we verify your email address.'}
              {status === 'success' && 'Your email has been successfully verified. You will be redirected to login shortly.'}
              {status === 'error' && 'There was a problem verifying your email address.'}
              {status === 'expired' && 'Your verification link has expired. Please request a new one.'}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {status === 'success' && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  You can now log in to your MantraPath account and start your wellness journey!
                </AlertDescription>
              </Alert>
            )}

            {(status === 'error' || status === 'expired') && (
              <>
                <Alert className="border-red-200 bg-red-50">
                  <XCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    {errorMessage}
                  </AlertDescription>
                </Alert>

                {status === 'expired' && (
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label htmlFor="resend-email" className="text-sm font-medium">
                        Email Address
                      </label>
                      <input
                        id="resend-email"
                        type="email"
                        placeholder="Enter your email address"
                        value={resendEmail}
                        onChange={(e) => setResendEmail(e.target.value)}
                        className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                    <Button 
                      onClick={handleResendVerification} 
                      className="w-full"
                      variant="outline"
                    >
                      <Mail className="h-4 w-4 mr-2" />
                      Send New Verification Email
                    </Button>
                  </div>
                )}
              </>
            )}

            <div className="space-y-2">
              <Button 
                onClick={onLoginRedirect} 
                className="w-full"
                variant={status === 'success' ? 'default' : 'outline'}
              >
                Go to Login
              </Button>
              
              <Button 
                onClick={onClose} 
                variant="ghost" 
                className="w-full"
              >
                Close
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="text-center p-4">
          <p className="text-xs text-muted-foreground">
            Need help? Contact support at{' '}
            <a href="mailto:support@mantrapath.com" className="text-primary hover:underline">
              support@mantrapath.com
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
