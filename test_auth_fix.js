// Test authentication after fixing token key inconsistency
console.log('=== Testing Authentication Fix ===');

// Clear any existing auth data
localStorage.removeItem('mantrapath_token');
localStorage.removeItem('mantrapath_refresh_token');
localStorage.removeItem('auth_token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('user_data');

console.log('Cleared all existing tokens');

// Test login
async function testLogin() {
  try {
    console.log('Testing login...');
    
    const loginResponse = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email_or_username: 'test@example.com',
        password: 'testpass123'
      }),
    });

    if (loginResponse.ok) {
      const loginData = await loginResponse.json();
      console.log('✅ Login successful:', loginData);
      
      // Store tokens using consistent keys
      localStorage.setItem('mantrapath_token', loginData.access_token);
      localStorage.setItem('mantrapath_refresh_token', loginData.refresh_token);
      
      // Test authenticated API call
      console.log('Testing authenticated API call...');
      
      const moodResponse = await fetch('http://localhost:8000/api/v1/mood/?limit=10', {
        headers: {
          'Authorization': `Bearer ${loginData.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Mood API Response Status:', moodResponse.status);
      
      if (moodResponse.ok) {
        const moodData = await moodResponse.json();
        console.log('✅ Authenticated API call successful:', moodData);
      } else {
        console.error('❌ Authenticated API call failed');
        const errorText = await moodResponse.text();
        console.error('Error:', errorText);
      }
      
    } else {
      console.error('❌ Login failed:', loginResponse.status);
      const errorText = await loginResponse.text();
      console.error('Error:', errorText);
    }
    
  } catch (error) {
    console.error('❌ Network error:', error);
  }
}

// Try to register a test user first, then login
async function testRegisterAndLogin() {
  try {
    console.log('Attempting to register test user...');
    
    const registerResponse = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'test@example.com',
        username: 'testuser',
        password: 'testpass123',
        first_name: 'Test',
        last_name: 'User'
      }),
    });

    if (registerResponse.ok) {
      const registerData = await registerResponse.json();
      console.log('✅ Registration successful:', registerData);
    } else {
      console.log('Registration failed (user may already exist), trying login...');
    }
    
    // Now try login
    await testLogin();
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testRegisterAndLogin();
