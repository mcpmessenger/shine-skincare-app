// Test script to verify frontend-backend connection
// Run this in your browser console or as a Node.js script

const BACKEND_URL = 'https://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com';

async function testBackendConnection() {
    console.log('Testing backend connection...');
    
    try {
        // Test health endpoint
        const healthResponse = await fetch(`${BACKEND_URL}/api/health`);
        console.log('Health endpoint status:', healthResponse.status);
        
        if (healthResponse.ok) {
            const healthData = await healthResponse.json();
            console.log('Health endpoint response:', healthData);
        }
        
        // Test trending products endpoint
        const trendingResponse = await fetch(`${BACKEND_URL}/api/recommendations/trending`);
        console.log('Trending endpoint status:', trendingResponse.status);
        
        if (trendingResponse.ok) {
            const trendingData = await trendingResponse.json();
            console.log('Trending endpoint response:', trendingData);
        }
        
        console.log('✅ Backend connection test completed successfully!');
        
    } catch (error) {
        console.error('❌ Backend connection test failed:', error);
    }
}

// Run the test
testBackendConnection(); 