function handler(event) {
    var request = event.request;
    
    // Handle large file uploads for skin analysis
    if (request.uri === '/api/v2/analyze/guest' && request.method === 'POST') {
        // Set headers to allow larger file uploads
        request.headers['content-length'] = { value: '104857600' }; // 100MB limit
        request.headers['x-upload-size-limit'] = { value: '104857600' };
        
        // Remove any existing CORS headers from request to prevent duplication
        delete request.headers['access-control-allow-origin'];
        delete request.headers['access-control-allow-methods'];
        delete request.headers['access-control-allow-headers'];
        delete request.headers['access-control-allow-credentials'];
    }
    
    // Handle OPTIONS preflight requests
    if (request.method === 'OPTIONS') {
        return {
            statusCode: 200,
            statusDescription: 'OK',
            headers: {
                'access-control-allow-origin': { value: 'https://www.shineskincollective.com' },
                'access-control-allow-methods': { value: 'GET, POST, OPTIONS, PUT, DELETE' },
                'access-control-allow-headers': { value: 'Content-Type, Authorization, X-Requested-With, Origin, Accept' },
                'access-control-allow-credentials': { value: 'true' },
                'access-control-max-age': { value: '86400' },
                'content-type': { value: 'text/plain' }
            }
        };
    }
    
    return request;
} 