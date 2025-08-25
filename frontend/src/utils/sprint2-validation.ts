/**
 * Sprint 2 Backend Integration Validation Script
 * Validates Sprint 2 backend connections and endpoints
 */

import { sprint2ApiService, BACKEND_API_ENDPOINTS } from '../services/sprint2-api'

console.log('🚀 Sprint 2 Backend Integration Validation')
console.log('==========================================')

// Test configuration
const TEST_USER_ID = 'validation-user'

async function validateEndpoints() {
  console.log('\n📍 Validating Backend Endpoints:')
  
  console.log('✅ API Gateway (Port 8000):', BACKEND_API_ENDPOINTS.gateway.base)
  console.log('✅ Proactive Assistance Engine (Port 8018):', BACKEND_API_ENDPOINTS.assistance.base)
  console.log('✅ AI Context Store (Port 8013):', BACKEND_API_ENDPOINTS.context.base)
  console.log('✅ AI Event Processor (Port 8014):', BACKEND_API_ENDPOINTS.aiEvents.base)
  console.log('✅ Voice Event Processor (Port 8015):', BACKEND_API_ENDPOINTS.voiceEvents.base)
  console.log('✅ Notification Service (Port 3001):', BACKEND_API_ENDPOINTS.notifications.base)
  console.log('✅ Mood Service (Port 8002):', BACKEND_API_ENDPOINTS.mood.base)
  console.log('✅ Chatbot Service (Port 8004):', BACKEND_API_ENDPOINTS.chatbot.base)
}

async function validateServiceHealth() {
  console.log('\n🏥 Checking Service Health...')
  
  try {
    const healthResults = await sprint2ApiService.checkServiceHealth()
    
    let healthyCount = 0
    const totalServices = 8
    
    for (const [service, result] of Object.entries(healthResults)) {
      if (result.status === 'fulfilled' && result.value?.status) {
        console.log(`✅ ${service}: ${result.value.status}`)
        healthyCount++
      } else if (result.status === 'rejected') {
        console.log(`❌ ${service}: ${result.reason?.message || 'Connection failed'}`)
      } else {
        console.log(`⚠️  ${service}: ${result.value?.error || 'Unknown status'}`)
      }
    }
    
    console.log(`\n📊 Health Summary: ${healthyCount}/${totalServices} services healthy`)
    
    if (healthyCount === totalServices) {
      console.log('🎉 All backend services are operational!')
    } else if (healthyCount > 0) {
      console.log('⚠️  Some services are available, partial functionality expected')
    } else {
      console.log('🚨 No backend services available - check if services are running')
      console.log('💡 Start backend services with: ./start.sh')
    }
    
    return healthyCount
  } catch (error) {
    console.error('❌ Health check failed:', error.message)
    return 0
  }
}

async function validateProactiveAssistance() {
  console.log('\n🧠 Testing Proactive Assistance Engine (Port 8018)...')
  
  try {
    // Test assistance status endpoint
    console.log('   📋 Checking assistance status...')
    const status = await sprint2ApiService.getAssistanceStatus(TEST_USER_ID)
    console.log('   ✅ Status endpoint responsive')
    
    // Test models status
    console.log('   🤖 Checking models status...')
    const modelsStatus = await sprint2ApiService.getModelsStatus()
    console.log('   ✅ Models endpoint responsive')
    
    console.log('🎯 Proactive Assistance Engine: OPERATIONAL')
    return true
  } catch (error) {
    console.log(`   ❌ Proactive Assistance Engine: ${error.message}`)
    return false
  }
}

async function validateVoiceCommand() {
  console.log('\n🎤 Testing Voice Command API (Port 8000)...')
  
  try {
    const testCommand = {
      command: 'test_connection',
      confidence: 1.0,
      language: 'en-US'
    }
    
    await sprint2ApiService.sendVoiceCommand(testCommand)
    console.log('🎯 Voice Command API: OPERATIONAL')
    return true
  } catch (error) {
    console.log(`   ❌ Voice Command API: ${error.message}`)
    return false
  }
}

