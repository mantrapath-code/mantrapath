/**
 * Test file to verify notification filtering works correctly
 * Run this in browser console on localhost:5175 to test
 */

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
window.testNotificationFiltering = testNotificationFiltering
window.testSeverityFiltering = testSeverityFiltering
window.testNotifications = testNotifications

console.log('🧪 Notification testing functions loaded!')
console.log('💡 Run testNotificationFiltering() to test the system')
console.log('💡 Run testSeverityFiltering() to see filtering logic')
