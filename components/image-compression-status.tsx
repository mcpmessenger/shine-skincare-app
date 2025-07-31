'use client';

import { useState } from 'react';
import { ImageCompressor } from '@/lib/image-compression';

interface ImageCompressionStatusProps {
  file: File;
  onCompressionComplete: (compressedFile: File) => void;
  onError: (error: string) => void;
}

export function ImageCompressionStatus({ file, onCompressionComplete, onError }: ImageCompressionStatusProps) {
  const [isCompressing, setIsCompressing] = useState(false);
  const [compressionInfo, setCompressionInfo] = useState<{
    originalSize: string;
    compressedSize: string;
    compressionRatio: number;
  } | null>(null);

  const handleCompression = async () => {
    if (!ImageCompressor.needsCompression(file, 1.0)) {
      // No compression needed
      onCompressionComplete(file);
      return;
    }

    setIsCompressing(true);
    
    try {
      const compressed = await ImageCompressor.compressImage(file, {
        maxWidth: 1920,
        maxHeight: 1920,
        quality: 0.8,
        maxSizeMB: 1.0
      });

      setCompressionInfo({
        originalSize: ImageCompressor.formatFileSize(compressed.originalSize),
        compressedSize: ImageCompressor.formatFileSize(compressed.compressedSize),
        compressionRatio: Math.round((1 - compressed.compressionRatio) * 100)
      });

      onCompressionComplete(compressed.file);
    } catch (error) {
      onError('Failed to compress image. Please try a smaller image.');
    } finally {
      setIsCompressing(false);
    }
  };

  // Auto-compress when component mounts
  useState(() => {
    handleCompression();
  });

  if (isCompressing) {
    return (
      <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        <span className="text-sm text-blue-700">
          Optimizing image for upload...
        </span>
      </div>
    );
  }

  if (compressionInfo) {
    return (
      <div className="p-3 bg-green-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded-full flex-shrink-0"></div>
          <span className="text-sm text-green-700">
            Image optimized: {compressionInfo.originalSize} → {compressionInfo.compressedSize} ({compressionInfo.compressionRatio}% smaller)
          </span>
        </div>
      </div>
    );
  }

  return null;
} 