#!/usr/bin/env node
/**
 * Test script to check backend connection
 */

const http = require('http');

async function testBackendConnection() {
  const endpoints = [
    { url: 'http://localhost:8000', name: 'API Gateway' },
    { url: 'http://localhost:8001', name: 'Auth Service' },
    { url: 'http://localhost:8003', name: 'Mood Service' },
  ];

  console.log('🔍 Testing backend connections...\n');

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${endpoint.url}/health`);
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ ${endpoint.name}: Connected (${endpoint.url})`);
        console.log(`   Status: ${data.status || 'OK'}`);
      } else {
        console.log(`❌ ${endpoint.name}: Not responding (${endpoint.url})`);
      }
    } catch (error) {
      console.log(`❌ ${endpoint.name}: Connection failed (${endpoint.url})`);
      console.log(`   Error: ${error.message}`);
    }
  }

  console.log('\n📋 To start the backend services:');
  console.log('   cd backend');
  console.log('   python3 simple_start.py');
  console.log('   # OR use the startup script');
  console.log('   ./start-backend.sh');
}

// Run the test
testBackendConnection().catch(console.error);