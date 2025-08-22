"use client";

import { useState, useRef } from 'react';
// import { Button } from '@/components/ui/button';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { Badge } from '@/components/ui/badge';
import { Loader2, Camera, Upload, CheckCircle, AlertCircle } from 'lucide-react';

export default function TestMedicalGrade() {
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
      const response = await fetch('/api/v6/skin/analyze-medical-grade', {
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
          🔬 Medical Grade Skin Analysis Test
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300">
          Test our 99.15% accurate trained model with your selfies
        </p>
        <div className="flex justify-center gap-2 mt-4">
          {/* <Badge variant="secondary">Model: Medical_Grade_v1.0</Badge> */}
          {/* <Badge variant="secondary">Accuracy: 99.15%</Badge> */}
          {/* <Badge variant="secondary">Features: 478 MediaPipe landmarks</Badge> */}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Image Capture/Upload Section */}
        <div className="space-y-4">
          <div className="space-y-2">
            <button onClick={startCamera} className="w-full p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
              <Camera className="h-6 w-6 mr-2" />
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
                <Camera className="h-6 w-6" />
              </button>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="space-y-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full p-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            >
              <Upload className="h-6 w-6 mr-2" />
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

          {/* Display Captured/Uploaded Image */}
          {image && (
            <div className="space-y-2">
              <img
                src={image}
                alt="Captured/Uploaded"
                className="w-full h-64 object-cover rounded-lg border"
              />
              <button
                onClick={analyzeImage}
                disabled={loading}
                className="w-full p-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-6 w-6 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-6 w-6 mr-2" />
                    Analyze Skin Condition
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Analysis Results Section */}
        <div className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <AlertCircle className="h-6 w-6 text-red-500" />
              <span className="text-red-700 dark:text-red-300">{error}</span>
            </div>
          )}

          {analysis && (
            <div className="space-y-4">
              {/* Model Info */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                  Model Information
                </h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>Version: {analysis.model_info.version}</div>
                  <div>Accuracy: {analysis.model_info.accuracy}</div>
                  <div>Parameters: {analysis.model_info.model_size}</div>
                  <div>Features: {analysis.model_info.features}</div>
                </div>
              </div>

              {/* Analysis Results */}
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                  Analysis Results
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Primary Condition:</span>
                    <span className="font-mono">
                      {analysis.result.primary_condition.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Confidence:</span>
                    <span className="font-mono">{(analysis.result.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Severity:</span>
                    <span className="font-mono">{analysis.result.severity}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Skin Health Score:</span>
                    <span className="font-mono">{analysis.result.skin_health_score}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Processing Time:</span>
                    <span className="font-mono">{analysis.result.processing_time_seconds}s</span>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              {analysis.recommendations && (
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                  <h3 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">
                    Personalized Recommendations
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(analysis.recommendations).map(([category, tips]) => (
                      <div key={category}>
                        <h4 className="font-medium text-purple-800 dark:text-purple-200 capitalize">
                          {category.replace(/_/g, ' ')}:
                        </h4>
                        <ul className="list-disc list-inside text-sm text-purple-700 dark:text-purple-300 ml-4">
                          {Array.isArray(tips) && tips.map((tip, index) => (
                            <li key={index}>{tip}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* API Metadata */}
              <div className="p-4 bg-gray-50 dark:bg-gray-900/20 border border-gray-200 dark:border-gray-800 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  API Metadata
                </h3>
                <div className="text-sm space-y-1">
                  <div>Endpoint: {analysis.api_metadata.endpoint}</div>
                  <div>Timestamp: {new Date(analysis.api_metadata.timestamp).toLocaleString()}</div>
                  <div>Processing Time: {analysis.api_metadata.processing_time}s</div>
                </div>
              </div>
            </div>
          )}

          {!analysis && !error && (
            <div className="text-center text-gray-500 dark:text-gray-400 py-8">
              Capture or upload an image to analyze
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
