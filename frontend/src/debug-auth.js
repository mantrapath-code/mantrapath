console.log('=== Frontend Auth Debug ===');

// Test if we can manually set authentication and see if it works
const testAuth = () => {
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNTA2NGYzMy0wNzRhLTQwZGYtYWRlMC1jOTI2NTA4ZGNjY2YiLCJlbWFpbCI6InNhQGdtYWlsLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzU1NDUwNzM3LCJ0eXBlIjoiYWNjZXNzIn0.jDTsGSH_cAzNl5CbiQq8qyFteHSFunEB79sODnWdnlU';
  
  localStorage.setItem('mantrapath_token', token);
  localStorage.setItem('user_data', JSON.stringify({
    id: 'f5064f33-074a-40df-ade0-c926508dcccf',
    email: 'sa@gmail.com',
    username: 'Dev',
    first_name: 'sachin',
    last_name: 'sharma',
    is_active: true,
    is_verified: true,
    role: 'user'
  }));
  
  console.log('🔐 Test auth data set - refresh page to test');
};

// Make it available globally for testing
window.testAuth = testAuth;

console.log('Run window.testAuth() in console to test authentication');
