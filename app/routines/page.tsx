'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useAuth } from "@/hooks/useAuth";
import { Loader2, Clock, CheckCircle, Play } from "lucide-react";

interface Routine {
  id: string;
  name: string;
  description: string;
  steps: RoutineStep[];
  duration: number; // in minutes
  frequency: string;
  completedToday: boolean;
  progress: number; // 0-100
}

interface RoutineStep {
  id: string;
  name: string;
  description: string;
  duration: number; // in minutes
  completed: boolean;
}

export default function RoutinesPage() {
  const { isAuthenticated, user } = useAuth();
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadRoutines = async () => {
      try {
        setLoading(true);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockRoutines: Routine[] = [
          {
            id: '1',
            name: 'Morning Glow Routine',
            description: 'Start your day with a bright, hydrated complexion',
            duration: 8,
            frequency: 'Daily',
            completedToday: false,
            progress: 0,
            steps: [
              {
                id: '1-1',
                name: 'Gentle Cleanser',
                description: 'Remove overnight buildup',
                duration: 2,
                completed: false
              },
              {
                id: '1-2',
                name: 'Vitamin C Serum',
                description: 'Brighten and protect',
                duration: 1,
                completed: false
              },
              {
                id: '1-3',
                name: 'Moisturizer',
                description: 'Hydrate and seal',
                duration: 1,
                completed: false
              },
              {
                id: '1-4',
                name: 'Sunscreen',
                description: 'Protect from UV damage',
                duration: 1,
                completed: false
              }
            ]
          },
          {
            id: '2',
            name: 'Evening Recovery',
            description: 'Repair and rejuvenate while you sleep',
            duration: 12,
            frequency: 'Daily',
            completedToday: true,
            progress: 100,
            steps: [
              {
                id: '2-1',
                name: 'Double Cleanse',
                description: 'Remove makeup and impurities',
                duration: 3,
                completed: true
              },
              {
                id: '2-2',
                name: 'Exfoliant',
                description: 'Gentle chemical exfoliation',
                duration: 2,
                completed: true
              },
              {
                id: '2-3',
                name: 'Hydrating Serum',
                description: 'Deep hydration',
                duration: 2,
                completed: true
              },
              {
                id: '2-4',
                name: 'Night Cream',
                description: 'Rich moisturizer for overnight repair',
                duration: 2,
                completed: true
              }
            ]
          }
        ];
        
        setRoutines(mockRoutines);
      } catch (err) {
        setError('Failed to load routines');
        console.error('Error loading routines:', err);
      } finally {
        setLoading(false);
      }
    };

    loadRoutines();
  }, []);

  const toggleStep = (routineId: string, stepId: string) => {
    setRoutines(prev => prev.map(routine => {
      if (routine.id === routineId) {
        const updatedSteps = routine.steps.map(step => 
          step.id === stepId ? { ...step, completed: !step.completed } : step
        );
        const progress = (updatedSteps.filter(s => s.completed).length / updatedSteps.length) * 100;
        return { ...routine, steps: updatedSteps, progress };
      }
      return routine;
    }));
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>
              Please log in to view your skincare routines.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <a href="/auth/login?redirect=/routines">Login to Continue</a>
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
            <p>Loading your skincare routines...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Your Skincare Routines</h1>
        <p className="text-muted-foreground">
          Personalized routines based on your skin analysis and goals
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {routines.map((routine) => (
          <Card key={routine.id} className="overflow-hidden">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-xl">{routine.name}</CardTitle>
                  <CardDescription className="mt-1">{routine.description}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">{routine.duration} min</span>
                </div>
              </div>
              
              <div className="flex items-center gap-2 mt-3">
                <Badge variant={routine.completedToday ? "default" : "secondary"}>
                  {routine.completedToday ? "Completed Today" : "Not Started"}
                </Badge>
                <Badge variant="outline">{routine.frequency}</Badge>
              </div>
              
              <div className="mt-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span>Progress</span>
                  <span>{Math.round(routine.progress)}%</span>
                </div>
                <Progress value={routine.progress} className="h-2" />
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-3">
                {routine.steps.map((step) => (
                  <div key={step.id} className="flex items-center gap-3 p-3 rounded-lg border">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleStep(routine.id, step.id)}
                      className="h-8 w-8 p-0"
                    >
                      {step.completed ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <div className="h-4 w-4 rounded-full border-2 border-muted-foreground" />
                      )}
                    </Button>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-sm">{step.name}</h4>
                        <span className="text-xs text-muted-foreground">{step.duration} min</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
              
              <Button className="w-full mt-4" variant="outline">
                <Play className="h-4 w-4 mr-2" />
                Start Routine
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
} 