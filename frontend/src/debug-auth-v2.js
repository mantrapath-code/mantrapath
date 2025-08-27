// Frontend Authentication Debug Script
// Test the authentication flow directly in the browser console

console.log('🔧 MantraPath Frontend Authentication Debug');

// Test environment variables
console.log('Environment Variables:');
console.log('API URL:', import.meta.env.VITE_API_URL);
console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL);

// Test API connection
async function testApiConnection() {
  try {
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    console.log('✅ API Gateway Health:', data);
  } catch (error) {
    console.error('❌ API Gateway connection failed:', error);
  }
}

// Test registration
async function testRegistration() {
  const testUser = {
    email: 'debug@mantrapath.com',
    username: 'debuguser',
    password: 'DebugPass123!',
    first_name: 'Debug',
    last_name: 'User'
  };

  try {
    const response = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testUser),
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Registration successful:', data);
      
      // Store tokens
      if (data.body) {
        const tokenData = JSON.parse(data.body);
        localStorage.setItem('mantrapath_token', tokenData.access_token);
        localStorage.setItem('mantrapath_refresh_token', tokenData.refresh_token);
        console.log('✅ Tokens stored successfully');
      }
    } else {
      console.log('⚠️  Registration response:', data);
    }
  } catch (error) {
    console.error('❌ Registration failed:', error);
  }
}

// Test login
async function testLogin() {
  const loginData = {
    email_or_username: 'debug@mantrapath.com',
    password: 'DebugPass123!'
  };

  try {
    const response = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(loginData),
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Login successful:', data);
      
      // Store tokens
      if (data.body) {
        const tokenData = JSON.parse(data.body);
        localStorage.setItem('mantrapath_token', tokenData.access_token);
        localStorage.setItem('mantrapath_refresh_token', tokenData.refresh_token);
        console.log('✅ Tokens stored successfully');
      }
    } else {
      console.log('⚠️  Login response:', data);
    }
  } catch (error) {
    console.error('❌ Login failed:', error);
  }
}

// Test getting current user
async function testCurrentUser() {
  const token = localStorage.getItem('mantrapath_token');
  
  if (!token) {
    console.log('❌ No token found. Please login first.');
    return;
  }

  try {
    const response = await fetch('http://localhost:8000/me', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Current user data:', data);
    } else {
      console.log('⚠️  Current user response:', data);
    }
  } catch (error) {
    console.error('❌ Get current user failed:', error);
  }
}

// Run tests
console.log('Running authentication tests...');
testApiConnection();

// Export functions for manual testing
window.debugAuth = {
  testApiConnection,
  testRegistration,
  testLogin,
  testCurrentUser,
  clearTokens: () => {
    localStorage.removeItem('mantrapath_token');
    localStorage.removeItem('mantrapath_refresh_token');
    localStorage.removeItem('user_data');
    console.log('✅ Tokens cleared');
  }
};

console.log('Use window.debugAuth.testRegistration(), window.debugAuth.testLogin(), etc. to test manually');
