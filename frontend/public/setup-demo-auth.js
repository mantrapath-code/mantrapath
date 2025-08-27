// Demo authentication setup for testing
// This simulates a logged-in user for testing purposes

const demoToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNTA2NGYzMy0wNzRhLTQwZGYtYWRlMC1jOTI2NTA4ZGNjY2YiLCJlbWFpbCI6InNhQGdtYWlsLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzU1NDY0MjI5LCJ0eXBlIjoiYWNjZXNzIn0.kpSf99nn-sc3MTwJO5dV8mKcp7NvrN-V6gFCXOnOdGw"
const demoUser = {
  id: "f5064f33-074a-40df-ade0-c926508dcccf",
  email: "sa@gmail.com",
  username: "Dev",
  first_name: "Demo",
  last_name: "User",
  role: "user"
}

// Set authentication data in localStorage
localStorage.setItem('mantrapath_token', demoToken)
localStorage.setItem('user_data', JSON.stringify(demoUser))

console.log('✅ Demo authentication data set')
console.log('🔐 Token:', demoToken.slice(0, 50) + '...')
console.log('👤 User:', demoUser)
