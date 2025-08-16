'use client'

import { useState, useRef, useEffect } from 'react'

interface ImageThumbnailProps {
  imageData: string
  faceBounds?: {
    x: number
    y: number
    width: number
    height: number
  }
  className?: string
}

export function ImageThumbnail({ imageData, faceBounds, className = '' }: ImageThumbnailProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    if (!imageData || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const img = new Image()
    img.onload = () => {
      // Set canvas dimensions to match image aspect ratio
      const maxSize = 200
      const aspectRatio = img.width / img.height
      
      if (aspectRatio > 1) {
        canvas.width = maxSize
        canvas.height = maxSize / aspectRatio
      } else {
        canvas.width = maxSize * aspectRatio
        canvas.height = maxSize
      }

      // Draw the image
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      // Draw face isolation circle if face bounds are provided
      if (faceBounds) {
        const scaleX = canvas.width / img.width
        const scaleY = canvas.height / img.height
        
        const centerX = (faceBounds.x + faceBounds.width / 2) * scaleX
        const centerY = (faceBounds.y + faceBounds.height / 2) * scaleY
        const radius = Math.max(faceBounds.width * scaleX, faceBounds.height * scaleY) / 2

        // Draw circle outline
        ctx.strokeStyle = '#3B82F6'
        ctx.lineWidth = 3
        ctx.beginPath()
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
        ctx.stroke()

        // Add a subtle glow effect
        ctx.shadowColor = '#3B82F6'
        ctx.shadowBlur = 10
        ctx.stroke()
        ctx.shadowBlur = 0
      }

      setIsLoaded(true)
    }

    img.src = imageData
  }, [imageData, faceBounds])

  return (
    <div className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        className={`rounded-lg border-2 border-gray-200 dark:border-gray-700 transition-opacity duration-300 ${
          isLoaded ? 'opacity-100' : 'opacity-0'
        }`}
      />
      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-lg">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}
      {faceBounds && (
        <div className="absolute bottom-2 left-2 bg-blue-500 text-white text-xs px-2 py-1 rounded">
          Face Detected
        </div>
      )}
    </div>
  )
}

