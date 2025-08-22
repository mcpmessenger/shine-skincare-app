'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AnalysisData {
  originalImage: string;
  croppedFaceImage: string | null;
  faceConfidence: number;
  analysisResults: any;
  // Enhanced preprocessing data
  preprocessingMetrics?: {
    geometric: any;
    colorLighting: any;
    enhancement: any;
    mediapipe: any;
  };
  mediapipeLandmarks?: Array<[number, number, number]>;
  // Product recommendations
  productRecommendations?: Array<{
    name: string;
    category: string;
    description: string;
  }>;
  // Add fields for Settings page integration
  processedImages?: {
    rgbChannels: {
      red: string;
      green: string;
      blue: string;
      grayscale: string;
    };
    gaborFiltered: string;
    dermatoscopic: string;
    surfaceMap: string;
  };
  processingTime?: number;
}

interface AnalysisContextType {
  analysisData: AnalysisData | null;
  setAnalysisData: (data: AnalysisData) => void;
  clearAnalysisData: () => void;
  // Add method to update processed images
  updateProcessedImages: (processedImages: AnalysisData['processedImages']) => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
};

interface AnalysisProviderProps {
  children: ReactNode;
}

export const AnalysisProvider: React.FC<AnalysisProviderProps> = ({ children }) => {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);

  const clearAnalysisData = () => {
    setAnalysisData(null);
  };

  const updateProcessedImages = (processedImages: AnalysisData['processedImages']) => {
    if (analysisData) {
      setAnalysisData({
        ...analysisData,
        processedImages,
        processingTime: Date.now()
      });
    }
  };

  return (
    <AnalysisContext.Provider value={{
      analysisData,
      setAnalysisData,
      clearAnalysisData,
      updateProcessedImages
    }}>
      {children}
    </AnalysisContext.Provider>
  );
};
