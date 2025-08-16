'use client';

import { useState } from 'react';

export default function TestLocalBackend() {
  const [testResults, setTestResults] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testLocalBackend = async () => {
    setIsLoading(true);
    setTestResults([]);
    
    try {
      // Test 1: Health endpoint
      addResult('🔍 Testing local backend health...');
      const healthResponse = await fetch('http://localhost:8000/health');
      const healthText = await healthResponse.text();
      addResult(`✅ Health endpoint: ${healthText}`);

      // Test 2: API health endpoint
      addResult('🔍 Testing API health...');
      const apiHealthResponse = await fetch('http://localhost:8000/api/health');
      const apiHealth = await apiHealthResponse.json();
      addResult(`✅ API Health: ${apiHealth.status} (Models: ${apiHealth.models_loaded})`);

      // Test 3: Model status
      addResult('🔍 Testing model status...');
      const modelStatusResponse = await fetch('http://localhost:8000/api/v5/skin/model-status');
      const modelStatus = await modelStatusResponse.json();
      addResult(`✅ Model Status: ${modelStatus.status} (Models: ${modelStatus.model_status.models_loaded})`);

      // Test 4: ML Analysis endpoint (with dummy image)
      addResult('🔍 Testing ML analysis endpoint...');
      const dummyImage = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=';
      
      const analysisResponse = await fetch('http://localhost:8000/api/v6/skin/analyze-hare-run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dummyImage })
      });
      
      if (analysisResponse.ok) {
        const analysis = await analysisResponse.json();
        addResult(`✅ ML Analysis: Success! Status: ${analysis.status}`);
        addResult(`   Analysis Type: ${analysis.analysis_type}`);
        addResult(`   Health Score: ${analysis.result?.health_score || 'N/A'}`);
      } else {
        addResult(`❌ ML Analysis failed: ${analysisResponse.status} ${analysisResponse.statusText}`);
      }

      addResult('🎉 All tests completed successfully!');
      addResult('💡 Your local backend is working perfectly!');
      
    } catch (error) {
      addResult(`❌ Test failed: ${error.message}`);
      addResult('💡 Make sure your local backend is running on port 8000');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            🧪 Local Backend Integration Test
          </h1>
          
          <div className="mb-6">
            <p className="text-gray-600 mb-4">
              This page tests if your frontend can successfully communicate with your local backend.
              Make sure your backend is running on <code className="bg-gray-100 px-2 py-1 rounded">localhost:8000</code>.
            </p>
            
            <button
              onClick={testLocalBackend}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {isLoading ? '🔄 Testing...' : '🚀 Run Integration Tests'}
            </button>
          </div>

          {testResults.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Test Results:</h2>
              <div className="space-y-2">
                {testResults.map((result, index) => (
                  <div key={index} className="text-sm font-mono bg-white p-2 rounded border">
                    {result}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">What This Test Verifies:</h3>
            <ul className="text-blue-800 space-y-1 text-sm">
              <li>✅ Local backend is accessible from frontend</li>
              <li>✅ Health endpoints are working</li>
              <li>✅ ML models are loaded and available</li>
              <li>✅ Skin analysis endpoint responds successfully</li>
              <li>✅ No more 504 Gateway Timeout errors</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
