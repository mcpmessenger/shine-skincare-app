'use client';

import React, { useRef, useEffect, useState } from 'react';

interface FacialMatrixOverlayProps {
  isActive: boolean;
  onScanComplete?: () => void;
}

export function FacialMatrixOverlay({ isActive, onScanComplete }: FacialMatrixOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [scanProgress, setScanProgress] = useState(0);

  useEffect(() => {
    if (!isActive || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Animation variables
    let animationId: number;
    let scanAngle = 0;
    const scanDuration = 3000; // 3 seconds total
    const startTime = Date.now();

    const drawFaceGuide = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const radius = Math.min(canvas.width, canvas.height) * 0.35; // Larger, more prominent circle

      // Draw main face positioning circle
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.stroke();

      // Draw inner circle for face boundary
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius * 0.7, 0, 2 * Math.PI);
      ctx.stroke();

      // Draw scanning animation
      if (scanProgress < 100) {
        ctx.strokeStyle = 'rgba(0, 255, 0, 0.8)';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, scanAngle, scanAngle + Math.PI / 2);
        ctx.stroke();
      }

      // Draw facial feature guides (subtle)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.lineWidth = 1;

      // Eye guides
      ctx.beginPath();
      ctx.arc(centerX - radius * 0.25, centerY - radius * 0.15, 6, 0, 2 * Math.PI);
      ctx.arc(centerX + radius * 0.25, centerY - radius * 0.15, 6, 0, 2 * Math.PI);
      ctx.stroke();

      // Nose guide
      ctx.beginPath();
      ctx.moveTo(centerX, centerY - radius * 0.1);
      ctx.lineTo(centerX, centerY + radius * 0.1);
      ctx.stroke();

      // Mouth guide
      ctx.beginPath();
      ctx.arc(centerX, centerY + radius * 0.2, radius * 0.15, 0, Math.PI);
      ctx.stroke();

      // Draw "Position Face Here" text
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.font = 'bold 14px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('Position Face Here', centerX, centerY + radius + 30);
    };

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / scanDuration, 1);
      
      setScanProgress(Math.round(progress * 100));
      scanAngle = progress * 2 * Math.PI;

      drawFaceGuide();

      if (progress < 1) {
        animationId = requestAnimationFrame(animate);
      } else {
        // Scan complete
        setScanProgress(100);
        if (onScanComplete) {
          onScanComplete();
        }
      }
    };

    animate();

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [isActive, scanProgress, onScanComplete]);

  if (!isActive) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ position: 'absolute', top: 0, left: 0 }}
      />
      
      {/* Scan Progress Indicator */}
      <div className="absolute bottom-4 left-4 right-4 bg-black/50 rounded-lg p-3">
        <div className="flex items-center justify-between text-white text-sm mb-2">
          <span>Facial Matrix Scan</span>
          <span>{Math.round(scanProgress)}%</span>
        </div>
        <div className="w-full bg-gray-600 rounded-full h-2">
          <div 
            className="bg-green-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${scanProgress}%` }}
          />
        </div>
      </div>

      {/* Clear Instructions */}
      <div className="absolute top-4 left-4 right-4 bg-black/50 rounded-lg p-3">
        <p className="text-white text-sm text-center font-medium">
          Position your face within the circle and hold still
        </p>
      </div>
    </div>
  );
} 