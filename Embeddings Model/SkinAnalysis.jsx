import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Camera, Upload, Loader2, CheckCircle, AlertCircle, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

export default function SkinAnalysis({ user }) {
  const [selectedImage, setSelectedImage] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [age, setAge] = useState('')
  const [ethnicity, setEthnicity] = useState('')
  const fileInputRef = useRef(null)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [isCameraActive, setIsCameraActive] = useState(false)

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640, 
          height: 480,
          facingMode: 'user'
        } 
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        setIsCameraActive(true)
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      alert('Unable to access camera. Please check permissions.')
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks()
      tracks.forEach(track => track.stop())
      videoRef.current.srcObject = null
      setIsCameraActive(false)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0)
      
      canvas.toBlob((blob) => {
        const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' })
        handleImageSelect(file)
        stopCamera()
      }, 'image/jpeg', 0.8)
    }
  }

  const handleImageSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage({
          file,
          preview: e.target.result
        })
      }
      reader.readAsDataURL(file)
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleImageSelect(file)
    }
  }

  const analyzeImage = async () => {
    if (!selectedImage) return

    setIsAnalyzing(true)
    setAnalysisProgress(0)
    setAnalysisResult(null)

    try {
      // Convert image to base64
      const reader = new FileReader()
      reader.onload = async (e) => {
        const base64Image = e.target.result

        // Simulate progress updates
        const progressSteps = [
          { progress: 20, message: 'Detecting face region...' },
          { progress: 40, message: 'Generating embeddings...' },
          { progress: 60, message: 'Searching SCIN dataset...' },
          { progress: 80, message: 'Analyzing conditions...' },
          { progress: 100, message: 'Complete!' }
        ]

        for (const step of progressSteps) {
          setAnalysisProgress(step.progress)
          await new Promise(resolve => setTimeout(resolve, 1000))
        }

        // Make API call
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': user ? `Bearer ${localStorage.getItem('shine_token')}` : ''
          },
          body: JSON.stringify({
            image: base64Image,
            age: age || null,
            ethnicity: ethnicity || null
          })
        })

        if (response.ok) {
          const result = await response.json()
          setAnalysisResult(result)
        } else {
          throw new Error('Analysis failed')
        }
      }
      reader.readAsDataURL(selectedImage.file)
    } catch (error) {
      console.error('Analysis error:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
      setAnalysisProgress(0)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            AI-Powered Skin Analysis
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload a clear photo of your face for personalized skin analysis using advanced AI technology
          </p>
        </div>

        {/* Image Capture Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-5 h-5" />
              Capture Your Photo
            </CardTitle>
            <CardDescription>
              For best results, ensure good lighting and remove makeup or glasses
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Camera/Upload Options */}
            <div className="grid md:grid-cols-2 gap-4">
              <Button
                onClick={startCamera}
                disabled={isCameraActive}
                className="h-20 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                <Camera className="w-6 h-6 mr-2" />
                {isCameraActive ? 'Camera Active' : 'Take Photo'}
              </Button>
              
              <Button
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                className="h-20 border-2 border-dashed border-gray-300 hover:border-purple-300"
              >
                <Upload className="w-6 h-6 mr-2" />
                Upload Photo
              </Button>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />

            {/* Camera View */}
            {isCameraActive && (
              <div className="relative">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full max-w-md mx-auto rounded-lg"
                />
                <canvas ref={canvasRef} className="hidden" />
                <div className="flex justify-center gap-4 mt-4">
                  <Button onClick={capturePhoto} className="bg-green-600 hover:bg-green-700">
                    Capture
                  </Button>
                  <Button onClick={stopCamera} variant="outline">
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* Image Preview */}
            {selectedImage && (
              <div className="text-center">
                <img
                  src={selectedImage.preview}
                  alt="Selected"
                  className="max-w-md mx-auto rounded-lg shadow-lg"
                />
                <Button
                  onClick={() => setSelectedImage(null)}
                  variant="outline"
                  className="mt-4"
                >
                  Remove Image
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Optional Information */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Additional Information (Optional)</CardTitle>
            <CardDescription>
              Providing this information can help improve analysis accuracy
            </CardDescription>
          </CardHeader>
          <CardContent className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                placeholder="Enter your age"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                min="13"
                max="100"
              />
            </div>
            <div>
              <Label htmlFor="ethnicity">Ethnicity</Label>
              <Select value={ethnicity} onValueChange={setEthnicity}>
                <SelectTrigger>
                  <SelectValue placeholder="Select ethnicity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="african">African</SelectItem>
                  <SelectItem value="east-asian">East Asian</SelectItem>
                  <SelectItem value="south-asian">South Asian</SelectItem>
                  <SelectItem value="caucasian">Caucasian</SelectItem>
                  <SelectItem value="hispanic">Hispanic</SelectItem>
                  <SelectItem value="middle-eastern">Middle Eastern</SelectItem>
                  <SelectItem value="mixed">Mixed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Analysis Button */}
        <div className="text-center mb-8">
          <Button
            onClick={analyzeImage}
            disabled={!selectedImage || isAnalyzing}
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-12 py-6 text-lg"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Analyze My Skin
              </>
            )}
          </Button>
        </div>

        {/* Analysis Progress */}
        {isAnalyzing && (
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Analysis Progress</span>
                  <span className="text-sm text-gray-500">{analysisProgress}%</span>
                </div>
                <Progress value={analysisProgress} className="w-full" />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  Analysis Complete
                </CardTitle>
                <CardDescription>
                  Your personalized skin analysis results
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Primary Concerns */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">Primary Skin Concerns</h3>
                  <div className="grid gap-3">
                    {analysisResult.analysis?.primary_concerns?.map((concern, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="font-medium">{concern.condition}</span>
                          <Badge variant="secondary" className="ml-2">
                            {concern.severity}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                          {Math.round(concern.confidence * 100)}% confidence
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">Recommended Products</h3>
                  <div className="grid gap-2">
                    {analysisResult.analysis?.recommendations?.map((rec, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-blue-50 rounded">
                        <CheckCircle className="w-4 h-4 text-blue-500" />
                        <span className="text-sm">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Similar Conditions */}
                {analysisResult.similar_conditions && analysisResult.similar_conditions.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Similar Cases from Medical Dataset</h3>
                    <div className="grid gap-3">
                      {analysisResult.similar_conditions.slice(0, 3).map((condition, index) => (
                        <div key={index} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{condition.condition}</span>
                            <Badge variant="outline">
                              {Math.round(condition.similarity * 100)}% match
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600">{condition.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

