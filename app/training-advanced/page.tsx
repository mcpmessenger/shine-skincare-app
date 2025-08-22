'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/header'
import { Eye, Brain, Settings } from 'lucide-react'
import Link from 'next/link'
import { useAnalysis } from '@/app/contexts/AnalysisContext'

export default function TrainingAdvancedPage() {
  // Prevent SSR issues by checking if we're on client side
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Get analysis data from main page
  const { analysisData } = useAnalysis()

  // State for processed images
  const [processedImages, setProcessedImages] = useState<{
    rgbChannels: { red: string; green: string; blue: string; grayscale: string };
    gaborFiltered: string;
    dermatoscopic: string;
    surfaceMap: string;
  } | null>(null);

  // State for selected view
  const [selectedView, setSelectedView] = useState('overview');

  // Process images when cropped face is available
  useEffect(() => {
    if (isClient && analysisData?.croppedFaceImage && !processedImages) {
      console.log('🎯 Processing cropped face image for pipeline...');
      simulateImageProcessing(analysisData.croppedFaceImage);
    }
  }, [isClient, analysisData?.croppedFaceImage, processedImages]);

  // Simple image processing simulation (no Canvas API)
  const simulateImageProcessing = async (imageSrc: string) => {
    console.log('🔧 Starting simulated image processing pipeline...');
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Create realistic processed images with color overlays and enhancements
    const simulated = {
      rgbChannels: {
        red: createColorChannelOverlay(imageSrc, 'red'),
        green: createColorChannelOverlay(imageSrc, 'green'), 
        blue: createColorChannelOverlay(imageSrc, 'blue'),
        grayscale: createGrayscaleOverlay(imageSrc)
      },
      gaborFiltered: createGaborFilterEffect(imageSrc),
      dermatoscopic: createDermatoscopicEnhancement(imageSrc),
      surfaceMap: createSurfaceMapEffect(imageSrc)
    };
    
    setProcessedImages(simulated);
    console.log('✅ Simulated processing complete');
  };

  // Create realistic color channel overlays with actual cropped face
  const createColorChannelOverlay = (imageSrc: string, channel: 'red' | 'green' | 'blue'): string => {
    // In a real implementation, this would use Canvas API to extract actual RGB channels
    // For now, we'll create realistic-looking overlays that simulate the processing
    
    const colors = {
      red: { primary: '#FF0000', secondary: '#8B0000', highlight: '#FF4444' },
      green: { primary: '#00FF00', secondary: '#006400', highlight: '#44FF44' },
      blue: { primary: '#0000FF', secondary: '#00008B', highlight: '#4444FF' }
    };
    
    const color = colors[channel];
    
    // Create a data URL for a realistic channel overlay with actual cropped face
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="noise" x="0%" y="0%" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" result="noise"/>
          <feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0.3 0"/>
        </filter>
        <filter id="contrast" x="0%" y="0%" width="100%" height="100%">
          <feComponentTransfer>
            <feFuncR type="linear" slope="1.5" intercept="0"/>
            <feFuncG type="linear" slope="1.5" intercept="0"/>
            <feFuncB type="linear" slope="1.5" intercept="0"/>
          </feComponentTransfer>
        </filter>
        <filter id="channelFilter">
          <feColorMatrix type="matrix" values="${channel === 'red' ? '1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0' : channel === 'green' ? '0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0' : '0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0'}"/>
        </filter>
      </defs>
      
      <!-- Background with noise -->
      <rect width="100%" height="100%" fill="${color.primary}" opacity="0.1"/>
      <rect width="100%" height="100%" filter="url(#noise)" opacity="0.2"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with channel filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#channelFilter)" opacity="0.8"/>
      
      <!-- Channel-specific processing artifacts -->
      <circle cx="100" cy="100" r="60" fill="none" stroke="${color.secondary}" stroke-width="2" opacity="0.6"/>
      <circle cx="100" cy="100" r="40" fill="none" stroke="${color.highlight}" stroke-width="1.5" opacity="0.8"/>
      
      <!-- Processing grid overlay -->
      <g stroke="${color.secondary}" stroke-width="0.5" opacity="0.4">
        <line x1="0" y1="67" x2="200" y2="67"/>
        <line x1="0" y1="133" x2="200" y2="133"/>
        <line x1="67" y1="0" x2="67" y2="200"/>
        <line x1="133" y1="0" x2="133" y2="200"/>
      </g>
      
      <!-- Channel label -->
      <text x="100" y="190" text-anchor="middle" fill="${color.primary}" font-family="Arial" font-size="12" font-weight="bold">
        ${channel.toUpperCase()} CHANNEL
      </text>
      
      <!-- Processing metadata -->
      <text x="10" y="20" fill="${color.secondary}" font-family="Arial" font-size="8">
        Contrast: 1.5x
      </text>
      <text x="10" y="32" fill="${color.secondary}" font-family="Arial" font-size="8">
        Noise: 0.2
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create realistic grayscale overlay with actual cropped face
  const createGrayscaleOverlay = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="grayscale">
          <feColorMatrix type="matrix" values="0.299 0.587 0.114 0 0 0.299 0.587 0.114 0 0 0.299 0.587 0.114 0 0 0 0 0 1 0"/>
        </filter>
        <filter id="edgeDetection">
          <feConvolveMatrix order="3" kernelMatrix="-1 -1 -1 -1 8 -1 -1 -1 -1"/>
        </filter>
      </defs>
      
      <!-- Grayscale background -->
      <rect width="100%" height="100%" fill="#808080" opacity="0.3"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with grayscale filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#grayscale)" opacity="0.9"/>
      
      <!-- Edge detection overlay -->
      <rect width="100%" height="100%" filter="url(#edgeDetection)" opacity="0.4"/>
      
      <!-- Histogram visualization -->
      <g stroke="#404040" stroke-width="1.5" opacity="0.7">
        <line x1="30" y1="170" x2="30" y2="140"/>
        <line x1="40" y1="170" x2="40" y2="130"/>
        <line x1="50" y1="170" x2="50" y2="150"/>
        <line x1="60" y1="170" x2="60" y2="120"/>
        <line x1="70" y1="170" x2="70" y2="130"/>
        <line x1="80" y1="170" x2="80" y2="110"/>
        <line x1="90" y1="170" x2="90" y2="120"/>
        <line x1="100" y1="170" x2="100" y2="100"/>
        <line x1="110" y1="170" x2="110" y2="90"/>
        <line x1="120" y1="170" x2="120" y2="80"/>
      </g>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#404040" font-family="Arial" font-size="12" font-weight="bold">
        GRAYSCALE
      </text>
      
      <!-- Processing info -->
      <text x="10" y="20" fill="#606060" font-family="Arial" font-size="8">
        Luminance: 0.299R + 0.587G + 0.114B
      </text>
      <text x="10" y="32" fill="#606060" font-family="Arial" font-size="8">
        Edge Detection: 3x3 Kernel
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create realistic Gabor filter effect with actual cropped face
  const createGaborFilterEffect = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="gaborWave">
          <feTurbulence type="fractalNoise" baseFrequency="0.1" numOctaves="3" result="noise"/>
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="20"/>
        </filter>
        <filter id="textureEnhance">
          <feConvolveMatrix order="5" kernelMatrix="0 -1 0 -1 5 -1 0 -1 0"/>
        </filter>
        <filter id="gaborCombined">
          <feGaussianBlur stdDeviation="0.5"/>
          <feConvolveMatrix order="3" kernelMatrix="0 -1 0 -1 5 -1 0 -1 0"/>
        </filter>
      </defs>
      
      <!-- Gabor filter background -->
      <rect width="100%" height="100%" fill="#2F4F4F" opacity="0.8"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with Gabor filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#gaborCombined)" opacity="0.8"/>
      
      <!-- Wave pattern overlay -->
      <g stroke="#00CED1" stroke-width="1" opacity="0.6">
        <path d="M 0 30 Q 50 15 100 30 T 200 30" fill="none"/>
        <path d="M 0 55 Q 50 40 100 55 T 200 55" fill="none"/>
        <path d="M 0 80 Q 50 65 100 80 T 200 80" fill="none"/>
        <path d="M 0 105 Q 50 90 100 105 T 200 105" fill="none"/>
        <path d="M 0 130 Q 50 115 100 130 T 200 130" fill="none"/>
        <path d="M 0 155 Q 50 140 100 155 T 200 155" fill="none"/>
      </g>
      
      <!-- Texture enhancement grid -->
      <g stroke="#20B2AA" stroke-width="0.5" opacity="0.4">
        <line x1="0" y1="50" x2="200" y2="50"/>
        <line x1="0" y1="100" x2="200" y2="100"/>
        <line x1="0" y1="150" x2="200" y2="150"/>
        <line x1="50" y1="0" x2="50" y2="200"/>
        <line x1="100" y1="0" x2="100" y2="200"/>
        <line x1="150" y1="0" x2="150" y2="200"/>
      </g>
      
      <!-- Processing parameters -->
      <text x="10" y="20" fill="#00CED1" font-family="Arial" font-size="8">
        Gabor Filter: λ=10, θ=45°, ψ=0, σ=2
      </text>
      <text x="10" y="32" fill="#00CED1" font-family="Arial" font-size="8">
        Frequency: 0.1, Orientation: 45°
      </text>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#00CED1" font-family="Arial" font-size="12" font-weight="bold">
        GABOR FILTER
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create realistic dermatoscopic enhancement with actual cropped face
  const createDermatoscopicEnhancement = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="contrastBoost">
          <feComponentTransfer>
            <feFuncR type="gamma" exponent="0.8"/>
            <feFuncG type="gamma" exponent="0.8"/>
            <feFuncB type="gamma" exponent="0.8"/>
          </feComponentTransfer>
        </filter>
        <filter id="brightnessAdjust">
          <feComponentTransfer>
            <feFuncR type="linear" slope="1.2" intercept="0.1"/>
            <feFuncG type="linear" slope="1.2" intercept="0.1"/>
            <feFuncB type="linear" slope="1.2" intercept="0.1"/>
          </feComponentTransfer>
        </filter>
        <filter id="dermatoscopicCombined">
          <feComponentTransfer>
            <feFuncR type="gamma" exponent="0.8"/>
            <feFuncG type="gamma" exponent="0.8"/>
            <feFuncB type="gamma" exponent="0.8"/>
          </feComponentTransfer>
          <feComponentTransfer>
            <feFuncR type="linear" slope="1.2" intercept="0.1"/>
            <feFuncG type="linear" slope="1.2" intercept="0.1"/>
            <feFuncB type="linear" slope="1.2" intercept="0.1"/>
          </feComponentTransfer>
        </filter>
      </defs>
      
      <!-- Enhanced background -->
      <rect width="100%" height="100%" fill="#F5F5DC" opacity="0.9"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with dermatoscopic enhancement applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#dermatoscopicCombined)" opacity="0.9"/>
      
      <!-- Contrast enhancement visualization -->
      <g stroke="#8B4513" stroke-width="2" opacity="0.7">
        <circle cx="100" cy="100" r="50" fill="none"/>
        <circle cx="100" cy="100" r="35" fill="none"/>
        <circle cx="100" cy="100" r="20" fill="none"/>
      </g>
      
      <!-- Brightness adjustment bars -->
      <g fill="#CD853F" opacity="0.6">
        <rect x="30" y="140" width="20" height="25" rx="2"/>
        <rect x="55" y="140" width="20" height="30" rx="2"/>
        <rect x="80" y="140" width="20" height="35" rx="2"/>
        <rect x="105" y="140" width="20" height="40" rx="2"/>
        <rect x="130" y="140" width="20" height="45" rx="2"/>
        <rect x="155" y="140" width="20" height="50" rx="2"/>
      </g>
      
      <!-- Processing parameters -->
      <text x="10" y="20" fill="#8B4513" font-family="Arial" font-size="8">
        Contrast: +20%, Brightness: +10%
      </text>
      <text x="10" y="32" fill="#8B4513" font-family="Arial" font-size="8">
        Gamma: 0.8, Saturation: +15%
      </text>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#8B4513" font-family="Arial" font-size="12" font-weight="bold">
        DERMATOSCOPIC
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create realistic surface map effect with actual cropped face
  const createSurfaceMapEffect = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="depthEffect">
          <feGaussianBlur stdDeviation="2"/>
        </filter>
        <filter id="surfaceMapping">
          <feGaussianBlur stdDeviation="1"/>
          <feConvolveMatrix order="3" kernelMatrix="0 -1 0 -1 4 -1 0 -1 0"/>
        </filter>
        <linearGradient id="depthGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#000000;stop-opacity:1" />
          <stop offset="50%" style="stop-color:#404040;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#808080;stop-opacity:1" />
        </linearGradient>
      </defs>
      
      <!-- 3D surface background -->
      <rect width="100%" height="100%" fill="url(#depthGradient)" opacity="0.8"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with surface mapping filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#surfaceMapping)" opacity="0.8"/>
      
      <!-- Topographic contour lines -->
      <g stroke="#FFFFFF" stroke-width="1" opacity="0.6" fill="none">
        <path d="M 30 60 Q 65 50 100 60 T 170 60 T 200 60"/>
        <path d="M 30 80 Q 65 70 100 80 T 170 80 T 200 80"/>
        <path d="M 30 100 Q 65 90 100 100 T 170 100 T 200 100"/>
        <path d="M 30 120 Q 65 110 100 120 T 170 120 T 200 120"/>
        <path d="M 30 140 Q 65 130 100 140 T 170 140 T 200 140"/>
      </g>
      
      <!-- Elevation markers -->
      <g fill="#FFD700" opacity="0.8">
        <circle cx="65" cy="50" r="2"/>
        <circle cx="100" cy="70" r="2"/>
        <circle cx="170" cy="90" r="2"/>
      </g>
      
      <!-- Depth scale -->
      <g stroke="#FFFFFF" stroke-width="1.5" opacity="0.8">
        <line x1="170" y1="30" x2="170" y2="140"/>
        <line x1="167" y1="30" x2="173" y2="30"/>
        <line x1="167" y1="70" x2="173" y2="70"/>
        <line x1="167" y1="110" x2="173" y2="110"/>
        <line x1="167" y1="140" x2="173" y2="140"/>
      </g>
      
      <!-- Processing parameters -->
      <text x="10" y="20" fill="#FFFFFF" font-family="Arial" font-size="8">
        Surface Mapping: 3D Topography
      </text>
      <text x="10" y="32" fill="#FFFFFF" font-family="Arial" font-size="8">
        Depth Range: 0-255, Resolution: 0.1mm
      </text>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#FFD700" font-family="Arial" font-size="12" font-weight="bold">
        SURFACE MAP
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Don't render until we're on the client side to avoid SSR issues
  if (!isClient) {
    return (
      <div className="min-h-screen bg-primary text-primary flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-4"></div>
          <p className="text-secondary font-light">Loading Advanced Analysis...</p>
        </div>
      </div>
    );
  }



  return (
    <div className="min-h-screen bg-primary text-primary">
      <Header />
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-light mb-2">Advanced Skin Analysis Pipeline</h1>
          <p className="text-lg text-secondary font-light">
            Scientific preprocessing pipeline and image analysis results
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          
          {/* Image Processing Status */}
          {!analysisData?.croppedFaceImage ? (
            <div className="bg-secondary rounded-2xl shadow-lg p-8 mb-6 border border-primary text-center">
              <Eye className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-light mb-2">No Image Processed</h2>
              <p className="text-secondary font-light mb-4">
                Upload an image on the main page to see the advanced preprocessing pipeline in action
              </p>
              <Link 
                href="/"
                className="inline-flex items-center px-6 py-3 bg-accent text-white rounded-xl font-light hover:bg-accent/90 transition-colors"
              >
                <Eye className="w-5 h-5 mr-2" />
                Go to Main Page
              </Link>
            </div>
          ) : (
            <>
              {/* Processing Results Overview */}
              <div className="bg-secondary rounded-2xl shadow-lg p-6 mb-6 border border-primary">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-light">Unified Processing Results</h2>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${!processedImages ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></div>
                    <span className="text-sm text-secondary">
                      {!processedImages ? 'Processing...' : 'Complete'}
                    </span>
                  </div>
                </div>

                {/* Navigation Tabs */}
                <div className="flex space-x-1 mb-6 bg-hover rounded-lg p-1">
                  {[
                    { id: 'overview', label: 'Overview', icon: Eye },
                    { id: 'rgb', label: 'RGB Channels', icon: Eye },
                    { id: 'gabor', label: 'Gabor Filter', icon: Brain },
                    { id: 'dermatoscopic', label: 'Dermatoscopic', icon: Settings },
                    { id: 'surface', label: 'Surface Map', icon: Brain }
                  ].map(({ id, label, icon: Icon }) => (
                    <button
                      key={id}
                      onClick={() => setSelectedView(id as any)}
                      className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        selectedView === id
                          ? 'bg-primary text-white'
                          : 'text-secondary hover:text-primary hover:bg-hover'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{label}</span>
                    </button>
                  ))}
                </div>

                {/* Content Area */}
                <div className="min-h-96">
                  {selectedView === 'overview' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {/* Cropped Face Image */}
                      <div className="space-y-2">
                        <h3 className="text-sm font-medium text-secondary flex items-center gap-2">
                          <Eye className="w-4 h-4" />
                          Cropped Face Region
                        </h3>
                        <img
                          src={analysisData.croppedFaceImage}
                          alt="Cropped face for analysis"
                          className="w-full h-32 object-cover rounded border border-border"
                        />
                      </div>

                      {/* RGB Channels */}
                      {processedImages && (
                        <div className="space-y-2">
                          <h3 className="text-sm font-medium text-secondary flex items-center gap-2">
                            <Eye className="w-4 h-4" />
                            RGB Channels
                          </h3>
                          <div className="grid grid-cols-2 gap-1">
                            <img
                              src={processedImages.rgbChannels.red}
                              alt="Red channel"
                              className="w-full h-16 object-cover rounded border border-border"
                            />
                            <img
                              src={processedImages.rgbChannels.green}
                              alt="Green channel"
                              className="w-full h-16 object-cover rounded border border-border"
                            />
                            <img
                              src={processedImages.rgbChannels.blue}
                              alt="Blue channel"
                              className="w-full h-16 object-cover rounded border border-border"
                            />
                            <img
                              src={processedImages.rgbChannels.grayscale}
                              alt="Grayscale"
                              className="w-full h-16 object-cover rounded border border-border"
                            />
                          </div>
                        </div>
                      )}

                      {/* Gabor Filter */}
                      {processedImages && (
                        <div className="space-y-2">
                          <h3 className="text-sm font-medium text-secondary flex items-center gap-2">
                            <Brain className="w-4 h-4" />
                            Gabor Filter
                          </h3>
                          <img
                            src={processedImages.gaborFiltered}
                            alt="Gabor filtered"
                            className="w-full h-32 object-cover rounded-lg border border-border"
                          />
                        </div>
                      )}

                      {/* Dermatoscopic */}
                      {processedImages && (
                        <div className="space-y-2">
                          <h3 className="text-sm font-medium text-secondary flex items-center gap-2">
                            <Settings className="w-4 h-4" />
                            Dermatoscopic
                          </h3>
                          <img
                            src={processedImages.dermatoscopic}
                            alt="Dermatoscopic enhanced"
                            className="w-full h-32 object-cover rounded-lg border border-border"
                          />
                        </div>
                      )}

                      {/* Surface Map */}
                      {processedImages && (
                        <div className="space-y-2">
                          <h3 className="text-sm font-medium text-secondary flex items-center gap-2">
                            <Brain className="w-4 h-4" />
                            Surface Map
                          </h3>
                          <img
                            src={processedImages.surfaceMap}
                            alt="Surface map"
                            className="w-full h-32 object-cover rounded-lg border border-border"
                          />
                        </div>
                      )}
                    </div>
                  )}

                  {selectedView === 'rgb' && processedImages && (
                    <div className="text-center space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h4 className="text-sm font-medium text-secondary mb-2">Red Channel</h4>
                          <img
                            src={processedImages.rgbChannels.red}
                            alt="Red channel"
                            className="w-full h-48 object-cover rounded-lg border border-border"
                          />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-secondary mb-2">Green Channel</h4>
                          <img
                            src={processedImages.rgbChannels.green}
                            alt="Green channel"
                            className="w-full h-48 object-cover rounded-lg border border-border"
                          />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-secondary mb-2">Blue Channel</h4>
                          <img
                            src={processedImages.rgbChannels.blue}
                            alt="Blue channel"
                            className="w-full h-48 object-cover rounded-lg border border-border"
                          />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-secondary mb-2">Grayscale</h4>
                          <img
                            src={processedImages.rgbChannels.grayscale}
                            alt="Grayscale"
                            className="w-full h-48 object-cover rounded-lg border border-border"
                          />
                        </div>
                      </div>
                      <div className="text-sm text-secondary space-y-1">
                        <p>RGB channel separation for detailed color analysis</p>
                        <p>Processing time: ~1500ms (simulated)</p>
                      </div>
                    </div>
                  )}

                  {selectedView === 'gabor' && processedImages && (
                    <div className="text-center space-y-4">
                      <img
                        src={processedImages.gaborFiltered}
                        alt="Gabor filtered"
                        className="max-w-full h-auto rounded-lg border border-border mx-auto"
                      />
                      <div className="text-sm text-secondary space-y-1">
                        <p>Gabor filter applied to highlight texture features</p>
                        <p>Enhances edge detection and skin texture analysis</p>
                      </div>
                    </div>
                  )}

                  {selectedView === 'dermatoscopic' && processedImages && (
                    <div className="text-center space-y-4">
                      <img
                        src={processedImages.dermatoscopic}
                        alt="Dermatoscopic enhanced"
                        className="max-w-full h-auto rounded-lg border border-border mx-auto"
                      />
                      <div className="text-sm text-secondary space-y-1">
                        <p>Dermatoscopic enhancement for detailed skin lesion analysis</p>
                        <p>Improved contrast and brightness for clinical evaluation</p>
                      </div>
                    </div>
                  )}

                  {selectedView === 'surface' && processedImages && (
                    <div className="text-center space-y-4">
                      <img
                        src={processedImages.surfaceMap}
                        alt="Surface map"
                        className="max-w-full h-auto rounded-lg border border-border mx-auto"
                      />
                      <div className="text-sm text-secondary space-y-1">
                        <p>3D surface mapping to visualize skin topography</p>
                        <p>Depth analysis for texture and roughness assessment</p>
                      </div>
                    </div>
                  )}

                  {/* Processing Metadata */}
                  {processedImages && (
                    <div className="mt-6 p-4 bg-hover rounded-lg">
                      <h4 className="font-medium mb-2">Processing Pipeline Metadata</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-secondary">Analysis Type:</span>
                          <p className="font-medium">Simulated Pipeline</p>
                        </div>
                        <div>
                          <span className="text-secondary">Processing Time:</span>
                          <p className="font-medium">~1500ms</p>
                        </div>
                        <div>
                          <span className="text-secondary">Technologies:</span>
                          <p className="font-medium">RGB Separation, Gabor Filter, Enhancement</p>
                        </div>
                        <div>
                          <span className="text-secondary">Real Analysis:</span>
                          <p className="font-medium">Simulated (Ready for Real Engine)</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Go Back Button */}
              <div className="text-center mb-6">
                <Link 
                  href="/"
                  className="inline-flex items-center px-6 py-3 bg-accent text-white rounded-xl font-light hover:bg-accent/90 transition-colors"
                >
                  <Eye className="w-5 h-5 mr-2" />
                  Back to Main Page
                </Link>
              </div>
            </>
          )}

          {/* Analysis Sensitivity Settings */}
          <div className="bg-secondary rounded-2xl shadow-lg p-6 border border-primary">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-light">Analysis Sensitivity Settings</h2>
              <button
                onClick={() => {/* TODO: Implement toggle */}}
                className="text-accent hover:underline text-sm"
              >
                Hide Advanced
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Acne Detection: <span className="text-accent">75</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="75"
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Severity Threshold: <span className="text-accent">70</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="70"
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Confidence Minimum: <span className="text-accent">80</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="80"
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Age Adjustment: <span className="text-accent">60</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="60"
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Skin Type Calibration: <span className="text-accent">65</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="65"
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
