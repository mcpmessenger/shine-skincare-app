'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ImageCompressor } from '@/lib/image-compression';

export default function TestCompressionPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [compressedFile, setCompressedFile] = useState<any>(null);
  const [isCompressing, setIsCompressing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setCompressedFile(null);
      setError(null);
    }
  };

  const handleCompress = async () => {
    if (!selectedFile) return;

    setIsCompressing(true);
    setError(null);

    try {
      const compressed = await ImageCompressor.compressImage(selectedFile, {
        maxWidth: 1920,
        maxHeight: 1920,
        quality: 0.8,
        maxSizeMB: 1.0
      });

      setCompressedFile({
        originalSize: ImageCompressor.formatFileSize(compressed.originalSize),
        compressedSize: ImageCompressor.formatFileSize(compressed.compressedSize),
        compressionRatio: Math.round((1 - compressed.compressionRatio) * 100),
        file: compressed.file
      });
    } catch (err) {
      setError('Compression failed: ' + (err as Error).message);
    } finally {
      setIsCompressing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Image Compression Test</CardTitle>
            <CardDescription>
              Test the client-side image compression functionality
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Select Image File
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="w-full p-2 border rounded"
              />
            </div>

            {selectedFile && (
              <div className="p-4 bg-gray-50 rounded">
                <h3 className="font-medium mb-2">Original File:</h3>
                <p>Name: {selectedFile.name}</p>
                <p>Size: {ImageCompressor.formatFileSize(selectedFile.size)}</p>
                <p>Type: {selectedFile.type}</p>
                {ImageCompressor.needsCompression(selectedFile, 1.0) && (
                  <p className="text-orange-600 font-medium">
                    ⚠️ This file needs compression (over 1MB)
                  </p>
                )}
              </div>
            )}

            {selectedFile && (
              <Button
                onClick={handleCompress}
                disabled={isCompressing}
                className="w-full"
              >
                {isCompressing ? 'Compressing...' : 'Compress Image'}
              </Button>
            )}

            {compressedFile && (
              <div className="p-4 bg-green-50 rounded">
                <h3 className="font-medium mb-2 text-green-800">Compression Results:</h3>
                <p>Original: {compressedFile.originalSize}</p>
                <p>Compressed: {compressedFile.compressedSize}</p>
                <p>Reduction: {compressedFile.compressionRatio}%</p>
                <p className="text-green-600 font-medium">
                  ✅ Successfully compressed!
                </p>
              </div>
            )}

            {error && (
              <div className="p-4 bg-red-50 rounded">
                <h3 className="font-medium mb-2 text-red-800">Error:</h3>
                <p className="text-red-600">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 