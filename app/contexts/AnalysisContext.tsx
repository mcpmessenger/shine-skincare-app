'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AnalysisData {
  originalImage: string | null;
  croppedFaceImage: string | null;
  faceConfidence: number;
  analysisResults: any | null;
}

interface AnalysisContextType {
  analysisData: AnalysisData;
  setAnalysisData: (data: Partial<AnalysisData>) => void;
  clearAnalysisData: () => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [analysisData, setAnalysisDataState] = useState<AnalysisData>({
    originalImage: null,
    croppedFaceImage: null,
    faceConfidence: 0,
    analysisResults: null,
  });

  const setAnalysisData = (data: Partial<AnalysisData>) => {
    setAnalysisDataState(prev => ({ ...prev, ...data }));
  };

  const clearAnalysisData = () => {
    setAnalysisDataState({
      originalImage: null,
      croppedFaceImage: null,
      faceConfidence: 0,
      analysisResults: null,
    });
  };

  return (
    <AnalysisContext.Provider value={{ analysisData, setAnalysisData, clearAnalysisData }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
}
