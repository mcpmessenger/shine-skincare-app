'use client'

import { Camera } from 'lucide-react'

interface ImageCaptureGuidanceProps {
  onStartCapture: () => void
  onUploadImage: () => void
  isVisible: boolean
}

export function ImageCaptureGuidance({ onStartCapture, onUploadImage, isVisible }: ImageCaptureGuidanceProps) {
  if (!isVisible) return null

  return (
    <div className="bg-secondary rounded-2xl shadow-lg p-8 border border-primary">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-light mb-2">Professional Image Capture Guide</h2>
        <p className="text-secondary font-light">
          Follow these guidelines for medical-grade image quality and accurate analysis
        </p>
      </div>

      {/* Quick Start Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Camera Option */}
        <button
          onClick={onStartCapture}
          className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl hover:border-gray-400 dark:hover:border-gray-500 transition-colors group"
        >
          <Camera className="w-12 h-12 text-gray-600 mb-4 group-hover:scale-110 transition-transform" />
          <h3 className="font-light mb-2">Use Camera</h3>
          <p className="text-sm opacity-75 text-center font-light">
            Capture and crop face, then optionally enhance with AI
          </p>
          <div className="mt-2 text-xs text-green-600 font-medium">
            ✓ Face detection & cropping
          </div>
          <div className="mt-1 text-xs text-blue-600 font-medium">
            ✓ Optional MediaPipe enhancement
          </div>
        </button>

        {/* Upload Option */}
        <button
          onClick={onUploadImage}
          className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl hover:border-gray-400 dark:hover:border-gray-500 transition-colors group"
        >
          <div className="w-12 h-12 text-gray-600 mb-4 group-hover:scale-110 transition-transform">
            <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <h3 className="font-light mb-2">Upload Photo</h3>
          <p className="text-sm opacity-75 text-center font-light">
            Upload an existing photo from your device
          </p>
          <div className="mt-2 text-xs text-blue-600 font-medium">
            ℹ Follow guidelines for best results
          </div>
        </button>
      </div>
    </div>
  )
}
