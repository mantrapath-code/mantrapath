// Simple console debug script - paste this in browser console on http://localhost:5173

console.log('=== MantraPath Auth Debug ===');

// Check all auth-related localStorage items
console.log('localStorage items:');
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  if (key && (key.includes('auth') || key.includes('token') || key.includes('user') || key.includes('mantra'))) {
    const value = localStorage.getItem(key);
    console.log(`${key}:`, value?.substring(0, 50) + (value && value.length > 50 ? '...' : ''));
  }
}

// Check specific keys we expect
const expectedKeys = ['mantrapath_token', 'token', 'user', 'auth_user'];
expectedKeys.forEach(key => {
  const value = localStorage.getItem(key);
  console.log(`${key}:`, value ? 'EXISTS' : 'NOT FOUND');
});

// Test if we can make authenticated requests
async function testAuth() {
  const token = localStorage.getItem('mantrapath_token') || localStorage.getItem('token');
  console.log('Using token:', token ? 'Token found' : 'No token');
  
  if (token) {
    try {
      const response = await fetch('http://localhost:8000/forums/challenges', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('Auth test response:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Response data:', data);
      } else {
        const error = await response.text();
        console.log('Error response:', error);
      }
    } catch (error) {
      console.error('Request failed:', error);
    }
  }
}

testAuth();
