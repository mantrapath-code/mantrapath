import { useState, useEffect, useCallback } from 'react'
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
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login')
  
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
      
      // Enhanced error handling for better user experience
      const errorMessage = error.message || 'Failed to login'
      const errorStatus = error.status || 0
      
      if (errorMessage.includes('verify your email')) {
        setVerificationEmail(loginData.emailOrUsername.includes('@') ? loginData.emailOrUsername : '')
        setShowVerification(true)
        notificationService.warning('Email Verification Required', 'Please verify your email before logging in. Check your inbox for a verification link.')
      } else if (errorStatus === 401) {
        // Handle authentication errors more specifically
        if (errorMessage.toLowerCase().includes('invalid credentials') || 
            errorMessage.toLowerCase().includes('incorrect password') ||
            errorMessage.toLowerCase().includes('wrong password')) {
          notificationService.warning('Invalid Credentials', 'The email/username or password you entered is incorrect. Please check your credentials and try again.')
        } else if (errorMessage.toLowerCase().includes('user not found') || 
                   errorMessage.toLowerCase().includes('does not exist') ||
                   errorMessage.toLowerCase().includes('no account')) {
          notificationService.warning('Account Not Found', 'No account found with these credentials. Please check your email/username or create a new account.')
        } else {
          notificationService.error(error)
        }
      } else if (errorStatus === 0 || errorMessage.includes('fetch')) {
        notificationService.warning('Backend Offline', 'Unable to connect to the server. Please check your connection and try again.')
      } else {
        notificationService.error(error)
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
        // Registration successful - redirect to login with success message
        notificationService.success('register', { context: 'Your account has been created successfully. You can now log in with your credentials.' })
        
        // Clear the registration form
        setRegisterData({
          email: '',
          username: '',
          password: '',
          first_name: '',
          last_name: ''
        })
        
        // Switch to login tab and show success message
        setActiveTab('login')
        
        // Pre-fill the login form with the registered email/username
        setLoginData(prev => ({
          ...prev,
          emailOrUsername: registerData.email
        }))
        
        // Show a helpful message in the login form
        setTimeout(() => {
          notificationService.info('Ready to Login', `Welcome to MantraPath! Please sign in with your email (${registerData.email}) and password.`)
        }, 500)
      }
    } catch (error: any) {
      console.error('❌ Could not register user:', error)
      
      // Enhanced error handling for registration issues
      const errorMessage = error.message || 'Registration failed'
      
      if (errorMessage.toLowerCase().includes('already registered') || 
          errorMessage.toLowerCase().includes('already exists') ||
          errorMessage.toLowerCase().includes('duplicate')) {
        notificationService.warning('Account Already Exists', 'This email is already registered. Please try logging in instead, or use a different email address.')
      } else if (errorMessage.toLowerCase().includes('username') && 
                 errorMessage.toLowerCase().includes('taken')) {
        notificationService.warning('Username Unavailable', 'This username is already taken. Please choose a different username.')
      } else if (errorMessage.toLowerCase().includes('email') && 
                 errorMessage.toLowerCase().includes('invalid')) {
        notificationService.warning('Invalid Email', 'Please enter a valid email address.')
      } else if (errorMessage.toLowerCase().includes('password') && 
                 errorMessage.toLowerCase().includes('weak')) {
        notificationService.warning('Password Too Weak', 'Please create a stronger password that meets our security requirements.')
      } else {
        notificationService.error(error)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyEmail = useCallback(async (token: string) => {
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
  }, [verifyEmail])

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

  // Note: Token verification is now handled in App.tsx



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
            <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'login' | 'register')} className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login">Login</TabsTrigger>
                <TabsTrigger value="register">Register</TabsTrigger>
              </TabsList>
              
              <TabsContent value="login" className="space-y-4">
                {/* Show welcome message for newly registered users */}
                {activeTab === 'login' && loginData.emailOrUsername && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center gap-2 text-green-800">
                      <CheckCircle size={16} />
                      <span className="text-sm font-medium">Welcome! You can now sign in with your credentials.</span>
                    </div>
                  </div>
                )}
                
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
                  
                  {/* Forgot Password Link */}
                  <div className="text-center">
                    <button
                      type="button"
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                      onClick={() => {
                        notificationService.info('Password Recovery', 'Please contact our support team to reset your password, or try logging in with your email address instead of username.')
                      }}
                    >
                      Forgot your password?
                    </button>
                  </div>
                  
                  {/* Login Help */}
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <div className="flex items-start gap-2 text-amber-800">
                      <div className="w-5 h-5 bg-amber-200 rounded-full flex items-center justify-center mt-0.5">
                        <span className="text-xs font-bold">💡</span>
                      </div>
                      <div className="text-sm">
                        <p className="font-medium mb-1">Having trouble logging in?</p>
                        <ul className="text-xs space-y-1">
                          <li>• Try using your email address instead of username</li>
                          <li>• Check if Caps Lock is enabled</li>
                          <li>• Make sure your account is verified</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </form>
              </TabsContent>
              
              <TabsContent value="register" className="space-y-4">
                {/* Registration Tips */}
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start gap-2 text-blue-800">
                    <div className="w-5 h-5 bg-blue-200 rounded-full flex items-center justify-center mt-0.5">
                      <span className="text-xs font-bold">💡</span>
                    </div>
                    <div className="text-sm">
                      <p className="font-medium mb-1">Quick Tips:</p>
                      <ul className="text-xs space-y-1">
                        <li>• Use a strong password with 8+ characters</li>
                        <li>• Choose a unique username that's easy to remember</li>
                        <li>• Verify your email to activate your account</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
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