'use client';

import { useEffect, useRef, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Eye, Target, CheckCircle, AlertCircle } from 'lucide-react';

interface FacialMatrixProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  isActive: boolean;
  onFaceDetected?: (faceData: any) => void;
  onAnalysisComplete?: () => void;
}

interface FaceRegion {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
  landmarks?: Array<{ x: number; y: number }>;
}

export default function FacialMatrixOverlay({
  videoRef,
  isActive,
  onFaceDetected,
  onAnalysisComplete
}: FacialMatrixProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [faceRegions, setFaceRegions] = useState<FaceRegion[]>([]);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'complete' | 'error'>('idle');
  const [scanAreas, setScanAreas] = useState<string[]>([]);
  const animationRef = useRef<number>();

  // Facial regions to scan
  const facialRegions = [
    { name: 'forehead', color: '#3B82F6', progress: 0 },
    { name: 'cheeks', color: '#10B981', progress: 0 },
    { name: 'nose', color: '#F59E0B', progress: 0 },
    { name: 'mouth', color: '#EF4444', progress: 0 },
    { name: 'chin', color: '#8B5CF6', progress: 0 }
  ];

  useEffect(() => {
    if (isActive && videoRef.current) {
      startFaceDetection();
    } else {
      stopFaceDetection();
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive]);

  const startFaceDetection = () => {
    setScanStatus('scanning');
    setScanProgress(0);
    setScanAreas([]);
    
    const detectFaces = async () => {
      if (!videoRef.current || !canvasRef.current) return;

      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      if (!ctx) return;

      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw video frame to canvas
      ctx.drawImage(video, 0, 0);

      try {
        // Simulate face detection with Google Vision API
        const detectedFaces = await simulateFaceDetection(canvas);
        setFaceRegions(detectedFaces);

        // Update scan progress based on detected faces
        if (detectedFaces.length > 0) {
          const progress = Math.min(scanProgress + 10, 100);
          setScanProgress(progress);

          // Simulate scanning different facial regions
          const newAreas = [...scanAreas];
          if (progress > 20 && !newAreas.includes('forehead')) newAreas.push('forehead');
          if (progress > 40 && !newAreas.includes('cheeks')) newAreas.push('cheeks');
          if (progress > 60 && !newAreas.includes('nose')) newAreas.push('nose');
          if (progress > 80 && !newAreas.includes('mouth')) newAreas.push('mouth');
          if (progress > 90 && !newAreas.includes('chin')) newAreas.push('chin');
          
          setScanAreas(newAreas);

          if (progress >= 100) {
            setScanStatus('complete');
            onAnalysisComplete?.();
            return;
          }
        }

        // Draw facial matrix overlay
        drawFacialMatrix(ctx, detectedFaces);

        // Continue detection
        animationRef.current = requestAnimationFrame(detectFaces);
      } catch (error) {
        console.error('Face detection error:', error);
        setScanStatus('error');
      }
    };

    detectFaces();
  };

  const stopFaceDetection = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    setScanStatus('idle');
    setScanProgress(0);
    setFaceRegions([]);
    setScanAreas([]);
  };

  const simulateFaceDetection = async (canvas: HTMLCanvasElement): Promise<FaceRegion[]> => {
    // Simulate Google Vision API face detection
    return new Promise((resolve) => {
      setTimeout(() => {
        const width = canvas.width;
        const height = canvas.height;
        
        // Simulate a face in the center of the frame
        const faceWidth = width * 0.6;
        const faceHeight = height * 0.8;
        const faceX = (width - faceWidth) / 2;
        const faceY = (height - faceHeight) / 2;

        resolve([{
          x: faceX,
          y: faceY,
          width: faceWidth,
          height: faceHeight,
          confidence: 0.85 + Math.random() * 0.1,
          landmarks: generateFacialLandmarks(faceX, faceY, faceWidth, faceHeight)
        }]);
      }, 100);
    });
  };

  const generateFacialLandmarks = (x: number, y: number, width: number, height: number) => {
    // Generate facial landmarks for visualization
    return [
      { x: x + width * 0.5, y: y + height * 0.3 }, // Left eye
      { x: x + width * 0.5, y: y + height * 0.3 }, // Right eye
      { x: x + width * 0.5, y: y + height * 0.5 }, // Nose
      { x: x + width * 0.4, y: y + height * 0.7 }, // Left mouth
      { x: x + width * 0.6, y: y + height * 0.7 }, // Right mouth
    ];
  };

  const drawFacialMatrix = (ctx: CanvasRenderingContext2D, faces: FaceRegion[]) => {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    faces.forEach((face, index) => {
      // Draw face bounding box
      ctx.strokeStyle = '#00FF00';
      ctx.lineWidth = 2;
      ctx.strokeRect(face.x, face.y, face.width, face.height);

      // Draw facial landmarks
      if (face.landmarks) {
        ctx.fillStyle = '#FF0000';
        face.landmarks.forEach(landmark => {
          ctx.beginPath();
          ctx.arc(landmark.x, landmark.y, 3, 0, 2 * Math.PI);
          ctx.fill();
        });
      }

      // Draw scan grid
      drawScanGrid(ctx, face);

      // Draw confidence indicator
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '14px Arial';
      ctx.fillText(`Confidence: ${(face.confidence * 100).toFixed(1)}%`, face.x, face.y - 10);
    });
  };

  const drawScanGrid = (ctx: CanvasRenderingContext2D, face: FaceRegion) => {
    const gridSize = 20;
    const alpha = 0.3;

    ctx.strokeStyle = `rgba(0, 255, 0, ${alpha})`;
    ctx.lineWidth = 1;

    // Draw vertical lines
    for (let x = face.x; x <= face.x + face.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, face.y);
      ctx.lineTo(x, face.y + face.height);
      ctx.stroke();
    }

    // Draw horizontal lines
    for (let y = face.y; y <= face.y + face.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(face.x, y);
      ctx.lineTo(face.x + face.width, y);
      ctx.stroke();
    }
  };

  const getStatusIcon = () => {
    switch (scanStatus) {
      case 'scanning':
        return <Target className="h-4 w-4 animate-pulse" />;
      case 'complete':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Eye className="h-4 w-4" />;
    }
  };

  const getStatusColor = () => {
    switch (scanStatus) {
      case 'scanning':
        return 'bg-blue-500';
      case 'complete':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="relative">
      {/* Video with overlay */}
      <div className="relative">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-64 object-cover rounded-lg"
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full pointer-events-none"
        />
      </div>

      {/* Scan Status Overlay */}
      <Card className="absolute top-4 left-4 right-4 bg-white/90 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {getStatusIcon()}
              <span className="font-medium">
                {scanStatus === 'scanning' && 'Scanning Face...'}
                {scanStatus === 'complete' && 'Analysis Complete'}
                {scanStatus === 'error' && 'Detection Error'}
                {scanStatus === 'idle' && 'Ready to Scan'}
              </span>
            </div>
            <Badge variant="outline">
              {faceRegions.length} face{faceRegions.length !== 1 ? 's' : ''} detected
            </Badge>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Scan Progress</span>
              <span>{scanProgress}%</span>
            </div>
            <Progress value={scanProgress} className="w-full" />
          </div>

          {/* Facial Regions */}
          {scanAreas.length > 0 && (
            <div className="mt-3">
              <p className="text-sm font-medium mb-2">Scanned Areas:</p>
              <div className="flex flex-wrap gap-1">
                {facialRegions.map((region) => (
                  <Badge
                    key={region.name}
                    variant={scanAreas.includes(region.name) ? "default" : "outline"}
                    className="text-xs"
                    style={{
                      backgroundColor: scanAreas.includes(region.name) ? region.color : undefined,
                      color: scanAreas.includes(region.name) ? 'white' : undefined
                    }}
                  >
                    {region.name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Face Detection Info */}
          {faceRegions.length > 0 && (
            <div className="mt-3 text-xs text-gray-600">
              <p>Face detected with {(faceRegions[0]?.confidence * 100).toFixed(1)}% confidence</p>
              <p>Position: {faceRegions[0]?.x.toFixed(0)}, {faceRegions[0]?.y.toFixed(0)}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Instructions */}
      {scanStatus === 'idle' && (
        <div className="absolute bottom-4 left-4 right-4">
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-3">
              <p className="text-sm text-blue-800">
                Position your face in the center of the frame for optimal scanning
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 