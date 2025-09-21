/**
 * Simple health check and authentication test
 * Run this in the browser console to test connectivity
 */

export async function runHealthCheck() {
  console.log('🏥 Running MantraPath Health Check...')
  
  const results = {
    backendConnectivity: false,
    authentication: false,
    services: {} as Record<string, boolean>
  }

  // 1. Test backend connectivity
  try {
    const { getApiBaseUrl } = await import('@/config/api-config')
    const apiBase = getApiBaseUrl().replace(/\/$/, '')
    const response = await fetch(`${apiBase}/health`)
    if (response.ok) {
      results.backendConnectivity = true
      console.log('✅ Backend connectivity: OK')
    } else {
      console.log('❌ Backend connectivity: Failed')
    }
  } catch (error) {
    console.log('❌ Backend connectivity: Failed', error)
  }

  // 2. Test authentication
  try {
    const { authService } = await import('@/services/auth')
    
    if (!authService.isAuthenticated()) {
      console.log('🔐 No authentication found')
      results.authentication = false
      console.log('❌ Authentication: Not authenticated')
    } else {
      results.authentication = true
      console.log('✅ Authentication: Already authenticated')
    }
  } catch (error) {
    console.log('❌ Authentication test failed:', error)
  }

  // 3. Test individual services
  const servicesToTest = [
    { name: 'auth', path: '/api/auth/health' },
    { name: 'profile', path: '/api/profile/health' },
    { name: 'mood', path: '/api/mood/health' },
    { name: 'chatbot', path: '/api/chatbot/health' },
    { name: 'content', path: '/api/content/health' },
    { name: 'community', path: '/api/community/health' },
    { name: 'notification', path: '/api/notifications/health' },
    { name: 'ml', path: '/api/ml/health' }
  ]

  for (const service of servicesToTest) {
    try {
      const { getApiBaseUrl } = await import('@/config/api-config')
      const apiBase = getApiBaseUrl().replace(/\/$/, '')
      const response = await fetch(`${apiBase}${service.path}`)
      results.services[service.name] = response.ok
      console.log(`${response.ok ? '✅' : '❌'} ${service.name} service: ${response.ok ? 'OK' : 'DOWN'}`)
    } catch (error) {
      results.services[service.name] = false
      console.log(`❌ ${service.name} service: DOWN`)
    }
  }

  // 4. Test API with authentication
  if (results.authentication) {
    try {
      const { apiService } = await import('@/services/api')
      apiService.refreshToken()
      
      // Test a simple API call
      const baseUrl = import.meta.env.VITE_API_GATEWAY_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${baseUrl}/api/profiles/me`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`,
          'Content-Type': 'application/json'
        }
      })
      
      console.log(`🔗 Authenticated API test: ${response.ok ? 'SUCCESS' : 'FAILED'} (${response.status})`)
    } catch (error) {
      console.log('❌ Authenticated API test failed:', error)
    }
  }

  // Summary
  console.log('\n📊 Health Check Summary:')
  console.log('=' .repeat(40))
  console.log(`Backend: ${results.backendConnectivity ? '✅ UP' : '❌ DOWN'}`)
  console.log(`Auth: ${results.authentication ? '✅ OK' : '❌ FAILED'}`)
  console.log('Services:')
  Object.entries(results.services).forEach(([name, status]) => {
    console.log(`  ${name}: ${status ? '✅ UP' : '❌ DOWN'}`)
  })
  
  return results
}

// Make it available globally for browser console
declare global {
  interface Window {
    runHealthCheck: () => Promise<any>
  }
}

if (typeof window !== 'undefined') {
  window.runHealthCheck = runHealthCheck
}

// Auto-run in development
if (import.meta.env.DEV) {
  setTimeout(() => {
    runHealthCheck()
  }, 3000)
}
