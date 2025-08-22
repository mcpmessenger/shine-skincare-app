"use client";

import { useState, useRef } from 'react';
// import { Button } from '@/components/ui/button';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { Badge } from '@/components/ui/badge';
import { Loader2, Camera, Upload, CheckCircle, AlertCircle } from 'lucide-react';

export default function TestAdvanced() {
  const [image, setImage] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const context = canvas.getContext('2d');
      
      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL('image/jpeg');
        setImage(imageData);
        setAnalysis(null);
        setError(null);
      }
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImage(e.target?.result as string);
        setAnalysis(null);
        setError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeImage = async () => {
    if (!image) return;

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const response = await fetch('/api/v6/skin/analyze-advanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: image
        }),
      });

      const result = await response.json();

      if (result.status === 'success') {
        setAnalysis(result);
      } else {
        setError(result.error || 'Analysis failed');
      }
    } catch (err) {
      setError('Failed to connect to analysis service');
    } finally {
      setLoading(false);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError('Failed to access camera');
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Advanced Skin Analysis Test
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300">
          Test our enhanced trained model with your selfies
        </p>
        <div className="flex justify-center gap-2 mt-4">
          {/* <Badge variant="secondary">Model: Advanced_v1.0</Badge> */}
          {/* <Badge variant="secondary">Features: 468 MediaPipe landmarks</Badge> */}
          {/* <Badge variant="secondary">Multi-task Learning</Badge> */}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Image Capture/Upload Section */}
                 <div className="card space-y-4">
          <h3 className="text-xl font-light mb-4">Capture or Upload Image</h3>
          <div className="space-y-2">
            <button onClick={startCamera} className="btn btn-secondary w-full">
              <Camera className="h-5 w-5 mr-2" />
              Start Camera
            </button>
            <div className="relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-64 object-cover rounded-lg border"
              />
              <canvas ref={canvasRef} className="hidden" />
              <button
                onClick={captureImage}
                className="absolute bottom-2 right-2 p-2 bg-white rounded-full shadow-lg"
              >
                <Camera className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="space-y-2">
            <button 
              onClick={() => fileInputRef.current?.click()} 
              className="w-full p-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            >
              <Upload className="h-5 w-5 mr-2" />
              Upload Image
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>

          {/* Analysis Button */}
          {image && (
            <button 
              onClick={analyzeImage} 
              disabled={loading} 
              className="w-full p-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Analyze Image
                </>
              )}
            </button>
          )}
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Model Information</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>Version: {analysis?.model_info?.version || 'Unknown'}</p>
              <p>Processing Time: {analysis?.processing_time_seconds}s</p>
              <p>Features: {analysis?.model_info?.features || 'Unknown'}</p>
            </div>
          </div>

          {/* Analysis Results */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900">Analysis Results</h3>
            
            {error && (
              <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            {analysis && (
              <div className="space-y-4">
                {/* Model Info */}
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2">Model Information</h3>
                  <div className="text-sm text-blue-700 space-y-1">
                    <p>Version: {analysis.model_info?.version || 'Unknown'}</p>
                    <p>Processing Time: {analysis.processing_time_seconds}s</p>
                    <p>Features: {analysis.model_info?.features || 'Unknown'}</p>
                  </div>
                </div>

                {/* Analysis Results */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-gray-900">Analysis Results</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Primary Condition</p>
                      <p className="font-semibold text-gray-900 capitalize">
                        {analysis.result?.primary_condition || 'Unknown'}
                      </p>
                    </div>
                    
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Confidence</p>
                      <p className="font-semibold text-gray-900">
                        {analysis.result?.confidence ? `${(analysis.result.confidence * 100).toFixed(1)}%` : 'Unknown'}
                      </p>
                    </div>
                    
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Severity</p>
                      <p className="font-semibold text-gray-900">
                        {analysis.result?.severity ? analysis.result.severity.toFixed(2) : 'Unknown'}
                      </p>
                    </div>
                    
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Skin Health Score</p>
                      <p className="font-semibold text-gray-900">
                        {analysis.result?.skin_health_score ? (analysis.result.skin_health_score * 100).toFixed(1) : 'Unknown'}
                      </p>
                    </div>
                  </div>

                  {/* Demographic Info */}
                  {analysis.result?.age_group && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <h4 className="font-semibold text-green-900 mb-2">Demographic Analysis</h4>
                      <div className="grid grid-cols-3 gap-2 text-sm text-green-700">
                        <div>
                          <p className="font-medium">Age Group</p>
                          <p className="capitalize">{analysis.result.age_group}</p>
                        </div>
                        <div>
                          <p className="font-medium">Ethnicity</p>
                          <p className="capitalize">{analysis.result.ethnicity}</p>
                        </div>
                        <div>
                          <p className="font-medium">Gender</p>
                          <p className="capitalize">{analysis.result.gender}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Guidance */}
                  {analysis.guidance?.suggestions && (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <h4 className="font-semibold text-yellow-900 mb-2">Recommendations</h4>
                      <ul className="text-sm text-yellow-700 space-y-1">
                        {analysis.guidance.suggestions.map((suggestion: string, index: number) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-yellow-600">•</span>
                            {suggestion}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {!analysis && !error && (
              <div className="text-center text-gray-500 py-8">
                <Camera className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Capture or upload an image to begin analysis</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
