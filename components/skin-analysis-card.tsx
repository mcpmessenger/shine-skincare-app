import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Camera, Upload, CheckCircle, Sparkles } from "lucide-react"
import Image from "next/image"
import { useState } from "react"
import { CameraCapture } from "./camera-capture"
import { useAuth } from "@/hooks/useAuth"
import { useRouter } from "next/navigation"

export default function SkinAnalysisCard() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  const handleImageCapture = async (imageData: string) => {
    setCapturedImage(imageData);
    setShowCamera(false);
    
    if (!isAuthenticated) {
      // For non-authenticated users, just show the image
      return;
    }
    
    // Start analysis
    setIsAnalyzing(true);
    
    try {
      // Convert base64 to blob
      const response = await fetch(imageData);
      const blob = await response.blob();
      
      // Create form data
      const formData = new FormData();
      formData.append('image', blob, 'selfie.jpg');
      
      const token = localStorage.getItem('token');
      const headers: Record<string,string> = {};
      if (token && token !== 'guest') {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Call the analysis API
      const analysisResponse = await fetch('/api/analysis/skin', {
        method: 'POST',
        body: formData,
        headers: headers,
      });
      
      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        
        // Store analysis ID in localStorage for the results page
        if (analysisData.analysis_id) {
          localStorage.setItem('lastAnalysisId', analysisData.analysis_id);
        }
        
        setIsAnalyzing(false);
        setAnalysisComplete(true);
        
        // Redirect to results page
        router.push(`/analysis-results?analysisId=${analysisData.analysis_id}`);
      } else {
        const errorData = await analysisResponse.json();
        console.error('Analysis failed:', errorData);
        setIsAnalyzing(false);
        // You could show an error message here
      }
    } catch (error) {
      console.error('Error during analysis:', error);
      setIsAnalyzing(false);
      // You could show an error message here
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const result = e.target?.result as string;
        setCapturedImage(result);
        
        if (!isAuthenticated) {
          // For non-authenticated users, just show the image
          return;
        }
        
        setIsAnalyzing(true);
        
        try {
          // Create form data
          const formData = new FormData();
          formData.append('image', file);
          
          const token = localStorage.getItem('token');
          const headers: Record<string,string> = {};
          if (token && token !== 'guest') {
            headers['Authorization'] = `Bearer ${token}`;
          }
          
          // Call the analysis API
          const analysisResponse = await fetch('/api/analysis/skin', {
            method: 'POST',
            body: formData,
            headers: headers,
          });
          
          if (analysisResponse.ok) {
            const analysisData = await analysisResponse.json();
            
            // Store analysis ID in localStorage for the results page
            if (analysisData.analysis_id) {
              localStorage.setItem('lastAnalysisId', analysisData.analysis_id);
            }
            
            setIsAnalyzing(false);
            setAnalysisComplete(true);
            
            // Redirect to results page
            router.push(`/analysis-results?analysisId=${analysisData.analysis_id}`);
          } else {
            const errorData = await analysisResponse.json();
            console.error('Analysis failed:', errorData);
            setIsAnalyzing(false);
            // You could show an error message here
          }
        } catch (error) {
          console.error('Error during analysis:', error);
          setIsAnalyzing(false);
          // You could show an error message here
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Skin Analysis</CardTitle>
        <CardDescription>Capture a selfie to get a detailed analysis of your skin.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="relative w-full h-48 bg-muted rounded-lg flex items-center justify-center overflow-hidden">
          {capturedImage ? (
            <Image
              src={capturedImage}
              alt="Captured Selfie"
              width={200}
              height={200}
              className="object-cover w-full h-full"
            />
          ) : (
            <Image
              src="/placeholder.svg?height=200&width=200"
              alt="Selfie Placeholder"
              width={200}
              height={200}
              className="object-cover w-full h-full"
            />
          )}
          {/* Overlay */}
          {(!capturedImage || isAnalyzing || analysisComplete) && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 text-white text-center p-4">
              {isAnalyzing ? (
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                  <p>Analyzing your skin...</p>
                </div>
              ) : analysisComplete ? (
                <div className="text-center">
                  <Sparkles className="h-8 w-8 mx-auto mb-2 text-yellow-400" />
                  <p>Analysis complete!</p>
                </div>
              ) : (
                <p>Click "Capture Selfie" to begin your analysis.</p>
              )}
            </div>
          )}
        </div>
        <div className="flex flex-col gap-2">
          <Button 
            className="w-full" 
            onClick={() => setShowCamera(true)}
            disabled={isAnalyzing}
          >
            <Camera className="mr-2 h-4 w-4" />
            Capture Selfie
          </Button>
          <label htmlFor="image-upload">
            <Button variant="outline" className="w-full bg-transparent" asChild>
              <div>
                <Upload className="mr-2 h-4 w-4" />
                Upload Image
              </div>
            </Button>
          </label>
          <input
            id="image-upload"
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>

        {/* Authenticated User Info */}
        {isAuthenticated && user && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-800">
                Signed in as {user.email}
              </span>
            </div>
          </div>
        )}
        <div className="grid gap-2 text-sm text-muted-foreground">
          {capturedImage ? (
            <>
              <p className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Image captured successfully
              </p>
              <p className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Ready for analysis
              </p>
            </>
          ) : (
            <>
              <p className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Good lighting detected
              </p>
              <p className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Face in frame
              </p>
            </>
          )}
          <p>Ensure a clear, well-lit photo for best results.</p>
        </div>
      </CardContent>
      <CardFooter className="flex justify-end">
        {!isAuthenticated ? (
          <Button 
            variant="secondary" 
            disabled={!capturedImage}
            onClick={() => {
              // Navigate to analysis results page
              router.push('/analysis-results');
            }}
          >
            <Sparkles className="mr-2 h-4 w-4" />
            View Analysis Results
          </Button>
        ) : (
          <Button 
            variant="secondary" 
            disabled={!analysisComplete}
            onClick={() => {
              // Navigate to analysis results page
              router.push('/analysis-results');
            }}
          >
            <Sparkles className="mr-2 h-4 w-4" />
            View Analysis Results
          </Button>
        )}
      </CardFooter>
      
      {/* Camera Modal */}
      {showCamera && (
        <CameraCapture
          onImageCapture={handleImageCapture}
          onClose={() => setShowCamera(false)}
        />
      )}
    </Card>
  )
}
