import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/hooks/useAuth'
import { apiService } from '@/services/api'
import { notificationService } from '@/services/notifications'
import { Eye, EyeSlash, CheckCircle, X, Warning, Envelope } from '@phosphor-icons/react'

export function AuthScreen() {
  const { login, register, verifyEmail, resendVerification } = useAuth()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  const [showVerification, setShowVerification] = useState(false)
  const [verificationEmail, setVerificationEmail] = useState('')
  
  // Login form state
  const [loginData, setLoginData] = useState({
    emailOrUsername: '',
    password: ''
  })
  
  // Register form state
  const [registerData, setRegisterData] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: ''
  })

  // Password strength validation
  const validatePassword = (password: string) => {
    const checks = {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    }
    
    const score = Object.values(checks).filter(Boolean).length
    return { checks, score, isValid: score === 5 }
  }

  const passwordValidation = validatePassword(registerData.password)

  // Check backend connection on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await apiService.request('/health')
        setBackendStatus('connected')
      } catch (error) {
        setBackendStatus('disconnected')
      }
    }
    
    checkBackend()
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!loginData.emailOrUsername || !loginData.password) {
      notificationService.warning('Required Fields', 'Please fill in all required fields')
      return
    }

    try {
      setLoading(true)
      console.log('🔐 Attempting login for:', loginData.emailOrUsername)
      await login(loginData.emailOrUsername, loginData.password)
      notificationService.success('login')
    } catch (error: any) {
      console.error('Login failed:', error)
      notificationService.error(error)
      
      const errorMessage = error.message || 'Failed to login'
      if (errorMessage.includes('verify your email')) {
        setVerificationEmail(loginData.emailOrUsername.includes('@') ? loginData.emailOrUsername : '')
        setShowVerification(true)
      }
      
      // Provide helpful hints for common issues
      if (error.status === 0 || errorMessage.includes('fetch')) {
        notificationService.warning('Backend Offline', 'Unable to connect to the server. Please check your connection and try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!registerData.email || !registerData.username || !registerData.password || !registerData.first_name || !registerData.last_name) {
      notificationService.warning('Required Fields', 'Please fill in all required fields')
      return
    }

    if (!passwordValidation.isValid) {
      notificationService.warning('Password Requirements', 'Please ensure your password meets all requirements')
      return
    }

    try {
      setLoading(true)
      console.log('📝 Attempting registration for:', registerData.email)
      const result = await register(registerData)
      
      if (result.verification_required) {
        notificationService.success('register', { context: result.message })
        setVerificationEmail(registerData.email)
        setShowVerification(true)
      } else {
        notificationService.success('register', { context: 'Registration successful! You can now log in with your credentials.' })
        // Clear the registration form
        setRegisterData({
          email: '',
          username: '',
          password: '',
          first_name: '',
          last_name: ''
        })
      }
    } catch (error: any) {
      console.error('❌ Could not register user:', error)
      
      // Provide helpful feedback for common registration issues
      if (error.message && error.message.includes('already registered')) {
        notificationService.warning('Account Exists', 'This email is already registered. Please try logging in instead.')
      } else {
        notificationService.error(error)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyEmail = async (token: string) => {
    try {
      setLoading(true)
      const result = await verifyEmail(token)
      notificationService.info('Email Verification', result.message)
      setShowVerification(false)
    } catch (error: any) {
      console.error('Email verification failed:', error)
      notificationService.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleResendVerification = async () => {
    if (!verificationEmail) {
      notificationService.warning('Email Required', 'Please provide your email address')
      return
    }

    try {
      setLoading(true)
      const result = await resendVerification(verificationEmail)
      notificationService.info('Verification Email Sent', result.message)
    } catch (error: any) {
      console.error('Resend verification failed:', error)
      notificationService.error(error)
    } finally {
      setLoading(false)
    }
  }

  // Check for verification token in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get('token')
    if (token) {
      handleVerifyEmail(token)
      // Clean the URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])



  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mood-ring mx-auto mb-4 flex items-center justify-center">
            <span className="text-white font-bold text-2xl">M</span>
          </div>
          <h1 className="text-3xl font-bold text-foreground">MantraPath</h1>
          <p className="text-muted-foreground mt-2">Your AI-powered wellness companion</p>
          
          {/* Backend Status Badge */}
          <div className="flex justify-center mt-3">
            {backendStatus === 'checking' && (
              <Badge variant="secondary" className="gap-2">
                <div className="w-2 h-2 bg-current rounded-full animate-pulse" />
                Checking backend...
              </Badge>
            )}
            {backendStatus === 'connected' && (
              <Badge variant="default" className="gap-2 bg-green-600">
                <CheckCircle size={12} />
                Backend Connected
              </Badge>
            )}
            {backendStatus === 'disconnected' && (
              <Badge variant="destructive" className="gap-2">
                <Warning size={12} />
                Backend Offline
              </Badge>
            )}
          </div>
        </div>

        <Card className="backdrop-blur-sm bg-card/80">
          <CardHeader className="space-y-2">
            <CardTitle className="text-2xl text-center">Welcome</CardTitle>
            <CardDescription className="text-center">
              Start your journey to better mental wellness
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login">Login</TabsTrigger>
                <TabsTrigger value="register">Register</TabsTrigger>
              </TabsList>
              
              <TabsContent value="login" className="space-y-4">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email or Username</Label>
                    <Input
                      id="login-email"
                      type="text"
                      placeholder="your@email.com or username"
                      value={loginData.emailOrUsername}
                      onChange={(e) => setLoginData(prev => ({ ...prev, emailOrUsername: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="login-password">Password</Label>
                    <div className="relative">
                      <Input
                        id="login-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={loginData.password}
                        onChange={(e) => setLoginData(prev => ({ ...prev, password: e.target.value }))}
                        required
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeSlash size={16} /> : <Eye size={16} />}
                      </Button>
                    </div>
                  </div>
                  
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? 'Signing in...' : 'Sign In'}
                  </Button>
                </form>
              </TabsContent>
              
              <TabsContent value="register" className="space-y-4">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first-name">First Name *</Label>
                      <Input
                        id="first-name"
                        placeholder="John"
                        value={registerData.first_name}
                        onChange={(e) => setRegisterData(prev => ({ ...prev, first_name: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last-name">Last Name *</Label>
                      <Input
                        id="last-name"
                        placeholder="Doe"
                        value={registerData.last_name}
                        onChange={(e) => setRegisterData(prev => ({ ...prev, last_name: e.target.value }))}
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="register-email">Email</Label>
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="your@email.com"
                      value={registerData.email}
                      onChange={(e) => setRegisterData(prev => ({ ...prev, email: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      placeholder="johndoe"
                      value={registerData.username}
                      onChange={(e) => setRegisterData(prev => ({ ...prev, username: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="register-password">Password</Label>
                    <div className="relative">
                      <Input
                        id="register-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Create a strong password"
                        value={registerData.password}
                        onChange={(e) => setRegisterData(prev => ({ ...prev, password: e.target.value }))}
                        required
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeSlash size={16} /> : <Eye size={16} />}
                      </Button>
                    </div>
                    
                    {/* Password Strength Indicator */}
                    {registerData.password && (
                      <div className="space-y-2 p-3 bg-muted/50 rounded-lg text-sm">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Password Strength:</span>
                          <Badge variant={passwordValidation.score >= 4 ? "default" : passwordValidation.score >= 3 ? "secondary" : "destructive"}>
                            {passwordValidation.score >= 4 ? "Strong" : passwordValidation.score >= 3 ? "Medium" : "Weak"}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-1 gap-1">
                          <div className={`flex items-center gap-2 ${passwordValidation.checks.length ? 'text-green-600' : 'text-muted-foreground'}`}>
                            {passwordValidation.checks.length ? <CheckCircle size={12} /> : <X size={12} />}
                            <span>At least 8 characters</span>
                          </div>
                          <div className={`flex items-center gap-2 ${passwordValidation.checks.lowercase ? 'text-green-600' : 'text-muted-foreground'}`}>
                            {passwordValidation.checks.lowercase ? <CheckCircle size={12} /> : <X size={12} />}
                            <span>Lowercase letter</span>
                          </div>
                          <div className={`flex items-center gap-2 ${passwordValidation.checks.uppercase ? 'text-green-600' : 'text-muted-foreground'}`}>
                            {passwordValidation.checks.uppercase ? <CheckCircle size={12} /> : <X size={12} />}
                            <span>Uppercase letter</span>
                          </div>
                          <div className={`flex items-center gap-2 ${passwordValidation.checks.number ? 'text-green-600' : 'text-muted-foreground'}`}>
                            {passwordValidation.checks.number ? <CheckCircle size={12} /> : <X size={12} />}
                            <span>Number</span>
                          </div>
                          <div className={`flex items-center gap-2 ${passwordValidation.checks.special ? 'text-green-600' : 'text-muted-foreground'}`}>
                            {passwordValidation.checks.special ? <CheckCircle size={12} /> : <X size={12} />}
                            <span>Special character</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? 'Creating account...' : 'Create Account'}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
            
            
            <p className="text-xs text-muted-foreground text-center mt-4">
              By creating an account, you agree to our terms of service and privacy policy.
              MantraPath is designed to complement, not replace, professional mental health care.
            </p>
          </CardContent>
        </Card>
        
        {/* Email Verification Modal */}
        {showVerification && (
          <Card className="mt-6 border-blue-200 bg-blue-50/50">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Envelope className="w-8 h-8 text-blue-600" />
              </div>
              <CardTitle className="text-blue-900">Check Your Email</CardTitle>
              <CardDescription className="text-blue-700">
                We've sent a verification link to {verificationEmail}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-blue-700 text-center">
                Click the link in your email to verify your account and complete registration.
              </p>
              
              <div className="space-y-2">
                <Label htmlFor="verification-email">Didn't receive the email?</Label>
                <div className="flex gap-2">
                  <Input
                    id="verification-email"
                    type="email"
                    placeholder="Enter your email"
                    value={verificationEmail}
                    onChange={(e) => setVerificationEmail(e.target.value)}
                  />
                  <Button 
                    onClick={handleResendVerification}
                    disabled={loading || !verificationEmail}
                    variant="outline"
                  >
                    {loading ? 'Sending...' : 'Resend'}
                  </Button>
                </div>
              </div>
              
              <Button 
                variant="ghost" 
                className="w-full"
                onClick={() => setShowVerification(false)}
              >
                Back to Login
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}