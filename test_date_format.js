// Test script to check date formatting
const API_BASE = 'http://localhost:8000'

async function testDates() {
  try {
    console.log('Fetching forums...')
    const response = await fetch(`${API_BASE}/forums`, {
      headers: {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const forums = await response.json()
    console.log('Forums response:', JSON.stringify(forums, null, 2))
    
    if (forums.length > 0) {
      console.log('\nFetching threads for first forum...')
      const threadsResponse = await fetch(`${API_BASE}/forums/${forums[0].id}/threads`, {
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json'
        }
      })
      
      if (threadsResponse.ok) {
        const threads = await threadsResponse.json()
        console.log('Threads response:', JSON.stringify(threads, null, 2))
        
        if (threads.length > 0) {
          const thread = threads[0]
          console.log('\nAnalyzing date format for first thread:')
          console.log('created_at:', thread.created_at)
          console.log('updated_at:', thread.updated_at)
          
          // Test date parsing
          const createdDate = new Date(thread.created_at)
          const now = new Date()
          const diff = now.getTime() - createdDate.getTime()
          
          console.log('\nDate parsing results:')
          console.log('Parsed date:', createdDate.toISOString())
          console.log('Current time:', now.toISOString())
          console.log('Difference (ms):', diff)
          console.log('Difference (seconds):', Math.floor(diff / 1000))
          console.log('Difference (minutes):', Math.floor(diff / 1000 / 60))
          console.log('Difference (hours):', Math.floor(diff / 1000 / 60 / 60))
        }
      }
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

testDates()