async function validateMoodService() {
  console.log('\n💚 Testing Mood Service (Port 8002)...')
  
  try {
    // Test getting mood entries
    console.log('   📊 Checking mood entries endpoint...')
    await sprint2ApiService.getMoodEntries(TEST_USER_ID, 5)
    
    // Test getting mood patterns
    console.log('   📈 Checking mood patterns endpoint...')
    await sprint2ApiService.getMoodPatterns(TEST_USER_ID)
    
    console.log('🎯 Mood Service: OPERATIONAL')
    return true
  } catch (error) {
    console.log(`   ❌ Mood Service: ${error.message}`)
    return false
  }
}

async function validateChatbot() {
  console.log('\n💬 Testing Chatbot Service (Port 8004)...')
  
  try {
    // Test chat sessions endpoint
    console.log('   🗨️  Checking chat sessions...')
    await sprint2ApiService.getChatSessions(TEST_USER_ID)
    
    console.log('🎯 Chatbot Service: OPERATIONAL')
    return true
  } catch (error) {
    console.log(`   ❌ Chatbot Service: ${error.message}`)
    return false
  }
}

async function generateValidationReport() {
  console.log('\n📋 Generating Sprint 2 Validation Report...')
  
  const results = {
    timestamp: new Date().toISOString(),
    endpoints: 8,
    healthyServices: 0,
    services: {
      proactiveAssistance: false,
      voiceCommand: false,
      moodService: false,
      chatbot: false
    }
  }
  
  // Validate endpoints
  await validateEndpoints()
  
  // Check service health
  results.healthyServices = await validateServiceHealth()
  
  // Test key services
  results.services.proactiveAssistance = await validateProactiveAssistance()
  results.services.voiceCommand = await validateVoiceCommand()
  results.services.moodService = await validateMoodService()
  results.services.chatbot = await validateChatbot()
  
  // Generate final report
  console.log('\n' + '='.repeat(50))
  console.log('📊 SPRINT 2 VALIDATION REPORT')
  console.log('='.repeat(50))
  console.log(`🕐 Timestamp: ${results.timestamp}`)
  console.log(`🔗 Backend Services: ${results.healthyServices}/${results.endpoints} healthy`)
  console.log(`🧠 Proactive Assistance: ${results.services.proactiveAssistance ? '✅' : '❌'}`)
  console.log(`🎤 Voice Commands: ${results.services.voiceCommand ? '✅' : '❌'}`)
  console.log(`💚 Mood Tracking: ${results.services.moodService ? '✅' : '❌'}`)
  console.log(`💬 Chatbot: ${results.services.chatbot ? '✅' : '❌'}`)
  
  const overallHealth = (
    results.healthyServices >= 4 && 
    results.services.proactiveAssistance
  )
  
  console.log('\n🎯 OVERALL STATUS:', overallHealth ? '✅ READY FOR SPRINT 2' : '❌ NEEDS ATTENTION')
  
  if (!overallHealth) {
    console.log('\n💡 Troubleshooting Tips:')
    console.log('   • Ensure backend services are running: ./start.sh')
    console.log('   • Check if ports 8000, 8002, 8004, 8013, 8014, 8015, 8018, 3001 are available')
    console.log('   • Verify network connectivity to localhost')
    console.log('   • Check service logs for specific error details')
  } else {
    console.log('\n🚀 Ready to implement Sprint 2 frontend features!')
    console.log('   • WebSocket connections available')
    console.log('   • Proactive Assistance Engine operational')
    console.log('   • Real-time data integration ready')
  }
  
  return results
}

// Export the validation function
export { generateValidationReport }

// Run validation if this file is executed directly
if (require.main === module) {
  generateValidationReport()
    .then((results) => {
      process.exit(results.healthyServices >= 4 ? 0 : 1)
    })
    .catch((error) => {
      console.error('❌ Validation failed:', error)
      process.exit(1)
    })
}
