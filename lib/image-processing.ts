export interface ProcessedImage {
  dataUrl: string
  base64: string
  width: number
  height: number
  size: number
  format: string
}

export async function processImageForAnalysis(
  source: File | string,
  options: {
    maxWidth?: number
    maxHeight?: number
    quality?: number
    format?: 'jpeg' | 'png'
  } = {}
): Promise<ProcessedImage> {
  const {
    maxWidth = 1024,
    maxHeight = 1024,
    quality = 0.9,
    format = 'jpeg'
  } = options

  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()

    if (!ctx) {
      reject(new Error('Could not get canvas context'))
      return
    }

    img.onload = () => {
      try {
        // Calculate new dimensions while maintaining aspect ratio
        let { width, height } = img
        
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height)
          width *= ratio
          height *= ratio
        }

        // Set canvas dimensions
        canvas.width = width
        canvas.height = height

        // Draw image with high quality
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        ctx.drawImage(img, 0, 0, width, height)

        // Convert to data URL with specified format and quality
        const mimeType = `image/${format}`
        const dataUrl = canvas.toDataURL(mimeType, quality)
        const base64 = dataUrl.split(',')[1]

        // Calculate approximate size
        const size = Math.round((base64.length * 3) / 4)

        resolve({
          dataUrl,
          base64,
          width: Math.round(width),
          height: Math.round(height),
          size,
          format
        })
      } catch (error) {
        reject(error)
      }
    }

    img.onerror = () => {
      reject(new Error('Failed to load image'))
    }

    // Handle different source types
    if (typeof source === 'string') {
      // Source is already a data URL or blob URL
      img.src = source
    } else {
      // Source is a File object
      const reader = new FileReader()
      reader.onload = (e) => {
        img.src = e.target?.result as string
      }
      reader.onerror = () => {
        reject(new Error('Failed to read file'))
      }
      reader.readAsDataURL(source)
    }
  })
}

// Enhanced file upload handler
export async function handleFileUpload(
  file: File,
  onProgress?: (progress: number) => void
): Promise<ProcessedImage> {
  // Validate file type
  if (!file.type.startsWith('image/')) {
    throw new Error('Please select a valid image file')
  }

  // Validate file size (max 10MB)
  if (file.size > 10 * 1024 * 1024) {
    throw new Error('Image file is too large. Please select a file smaller than 10MB')
  }

  onProgress?.(25)

  try {
    const processedImage = await processImageForAnalysis(file, {
      maxWidth: 1024,
      maxHeight: 1024,
      quality: 0.9,
      format: 'jpeg'
    })

    onProgress?.(100)
    return processedImage
  } catch (error) {
    throw new Error(`Failed to process image: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

// Enhanced camera capture handler
export async function handleCameraCapture(
  videoElement: HTMLVideoElement,
  onProgress?: (progress: number) => void
): Promise<ProcessedImage> {
  if (!videoElement || videoElement.readyState !== 4) {
    throw new Error('Camera not ready for capture')
  }

  onProgress?.(25)

  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    if (!ctx) {
      throw new Error('Could not get canvas context')
    }

    // Set canvas size to match video
    canvas.width = videoElement.videoWidth
    canvas.height = videoElement.videoHeight

    onProgress?.(50)

    // Draw video frame to canvas
    ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height)

    // Convert to high-quality JPEG
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
    const base64 = dataUrl.split(',')[1]

    onProgress?.(75)

    // Validate the captured image
    if (!base64 || base64.length < 1000) {
      throw new Error('Captured image appears to be invalid or too small')
    }

    const size = Math.round((base64.length * 3) / 4)

    onProgress?.(100)

    return {
      dataUrl,
      base64,
      width: canvas.width,
      height: canvas.height,
      size,
      format: 'jpeg'
    }
  } catch (error) {
    throw new Error(`Failed to capture image: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

// Image validation utility
export function validateImage(image: ProcessedImage): {
  isValid: boolean
  errors: string[]
  warnings: string[]
} {
  const errors: string[] = []
  const warnings: string[] = []

  // Check minimum dimensions
  if (image.width < 100 || image.height < 100) {
    errors.push('Image is too small. Please use an image with dimensions at least 100x100 pixels.')
  }

  // Check maximum dimensions
  if (image.width > 4000 || image.height > 4000) {
    warnings.push('Image is very large and may take longer to process.')
  }

  // Check file size
  if (image.size > 5 * 1024 * 1024) { // 5MB
    warnings.push('Image file is large and may take longer to upload.')
  }

  // Check aspect ratio (should be roughly square for face detection)
  const aspectRatio = image.width / image.height
  if (aspectRatio < 0.5 || aspectRatio > 2) {
    warnings.push('For best face detection results, use an image with a roughly square aspect ratio.')
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  }
} 