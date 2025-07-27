import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/hooks/useAuth'
import { apiService } from '@/services/api'
import { toast } from 'sonner'
import { Eye, EyeSlash, CheckCircle, X, Warning } from '@phosphor-icons/react'

export function AuthScreen() {
  const { login, register } = useAuth()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  
  // Login form state
  const [loginData, setLoginData] = useState({
    email: '',
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

  // Check backend connection on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await apiService.healthCheck()
        setBackendStatus('connected')
      } catch (error) {
        setBackendStatus('disconnected')
      }
    }
    
    checkBackend()
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!loginData.email || !loginData.password) {
      toast.error('Please fill in all required fields')
      return
    }

    try {
      setLoading(true)
      console.log('🔐 Attempting login for:', loginData.email)
      await login(loginData.email, loginData.password)
      toast.success('Welcome back!')
    } catch (error: any) {
      console.error('Login failed:', error)
      const errorMessage = error.message || 'Failed to login'
      toast.error(errorMessage)
      
      // Provide helpful hints for common issues
      if (error.status === 0 || errorMessage.includes('fetch')) {
        toast.error('Backend connection issue - using demo mode', {
          description: 'Try the demo account or start the backend services'
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!registerData.email || !registerData.username || !registerData.password) {
      toast.error('Please fill in all required fields')
      return
    }

    if (registerData.password.length < 6) {
      toast.error('Password must be at least 6 characters long')
      return
    }

    try {
      setLoading(true)
      console.log('📝 Attempting registration for:', registerData.email)
      await register(registerData)
      toast.success('Welcome to MantraPath!')
    } catch (error: any) {
      console.error('Registration failed:', error)
      const errorMessage = error.message || 'Failed to create account'
      toast.error(errorMessage)
      
      // Provide helpful hints for common issues
      if (error.status === 0 || errorMessage.includes('fetch')) {
        toast.error('Backend connection issue - using demo mode', {
          description: 'Try the demo account or start the backend services'
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    try {
      setLoading(true)
      console.log('🎯 Attempting demo login...')
      await login('demo@mantrapath.com', 'demo123')
      toast.success('Welcome to the demo!')
    } catch (error: any) {
      console.log('Demo login failed, trying to create demo account...')
      // If demo account doesn't exist, create it
      try {
        await register({
          email: 'demo@mantrapath.com',
          username: 'demo_user',
          password: 'demo123',
          first_name: 'Demo',
          last_name: 'User'
        })
        toast.success('Demo account created! Welcome!')
      } catch (registerError: any) {
        console.error('Demo account creation failed:', registerError)
        toast.error(`Demo access failed: ${registerError.message || 'Unknown error'}`)
      }
    } finally {
      setLoading(false)
    }
  }

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
                Using Demo Mode
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
                    <Label htmlFor="login-email">Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="your@email.com"
                      value={loginData.email}
                      onChange={(e) => setLoginData(prev => ({ ...prev, email: e.target.value }))}
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
                      <Label htmlFor="first-name">First Name</Label>
                      <Input
                        id="first-name"
                        placeholder="John"
                        value={registerData.first_name}
                        onChange={(e) => setRegisterData(prev => ({ ...prev, first_name: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last-name">Last Name</Label>
                      <Input
                        id="last-name"
                        placeholder="Doe"
                        value={registerData.last_name}
                        onChange={(e) => setRegisterData(prev => ({ ...prev, last_name: e.target.value }))}
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
                        placeholder="Create a password (min 6 characters)"
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
                  </div>
                  
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? 'Creating account...' : 'Create Account'}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
            
            <div className="mt-6 relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">Or</span>
              </div>
            </div>
            
            <Button 
              variant="outline" 
              className="w-full mt-4" 
              onClick={handleDemoLogin}
              disabled={loading}
            >
              Try Demo Account
            </Button>
            
            <p className="text-xs text-muted-foreground text-center mt-4">
              By creating an account, you agree to our terms of service and privacy policy.
              MantraPath is designed to complement, not replace, professional mental health care.
            </p>
            
            {/* Backend Instructions for Disconnected State */}
            {backendStatus === 'disconnected' && (
              <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <h4 className="text-sm font-medium text-amber-800 mb-2">🔧 Demo Mode Active</h4>
                <p className="text-xs text-amber-700 mb-2">
                  The backend is not running. You can still explore with demo data.
                </p>
                <details className="text-xs text-amber-600">
                  <summary className="cursor-pointer hover:text-amber-800">Start Backend Services</summary>
                  <div className="mt-2 p-2 bg-amber-100 rounded font-mono text-xs">
                    <div>1. Open terminal in backend directory</div>
                    <div>2. Run: <code>python3 simple_start.py</code></div>
                    <div>3. Or use: <code>./start-backend.sh</code></div>
                    <div>4. Refresh this page</div>
                  </div>
                </details>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}