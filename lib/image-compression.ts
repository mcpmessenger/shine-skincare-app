/**
 * Client-side image compression utility
 * Converts images to JPEG and compresses them to fit upload limits
 */

export interface CompressionOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  maxSizeMB?: number;
}

export interface CompressedImage {
  blob: Blob;
  file: File;
  originalSize: number;
  compressedSize: number;
  compressionRatio: number;
}

export class ImageCompressor {
  private static readonly DEFAULT_OPTIONS: CompressionOptions = {
    maxWidth: 1920,
    maxHeight: 1920,
    quality: 0.8,
    maxSizeMB: 1.0
  };

  /**
   * Compress an image file to fit upload limits
   */
  static async compressImage(
    file: File,
    options: CompressionOptions = {}
  ): Promise<CompressedImage> {
    const opts = { ...this.DEFAULT_OPTIONS, ...options };
    
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        try {
          // Calculate new dimensions
          const { width, height } = this.calculateDimensions(
            img.width,
            img.height,
            opts.maxWidth!,
            opts.maxHeight!
          );
          
          // Set canvas size
          canvas.width = width;
          canvas.height = height;
          
          // Draw and compress
          ctx!.drawImage(img, 0, 0, width, height);
          
          // Convert to JPEG with quality
          canvas.toBlob(
            (blob) => {
              if (!blob) {
                reject(new Error('Failed to compress image'));
                return;
              }
              
              // Check if we need further compression
              if (blob.size > opts.maxSizeMB! * 1024 * 1024) {
                // Recursively compress with lower quality
                this.compressWithLowerQuality(file, opts, resolve, reject);
              } else {
                // Create new file
                const compressedFile = new File([blob], file.name.replace(/\.[^/.]+$/, '.jpg'), {
                  type: 'image/jpeg',
                  lastModified: Date.now()
                });
                
                resolve({
                  blob,
                  file: compressedFile,
                  originalSize: file.size,
                  compressedSize: blob.size,
                  compressionRatio: blob.size / file.size
                });
              }
            },
            'image/jpeg',
            opts.quality
          );
        } catch (error) {
          reject(error);
        }
      };
      
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = URL.createObjectURL(file);
    });
  }

  /**
   * Compress with progressively lower quality until size is acceptable
   */
  private static async compressWithLowerQuality(
    file: File,
    options: CompressionOptions,
    resolve: (result: CompressedImage) => void,
    reject: (error: Error) => void
  ) {
    const qualities = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2];
    
    for (const quality of qualities) {
      try {
        const result = await this.compressImage(file, { ...options, quality });
        if (result.compressedSize <= options.maxSizeMB! * 1024 * 1024) {
          resolve(result);
          return;
        }
      } catch (error) {
        // Continue to next quality level
      }
    }
    
    // If we still can't compress enough, return the smallest version
    try {
      const result = await this.compressImage(file, { ...options, quality: 0.1 });
      resolve(result);
    } catch (error) {
      reject(new Error('Unable to compress image to acceptable size'));
    }
  }

  /**
   * Calculate new dimensions while maintaining aspect ratio
   */
  private static calculateDimensions(
    originalWidth: number,
    originalHeight: number,
    maxWidth: number,
    maxHeight: number
  ): { width: number; height: number } {
    let { width, height } = { width: originalWidth, height: originalHeight };
    
    // Scale down if too large
    if (width > maxWidth) {
      height = (height * maxWidth) / width;
      width = maxWidth;
    }
    
    if (height > maxHeight) {
      width = (width * maxHeight) / height;
      height = maxHeight;
    }
    
    return { width: Math.round(width), height: Math.round(height) };
  }

  /**
   * Check if image needs compression
   */
  static needsCompression(file: File, maxSizeMB: number = 1.0): boolean {
    return file.size > maxSizeMB * 1024 * 1024;
  }

  /**
   * Get file size in MB
   */
  static getFileSizeMB(file: File): number {
    return file.size / (1024 * 1024);
  }

  /**
   * Format file size for display
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
} 