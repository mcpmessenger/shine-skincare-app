'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/hooks/useAuth";
import { Loader2, User, Settings, History, Heart, LogOut } from "lucide-react";

interface SkinProfile {
  skinType: string;
  concerns: string[];
  goals: string[];
  lastAnalysis: string;
  analysisCount: number;
}

export default function ProfilePage() {
  const { user, isAuthenticated, logout } = useAuth();
  const [skinProfile, setSkinProfile] = useState<SkinProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock skin profile data
        setSkinProfile({
          skinType: 'Combination',
          concerns: ['Acne', 'Hyperpigmentation', 'Fine Lines'],
          goals: ['Clear Skin', 'Even Tone', 'Anti-aging'],
          lastAnalysis: '2024-01-15',
          analysisCount: 5
        });
      } catch (error) {
        console.error('Error loading profile:', error);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      loadProfile();
    }
  }, [isAuthenticated]);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>
              Please log in to view your profile.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <a href="/auth/login?redirect=/profile">Login to Continue</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Loading your profile...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Profile</h1>
        <p className="text-muted-foreground">
          Manage your account and skincare preferences
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile Overview */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader className="text-center">
              <Avatar className="h-24 w-24 mx-auto mb-4">
                <AvatarImage src={user?.profile_picture_url} alt={user?.name} />
                <AvatarFallback>
                  <User className="h-12 w-12" />
                </AvatarFallback>
              </Avatar>
              <CardTitle>{user?.name || 'User'}</CardTitle>
              <CardDescription>{user?.email}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button variant="outline" className="w-full">
                  <Settings className="h-4 w-4 mr-2" />
                  Edit Profile
                </Button>
                <Button variant="outline" className="w-full">
                  <History className="h-4 w-4 mr-2" />
                  View History
                </Button>
                <Button variant="outline" className="w-full">
                  <Heart className="h-4 w-4 mr-2" />
                  Favorites
                </Button>
                <Separator />
                <Button variant="destructive" className="w-full" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Skin Profile */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Skin Profile</CardTitle>
              <CardDescription>
                Your personalized skincare information and analysis history
              </CardDescription>
            </CardHeader>
            <CardContent>
              {skinProfile ? (
                <div className="space-y-6">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <h3 className="font-medium mb-2">Skin Type</h3>
                      <Badge variant="secondary">{skinProfile.skinType}</Badge>
                    </div>
                    <div>
                      <h3 className="font-medium mb-2">Analysis Count</h3>
                      <p className="text-2xl font-bold">{skinProfile.analysisCount}</p>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Skin Concerns</h3>
                    <div className="flex flex-wrap gap-2">
                      {skinProfile.concerns.map((concern) => (
                        <Badge key={concern} variant="outline">
                          {concern}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Skincare Goals</h3>
                    <div className="flex flex-wrap gap-2">
                      {skinProfile.goals.map((goal) => (
                        <Badge key={goal} variant="default">
                          {goal}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Last Analysis</h3>
                    <p className="text-muted-foreground">
                      {new Date(skinProfile.lastAnalysis).toLocaleDateString()}
                    </p>
                  </div>

                  <Separator />

                  <div className="flex gap-4">
                    <Button asChild>
                      <a href="/skin-analysis">New Analysis</a>
                    </Button>
                    <Button variant="outline" asChild>
                      <a href="/recommendations">View Recommendations</a>
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    No skin profile found. Complete your first analysis to get started.
                  </p>
                  <Button asChild>
                    <a href="/skin-analysis">Start Analysis</a>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 