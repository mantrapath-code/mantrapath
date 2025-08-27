// Debug script to check community feed API calls
// Run this in browser console to debug authentication and API calls

console.log('=== Community Feed Debug ===');

// Check localStorage for auth token
const token = localStorage.getItem('token');
console.log('Auth token exists:', !!token);
console.log('Token preview:', token ? token.substring(0, 20) + '...' : 'No token');

// Check if user is logged in
const userStr = localStorage.getItem('user');
const user = userStr ? JSON.parse(userStr) : null;
console.log('User logged in:', !!user);
console.log('User ID:', user?.id);

// Test API endpoints directly
async function testEndpoints() {
  const baseURL = 'http://localhost:8000';
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
  
  console.log('Testing endpoints with headers:', headers);
  
  // Test 1: API Gateway health
  try {
    const healthResponse = await fetch(`${baseURL}/health`);
    console.log('API Gateway health:', healthResponse.status, await healthResponse.text());
  } catch (error) {
    console.error('API Gateway health error:', error);
  }
  
  // Test 2: Forums challenges endpoint
  try {
    const challengesResponse = await fetch(`${baseURL}/forums/challenges`, { headers });
    console.log('Forums challenges:', challengesResponse.status);
    if (challengesResponse.ok) {
      const data = await challengesResponse.json();
      console.log('Challenges data:', data);
    } else {
      console.log('Challenges error:', await challengesResponse.text());
    }
  } catch (error) {
    console.error('Challenges endpoint error:', error);
  }
  
  // Test 3: Forums events endpoint
  try {
    const eventsResponse = await fetch(`${baseURL}/forums/events`, { headers });
    console.log('Forums events:', eventsResponse.status);
    if (eventsResponse.ok) {
      const data = await eventsResponse.json();
      console.log('Events data:', data);
    } else {
      console.log('Events error:', await eventsResponse.text());
    }
  } catch (error) {
    console.error('Events endpoint error:', error);
  }
  
  // Test 4: Check if we can access any community endpoints
  const communityEndpoints = [
    '/community/feed',
    '/community/posts',
    '/community/discussions',
    '/forums/discussions',
    '/forums/posts'
  ];
  
  for (const endpoint of communityEndpoints) {
    try {
      const response = await fetch(`${baseURL}${endpoint}`, { headers });
      console.log(`${endpoint}:`, response.status);
      if (response.ok) {
        const data = await response.json();
        console.log(`${endpoint} data:`, data);
      }
    } catch (error) {
      console.log(`${endpoint} error:`, error.message);
    }
  }
}

testEndpoints();

// Also check WebSocket connection
console.log('WebSocket connection check...');
try {
  const ws = new WebSocket('ws://localhost:8000/ws');
  ws.onopen = () => console.log('WebSocket connected successfully');
  ws.onerror = (error) => console.log('WebSocket error:', error);
  ws.onclose = () => console.log('WebSocket connection closed');
  
  // Close after testing
  setTimeout(() => ws.close(), 2000);
} catch (error) {
  console.log('WebSocket test error:', error);
}
