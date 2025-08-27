/**
 * Test file to verify notification filtering works correctly
 * Run this in browser console on localhost:5176 to test
 */

// Debug function to check authentication
function checkAuthStatus() {
  console.log('🔍 Checking authentication status...')
  
  const token = localStorage.getItem('mantrapath_token')
  console.log('Token in localStorage:', token ? 'EXISTS' : 'NOT FOUND')
  
  if (token) {
    try {
      // Decode JWT payload (not verifying signature, just checking content)
      const payload = JSON.parse(atob(token.split('.')[1]))
      console.log('Token payload:', payload)
      console.log('Token expires:', new Date(payload.exp * 1000))
      console.log('Token is expired:', Date.now() > payload.exp * 1000)
    } catch (e) {
      console.log('Invalid token format')
    }
  }
}
  }tication status...')
  
  const token = localStorage.getItem('mantrapath_token')
  console.log('Token in localStorage:', token ? 'EXISTS' : 'NOT FOUND')
  
  if (token) {
    try {
      // Decode JWT payload (not verifying signature, just checking content)
      const payload = JSON.parse(atob(token.split('.')[1]))
      console.log('Token payload:', payload)
      console.log('Token expires:', new Date(payload.exp * 1000))
      console.log('Token is expired:', Date.now() > payload.exp * 1000)
    } catch (e) {
      console.log('Invalid token format')
    }
  }
}

// Debug function to test API calls
async function testChallengeAPI() {
  console.log('🧪 Testing challenge API...')
  
  try {
    const response = await fetch('http://localhost:8000/forums/challenges', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('Response status:', response.status)
    const data = await response.json()
    console.log('Response data:', data)
    
    if (response.ok) {
      console.log('✅ API call successful!')
      return data
    } else {
      console.log('❌ API call failed:', data)
    }
  } catch (error) {
    console.error('❌ Network error:', error)
  }
}

// Function to manually set a test token (updated with longer expiry)
function setTestToken() {
  // Generate a token that expires in 1 hour
  const expiry = Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
  const payload = btoa(JSON.stringify({
    sub: 'test-user-123',
    email: 'test@example.com', 
    exp: expiry
  }))
  
  const testToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' + payload + '._hpRWHGb9i97S5UrFFE0RQ-FoeTtHZU4u3P7wRjVas0'
  localStorage.setItem('mantrapath_token', testToken)
  console.log('✅ Test token set! Refresh the page to use it.')
  console.log('Token expires at:', new Date(expiry * 1000))
}

// Function to trigger dev authentication
async function triggerDevAuth() {
  console.log('🔧 Triggering development authentication...')
  try {
    // Check if ensureDevAuthentication is available
    if (window.ensureDevAuthentication) {
      const result = await window.ensureDevAuthentication()
      console.log('Dev auth result:', result)
    } else {
      console.log('Dev auth function not available. Try logging in manually.')
    }
  } catch (error) {
    console.error('Dev auth failed:', error)
  }
}

// Test notification data
const testNotifications = [
  {
    id: 'test-critical-1',
    type: 'declining-trend',
    category: 'urgent',
    message: 'Your mood has declined significantly over the last 3 days',
    recommendation: 'Consider reaching out for immediate support',
    severity: 'high',
    timestamp: Date.now(),
    confidence: 0.9,
    basedOn: ['3 consecutive declining mood entries']
  },
  {
    id: 'test-medium-1',
    type: 'pattern-alert',
    category: 'preventive',
    message: 'You often experience afternoon energy dips',
    recommendation: 'Try a quick energy boost before your mood drops',
    severity: 'medium',
    timestamp: Date.now() - 60000,
    confidence: 0.7,
    basedOn: ['Historical afternoon patterns']
  },
  {
    id: 'test-low-1',
    type: 'wellness-reminder',
    category: 'supportive',
    message: 'You\'ve been doing great with your mood tracking!',
    recommendation: 'Keep up the excellent work',
    severity: 'low',
    timestamp: Date.now() - 120000,
    confidence: 0.8,
    basedOn: ['Consistent tracking behavior']
  }
]
    timestamp: Date.now() - 120000,
    confidence: 0.8,
    basedOn: ['Consistent tracking behavior']
  }
]

// Function to simulate notification events
function testNotificationFiltering() {
  console.log('🧪 Testing notification filtering...')
  
  // Check if global handler exists
  if (typeof window.handleMoodPatternNotifications === 'function') {
    console.log('✅ Global notification handler found')
    
    // Send test notifications
    window.handleMoodPatternNotifications(testNotifications)
    
    console.log('📤 Sent test notifications:')
    console.log('  - 1 CRITICAL (should appear in dashboard)')
    console.log('  - 1 MEDIUM (should appear in dropdown only)')  
    console.log('  - 1 LOW (should appear in dropdown only)')
    
    // Check notification counts
    setTimeout(() => {
      const bellButton = document.querySelector('[data-testid="notification-bell"]') || 
                        document.querySelector('button[aria-label*="notification"]') ||
                        document.querySelector('button:has(svg)')
      
      if (bellButton) {
        const badge = bellButton.querySelector('.absolute')
        if (badge) {
          console.log(`📊 Notification badge shows: ${badge.textContent}`)
        }
      }
    }, 1000)
    
  } else {
    console.log('❌ Global notification handler not found')
    console.log('💡 Make sure RealTimeNotifications component is mounted')
  }
}

