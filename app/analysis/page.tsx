'use client';

import { useAnalysis } from '../contexts/AnalysisContext';
import { ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function AnalysisPage() {
  const { analysisData } = useAnalysis();

  if (!analysisData.analysisResults) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">No Analysis Data</h1>
              <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
                Please complete a skin analysis first to view your results.
              </p>
              <Link 
                href="/"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start New Analysis
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">Your Skin Analysis Results</h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              AI-powered analysis with Hare Run V6 Enhanced ML
            </p>
          </div>
          
          {/* Face Thumbnail Section */}
          {analysisData.croppedFaceImage && (
            <div className="mb-8 p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Analyzed Region</h2>
              <div className="flex flex-col md:flex-row justify-center items-center space-y-6 md:space-y-0 md:space-x-8">
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Original Image</p>
                  <img
                    src={analysisData.originalImage!}
                    alt="Original uploaded photo"
                    className="w-40 h-40 object-cover rounded-lg border-2 border-gray-300 shadow-md"
                  />
                </div>
                <ArrowRight className="w-8 h-8 text-gray-400 hidden md:block" />
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Analyzed Face Region</p>
                  <img
                    src={analysisData.croppedFaceImage}
                    alt="Cropped face region"
                    className="w-40 h-40 object-cover rounded-lg border-2 border-green-500 shadow-md"
                  />
                  <p className="text-sm text-green-600 mt-2 font-medium">
                    Detection Confidence: {Math.round(analysisData.faceConfidence * 100)}%
                  </p>
                </div>
              </div>
              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-blue-800 dark:text-blue-200 text-center">
                  ✓ This specific face region was analyzed for skin conditions and used to generate your personalized product recommendations.
                </p>
              </div>
            </div>
          )}
          
          {/* Analysis Results Section */}
          <div className="mb-8 p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Skin Analysis Results</h2>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">Model Information</h3>
                  <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                    <p><span className="font-medium">Version:</span> {analysisData.analysisResults.model_version || 'Hare Run V6'}</p>
                    <p><span className="font-medium">Type:</span> {analysisData.analysisResults.model_type || 'Enhanced Facial ML'}</p>
                    <p><span className="font-medium">Accuracy:</span> {analysisData.analysisResults.accuracy || '97.13%'}</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">Analysis Details</h3>
                  <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                    <p><span className="font-medium">Status:</span> <span className="text-green-600">✓ Complete</span></p>
                    <p><span className="font-medium">Face Detected:</span> <span className="text-green-600">✓ Yes</span></p>
                    <p><span className="font-medium">Confidence:</span> {Math.round(analysisData.faceConfidence * 100)}%</p>
                  </div>
                </div>
              </div>
              
              {/* Raw Analysis Data */}
              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                  View Raw Analysis Data
                </summary>
                <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-800 rounded text-xs text-gray-800 dark:text-gray-200 overflow-auto max-h-64">
                  {JSON.stringify(analysisData.analysisResults, null, 2)}
                </pre>
              </details>
            </div>
          </div>
          
          {/* Product Recommendations Section */}
          <div className="mb-8 p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Recommended Products</h2>
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Product recommendations are being generated based on your analysis...
              </p>
              <Link 
                href="/suggestions"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Product Suggestions
              </Link>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/"
              className="inline-flex items-center justify-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              New Analysis
            </Link>
            <Link 
              href="/suggestions"
              className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              View Recommendations
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
