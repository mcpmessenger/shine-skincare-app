'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AnalysisData {
  originalImage: string | null;
  croppedFaceImage: string | null;
  faceConfidence: number;
  analysisResults: any | null;
  // SWAN Initiative: Demographic information for enhanced analysis
  demographics?: {
    age_group?: string;
    ethnicity?: string;
  };
}

interface AnalysisContextType {
  analysisData: AnalysisData;
  setAnalysisData: (data: Partial<AnalysisData>) => void;
  clearAnalysisData: () => void;
  // SWAN Initiative: Set demographics separately
  setDemographics: (demographics: { age_group?: string; ethnicity?: string }) => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [analysisData, setAnalysisDataState] = useState<AnalysisData>({
    originalImage: null,
    croppedFaceImage: null,
    faceConfidence: 0,
    analysisResults: null,
    demographics: {
      age_group: undefined,
      ethnicity: undefined,
    },
  });

  const setAnalysisData = (data: Partial<AnalysisData>) => {
    setAnalysisDataState(prev => ({ ...prev, ...data }));
  };

  const setDemographics = (demographics: { age_group?: string; ethnicity?: string }) => {
    setAnalysisDataState(prev => ({
      ...prev,
      demographics: {
        ...prev.demographics,
        ...demographics,
      },
    }));
  };

  const clearAnalysisData = () => {
    setAnalysisDataState({
      originalImage: null,
      croppedFaceImage: null,
      faceConfidence: 0,
      analysisResults: null,
      demographics: {
        age_group: undefined,
        ethnicity: undefined,
      },
    });
  };

  return (
    <AnalysisContext.Provider value={{ 
      analysisData, 
      setAnalysisData, 
      clearAnalysisData,
      setDemographics 
    }}>
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
