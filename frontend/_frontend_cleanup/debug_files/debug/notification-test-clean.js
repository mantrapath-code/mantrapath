/**
 * Test file to verify notification filtering and community features work correctly
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
  
  const testToken = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${payload}.test-signature`
  localStorage.setItem('mantrapath_token', testToken)
  console.log('✅ Test token set! Refresh the page to use it.')
}

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
    console.log('⚠️  Community feed component not found. Make sure you are on the community page.')
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

// Export for console usage
window.checkAuthStatus = checkAuthStatus
window.testChallengeAPI = testChallengeAPI
window.setTestToken = setTestToken
window.triggerDevAuth = triggerDevAuth
window.testCommunityFeedRealTime = testCommunityFeedRealTime
window.testCommunityAPI = testCommunityAPI

console.log('🧪 Debug functions loaded!')
console.log('💡 Available functions:')
console.log('  - checkAuthStatus() - Check authentication status')
console.log('  - testChallengeAPI() - Test challenge API directly') 
console.log('  - setTestToken() - Set a valid test token')
console.log('  - triggerDevAuth() - Trigger development authentication')
console.log('  - testCommunityFeedRealTime() - Test community feed real-time features')
console.log('  - testCommunityAPI() - Test community API endpoints')
console.log('')
console.log('🔍 Run checkAuthStatus() first to see if user is logged in')
