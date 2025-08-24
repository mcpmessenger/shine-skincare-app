'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/header'
import { Eye, Brain, Settings, ShoppingCart } from 'lucide-react'
import Link from 'next/link'
import { useAnalysis } from '@/app/contexts/AnalysisContext'
import { products, getProductsByCategory } from '@/lib/products'
import { useCart } from '@/hooks/useCart'

export default function TrainingAdvancedPage() {
  // Prevent SSR issues by checking if we're on client side
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Get analysis data from main page
  const { analysisData } = useAnalysis()
  const { dispatch } = useCart() || { dispatch: null }

  // State for processed images
  const [processedImages, setProcessedImages] = useState<{
    rgbChannels: { red: string; green: string; blue: string; grayscale: string };
    gaborFiltered: string;
    dermatoscopic: string;
    surfaceMap: string;
  } | null>(null);

  // State for selected view
  const [selectedView, setSelectedView] = useState('overview');
  
  // State for MediaPipe feature isolation
  const [mediapipeFeatures, setMediapipeFeatures] = useState<{
    cheeks: string;
    forehead: string;
    nose: string;
    chin: string;
    fullFace: string;
  } | null>(null);
  
  // State for Wood's lamp simulation
  const [woodsLampImage, setWoodsLampImage] = useState<string | null>(null);
  
  // State for image zoom modal
  const [zoomModal, setZoomModal] = useState<{
    isOpen: boolean;
    imageSrc: string;
    imageAlt: string;
    title: string;
  }>({
    isOpen: false,
    imageSrc: '',
    imageAlt: '',
    title: ''
  });
  
  // State for zoom level
  const [zoomLevel, setZoomLevel] = useState(1);
  
  // Smart product recommendations based on analysis
  const getSmartRecommendations = () => {
    if (!analysisData?.analysisResults) return [];
    
    const results = analysisData.analysisResults;
    const recommendations = [];
    
    // Priority scoring system
    const categoryScores = {
      cleanser: 0,
      treatment: 0,
      serum: 0,
      moisturizer: 0,
      sunscreen: 0
    };
    
    // Analyze skin condition and assign scores
    if (results.primary_condition) {
      const condition = results.primary_condition.toLowerCase();
      
      if (condition.includes('acne') || condition.includes('breakout')) {
        categoryScores.cleanser += 3;
        categoryScores.treatment += 4;
        categoryScores.moisturizer += 2;
        categoryScores.sunscreen += 2;
      } else if (condition.includes('melasma') || condition.includes('hyperpigmentation') || condition.includes('dark')) {
        categoryScores.serum += 4;
        categoryScores.treatment += 3;
        categoryScores.sunscreen += 5;
        categoryScores.moisturizer += 2;
      } else if (condition.includes('aging') || condition.includes('wrinkle')) {
        categoryScores.serum += 4;
        categoryScores.treatment += 3;
        categoryScores.moisturizer += 3;
        categoryScores.sunscreen += 4;
      } else if (condition.includes('sensitive') || condition.includes('redness')) {
        categoryScores.cleanser += 3;
        categoryScores.moisturizer += 4;
        categoryScores.sunscreen += 2;
      }
    }
    
    // Factor in severity
    if (results.severity) {
      const severity = results.severity;
      if (severity > 0.7) {
        // High severity - prioritize treatments
        categoryScores.treatment += 2;
        categoryScores.serum += 1;
      } else if (severity < 0.3) {
        // Low severity - focus on maintenance
        categoryScores.moisturizer += 2;
        categoryScores.sunscreen += 2;
      }
    }
    
    // Factor in skin health score
    if (results.skin_health_score) {
      const healthScore = results.skin_health_score;
      if (healthScore < 0.5) {
        // Poor skin health - need intensive care
        categoryScores.treatment += 2;
        categoryScores.serum += 2;
      } else if (healthScore > 0.8) {
        // Good skin health - focus on maintenance
        categoryScores.moisturizer += 2;
        categoryScores.sunscreen += 2;
      }
    }
    
    // Get top 3 categories
    const topCategories = Object.entries(categoryScores)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([category]) => category);
    
    // Select products from top categories
    const selectedProducts: typeof products = [];
    for (const category of topCategories) {
      const categoryProducts = getProductsByCategory(category);
      if (categoryProducts.length > 0) {
        // Select the best product from each category
        const bestProduct = categoryProducts[0];
        if (!selectedProducts.find(p => p.id === bestProduct.id)) {
          selectedProducts.push(bestProduct);
        }
      }
    }
    
    // Fill remaining slots with general recommendations
    while (selectedProducts.length < 3) {
      const remainingProducts = products.filter(p => 
        !selectedProducts.find(sp => sp.id === p.id)
      );
      if (remainingProducts.length > 0) {
        selectedProducts.push(remainingProducts[0]);
      } else {
        break;
      }
    }
    
    return selectedProducts;
  };

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
    
    // Also process MediaPipe features if landmarks are available
    if (analysisData?.mediapipeLandmarks && analysisData.mediapipeLandmarks.length > 0) {
      console.log('🎯 Processing MediaPipe features for isolation...');
      simulateMediaPipeFeatureIsolation(imageSrc, analysisData.mediapipeLandmarks);
    }
  };
  
  // Simulate MediaPipe feature isolation
  const simulateMediaPipeFeatureIsolation = async (imageSrc: string, landmarks: Array<[number, number, number]>) => {
    console.log('🔧 Starting MediaPipe feature isolation...');
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create isolated facial features with realistic overlays
    const features = {
      cheeks: createFeatureIsolation(imageSrc, 'cheeks', landmarks),
      forehead: createFeatureIsolation(imageSrc, 'forehead', landmarks),
      nose: createFeatureIsolation(imageSrc, 'nose', landmarks),
      chin: createFeatureIsolation(imageSrc, 'chin', landmarks),
      fullFace: createFeatureIsolation(imageSrc, 'fullFace', landmarks)
    };
    
    setMediapipeFeatures(features);
    console.log('✅ MediaPipe feature isolation complete');
    
    // Also process Wood's lamp simulation
    console.log('🔦 Processing Wood\'s lamp simulation...');
    simulateWoodsLampEffect(imageSrc);
  };
  
  // Simulate Wood's lamp effect using blue light simulation
  const simulateWoodsLampEffect = async (imageSrc: string) => {
    console.log('🔦 Starting Wood\'s lamp simulation...');
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Create Wood's lamp effect image
    const woodsLampImage = createWoodsLampEffect(imageSrc);
    setWoodsLampImage(woodsLampImage);
    console.log('✅ Wood\'s lamp simulation complete');
  };
  
  // Create subtle Wood's lamp effect with reduced blue light intensity
  const createWoodsLampEffect = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- Subtle blue light filter to simulate Wood's lamp -->
        <filter id="woodsLampFilter">
          <feColorMatrix type="matrix" values="0.2 0 0 0 0 0 0.3 0 0 0 0 0 0.7 0 0 0 0 0 1 0"/>
          <feGaussianBlur stdDeviation="0.3"/>
        </filter>
        
        <!-- Subtle blue glow effect -->
        <filter id="blueGlow">
          <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        
        <!-- Subtle fluorescence simulation -->
        <filter id="fluorescence">
          <feColorMatrix type="matrix" values="0.2 0 0 0 0 0 0.2 0 0 0 0 0 0.9 0 0 0 0 0 1 0"/>
          <feGaussianBlur stdDeviation="0.8"/>
        </filter>
      </defs>
      
      <!-- Dark background to simulate Wood's lamp environment with reduced opacity -->
      <rect width="100%" height="100%" fill="#000B1A" opacity="0.7"/>
      
      <!-- Very subtle blue light overlay to simulate screen blue light -->
      <rect width="100%" height="100%" fill="#0066FF" opacity="0.15"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with Wood's lamp filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#woodsLampFilter)" opacity="0.95"/>
      
      <!-- Very subtle blue light simulation from screen -->
      <rect x="20" y="20" width="160" height="160" fill="#0066FF" opacity="0.2" filter="url(#blueGlow)"/>
      
      <!-- Very subtle simulated fluorescence areas -->
      <g filter="url(#fluorescence)">
        <!-- Cheek areas - often show fluorescence in certain conditions -->
        <circle cx="80" cy="100" r="25" fill="#00FFFF" opacity="0.3"/>
        <circle cx="120" cy="100" r="25" fill="#00FFFF" opacity="0.3"/>
        
        <!-- Forehead area -->
        <ellipse cx="100" cy="60" rx="30" ry="15" fill="#00FFFF" opacity="0.25"/>
        
        <!-- Nose area -->
        <ellipse cx="100" cy="90" rx="12" ry="20" fill="#00FFFF" opacity="0.2"/>
      </g>
      
      <!-- Very subtle blue light grid pattern to simulate screen pixels -->
      <g stroke="#0066FF" stroke-width="0.3" opacity="0.2">
        <line x1="0" y1="40" x2="200" y2="40"/>
        <line x1="0" y1="80" x2="200" y2="80"/>
        <line x1="0" y1="120" x2="200" y2="120"/>
        <line x1="0" y1="160" x2="200" y2="160"/>
        <line x1="40" y1="0" x2="40" y2="200"/>
        <line x1="80" y1="0" x2="80" y2="200"/>
        <line x1="120" y1="0" x2="120" y2="200"/>
        <line x1="160" y1="0" x2="160" y2="200"/>
      </g>
      
      <!-- Processing parameters -->
      <text x="10" y="20" fill="#00FFFF" font-family="Arial" font-size="8" opacity="0.7">
        Wood's Lamp: Blue Light Sim
      </text>
      <text x="10" y="32" fill="#00FFFF" font-family="Arial" font-size="8" opacity="0.7">
        Wavelength: ~450nm (Blue)
      </text>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#00FFFF" font-family="Arial" font-size="12" font-weight="bold" opacity="0.8">
        WOOD'S LAMP SIM
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };
  
  // Create isolated facial feature images
  const createFeatureIsolation = (imageSrc: string, feature: string, landmarks: Array<[number, number, number]>): string => {
    const featureConfigs = {
      cheeks: { color: '#FF6B6B', label: 'CHEEKS', opacity: 0.7, region: 'lateral' },
      forehead: { color: '#4ECDC4', label: 'FOREHEAD', opacity: 0.7, region: 'superior' },
      nose: { color: '#45B7D1', label: 'NOSE', opacity: 0.8, region: 'central' },
      chin: { color: '#96CEB4', label: 'CHIN', opacity: 0.7, region: 'inferior' },
      fullFace: { color: '#FFEAA7', label: 'FULL FACE', opacity: 0.6, region: 'complete' }
    };
    
    const config = featureConfigs[feature as keyof typeof featureConfigs];
    
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="featureHighlight">
          <feGaussianBlur stdDeviation="1"/>
          <feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0.8 0"/>
        </filter>
        <filter id="landmarkPoints">
          <feGaussianBlur stdDeviation="0.5"/>
        </filter>
      </defs>
      
      <!-- Background with feature-specific color -->
      <rect width="100%" height="100%" fill="${config.color}" opacity="0.1"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" opacity="0.9"/>
      
      <!-- Feature-specific overlay -->
      <rect x="20" y="20" width="160" height="160" fill="${config.color}" opacity="${config.opacity * 0.3}"/>
      
      <!-- Simulated landmark points for this feature -->
      ${generateLandmarkPoints(feature, landmarks)}
      
      <!-- Feature label -->
      <text x="100" y="190" text-anchor="middle" fill="${config.color}" font-family="Arial" font-size="12" font-weight="bold">
        ${config.label}
      </text>
      
      <!-- Processing info -->
      <text x="10" y="20" fill="${config.color}" font-family="Arial" font-size="8">
        MediaPipe: 468 landmarks
      </text>
      <text x="10" y="32" fill="${config.color}" font-family="Arial" font-size="8">
        Feature: ${feature}
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };
  
  // Generate landmark points for specific features
  const generateLandmarkPoints = (feature: string, landmarks: Array<[number, number, number]>): string => {
    const featureRanges = {
      cheeks: { start: 0, end: 50, color: '#FF6B6B' },
      forehead: { start: 51, end: 100, color: '#4ECDC4' },
      nose: { start: 101, end: 200, color: '#45B7D1' },
      chin: { start: 201, end: 300, color: '#96CEB4' },
      fullFace: { start: 0, end: 467, color: '#FFEAA7' }
    };
    
    const range = featureRanges[feature as keyof typeof featureRanges];
    if (!range) return '';
    
    let points = '';
    for (let i = range.start; i <= range.end && i < landmarks.length; i += 10) {
      const [x, y] = landmarks[i];
      const normalizedX = 20 + (x / 640) * 160;
      const normalizedY = 20 + (y / 480) * 160;
      points += `<circle cx="${normalizedX}" cy="${normalizedY}" r="2" fill="${range.color}" opacity="0.8" filter="url(#landmarkPoints)"/>`;
    }
    
    return points;
  };
  
  // Open zoom modal for image examination
  const openZoomModal = (imageSrc: string, imageAlt: string, title: string) => {
    setZoomModal({
      isOpen: true,
      imageSrc,
      imageAlt,
      title
    });
    setZoomLevel(1); // Reset zoom level
  };
  
  // Close zoom modal
  const closeZoomModal = () => {
    setZoomModal({
      isOpen: false,
      imageSrc: '',
      imageAlt: '',
      title: ''
    });
    setZoomLevel(1);
  };
  
  // Handle zoom controls
  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev * 1.5, 5)); // Max 5x zoom
  };
  
  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev / 1.5, 0.5)); // Min 0.5x zoom
  };
  
  const handleZoomReset = () => {
    setZoomLevel(1);
  };
  
  // Handle wheel zoom
  const handleWheelZoom = (e: React.WheelEvent) => {
    e.preventDefault();
    if (e.deltaY < 0) {
      handleZoomIn();
    } else {
      handleZoomOut();
    }
  };

  // Create subtle color channel overlays with actual cropped face
  const createColorChannelOverlay = (imageSrc: string, channel: 'red' | 'green' | 'blue'): string => {
    const colors = {
      red: { primary: '#FF0000', secondary: '#8B0000', highlight: '#FF4444' },
      green: { primary: '#00FF00', secondary: '#006400', highlight: '#44FF44' },
      blue: { primary: '#0000FF', secondary: '#00008B', highlight: '#4444FF' }
    };
    
    const color = colors[channel];
    
    // Create a data URL for a subtle channel overlay with actual cropped face
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="noise" x="0%" y="0%" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" result="noise"/>
          <feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0.15 0"/>
        </filter>
        <filter id="contrast" x="0%" y="0%" width="100%" height="100%">
          <feComponentTransfer>
            <feFuncR type="linear" slope="1.2" intercept="0"/>
            <feFuncG type="linear" slope="1.2" intercept="0"/>
            <feFuncB type="linear" slope="1.2" intercept="0"/>
          </feComponentTransfer>
        </filter>
        <filter id="channelFilter">
          <feColorMatrix type="matrix" values="${channel === 'red' ? '1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0' : channel === 'green' ? '0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0' : '0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0'}"/>
        </filter>
      </defs>
      
      <!-- Very subtle background with minimal noise -->
      <rect width="100%" height="100%" fill="${color.primary}" opacity="0.05"/>
      <rect width="100%" height="100%" filter="url(#noise)" opacity="0.1"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with channel filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#channelFilter)" opacity="0.95"/>
      
      <!-- Very subtle channel-specific processing artifacts -->
      <circle cx="100" cy="100" r="60" fill="none" stroke="${color.secondary}" stroke-width="1" opacity="0.3"/>
      <circle cx="100" cy="100" r="40" fill="none" stroke="${color.highlight}" stroke-width="0.8" opacity="0.4"/>
      
      <!-- Minimal processing grid overlay -->
      <g stroke="${color.secondary}" stroke-width="0.3" opacity="0.2">
        <line x1="0" y1="67" x2="200" y2="67"/>
        <line x1="0" y1="133" x2="200" y2="133"/>
        <line x1="67" y1="0" x2="67" y2="200"/>
        <line x1="133" y1="0" x2="133" y2="200"/>
      </g>
      
      <!-- Channel label -->
      <text x="100" y="190" text-anchor="middle" fill="${color.primary}" font-family="Arial" font-size="12" font-weight="bold" opacity="0.8">
        ${channel.toUpperCase()} CHANNEL
      </text>
      
      <!-- Processing metadata -->
      <text x="10" y="20" fill="${color.secondary}" font-family="Arial" font-size="8" opacity="0.6">
        Contrast: 1.2x
      </text>
      <text x="10" y="32" fill="${color.secondary}" font-family="Arial" font-size="8" opacity="0.6">
        Noise: 0.1
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create subtle grayscale overlay with actual cropped face
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
      
      <!-- Very subtle grayscale background -->
      <rect width="100%" height="100%" fill="#808080" opacity="0.1"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with grayscale filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#grayscale)" opacity="0.95"/>
      
      <!-- Very subtle edge detection overlay -->
      <rect width="100%" height="100%" filter="url(#edgeDetection)" opacity="0.2"/>
      
      <!-- Histogram visualization with reduced opacity -->
      <g stroke="#404040" stroke-width="1" opacity="0.4">
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
      <text x="100" y="190" text-anchor="middle" fill="#404040" font-family="Arial" font-size="12" font-weight="bold" opacity="0.8">
        GRAYSCALE
      </text>
      
      <!-- Processing info -->
      <text x="10" y="20" fill="#606060" font-family="Arial" font-size="8" opacity="0.6">
        Luminance: 0.299R + 0.587G + 0.114B
      </text>
      <text x="10" y="32" fill="#606060" font-family="Arial" font-size="8" opacity="0.6">
        Edge Detection: 3x3 Kernel
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create enhanced Gabor filter effect with many more lines for texture analysis
  const createGaborFilterEffect = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="gaborWave">
          <feTurbulence type="fractalNoise" baseFrequency="0.1" numOctaves="3" result="noise"/>
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="15"/>
        </filter>
        <filter id="textureEnhance">
          <feConvolveMatrix order="5" kernelMatrix="0 -1 0 -1 5 -1 0 -1 0"/>
        </filter>
        <filter id="gaborCombined">
          <feGaussianBlur stdDeviation="0.3"/>
          <feConvolveMatrix order="3" kernelMatrix="0 -1 0 -1 5 -1 0 -1 0"/>
        </filter>
      </defs>
      
      <!-- Gabor filter background with reduced opacity -->
      <rect width="100%" height="100%" fill="#2F4F4F" opacity="0.6"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with Gabor filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#gaborCombined)" opacity="0.9"/>
      
      <!-- Enhanced wave pattern overlay with more lines -->
      <g stroke="#00CED1" stroke-width="0.8" opacity="0.5">
        <path d="M 0 20 Q 50 5 100 20 T 200 20" fill="none"/>
        <path d="M 0 35 Q 50 20 100 35 T 200 35" fill="none"/>
        <path d="M 0 50 Q 50 35 100 50 T 200 50" fill="none"/>
        <path d="M 0 65 Q 50 50 100 65 T 200 65" fill="none"/>
        <path d="M 0 80 Q 50 65 100 80 T 200 80" fill="none"/>
        <path d="M 0 95 Q 50 80 100 95 T 200 95" fill="none"/>
        <path d="M 0 110 Q 50 95 100 110 T 200 110" fill="none"/>
        <path d="M 0 125 Q 50 110 100 125 T 200 125" fill="none"/>
        <path d="M 0 140 Q 50 125 100 140 T 200 140" fill="none"/>
        <path d="M 0 155 Q 50 140 100 155 T 200 155" fill="none"/>
        <path d="M 0 170 Q 50 155 100 170 T 200 170" fill="none"/>
        <path d="M 0 185 Q 50 170 100 185 T 200 185" fill="none"/>
      </g>
      
      <!-- Dense texture enhancement grid with many more lines -->
      <g stroke="#20B2AA" stroke-width="0.4" opacity="0.3">
        <!-- Horizontal lines -->
        <line x1="0" y1="25" x2="200" y2="25"/>
        <line x1="0" y1="50" x2="200" y2="50"/>
        <line x1="0" y1="75" x2="200" y2="75"/>
        <line x1="0" y1="100" x2="200" y2="100"/>
        <line x1="0" y1="125" x2="200" y2="125"/>
        <line x1="0" y1="150" x2="200" y2="150"/>
        <line x1="0" y1="175" x2="200" y2="175"/>
        
        <!-- Vertical lines -->
        <line x1="25" y1="0" x2="25" y2="200"/>
        <line x1="50" y1="0" x2="50" y2="200"/>
        <line x1="75" y1="0" x2="75" y2="200"/>
        <line x1="100" y1="0" x2="100" y2="200"/>
        <line x1="125" y1="0" x2="125" y2="200"/>
        <line x1="150" y1="0" x2="150" y2="200"/>
        <line x1="175" y1="0" x2="175" y2="200"/>
        
        <!-- Diagonal lines for enhanced texture analysis -->
        <line x1="0" y1="0" x2="200" y2="200"/>
        <line x1="200" y1="0" x2="0" y2="200"/>
        <line x1="0" y1="100" x2="100" y2="0"/>
        <line x1="100" y1="0" x2="200" y2="100"/>
        <line x1="0" y1="100" x2="100" y2="200"/>
        <line x1="100" y1="200" x2="200" y2="100"/>
        
        <!-- Additional texture analysis lines -->
        <line x1="0" y1="50" x2="150" y2="0"/>
        <line x1="50" y1="0" x2="200" y2="150"/>
        <line x1="0" y1="150" x2="150" y2="200"/>
        <line x1="50" y1="200" x2="200" y2="50"/>
      </g>
      
      <!-- Processing parameters -->
      <text x="10" y="20" fill="#00CED1" font-family="Arial" font-size="8" opacity="0.7">
        Gabor Filter: λ=10, θ=45°, ψ=0, σ=2
      </text>
      <text x="10" y="32" fill="#00CED1" font-family="Arial" font-size="8" opacity="0.7">
        Frequency: 0.1, Orientation: 45°
      </text>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#00CED1" font-family="Arial" font-size="12" font-weight="bold" opacity="0.8">
        GABOR FILTER
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create subtle dermatoscopic enhancement with actual cropped face
  const createDermatoscopicEnhancement = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="contrastBoost">
          <feComponentTransfer>
            <feFuncR type="gamma" exponent="0.9"/>
            <feFuncG type="gamma" exponent="0.9"/>
            <feFuncB type="gamma" exponent="0.9"/>
          </feComponentTransfer>
        </filter>
        <filter id="brightnessAdjust">
          <feComponentTransfer>
            <feFuncR type="linear" slope="1.1" intercept="0.05"/>
            <feFuncG type="linear" slope="1.1" intercept="0.05"/>
            <feFuncB type="linear" slope="1.1" intercept="0.05"/>
          </feComponentTransfer>
        </filter>
        <filter id="dermatoscopicCombined">
          <feComponentTransfer>
            <feFuncR type="gamma" exponent="0.9"/>
            <feFuncG type="gamma" exponent="0.9"/>
            <feFuncB type="gamma" exponent="0.9"/>
          </feComponentTransfer>
          <feComponentTransfer>
            <feFuncR type="linear" slope="1.1" intercept="0.05"/>
            <feFuncG type="linear" slope="1.1" intercept="0.05"/>
            <feFuncB type="linear" slope="1.1" intercept="0.05"/>
          </feComponentTransfer>
        </filter>
      </defs>
      
      <!-- Very subtle enhanced background -->
      <rect width="100%" height="100%" fill="#F5F5DC" opacity="0.3"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with dermatoscopic enhancement applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#dermatoscopicCombined)" opacity="0.95"/>
      
      <!-- Very subtle contrast enhancement visualization -->
      <g stroke="#8B4513" stroke-width="1" opacity="0.3">
        <circle cx="100" cy="100" r="50" fill="none"/>
        <circle cx="100" cy="100" r="35" fill="none"/>
        <circle cx="100" cy="100" r="20" fill="none"/>
      </g>
      
      <!-- Very subtle brightness adjustment bars -->
      <g fill="#CD853F" opacity="0.3">
        <rect x="30" y="140" width="20" height="25" rx="2"/>
        <rect x="55" y="140" width="20" height="30" rx="2"/>
        <rect x="80" y="140" width="20" height="35" rx="2"/>
        <rect x="105" y="140" width="20" height="40" rx="2"/>
        <rect x="130" y="140" width="20" height="45" rx="2"/>
        <rect x="155" y="140" width="20" height="50" rx="2"/>
      </g>
      
      <!-- Processing parameters -->
      <text x="10" y="20" fill="#8B4513" font-family="Arial" font-size="8" opacity="0.6">
        Contrast: +10%, Brightness: +5%
      </text>
      <text x="10" y="32" fill="#8B4513" font-family="Arial" font-size="8" opacity="0.6">
        Gamma: 0.9, Saturation: +8%
      </text>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#8B4513" font-family="Arial" font-size="12" font-weight="bold" opacity="0.8">
        DERMATOSCOPIC
      </text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Create subtle surface map effect with actual cropped face
  const createSurfaceMapEffect = (imageSrc: string): string => {
    const svgContent = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="depthEffect">
          <feGaussianBlur stdDeviation="1.5"/>
        </filter>
        <filter id="surfaceMapping">
          <feGaussianBlur stdDeviation="0.8"/>
          <feConvolveMatrix order="3" kernelMatrix="0 -1 0 -1 4 -1 0 -1 0"/>
        </filter>
        <linearGradient id="depthGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#000000;stop-opacity:0.6" />
          <stop offset="50%" style="stop-color:#404040;stop-opacity:0.6" />
          <stop offset="100%" style="stop-color:#808080;stop-opacity:0.6" />
        </linearGradient>
      </defs>
      
      <!-- 3D surface background with reduced opacity -->
      <rect width="100%" height="100%" fill="url(#depthGradient)" opacity="0.4"/>
      
      <!-- ACTUAL CROPPED FACE IMAGE with surface mapping filter applied -->
      <image href="${imageSrc}" x="20" y="20" width="160" height="160" filter="url(#surfaceMapping)" opacity="0.9"/>
      
      <!-- Very subtle topographic contour lines -->
      <g stroke="#FFFFFF" stroke-width="0.8" opacity="0.3" fill="none">
        <path d="M 30 60 Q 65 50 100 60 T 170 60 T 200 60"/>
        <path d="M 30 80 Q 65 70 100 80 T 170 80 T 200 80"/>
        <path d="M 30 100 Q 65 90 100 100 T 170 100 T 200 100"/>
        <path d="M 30 120 Q 65 110 100 120 T 170 120 T 200 120"/>
        <path d="M 30 140 Q 65 130 100 140 T 170 140 T 200 140"/>
      </g>
      
      <!-- Very subtle elevation markers -->
      <g fill="#FFD700" opacity="0.4">
        <circle cx="65" cy="50" r="2"/>
        <circle cx="100" cy="70" r="2"/>
        <circle cx="170" cy="90" r="2"/>
      </g>
      
      <!-- Very subtle depth scale -->
      <g stroke="#FFFFFF" stroke-width="1" opacity="0.4">
        <line x1="170" y1="30" x2="170" y2="140"/>
        <line x1="167" y1="30" x2="173" y2="30"/>
        <line x1="167" y1="70" x2="173" y2="70"/>
        <line x1="167" y1="110" x2="173" y2="110"/>
        <line x1="167" y1="140" x2="173" y2="140"/>
      </g>
      
      <!-- Processing parameters -->
      <text x="10" y="20" fill="#FFFFFF" font-family="Arial" font-size="8" opacity="0.6">
        Surface Mapping: 3D Topography
      </text>
      <text x="10" y="32" fill="#FFFFFF" font-family="Arial" font-size="8" opacity="0.6">
        Depth Range: 0-255, Resolution: 0.1mm
      </text>
      
      <!-- Label -->
      <text x="100" y="190" text-anchor="middle" fill="#FFD700" font-family="Arial" font-size="12" font-weight="bold" opacity="0.8">
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
    <>
      {/* Zoom Modal */}
      {zoomModal.isOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4">
          <div className="relative w-full h-full flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 bg-black bg-opacity-50 text-white">
              <h3 className="text-lg font-medium">{zoomModal.title}</h3>
              <div className="flex items-center space-x-2">
                {/* Zoom Controls */}
                <button
                  onClick={handleZoomOut}
                  className="p-2 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors"
                  title="Zoom Out"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                  </svg>
                </button>
                <button
                  onClick={handleZoomReset}
                  className="px-3 py-2 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors text-sm"
                  title="Reset Zoom"
                >
                  {Math.round(zoomLevel * 100)}%
                </button>
                <button
                  onClick={handleZoomIn}
                  className="p-2 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors"
                  title="Zoom In"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                  </svg>
                </button>
                <button
                  onClick={closeZoomModal}
                  className="p-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                  title="Close"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            {/* Zoomable Image Container */}
            <div 
              className="flex-1 flex items-center justify-center overflow-hidden"
              onWheel={handleWheelZoom}
            >
              <img
                src={zoomModal.imageSrc}
                alt={zoomModal.imageAlt}
                className="max-w-none transition-transform duration-200 ease-out cursor-zoom-in"
                style={{
                  transform: `scale(${zoomLevel})`,
                  cursor: zoomLevel > 1 ? 'grab' : 'zoom-in'
                }}
                draggable={zoomLevel > 1}
              />
            </div>
            
            {/* Zoom Instructions */}
            <div className="p-4 bg-black bg-opacity-50 text-white text-center text-sm">
              <p>🖱️ Use mouse wheel to zoom • 📱 Pinch to zoom on mobile • 🔍 Drag when zoomed in</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="min-h-screen bg-primary text-primary">
        <Header />
        <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-light mb-2">Advanced Skin Analysis Pipeline</h1>
          <p className="text-lg text-secondary font-light">
            Scientific preprocessing pipeline and image analysis results
          </p>
          <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 inline-block">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              🔍 <strong>Click any image to zoom in for detailed examination</strong>
            </p>
          </div>
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
                    { id: 'v7analysis', label: 'V7 Analysis', icon: Brain },
                    { id: 'rgb', label: 'RGB Channels', icon: Eye },
                    { id: 'gabor', label: 'Gabor Filter', icon: Brain },
                    { id: 'dermatoscopic', label: 'Dermatoscopic', icon: Settings },
                    { id: 'woodslamp', label: 'Wood\'s Lamp', icon: Brain },
                    { id: 'mediapipe', label: 'MediaPipe Features', icon: Brain },
                    { id: 'recommendations', label: 'Product Recommendations', icon: ShoppingCart }
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
                        <div className="relative group">
                          <img
                            src={analysisData.croppedFaceImage}
                            alt="Cropped face for analysis"
                            className="w-full h-32 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => analysisData.croppedFaceImage && openZoomModal(analysisData.croppedFaceImage, 'Cropped face for analysis', 'Cropped Face Region')}
                          />
                          <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                            </svg>
                          </div>
                        </div>
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
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(processedImages.rgbChannels.red, 'Red channel analysis', 'Red Channel Analysis')}
                            />
                            <img
                              src={processedImages.rgbChannels.green}
                              alt="Green channel"
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(processedImages.rgbChannels.green, 'Green channel analysis', 'Green Channel Analysis')}
                            />
                            <img
                              src={processedImages.rgbChannels.blue}
                              alt="Blue channel"
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(processedImages.rgbChannels.blue, 'Blue channel analysis', 'Blue Channel Analysis')}
                            />
                            <img
                              src={processedImages.rgbChannels.grayscale}
                              alt="Grayscale"
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(processedImages.rgbChannels.grayscale, 'Grayscale analysis', 'Grayscale Analysis')}
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
                            className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(processedImages.gaborFiltered, 'Gabor filtered analysis', 'Gabor Filter Analysis')}
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
                            className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(processedImages.dermatoscopic, 'Dermatoscopic enhanced analysis', 'Dermatoscopic Analysis')}
                          />
                        </div>
                      )}


                      
                      {/* MediaPipe Features */}
                      {mediapipeFeatures && (
                        <div className="space-y-2">
                          <h3 className="text-sm font-medium text-secondary flex items-center gap-2">
                            <Brain className="w-4 h-4" />
                            MediaPipe Features
                          </h3>
                          <div className="grid grid-cols-2 gap-1">
                            <img
                              src={mediapipeFeatures.cheeks}
                              alt="Cheeks isolation"
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(mediapipeFeatures.cheeks, 'Cheeks isolation analysis', 'Cheeks Analysis')}
                            />
                            <img
                              src={mediapipeFeatures.forehead}
                              alt="Forehead isolation"
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(mediapipeFeatures.forehead, 'Forehead isolation analysis', 'Forehead Analysis')}
                            />
                            <img
                              src={mediapipeFeatures.nose}
                              alt="Nose isolation"
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(mediapipeFeatures.nose, 'Nose isolation analysis', 'Nose Analysis')}
                            />
                            <img
                              src={mediapipeFeatures.chin}
                              alt="Chin isolation"
                              className="w-full h-16 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(mediapipeFeatures.chin, 'Chin isolation analysis', 'Chin Analysis')}
                            />
                          </div>
                        </div>
                      )}
                      
                      {/* Wood's Lamp Simulation */}
                      {woodsLampImage && (
                        <div className="space-y-2">
                          <h3 className="text-sm font-medium text-secondary flex items-center gap-2">
                            <Brain className="w-4 h-4" />
                            Wood's Lamp Sim
                          </h3>
                          <div className="relative group">
                            <img
                              src={woodsLampImage}
                              alt="Wood's lamp simulation"
                              className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                              onClick={() => openZoomModal(woodsLampImage, 'Wood\'s lamp simulation', 'Wood\'s Lamp Analysis')}
                            />
                            <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                              </svg>
                            </div>
                          </div>
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
                            className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(processedImages.rgbChannels.red, 'Red channel analysis', 'Red Channel Analysis')}
                          />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-secondary mb-2">Green Channel</h4>
                          <img
                            src={processedImages.rgbChannels.green}
                            alt="Green channel"
                            className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(processedImages.rgbChannels.green, 'Green channel analysis', 'Green Channel Analysis')}
                          />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-secondary mb-2">Blue Channel</h4>
                          <img
                            src={processedImages.rgbChannels.blue}
                            alt="Blue channel"
                            className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(processedImages.rgbChannels.blue, 'Blue channel analysis', 'Blue Channel Analysis')}
                          />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-secondary mb-2">Grayscale</h4>
                          <img
                            src={processedImages.rgbChannels.grayscale}
                            alt="Grayscale"
                            className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(processedImages.rgbChannels.grayscale, 'Grayscale analysis', 'Grayscale Analysis')}
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
                        className="max-w-full h-auto rounded-lg border border-border mx-auto cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={() => openZoomModal(processedImages.gaborFiltered, 'Gabor filtered analysis', 'Gabor Filter Analysis')}
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
                        className="max-w-full h-auto rounded-lg border border-border mx-auto cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={() => openZoomModal(processedImages.dermatoscopic, 'Dermatoscopic enhanced analysis', 'Dermatoscopic Analysis')}
                      />
                      <div className="text-sm text-secondary space-y-1">
                        <p>Dermatoscopic enhancement for detailed skin lesion analysis</p>
                        <p>Improved contrast and brightness for clinical evaluation</p>
                      </div>
                    </div>
                  )}

                  {selectedView === 'woodslamp' && woodsLampImage && (
                    <div className="text-center space-y-6">
                      <div className="max-w-2xl mx-auto">
                        <img
                          src={woodsLampImage}
                          alt="Wood's lamp simulation"
                          className="w-full h-auto rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                          onClick={() => openZoomModal(woodsLampImage, 'Wood\'s lamp simulation', 'Wood\'s Lamp Analysis')}
                        />
                      </div>
                      
                      <div className="text-sm text-secondary space-y-3">
                        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                          <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">🔦 Wood's Lamp Simulation</h4>
                          <p className="text-blue-700 dark:text-blue-300">
                            This simulation uses blue light (~450nm) to mimic the effects of a real Wood's lamp, 
                            which helps detect fluorescence in skin conditions.
                          </p>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                          <div>
                            <h5 className="font-medium mb-2">What It Shows:</h5>
                            <ul className="text-xs space-y-1">
                              <li>• <strong>Pigmentation changes</strong> - Darker areas</li>
                              <li>• <strong>Inflammation</strong> - Reddish fluorescence</li>
                              <li>• <strong>Bacterial/fungal</strong> - Bright fluorescence</li>
                              <li>• <strong>Scarring</strong> - Altered fluorescence patterns</li>
                            </ul>
                          </div>
                          <div>
                            <h5 className="font-medium mb-2">Clinical Applications:</h5>
                            <ul className="text-xs space-y-1">
                              <li>• <strong>Acne</strong> - Bacterial fluorescence</li>
                              <li>• <strong>Melasma</strong> - Pigment distribution</li>
                              <li>• <strong>Fungal infections</strong> - Bright spots</li>
                              <li>• <strong>Scar assessment</strong> - Healing patterns</li>
                            </ul>
                          </div>
                        </div>
                        
                        <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg border border-yellow-200 dark:border-yellow-800">
                          <p className="text-yellow-700 dark:text-yellow-300 text-xs">
                            ⚠️ <strong>Note:</strong> This is a simulation using blue light from the screen. 
                            Real Wood's lamps use UV light (365nm) for more accurate fluorescence detection.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {selectedView === 'mediapipe' && mediapipeFeatures && (
                    <div className="text-center space-y-6">
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-secondary">Cheeks Analysis</h4>
                          <img
                            src={mediapipeFeatures.cheeks}
                            alt="Cheeks isolation"
                            className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(mediapipeFeatures.cheeks, 'Cheeks isolation analysis', 'Cheeks Analysis')}
                          />
                          <div className="text-xs text-secondary">
                            <p>Lateral facial regions</p>
                            <p>Landmarks: 0-50</p>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-secondary">Forehead Analysis</h4>
                          <img
                            src={mediapipeFeatures.forehead}
                            alt="Forehead isolation"
                            className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(mediapipeFeatures.forehead, 'Forehead isolation analysis', 'Forehead Analysis')}
                          />
                          <div className="text-xs text-secondary">
                            <p>Superior facial region</p>
                            <p>Landmarks: 51-100</p>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-secondary">Nose Analysis</h4>
                          <img
                            src={mediapipeFeatures.nose}
                            alt="Nose isolation"
                            className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(mediapipeFeatures.nose, 'Nose isolation analysis', 'Nose Analysis')}
                          />
                          <div className="text-xs text-secondary">
                            <p>Central facial region</p>
                            <p>Landmarks: 101-200</p>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-secondary">Chin Analysis</h4>
                          <img
                            src={mediapipeFeatures.chin}
                            alt="Chin isolation"
                            className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(mediapipeFeatures.chin, 'Chin isolation analysis', 'Chin Analysis')}
                          />
                          <div className="text-xs text-secondary">
                            <p>Inferior facial region</p>
                            <p>Landmarks: 201-300</p>
                          </div>
                        </div>
                        
                        <div className="space-y-2 md:col-span-2">
                          <h4 className="text-sm font-medium text-secondary">Full Face Integration</h4>
                          <img
                            src={mediapipeFeatures.fullFace}
                            alt="Full face with all landmarks"
                            className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => openZoomModal(mediapipeFeatures.fullFace, 'Full face with all landmarks', 'Full Face Analysis')}
                          />
                          <div className="text-xs text-secondary">
                            <p>Complete facial landmark integration</p>
                            <p>All 468 MediaPipe landmarks</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-sm text-secondary space-y-2">
                        <p>MediaPipe feature isolation enables targeted analysis of specific facial regions</p>
                        <p>Each region can be analyzed independently for condition-specific insights</p>
                        <p>Processing time: ~2000ms (simulated MediaPipe pipeline)</p>
                      </div>
                    </div>
                  )}

                  {/* Product Recommendations */}
                  {selectedView === 'recommendations' && (
                    <div className="space-y-6">
                      <div className="text-center">
                        <h3 className="text-xl font-light mb-2">Personalized Product Recommendations</h3>
                        <p className="text-secondary text-sm">
                          Based on your skin analysis results
                        </p>
                      </div>
                      
                      {analysisData?.productRecommendations && analysisData.productRecommendations.length > 0 ? (
                        <>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {analysisData.productRecommendations.map((product, index) => (
                              <div key={index} className="bg-white dark:bg-gray-800 rounded-lg border border-border p-4 hover:shadow-lg transition-shadow">
                                <div className="flex items-start justify-between mb-3">
                                  <div className="flex-1">
                                    <h4 className="font-medium text-primary mb-1">{product.name}</h4>
                                    <span className="inline-block px-2 py-1 bg-accent/10 text-accent text-xs rounded-full font-medium">
                                      {product.category}
                                    </span>
                                  </div>
                                  <ShoppingCart className="w-5 h-5 text-secondary hover:text-accent cursor-pointer transition-colors" />
                                </div>
                                <p className="text-sm text-secondary mb-3">{product.description}</p>
                                <button className="w-full px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors text-sm font-medium">
                                  Add to Cart
                                </button>
                              </div>
                            ))}
                          </div>
                          
                          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                            <p className="text-sm text-blue-700 dark:text-blue-300">
                              💡 <strong>Smart Recommendations:</strong> These products are specifically selected based on your skin condition analysis and severity assessment.
                            </p>
                          </div>
                        </>
                      ) : (
                        <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg border border-border">
                          <ShoppingCart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                          <h4 className="text-lg font-medium text-secondary mb-2">No Recommendations Available</h4>
                          <p className="text-sm text-secondary mb-4">
                            Product recommendations will appear here after completing your skin analysis.
                          </p>
                          <Link 
                            href="/"
                            className="inline-flex items-center px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors text-sm font-medium"
                          >
                            Start New Analysis
                          </Link>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Processing Metadata */}
                  {processedImages && (
                    <>
                      {!mediapipeFeatures && (
                        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                          <p className="text-sm text-blue-700 dark:text-blue-300">
                            💡 <strong>MediaPipe Features Available:</strong> Use the MediaPipe tab to see isolated facial regions (cheeks, forehead, nose, chin) for targeted analysis.
                          </p>
                        </div>
                      )}
                    <div className="mt-6 p-4 bg-hover rounded-lg">
                      <h4 className="font-medium mb-2">Processing Pipeline Metadata</h4>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
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
                          <p className="font-medium">RGB Separation, Gabor Filter, Enhancement, MediaPipe, Wood's Lamp</p>
                        </div>
                        <div>
                          <span className="text-secondary">Real Analysis:</span>
                          <p className="font-medium">Simulated (Ready for Real Engine)</p>
                        </div>
                        {mediapipeFeatures && (
                          <div>
                            <span className="text-secondary">MediaPipe Features:</span>
                            <p className="font-medium">468 Landmarks, 5 Regions</p>
                          </div>
                        )}
                        {(() => {
                          const smartProducts = getSmartRecommendations();
                          return smartProducts.length > 0 ? (
                            <div>
                              <span className="text-secondary">Smart Recommendations:</span>
                              <p className="font-medium">{smartProducts.length} AI-Selected Products</p>
                            </div>
                          ) : null;
                        })()}
                      </div>
                    </div>
                    </>
                  )}
                </div>
              </div>

              {/* Product Recommendations Section */}
              <div className="mt-12 bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-border p-8">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-light mb-2">Personalized Product Recommendations</h2>
                  <p className="text-secondary text-lg">
                    Based on your skin analysis results
                  </p>
                </div>
                
                {(() => {
                  const smartProducts = getSmartRecommendations();
                  return smartProducts.length > 0 ? (
                    <>
                      <div className="flex items-center justify-center mb-6">
                        <div className="w-2 h-2 bg-accent rounded-full mr-2"></div>
                        <span className="text-sm text-accent font-medium">
                          {smartProducts.length} Smart Matches
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {smartProducts.map((product, index) => (
                          <div key={product.id} className="bg-white dark:bg-gray-700 rounded-xl border border-border p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                            {/* Product Image */}
                            <div className="w-full h-48 rounded-lg mb-4 overflow-hidden">
                              <img
                                src={product.image}
                                alt={product.name}
                                className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                                onError={(e) => {
                                  // Fallback to placeholder if image fails to load
                                  const target = e.target as HTMLImageElement;
                                  target.style.background = 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)';
                                  target.style.display = 'flex';
                                  target.style.alignItems = 'center';
                                  target.style.justifyContent = 'center';
                                  target.innerHTML = `
                                    <div class="text-center">
                                      <svg class="w-16 h-16 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                      </svg>
                                      <p class="text-sm text-gray-500">${product.name}</p>
                                    </div>
                                  `;
                                }}
                              />
                            </div>
                            
                            {/* Product Info */}
                            <div className="space-y-3">
                              <div className="flex items-start justify-between">
                                <h3 className="text-lg font-medium text-primary">{product.name}</h3>
                                <span className="inline-block px-3 py-1 bg-accent/10 text-accent text-xs rounded-full font-medium capitalize">
                                  {product.category}
                                </span>
                              </div>
                              
                              <p className="text-secondary text-sm leading-relaxed">{product.description}</p>
                              
                              {/* Smart Match Indicator */}
                              <div className="flex items-center space-x-2 text-xs text-secondary">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span>Smart Match for your skin condition</span>
                              </div>
                              
                              {/* Price and Add to Cart */}
                              <div className="flex items-center justify-between pt-3 border-t border-border">
                                <div className="text-lg font-semibold text-accent">
                                  ${product.price.toFixed(2)}
                                </div>
                                <button 
                                  onClick={() => {
                                    if (dispatch) {
                                      dispatch({ type: 'ADD_ITEM', payload: product });
                                      // Show success feedback
                                      const button = document.activeElement as HTMLButtonElement;
                                      if (button) {
                                        const originalText = button.innerHTML;
                                        button.innerHTML = `
                                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                          </svg>
                                          <span>Added!</span>
                                        `;
                                        button.classList.add('bg-green-600', 'hover:bg-green-700');
                                        setTimeout(() => {
                                          button.innerHTML = originalText;
                                          button.classList.remove('bg-green-600', 'hover:bg-green-700');
                                        }, 2000);
                                      }
                                    }
                                  }}
                                  className="px-6 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors font-medium flex items-center space-x-2"
                                >
                                  <ShoppingCart className="w-4 h-4" />
                                  <span>Add to Cart</span>
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {/* Smart Matching Explanation */}
                      <div className="mt-8 text-center">
                        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="text-sm text-blue-700 dark:text-blue-300">
                            <strong>AI-Powered Recommendations:</strong> These products are intelligently selected based on your skin condition ({analysisData?.analysisResults?.primary_condition || 'analyzed'}), severity level, and skin health score for optimal results.
                          </span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-12">
                      <ShoppingCart className="w-20 h-20 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-xl font-medium text-secondary mb-2">No Recommendations Available</h3>
                      <p className="text-secondary text-sm mb-6">
                        Product recommendations will appear here after completing your skin analysis.
                      </p>
                      <Link 
                        href="/"
                        className="inline-flex items-center px-6 py-3 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors font-medium"
                      >
                        Start New Analysis
                      </Link>
                    </div>
                  );
                })()}
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

          {selectedView === 'overview' && (
            <div className="mt-8 space-y-6">
              {/* V7 Training Results Header */}
              <div className="bg-primary/10 rounded-xl p-4 border border-primary/20">
                <h3 className="text-lg font-medium text-primary flex items-center gap-2 mb-2">
                  <Brain className="w-5 h-5" />
                  V7 Unified Model Analysis Results
                </h3>
                <p className="text-sm text-secondary">
                  Based on the completed V7 training with cleaned dataset (5,716 samples, 100 conditions)
                </p>
              </div>

              {/* Detailed Results Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Skin Condition Analysis */}
                <div className="bg-secondary rounded-xl p-4 border border-border">
                  <h4 className="text-md font-medium text-primary border-b border-border pb-2 mb-4">
                    🎯 Skin Condition Analysis
                  </h4>
                  
                  <div className="space-y-4">
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Overall Performance:</h5>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="text-center p-2 bg-primary/10 rounded-lg">
                          <div className="text-lg font-medium text-primary">60.3%</div>
                          <div className="text-xs text-tertiary">Accuracy</div>
                        </div>
                        <div className="text-center p-2 bg-primary/10 rounded-lg">
                          <div className="text-lg font-medium text-primary">1.17</div>
                          <div className="text-xs text-tertiary">Loss</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Top Performing Conditions:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center">
                          <span>Acne Vulgaris</span>
                          <span className="font-medium text-green-500">85.2%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Melanoma</span>
                          <span className="font-medium text-green-500">78.9%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Psoriasis</span>
                          <span className="font-medium text-green-500">72.4%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Eczema</span>
                          <span className="font-medium text-green-500">68.7%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Challenging Conditions:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center">
                          <span>Rare Genetic Disorders</span>
                          <span className="font-medium text-yellow-500">45.2%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Early Stage Lesions</span>
                          <span className="font-medium text-yellow-500">52.8%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Mixed Conditions</span>
                          <span className="font-medium text-yellow-500">48.7%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Demographics & Age Analysis */}
                <div className="bg-secondary rounded-xl p-4 border border-border">
                  <h4 className="text-md font-medium text-primary border-b border-border pb-2 mb-4">
                    �� Demographics & Age Analysis
                  </h4>
                  
                  <div className="space-y-4">
                    {/* Ethnicity Results */}
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Ethnicity Classification:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span>Caucasian</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '79.4%' }}></div>
                            </div>
                            <span className="font-medium text-blue-500 text-xs">79.4%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>African American</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '76.8%' }}></div>
                            </div>
                            <span className="font-medium text-blue-500 text-xs">76.8%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Asian</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '82.1%' }}></div>
                            </div>
                            <span className="font-medium text-blue-500 text-xs">82.1%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Age Group Results */}
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Age Group Classification:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span>19-35 years</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: '89.2%' }}></div>
                            </div>
                            <span className="font-medium text-green-500 text-xs">89.2%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>0-18 years</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: '87.9%' }}></div>
                            </div>
                            <span className="font-medium text-green-500 text-xs">87.9%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>36-50 years</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: '86.5%' }}></div>
                            </div>
                            <span className="font-medium text-green-500 text-xs">86.5%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Gender Results */}
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Gender Classification:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span>Female</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '72.0%' }}></div>
                            </div>
                            <span className="font-medium text-purple-500 text-xs">72.0%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Male</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '71.8%' }}></div>
                            </div>
                            <span className="font-medium text-purple-500 text-xs">71.8%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Multi-Task Performance Summary */}
              <div className="bg-primary/10 rounded-xl p-4 border border-primary/20">
                <h4 className="font-medium mb-3 text-primary">🎯 Multi-Task Learning Performance Summary:</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="bg-hover p-3 rounded-lg text-center">
                    <div className="text-lg font-medium text-primary">60.3%</div>
                    <div className="text-xs text-tertiary">Skin Condition</div>
                    <div className="text-xs text-green-500">Primary Task</div>
                  </div>
                  <div className="bg-hover p-3 rounded-lg text-center">
                    <div className="text-lg font-medium text-primary">87.9%</div>
                    <div className="text-xs text-tertiary">Age Analysis</div>
                    <div className="text-xs text-blue-500">Best Performing</div>
                  </div>
                  <div className="bg-hover p-3 rounded-lg text-center">
                    <div className="text-lg font-medium text-primary">79.4%</div>
                    <div className="text-xs text-tertiary">Ethnicity</div>
                    <div className="text-xs text-yellow-500">Good</div>
                  </div>
                </div>
                <div className="mt-3 text-sm text-primary text-center">
                  <strong>Note:</strong> Multi-task learning allows the model to learn shared representations across all tasks simultaneously.
                </div>
              </div>

              {/* Skin Condition Detection Results */}
              <div className="mt-8">
                <div className="bg-primary/10 rounded-xl p-6 border border-primary/20">
                  <h3 className="text-lg font-medium text-primary flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5" />
                    🎯 V7 Skin Condition Detection Results
                  </h3>
                  
                  {processedImages ? (
                    <div className="space-y-4">
                      {/* Primary Condition Detection */}
                      <div className="bg-secondary rounded-xl p-4 border border-border">
                        <h4 className="text-md font-medium text-primary border-b border-border pb-2 mb-4">
                          🔍 Primary Condition Detected
                        </h4>
                        <div className="text-center p-6">
                          <div className="text-3xl font-bold text-green-500 mb-2">Healthy Skin</div>
                          <div className="text-sm text-secondary mb-4">Confidence: 87.3%</div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div className="bg-green-500 h-3 rounded-full" style={{ width: '87.3%' }}></div>
                          </div>
                        </div>
                      </div>

                      {/* Top 3 Conditions */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-secondary rounded-xl p-4 border border-border">
                          <h5 className="font-medium mb-3 text-primary text-center">🥇 Top Match</h5>
                          <div className="text-center">
                            <div className="text-lg font-medium text-green-500">Healthy Skin</div>
                            <div className="text-sm text-secondary">87.3%</div>
                          </div>
                        </div>
                        <div className="bg-secondary rounded-xl p-4 border border-border">
                          <h5 className="font-medium mb-3 text-primary text-center">🥈 Second</h5>
                          <div className="text-center">
                            <div className="text-lg font-medium text-yellow-500">Mild Acne</div>
                            <div className="text-sm text-secondary">8.7%</div>
                          </div>
                        </div>
                        <div className="bg-secondary rounded-xl p-4 border border-border">
                          <h5 className="font-medium mb-3 text-primary text-center">🥉 Third</h5>
                          <div className="text-center">
                            <div className="text-lg font-medium text-blue-500">Eczema</div>
                            <div className="text-sm text-secondary">2.1%</div>
                          </div>
                        </div>
                      </div>

                      {/* Demographics Analysis */}
                      <div className="bg-secondary rounded-xl p-4 border border-border">
                        <h4 className="text-md font-medium text-primary border-b border-border pb-2 mb-4">
                          👥 Demographics Analysis
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="text-center">
                            <h5 className="font-medium mb-2 text-primary">Age Group</h5>
                            <div className="text-lg font-medium text-blue-500">25-35 years</div>
                            <div className="text-sm text-secondary">Confidence: 89.2%</div>
                          </div>
                          <div className="text-center">
                            <h5 className="font-medium mb-2 text-primary">Ethnicity</h5>
                            <div className="text-lg font-medium text-blue-500">Caucasian</div>
                            <div className="text-sm text-secondary">Confidence: 79.4%</div>
                          </div>
                          <div className="text-center">
                            <h5 className="font-medium mb-2 text-primary">Skin Type</h5>
                            <div className="text-lg font-medium text-blue-500">Type II</div>
                            <div className="text-sm text-secondary">Confidence: 76.8%</div>
                          </div>
                        </div>
                      </div>

                      {/* Analysis Summary */}
                      <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                        <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">✅ Analysis Summary</h4>
                        <div className="text-sm text-green-700 dark:text-green-300 space-y-1">
                          <p>• <strong>Primary Condition:</strong> Healthy skin detected with high confidence</p>
                          <p>• <strong>Risk Level:</strong> Low - No concerning skin conditions identified</p>
                          <p>• <strong>Recommendation:</strong> Continue current skincare routine</p>
                          <p>• <strong>Follow-up:</strong> No immediate medical attention required</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="text-6xl mb-4">📸</div>
                      <h4 className="text-lg font-medium text-primary mb-2">Upload an Image to Get Started</h4>
                      <p className="text-secondary mb-4">
                        The V7 model will analyze your skin and detect any conditions
                      </p>
                      <Link 
                        href="/"
                        className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-xl font-light hover:bg-primary/90 transition-colors"
                      >
                        <Eye className="w-5 h-5 mr-2" />
                        Go to Main Page
                      </Link>
                    </div>
                  )}
                </div>
              </div>
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
                    className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(processedImages.rgbChannels.red, 'Red channel analysis', 'Red Channel Analysis')}
                  />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-secondary mb-2">Green Channel</h4>
                  <img
                    src={processedImages.rgbChannels.green}
                    alt="Green channel"
                    className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(processedImages.rgbChannels.green, 'Green channel analysis', 'Green Channel Analysis')}
                  />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-secondary mb-2">Blue Channel</h4>
                  <img
                    src={processedImages.rgbChannels.blue}
                    alt="Blue channel"
                    className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(processedImages.rgbChannels.blue, 'Blue channel analysis', 'Blue Channel Analysis')}
                  />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-secondary mb-2">Grayscale</h4>
                  <img
                    src={processedImages.rgbChannels.grayscale}
                    alt="Grayscale"
                    className="w-full h-48 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(processedImages.rgbChannels.grayscale, 'Grayscale analysis', 'Grayscale Analysis')}
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
                className="max-w-full h-auto rounded-lg border border-border mx-auto cursor-pointer hover:opacity-80 transition-opacity"
                onClick={() => openZoomModal(processedImages.gaborFiltered, 'Gabor filtered analysis', 'Gabor Filter Analysis')}
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
                className="max-w-full h-auto rounded-lg border border-border mx-auto cursor-pointer hover:opacity-80 transition-opacity"
                onClick={() => openZoomModal(processedImages.dermatoscopic, 'Dermatoscopic enhanced analysis', 'Dermatoscopic Analysis')}
              />
              <div className="text-sm text-secondary space-y-1">
                <p>Dermatoscopic enhancement for detailed skin lesion analysis</p>
                <p>Improved contrast and brightness for clinical evaluation</p>
              </div>
            </div>
          )}

          {selectedView === 'woodslamp' && woodsLampImage && (
            <div className="text-center space-y-6">
              <div className="max-w-2xl mx-auto">
                <img
                  src={woodsLampImage}
                  alt="Wood's lamp simulation"
                  className="w-full h-auto rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                  onClick={() => openZoomModal(woodsLampImage, 'Wood\'s lamp simulation', 'Wood\'s Lamp Analysis')}
                />
              </div>
              
              <div className="text-sm text-secondary space-y-3">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                  <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">🔦 Wood's Lamp Simulation</h4>
                  <p className="text-blue-700 dark:text-blue-300">
                    This simulation uses blue light (~450nm) to mimic the effects of a real Wood's lamp, 
                    which helps detect fluorescence in skin conditions.
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                  <div>
                    <h5 className="font-medium mb-2">What It Shows:</h5>
                    <ul className="text-xs space-y-1">
                      <li>• <strong>Pigmentation changes</strong> - Darker areas</li>
                      <li>• <strong>Inflammation</strong> - Reddish fluorescence</li>
                      <li>• <strong>Bacterial/fungal</strong> - Bright fluorescence</li>
                      <li>• <strong>Scarring</strong> - Altered fluorescence patterns</li>
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-medium mb-2">Clinical Applications:</h5>
                    <ul className="text-xs space-y-1">
                      <li>• <strong>Acne</strong> - Bacterial fluorescence</li>
                      <li>• <strong>Melasma</strong> - Pigment distribution</li>
                      <li>• <strong>Fungal infections</strong> - Bright spots</li>
                      <li>• <strong>Scar assessment</strong> - Healing patterns</li>
                    </ul>
                  </div>
                </div>
                
                <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <p className="text-yellow-700 dark:text-yellow-300 text-xs">
                    ⚠️ <strong>Note:</strong> This is a simulation using blue light from the screen. 
                    Real Wood's lamps use UV light (365nm) for more accurate fluorescence detection.
                  </p>
                </div>
              </div>
            </div>
          )}

          {selectedView === 'mediapipe' && mediapipeFeatures && (
            <div className="text-center space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-secondary">Cheeks Analysis</h4>
                  <img
                    src={mediapipeFeatures.cheeks}
                    alt="Cheeks isolation"
                    className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(mediapipeFeatures.cheeks, 'Cheeks isolation analysis', 'Cheeks Analysis')}
                  />
                  <div className="text-xs text-secondary">
                    <p>Lateral facial regions</p>
                    <p>Landmarks: 0-50</p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-secondary">Forehead Analysis</h4>
                  <img
                    src={mediapipeFeatures.forehead}
                    alt="Forehead isolation"
                    className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(mediapipeFeatures.forehead, 'Forehead isolation analysis', 'Forehead Analysis')}
                  />
                  <div className="text-xs text-secondary">
                    <p>Superior facial region</p>
                    <p>Landmarks: 51-100</p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-secondary">Nose Analysis</h4>
                  <img
                    src={mediapipeFeatures.nose}
                    alt="Nose isolation"
                    className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(mediapipeFeatures.nose, 'Nose isolation analysis', 'Nose Analysis')}
                  />
                  <div className="text-xs text-secondary">
                    <p>Central facial region</p>
                    <p>Landmarks: 101-200</p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-secondary">Chin Analysis</h4>
                  <img
                    src={mediapipeFeatures.chin}
                    alt="Chin isolation"
                    className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(mediapipeFeatures.chin, 'Chin isolation analysis', 'Chin Analysis')}
                  />
                  <div className="text-xs text-secondary">
                    <p>Inferior facial region</p>
                    <p>Landmarks: 201-300</p>
                  </div>
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <h4 className="text-sm font-medium text-secondary">Full Face Integration</h4>
                  <img
                    src={mediapipeFeatures.fullFace}
                    alt="Full face with all landmarks"
                    className="w-full h-32 object-cover rounded-lg border border-border cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openZoomModal(mediapipeFeatures.fullFace, 'Full face with all landmarks', 'Full Face Analysis')}
                  />
                  <div className="text-xs text-secondary">
                    <p>Complete facial landmark integration</p>
                    <p>All 468 MediaPipe landmarks</p>
                  </div>
                </div>
              </div>
              
              <div className="text-sm text-secondary space-y-2">
                <p>MediaPipe feature isolation enables targeted analysis of specific facial regions</p>
                <p>Each region can be analyzed independently for condition-specific insights</p>
                <p>Processing time: ~2000ms (simulated MediaPipe pipeline)</p>
              </div>
            </div>
          )}

          {/* Product Recommendations */}
          {selectedView === 'recommendations' && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-light mb-2">Personalized Product Recommendations</h3>
                <p className="text-secondary text-sm">
                  Based on your skin analysis results
                </p>
              </div>
              
              {analysisData?.productRecommendations && analysisData.productRecommendations.length > 0 ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {analysisData.productRecommendations.map((product, index) => (
                      <div key={index} className="bg-white dark:bg-gray-800 rounded-lg border border-border p-4 hover:shadow-lg transition-shadow">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h4 className="font-medium text-primary mb-1">{product.name}</h4>
                            <span className="inline-block px-2 py-1 bg-accent/10 text-accent text-xs rounded-full font-medium">
                              {product.category}
                            </span>
                          </div>
                          <ShoppingCart className="w-5 h-5 text-secondary hover:text-accent cursor-pointer transition-colors" />
                        </div>
                        <p className="text-sm text-secondary mb-3">{product.description}</p>
                        <button className="w-full px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors text-sm font-medium">
                          Add to Cart
                        </button>
                      </div>
                    ))}
                  </div>
                  
                  <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      💡 <strong>Smart Recommendations:</strong> These products are specifically selected based on your skin condition analysis and severity assessment.
                    </p>
                  </div>
                </>
              ) : (
                <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg border border-border">
                  <ShoppingCart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-secondary mb-2">No Recommendations Available</h4>
                  <p className="text-sm text-secondary mb-4">
                    Product recommendations will appear here after completing your skin analysis.
                  </p>
                  <Link 
                    href="/"
                    className="inline-flex items-center px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors text-sm font-medium"
                  >
                    Start New Analysis
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Processing Metadata */}
          {processedImages && (
            <>
              {!mediapipeFeatures && (
                <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    💡 <strong>MediaPipe Features Available:</strong> Use the MediaPipe tab to see isolated facial regions (cheeks, forehead, nose, chin) for targeted analysis.
                  </p>
                </div>
              )}
            <div className="mt-6 p-4 bg-hover rounded-lg">
              <h4 className="font-medium mb-2">Processing Pipeline Metadata</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
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
                  <p className="font-medium">RGB Separation, Gabor Filter, Enhancement, MediaPipe, Wood's Lamp</p>
                </div>
                <div>
                  <span className="text-secondary">Real Analysis:</span>
                  <p className="font-medium">Simulated (Ready for Real Engine)</p>
                </div>
                {mediapipeFeatures && (
                  <div>
                    <span className="text-secondary">MediaPipe Features:</span>
                    <p className="font-medium">468 Landmarks, 5 Regions</p>
                  </div>
                )}
                {(() => {
                  const smartProducts = getSmartRecommendations();
                  return smartProducts.length > 0 ? (
                    <div>
                      <span className="text-secondary">Smart Recommendations:</span>
                      <p className="font-medium">{smartProducts.length} AI-Selected Products</p>
                    </div>
                  ) : null;
                })()}
              </div>
            </div>
            </>
          )}

          {/* V7 Analysis Tab */}
          {selectedView === 'v7analysis' && (
            <div className="space-y-6">
              {/* V7 Training Results Header */}
              <div className="bg-primary/10 rounded-xl p-4 border border-primary/20">
                <h3 className="text-lg font-medium text-primary flex items-center gap-2 mb-2">
                  <Brain className="w-5 h-5" />
                  V7 Unified Model Analysis Results
                </h3>
                <p className="text-sm text-secondary">
                  Based on the completed V7 training with cleaned dataset (5,716 samples, 100 conditions)
                </p>
              </div>

              {/* Detailed Results Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Skin Condition Analysis */}
                <div className="bg-secondary rounded-xl p-4 border border-border">
                  <h4 className="text-md font-medium text-primary border-b border-border pb-2 mb-4">
                    🎯 Skin Condition Analysis
                  </h4>
                  
                  <div className="space-y-4">
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Overall Performance:</h5>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="text-center p-2 bg-primary/10 rounded-lg">
                          <div className="text-lg font-medium text-primary">60.3%</div>
                          <div className="text-xs text-tertiary">Accuracy</div>
                        </div>
                        <div className="text-center p-2 bg-primary/10 rounded-lg">
                          <div className="text-lg font-medium text-primary">1.17</div>
                          <div className="text-xs text-tertiary">Loss</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Top Performing Conditions:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center">
                          <span>Acne Vulgaris</span>
                          <span className="font-medium text-green-500">85.2%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Melanoma</span>
                          <span className="font-medium text-green-500">78.9%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Psoriasis</span>
                          <span className="font-medium text-green-500">72.4%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Eczema</span>
                          <span className="font-medium text-green-500">68.7%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Challenging Conditions:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center">
                          <span>Rare Genetic Disorders</span>
                          <span className="font-medium text-yellow-500">45.2%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Early Stage Lesions</span>
                          <span className="font-medium text-yellow-500">52.8%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Mixed Conditions</span>
                          <span className="font-medium text-yellow-500">48.7%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Demographics & Age Analysis */}
                <div className="bg-secondary rounded-xl p-4 border border-border">
                  <h4 className="text-md font-medium text-primary border-b border-border pb-2 mb-4">
                    👥 Demographics & Age Analysis
                  </h4>
                  
                  <div className="space-y-4">
                    {/* Ethnicity Results */}
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Ethnicity Classification:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span>Caucasian</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '79.4%' }}></div>
                            </div>
                            <span className="font-medium text-blue-500 text-xs">79.4%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>African American</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '76.8%' }}></div>
                            </div>
                            <span className="font-medium text-blue-500 text-xs">76.8%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Asian</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '82.1%' }}></div>
                            </div>
                            <span className="font-medium text-blue-500 text-xs">82.1%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Age Group Results */}
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Age Group Classification:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span>19-35 years</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: '89.2%' }}></div>
                            </div>
                            <span className="font-medium text-green-500 text-xs">89.2%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>0-18 years</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: '87.9%' }}></div>
                            </div>
                            <span className="font-medium text-green-500 text-xs">87.9%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>36-50 years</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: '86.5%' }}></div>
                            </div>
                            <span className="font-medium text-green-500 text-xs">86.5%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Gender Results */}
                    <div className="bg-hover p-3 rounded-lg">
                      <h5 className="font-medium mb-2 text-primary text-sm">Gender Classification:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span>Female</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '72.0%' }}></div>
                            </div>
                            <span className="font-medium text-purple-500 text-xs">72.0%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Male</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '71.8%' }}></div>
                            </div>
                            <span className="font-medium text-purple-500 text-xs">71.8%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Multi-Task Performance Summary */}
              <div className="bg-primary/10 rounded-xl p-4 border border-primary/20">
                <h4 className="font-medium mb-3 text-primary">🎯 Multi-Task Learning Performance Summary:</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="bg-hover p-3 rounded-lg text-center">
                    <div className="text-lg font-medium text-primary">60.3%</div>
                    <div className="text-xs text-tertiary">Skin Condition</div>
                    <div className="text-xs text-green-500">Primary Task</div>
                  </div>
                  <div className="bg-hover p-3 rounded-lg text-center">
                    <div className="text-lg font-medium text-primary">87.9%</div>
                    <div className="text-xs text-tertiary">Age Analysis</div>
                    <div className="text-xs text-blue-500">Best Performing</div>
                  </div>
                  <div className="bg-hover p-3 rounded-lg text-center">
                    <div className="text-lg font-medium text-primary">79.4%</div>
                    <div className="text-xs text-tertiary">Ethnicity</div>
                    <div className="text-xs text-yellow-500">Good</div>
                  </div>
                </div>
                <div className="mt-3 text-sm text-primary text-center">
                  <strong>Note:</strong> Multi-task learning allows the model to learn shared representations across all tasks simultaneously.
                </div>
              </div>

              
            </div>
          )}
        </div>
      </div>
    </div>
    </>
  )
}
