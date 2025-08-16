'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'

interface ProductImageProps {
  src: string
  alt: string
  className?: string
  fallbackSrc?: string
  onLoad?: () => void
  onError?: () => void
}

export function ProductImage({ 
  src, 
  alt, 
  className = "w-full h-48 object-cover rounded-lg border border-primary",
  fallbackSrc = "https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png",
  onLoad,
  onError
}: ProductImageProps) {
  const [imgSrc, setImgSrc] = useState(src)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string>('')

  useEffect(() => {
    setImgSrc(src)
    setIsLoading(true)
    setHasError(false)
    setDebugInfo('')
  }, [src])

  const handleLoad = () => {
    setIsLoading(false)
    setHasError(false)
    setDebugInfo('✅ Image loaded successfully')
    onLoad?.()
  }

  const handleError = () => {
    console.error(`🖼️ Product image failed to load: ${src}`)
    setIsLoading(false)
    setHasError(true)
    setDebugInfo(`❌ Failed to load: ${src}`)
    
    // Try fallback if we haven't already
    if (imgSrc !== fallbackSrc) {
      console.log(`🔄 Trying fallback image: ${fallbackSrc}`)
      setImgSrc(fallbackSrc)
    }
    
    onError?.()
  }

  // Debug information
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const fullUrl = window.location.origin + src
      const isLocalDev = process.env.NEXT_PUBLIC_IS_LOCAL_DEV === 'true'
      setDebugInfo(`Environment: ${process.env.NODE_ENV}, Local Dev: ${isLocalDev}, Full URL: ${fullUrl}`)
    }
  }, [src])

  return (
    <div className="relative">
      {/* Loading State */}
      {isLoading && (
        <div className={`${className} bg-gray-200 animate-pulse flex items-center justify-center`}>
          <div className="text-gray-500 text-sm">Loading...</div>
        </div>
      )}
      
      {/* Error State */}
      {hasError && imgSrc === fallbackSrc && (
        <div className={`${className} bg-gray-100 flex items-center justify-center`}>
          <div className="text-center">
            <div className="text-gray-500 text-sm mb-2">Image unavailable</div>
            <div className="text-xs text-gray-400">Using fallback</div>
          </div>
        </div>
      )}
      
      {/* Image */}
      <img
        src={imgSrc}
        alt={alt}
        className={`${className} ${isLoading ? 'hidden' : ''} ${hasError && imgSrc === fallbackSrc ? 'opacity-50' : ''}`}
        onLoad={handleLoad}
        onError={handleError}
        style={{ display: isLoading ? 'none' : 'block' }}
      />
      
      {/* Debug Info (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white text-xs p-2 opacity-75 hover:opacity-100 transition-opacity">
          <div className="font-mono">
            <div>Source: {src}</div>
            <div>Status: {isLoading ? 'Loading' : hasError ? 'Error' : 'Loaded'}</div>
            <div>Fallback: {imgSrc === fallbackSrc ? 'Yes' : 'No'}</div>
          </div>
        </div>
      )}
    </div>
  )
}
