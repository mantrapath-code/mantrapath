// Authentication Debug Script
// Paste this into your browser console to check auth status

console.log('=== MantraPath Authentication Debug ===');

// Check if token exists
const token = localStorage.getItem('mantrapath_token');
const refreshToken = localStorage.getItem('mantrapath_refresh_token');

console.log('Access Token:', token ? `${token.substring(0, 50)}...` : 'NOT FOUND');
console.log('Refresh Token:', refreshToken ? `${refreshToken.substring(0, 50)}...` : 'NOT FOUND');

if (token) {
  // Try to decode the JWT to see if it's expired
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const now = Math.floor(Date.now() / 1000);
    const isExpired = payload.exp < now;
    
    console.log('Token Payload:', payload);
    console.log('Token Expires:', new Date(payload.exp * 1000));
    console.log('Current Time:', new Date());
    console.log('Is Expired:', isExpired);
    
    if (isExpired) {
      console.error('❌ TOKEN IS EXPIRED! Please log in again.');
    } else {
      console.log('✅ Token is valid');
    }
  } catch (e) {
    console.error('❌ Invalid token format:', e);
  }
  
  // Test the token with a real API call
  fetch('http://localhost:8000/forums', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('API Test Response Status:', response.status);
    if (response.status === 401 || response.status === 403) {
      console.error('❌ Authentication failed - token is invalid or expired');
    } else if (response.ok) {
      console.log('✅ Authentication successful');
      return response.json();
    }
  })
  .then(data => {
    if (data) {
      console.log('Forums data received:', data);
    }
  })
  .catch(error => {
    console.error('API Test Error:', error);
  });
} else {
  console.error('❌ NO TOKEN FOUND - User needs to log in');
  console.log('💡 Go to the auth screen to log in');
}

// Also check if the auth context is working
if (window.localStorage) {
  console.log('All localStorage keys:', Object.keys(localStorage));
}
