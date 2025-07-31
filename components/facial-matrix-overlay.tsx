'use client';

import React, { useRef, useEffect, useState } from 'react';

interface FacialMatrixOverlayProps {
  isActive: boolean;
  onScanComplete?: () => void;
}

export function FacialMatrixOverlay({ isActive, onScanComplete }: FacialMatrixOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [scannedAreas, setScannedAreas] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!isActive || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Grid configuration
    const gridSize = 8; // 8x8 grid
    const cellWidth = canvas.width / gridSize;
    const cellHeight = canvas.height / gridSize;

    // Animation variables
    let animationId: number;
    let currentCell = 0;
    const totalCells = gridSize * gridSize;

    const drawGrid = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw grid lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.lineWidth = 1;

      for (let i = 0; i <= gridSize; i++) {
        // Vertical lines
        ctx.beginPath();
        ctx.moveTo(i * cellWidth, 0);
        ctx.lineTo(i * cellWidth, canvas.height);
        ctx.stroke();

        // Horizontal lines
        ctx.beginPath();
        ctx.moveTo(0, i * cellHeight);
        ctx.lineTo(canvas.width, i * cellHeight);
        ctx.stroke();
      }

      // Draw scanned areas
      scannedAreas.forEach((area) => {
        const [row, col] = area.split(',').map(Number);
        ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
        ctx.fillRect(col * cellWidth, row * cellHeight, cellWidth, cellHeight);
      });

      // Draw current scanning cell
      if (currentCell < totalCells) {
        const row = Math.floor(currentCell / gridSize);
        const col = currentCell % gridSize;
        
        ctx.fillStyle = 'rgba(255, 255, 0, 0.5)';
        ctx.fillRect(col * cellWidth, row * cellHeight, cellWidth, cellHeight);
        
        // Add border to current cell
        ctx.strokeStyle = 'rgba(255, 255, 0, 1)';
        ctx.lineWidth = 2;
        ctx.strokeRect(col * cellWidth, row * cellHeight, cellWidth, cellHeight);
      }

      // Draw facial landmarks guide
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      
      // Face outline guide
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(centerX, centerY, Math.min(canvas.width, canvas.height) * 0.3, 0, 2 * Math.PI);
      ctx.stroke();

      // Eye guides
      ctx.beginPath();
      ctx.arc(centerX - 40, centerY - 20, 8, 0, 2 * Math.PI);
      ctx.arc(centerX + 40, centerY - 20, 8, 0, 2 * Math.PI);
      ctx.stroke();

      // Nose guide
      ctx.beginPath();
      ctx.moveTo(centerX, centerY - 10);
      ctx.lineTo(centerX, centerY + 20);
      ctx.stroke();

      // Mouth guide
      ctx.beginPath();
      ctx.arc(centerX, centerY + 30, 20, 0, Math.PI);
      ctx.stroke();
    };

    const animate = () => {
      drawGrid();

      // Simulate scanning progress
      if (currentCell < totalCells) {
        const row = Math.floor(currentCell / gridSize);
        const col = currentCell % gridSize;
        setScannedAreas(prev => new Set([...prev, `${row},${col}`]));
        
        currentCell++;
        setScanProgress((currentCell / totalCells) * 100);
        
        // Slow down scanning for visual effect
        setTimeout(() => {
          animationId = requestAnimationFrame(animate);
        }, 100);
      } else {
        // Scanning complete
        setScanProgress(100);
        onScanComplete?.();
      }
    };

    animate();

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [isActive, scannedAreas, onScanComplete]);

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

      {/* Instructions */}
      <div className="absolute top-4 left-4 right-4 bg-black/50 rounded-lg p-3">
        <p className="text-white text-sm text-center">
          Position your face within the circle and hold still
        </p>
      </div>
    </div>
  );
} 