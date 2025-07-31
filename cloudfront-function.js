function handler(event) {
    var request = event.request;
    
    // Handle large file uploads for skin analysis
    if (request.uri === '/api/v2/analyze/guest' && request.method === 'POST') {
        // Set headers to allow larger file uploads
        request.headers['content-length'] = { value: '104857600' }; // 100MB limit
        request.headers['x-upload-size-limit'] = { value: '104857600' };
        
        // Ensure CORS headers are set
        request.headers['access-control-allow-origin'] = { value: 'https://www.shineskincollective.com' };
        request.headers['access-control-allow-methods'] = { value: 'POST, OPTIONS' };
        request.headers['access-control-allow-headers'] = { value: 'Content-Type, Authorization, X-Requested-With' };
        request.headers['access-control-allow-credentials'] = { value: 'true' };
    }
    
    // Handle OPTIONS preflight requests
    if (request.method === 'OPTIONS') {
        return {
            statusCode: 200,
            statusDescription: 'OK',
            headers: {
                'access-control-allow-origin': { value: 'https://www.shineskincollective.com' },
                'access-control-allow-methods': { value: 'POST, OPTIONS' },
                'access-control-allow-headers': { value: 'Content-Type, Authorization, X-Requested-With' },
                'access-control-allow-credentials': { value: 'true' },
                'content-type': { value: 'text/plain' }
            }
        };
    }
    
    return request;
} 