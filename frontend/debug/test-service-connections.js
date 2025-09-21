/**
 * Test Script to Verify Frontend-Backend Connections
 * This script tests all the service endpoints that the frontend dashboard uses
 */

const services = [
  { name: 'API Gateway', url: 'http://139.84.213.185:8000', port: 8000 },
  { name: 'AI Context Store', url: 'http://localhost:8001', port: 8001 },
  { name: 'AI Event Processor', url: 'http://localhost:8002', port: 8002 },
  { name: 'Voice Processor', url: 'http://localhost:8003', port: 8003 },
  { name: 'Assistance Engine', url: 'http://localhost:8004', port: 8004 },
  { name: 'Translation Service', url: 'http://localhost:8005', port: 8005 },
  { name: 'Notifications', url: 'http://localhost:8006', port: 8006 },
  { name: 'Mood Service', url: 'http://localhost:8007', port: 8007 },
  { name: 'Chatbot Service', url: 'http://localhost:8018', port: 8018 }
];

async function testService(service) {
  try {
    const startTime = Date.now();
    const response = await fetch(`${service.url}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(5000)
    });
    
    const responseTime = Date.now() - startTime;
    const data = await response.json();
    
    return {
      name: service.name,
      status: response.ok ? 'healthy' : 'unhealthy',
      responseTime: responseTime,
      statusCode: response.status,
      data: data
    };
  } catch (error) {
    return {
      name: service.name,
      status: 'error',
      responseTime: 0,
      statusCode: 0,
      error: error.message
    };
  }
}

async function testAllServices() {
  console.log('🔍 Testing Service Connections...\n');
  
  const results = await Promise.all(services.map(testService));
  
  console.log('📊 Service Health Report:');
  console.log('=' .repeat(60));
  
  let healthyCount = 0;
  
  results.forEach(result => {
    const statusIcon = result.status === 'healthy' ? '✅' : 
                      result.status === 'unhealthy' ? '⚠️' : '❌';
    
    console.log(`${statusIcon} ${result.name.padEnd(20)} | ${result.status.padEnd(10)} | ${result.responseTime}ms`);
    
    if (result.status === 'healthy') healthyCount++;
    if (result.error) console.log(`   Error: ${result.error}`);
  });
  
  console.log('=' .repeat(60));
  console.log(`📈 Overall Health: ${healthyCount}/${services.length} services healthy`);
  console.log(`🎯 Success Rate: ${Math.round((healthyCount / services.length) * 100)}%\n`);
  
  // Test specific endpoints that the frontend uses
  console.log('🎯 Testing Specific Frontend Endpoints...\n');
  
  try {
    // Test AI emotion detection endpoint
    const emotionResponse = await fetch('http://localhost:8002/emotion/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: "I'm feeling great today!" })
    });
    console.log(`✅ AI Emotion Detection: ${emotionResponse.ok ? 'Working' : 'Failed'}`);
  } catch (e) {
    console.log(`❌ AI Emotion Detection: Failed - ${e.message}`);
  }
  
  try {
    // Test assistance suggestions endpoint
    const assistanceResponse = await fetch('http://localhost:8004/assistance/suggestions');
    console.log(`✅ Assistance Suggestions: ${assistanceResponse.ok ? 'Working' : 'Failed'}`);
  } catch (e) {
    console.log(`❌ Assistance Suggestions: Failed - ${e.message}`);
  }
  
  try {
    // Test mood analysis endpoint
    const moodResponse = await fetch('http://localhost:8007/mood/current');
    console.log(`✅ Mood Analysis: ${moodResponse.ok ? 'Working' : 'Failed'}`);
  } catch (e) {
    console.log(`❌ Mood Analysis: Failed - ${e.message}`);
  }
}

// Run the tests
testAllServices().catch(console.error);
