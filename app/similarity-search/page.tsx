'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Camera, Upload, Search, Loader2, Eye, AlertTriangle, CheckCircle, AlertCircle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { apiClient } from "@/lib/api";
import { CameraCapture } from "@/components/camera-capture";

interface SimilarImage {
  case_id: string;
  distance: number;
  image_path: string;
  condition: string;
  skin_type: string;
  skin_tone: string;
  age?: number;
  gender?: string;
}

interface SearchResults {
  success: boolean;
  query_image: string;
  similar_images: SimilarImage[];
  error?: string;
}

export default function SimilaritySearchPage() {
  const { isAuthenticated } = useAuth();
  const [showCamera, setShowCamera] = useState(false);
  const [queryImage, setQueryImage] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  const [selectedSkinTypes, setSelectedSkinTypes] = useState<string[]>([]);
  const [k, setK] = useState(5);
  const [searchError, setSearchError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const skinConditions = [
    'Acne', 'Eczema', 'Psoriasis', 'Melanoma', 'Rosacea', 
    'Dermatitis', 'Vitiligo', 'Warts', 'Moles', 'Rashes'
  ];

  const skinTypes = ['I', 'II', 'III', 'IV', 'V', 'VI'];

  const handleImageCapture = async (imageData: string) => {
    setQueryImage(imageData);
    setShowCamera(false);
    setSearchError(null);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setQueryImage(result);
        setSearchError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const performSearch = async () => {
    if (!queryImage) return;

    setIsSearching(true);
    setSearchResults(null);
    setSearchError(null);

    try {
      // Convert base64 to File object
      const response = await fetch(queryImage);
      const blob = await response.blob();
      const file = new File([blob], 'query_image.jpg', { type: 'image/jpeg' });

      // Perform SCIN similarity search
      const results = await apiClient.searchSCINSimilar(
        file,
        k,
        selectedConditions.length > 0 ? selectedConditions : undefined,
        selectedSkinTypes.length > 0 ? selectedSkinTypes : undefined
      );

      if (results.success) {
        setSearchResults(results.data);
      } else {
        setSearchResults({
          success: false,
          query_image: queryImage,
          similar_images: [],
          error: 'Search failed'
        });
        setSearchError('Search failed. Please try again.');
      }
    } catch (error) {
      console.error('Similarity search failed:', error);
      setSearchResults({
        success: false,
        query_image: queryImage,
        similar_images: [],
        error: 'Search failed. Please try again.'
      });
      setSearchError('Network error. Please check your connection and try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const getSimilarityScore = (distance: number) => {
    // Convert distance to similarity score (0-100)
    const similarity = Math.max(0, 100 - (distance * 100));
    return Math.round(similarity);
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Similarity Search</h1>
        <p className="text-muted-foreground">
          Find similar skin conditions from our professional dermatology dataset
        </p>
        {!isAuthenticated && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="text-blue-800 font-medium">Try our similarity search for free!</p>
                <p className="text-blue-700">
                  You can test the similarity search now. Sign up to save your searches and get unlimited access.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Search Controls */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Upload Query Image
              </CardTitle>
              <CardDescription>
                Upload a photo or take a selfie to find similar skin conditions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!queryImage ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Button
                      onClick={() => setShowCamera(true)}
                      className="flex items-center gap-2"
                    >
                      <Camera className="h-4 w-4" />
                      Take Photo
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center gap-2"
                    >
                      <Upload className="h-4 w-4" />
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
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative">
                    <img
                      src={queryImage}
                      alt="Query image"
                      className="w-full h-64 object-cover rounded-lg"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => {
                        setQueryImage(null);
                        setSearchResults(null);
                        setSearchError(null);
                      }}
                      variant="outline"
                      className="flex-1"
                    >
                      Change Image
                    </Button>
                    <Button
                      onClick={performSearch}
                      disabled={isSearching}
                      className="flex-1"
                    >
                      {isSearching ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                          Searching...
                        </>
                      ) : (
                        <>
                          <Search className="h-4 w-4 mr-2" />
                          Search Similar
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Search Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Search Filters</CardTitle>
              <CardDescription>
                Refine your search with specific conditions and skin types
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="conditions">Skin Conditions</Label>
                <Select
                  value={selectedConditions.join(',')}
                  onValueChange={(value) => setSelectedConditions(value ? value.split(',') : [])}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select conditions" />
                  </SelectTrigger>
                  <SelectContent>
                    {skinConditions.map((condition) => (
                      <SelectItem key={condition} value={condition}>
                        {condition}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="skinTypes">Skin Types</Label>
                <Select
                  value={selectedSkinTypes.join(',')}
                  onValueChange={(value) => setSelectedSkinTypes(value ? value.split(',') : [])}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select skin types" />
                  </SelectTrigger>
                  <SelectContent>
                    {skinTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        Type {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="results">Number of Results</Label>
                <Input
                  id="results"
                  type="number"
                  min="1"
                  max="20"
                  value={k}
                  onChange={(e) => setK(parseInt(e.target.value) || 5)}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search Results */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Search Results</CardTitle>
              <CardDescription>
                Similar skin conditions from our professional dataset
              </CardDescription>
            </CardHeader>
            <CardContent>
              {searchError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                    <div className="text-sm text-red-800">
                      {searchError}
                    </div>
                  </div>
                </div>
              )}

              {!searchResults && !isSearching && (
                <div className="text-center py-8 text-muted-foreground">
                  <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Upload an image and click "Search Similar" to find matches</p>
                </div>
              )}

              {isSearching && (
                <div className="text-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                  <p>Searching for similar conditions...</p>
                </div>
              )}

              {searchResults && searchResults.similar_images && (
                <div className="space-y-4">
                  {searchResults.similar_images.map((image, index) => {
                    const similarityScore = getSimilarityScore(image.distance);
                    return (
                      <div key={image.case_id} className="border rounded-lg p-4">
                        <div className="flex items-start gap-4">
                          <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
                            <Eye className="h-6 w-6 text-gray-400" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-medium">Case {image.case_id}</h4>
                              <Badge className={getSimilarityColor(similarityScore)}>
                                {similarityScore}% Match
                              </Badge>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                              <div>
                                <span className="font-medium">Condition:</span> {image.condition}
                              </div>
                              <div>
                                <span className="font-medium">Skin Type:</span> {image.skin_type}
                              </div>
                              <div>
                                <span className="font-medium">Skin Tone:</span> {image.skin_tone}
                              </div>
                              {image.age && (
                                <div>
                                  <span className="font-medium">Age:</span> {image.age}
                                </div>
                              )}
                              {image.gender && (
                                <div>
                                  <span className="font-medium">Gender:</span> {image.gender}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {searchResults && searchResults.similar_images && searchResults.similar_images.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No similar conditions found. Try adjusting your filters or uploading a different image.</p>
                </div>
              )}

              {!isAuthenticated && searchResults && searchResults.similar_images && searchResults.similar_images.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 mt-4">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <div className="text-sm">
                      <p className="text-green-800 font-medium">Great! We found similar conditions.</p>
                      <p className="text-green-700">
                        Sign up to save your searches and get unlimited access to our professional dataset.
                      </p>
                      <Button 
                        size="sm" 
                        className="mt-2"
                        onClick={() => window.location.href = '/auth/signup'}
                      >
                        Sign Up Now
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {showCamera && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-4 max-w-md w-full mx-4">
            <CameraCapture
              onImageCapture={handleImageCapture}
              onClose={() => setShowCamera(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
} 