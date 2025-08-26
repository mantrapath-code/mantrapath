#!/usr/bin/env node

// Frontend Auth Integration Test
// This script tests the authentication flow from frontend perspective

const API_BASE_URL = 'http://localhost:8000'

async function testAuthFlow() {
  console.log('🔍 Testing Frontend Authentication Integration...\n')
  
  // Test 1: Check API Gateway Health
  console.log('1️⃣ Testing API Gateway Connection...')
  try {
    const healthResponse = await fetch(`${API_BASE_URL}/health`)
    const healthData = await healthResponse.json()
    console.log('✅ API Gateway Health:', healthData)
  } catch (error) {
    console.error('❌ API Gateway Connection Failed:', error.message)
    return
  }
  
  // Test 2: Test Registration
  console.log('\n2️⃣ Testing User Registration...')
  const testUser = {
    email: `test-${Date.now()}@example.com`,
    username: `testuser${Date.now()}`,
    password: 'TestPass123!',
    first_name: 'Frontend',
    last_name: 'Test'
  }
  
  try {
    const registerResponse = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testUser),
    })
    
    if (!registerResponse.ok) {
      const error = await registerResponse.json()
      throw new Error(JSON.stringify(error))
    }
    
    const gatewayResponse = await registerResponse.json()
    
    // Handle API Gateway wrapped response
    let registerData
    if (gatewayResponse.body) {
      registerData = JSON.parse(gatewayResponse.body)
    } else {
      registerData = gatewayResponse
    }
    
    console.log('✅ Registration Success!')
    console.log('   User ID:', registerData.user_id)
    console.log('   Token Type:', registerData.token_type)
    console.log('   Has Access Token:', !!registerData.access_token)
    console.log('   Has Refresh Token:', !!registerData.refresh_token)
    
    // Test 3: Test Login with same credentials
    console.log('\n3️⃣ Testing User Login...')
    const loginResponse = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email_or_username: testUser.email,
        password: testUser.password
      }),
    })
    
    if (!loginResponse.ok) {
      const error = await loginResponse.json()
      throw new Error(JSON.stringify(error))
    }
    
    const gatewayLoginResponse = await loginResponse.json()
    
    // Handle API Gateway wrapped response
    let loginData
    if (gatewayLoginResponse.body) {
      loginData = JSON.parse(gatewayLoginResponse.body)
    } else {
      loginData = gatewayLoginResponse
    }
    
    console.log('✅ Login Success!')
    console.log('   Token Type:', loginData.token_type)
    console.log('   Has Access Token:', !!loginData.access_token)
    console.log('   Has Refresh Token:', !!loginData.refresh_token)
    
    // Test 4: Test Protected Endpoint
    console.log('\n4️⃣ Testing Protected Endpoint Access...')
    const meResponse = await fetch(`${API_BASE_URL}/me`, {
      headers: {
        'Authorization': `Bearer ${loginData.access_token}`,
      },
    })
    
    if (!meResponse.ok) {
      const error = await meResponse.json()
      throw new Error(JSON.stringify(error))
    }
    
    const gatewayMeResponse = await meResponse.json()
    
    // Handle API Gateway wrapped response
    let meData
    if (gatewayMeResponse.body) {
      meData = JSON.parse(gatewayMeResponse.body)
    } else {
      meData = gatewayMeResponse
    }
    
    console.log('✅ Protected Endpoint Access Success!')
    console.log('   User Email:', meData.email)
    console.log('   User Username:', meData.username)
    console.log('   User Role:', meData.role)
    
    // Test 5: Test Token Refresh
    console.log('\n5️⃣ Testing Token Refresh...')
    const refreshResponse = await fetch(`${API_BASE_URL}/refresh-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: loginData.refresh_token
      }),
    })
    
    if (!refreshResponse.ok) {
      const error = await refreshResponse.json()
      throw new Error(JSON.stringify(error))
    }
    
    const gatewayRefreshResponse = await refreshResponse.json()
    
    // Handle API Gateway wrapped response
    let refreshData
    if (gatewayRefreshResponse.body) {
      refreshData = JSON.parse(gatewayRefreshResponse.body)
    } else {
      refreshData = gatewayRefreshResponse
    }
    
    console.log('✅ Token Refresh Success!')
    console.log('   New Token Type:', refreshData.token_type)
    console.log('   Has New Access Token:', !!refreshData.access_token)
    
    console.log('\n🎉 All Authentication Tests Passed!')
    console.log('✅ Frontend can successfully communicate with backend')
    console.log('✅ Registration, Login, Protected Routes, and Token Refresh all working')
    
  } catch (error) {
    console.error('❌ Authentication Test Failed:', error.message)
    console.log('\n🔧 Troubleshooting Tips:')
    console.log('- Check that the API Gateway is running on port 8000')
    console.log('- Check that the Auth Service is running on port 8001')
    console.log('- Verify CORS configuration allows frontend requests')
    console.log('- Check network connectivity between frontend and backend')
  }
}

// Run the test
testAuthFlow().catch(console.error)