// Function to test severity filtering
function testSeverityFiltering() {
  console.log('🔍 Testing severity-based filtering...')
  
  const criticalOnly = testNotifications.filter(n => 
    n.severity === 'high' && n.category === 'urgent'
  )
  
  const nonCritical = testNotifications.filter(n => 
    !(n.severity === 'high' && n.category === 'urgent')
  )
  
  console.log(`📊 Critical notifications (dashboard): ${criticalOnly.length}`)
  console.log(`📊 Non-critical notifications (dropdown): ${nonCritical.length}`)
  
  criticalOnly.forEach(n => console.log(`  🚨 CRITICAL: ${n.message}`))
  nonCritical.forEach(n => console.log(`  📋 DROPDOWN: ${n.message}`))
}

// Export for console usage
window.checkAuthStatus = checkAuthStatus
window.testChallengeAPI = testChallengeAPI
window.setTestToken = setTestToken
window.triggerDevAuth = triggerDevAuth
window.testCommunityFeedRealTime = testCommunityFeedRealTime
window.testCommunityAPI = testCommunityAPI
window.testNotificationFiltering = testNotificationFiltering
window.testSeverityFiltering = testSeverityFiltering
window.testNotifications = testNotifications

console.log('🧪 Debug functions loaded!')
console.log('💡 Available functions:')
console.log('  - checkAuthStatus() - Check authentication status')
console.log('  - testChallengeAPI() - Test challenge API directly') 
console.log('  - setTestToken() - Set a valid test token')
console.log('  - triggerDevAuth() - Trigger development authentication')
console.log('  - testCommunityFeedRealTime() - Test community feed real-time features')
console.log('  - testCommunityAPI() - Test community API endpoints')
console.log('  - testNotificationFiltering() - Test notification system')
console.log('  - testSeverityFiltering() - Test notification filtering')
console.log('')
console.log('🔍 Run checkAuthStatus() first to see if user is logged in')

// Function to trigger dev authentication
function triggerDevAuth() {
  // Set development token
  setTestToken()
  
  // Trigger a fake login event to update auth state
  window.dispatchEvent(new CustomEvent('auth-change', {
    detail: { 
      user: { id: 'test-user-123', email: 'test@example.com' },
      token: localStorage.getItem('mantrapath_token')
    }
  }))
  
  console.log('✅ Development authentication triggered!')
  console.log('🔄 Refresh the page to see the changes')
}

// Function to test community feed real-time updates
async function testCommunityFeedRealTime() {
  console.log('🧪 Testing Community Feed Real-time Features...')
  
  // Check if feed component is loaded
  const feedElements = document.querySelectorAll('[data-testid*="community"], .community-feed, [class*="community"]')
  if (feedElements.length === 0) {
    console.log('⚠️  Community feed component not found. Make sure you're on the community page.')
    return
  }
  
  // Test WebSocket connection
  console.log('📡 Testing WebSocket connection...')
  const wsConnected = window.localStorage.getItem('ws_connected') === 'true'
  console.log(`WebSocket Status: ${wsConnected ? '✅ Connected' : '❌ Disconnected'}`)
  
  // Test API connectivity for community endpoints
  await testCommunityAPI()
  
  // Simulate real-time updates
  console.log('🔄 Simulating real-time updates...')
  
  // Test like update
  if (typeof window.simulateCommunityUpdate === 'function') {
    window.simulateCommunityUpdate({
      type: 'community_like',
      data: {
        item_id: 'test-item-1',
        user_id: 'test-user-123',
        is_liked: true,
        total_likes: 15
      }
    })
    console.log('✅ Simulated like update')
  }
  
  // Test new post notification
  if (typeof window.simulateCommunityUpdate === 'function') {
    window.simulateCommunityUpdate({
      type: 'community_new_post',
      data: {
        id: 'new-post-' + Date.now(),
        type: 'thread',
        title: 'Real-time Test Post',
        content: 'This is a test post for real-time functionality',
        category: 'general'
      }
    })
    console.log('✅ Simulated new post notification')
  }
  
  console.log('🎯 Real-time test completed!')
}

// Enhanced API testing for community features
async function testCommunityAPI() {
  console.log('🧪 Testing Community API endpoints...')
  
  const endpoints = [
    { path: '/forums/challenges', method: 'GET', description: 'Get challenges' },
    { path: '/forums/threads', method: 'GET', description: 'Get forum threads' },
    { path: '/community/feed', method: 'GET', description: 'Get community feed' },
    { path: '/community/score', method: 'GET', description: 'Get community score' }
  ]
  
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`http://localhost:8000${endpoint.path}`, {
        method: endpoint.method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`,
          'Content-Type': 'application/json'
        }
      })
      
      const status = response.status
      console.log(`${status === 200 ? '✅' : '❌'} ${endpoint.description}: ${status}`)
      
      if (status !== 200) {
        const errorData = await response.text()
        console.log(`   Error: ${errorData}`)
      }
    } catch (error) {
      console.log(`❌ ${endpoint.description}: Network error - ${error.message}`)
    }
  }
}