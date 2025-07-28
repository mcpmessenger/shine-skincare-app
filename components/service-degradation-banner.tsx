'use client';

import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AlertTriangle, X, RefreshCw, ArrowRight } from "lucide-react";
import { serviceDegradationManager } from "@/lib/service-degradation";
import { useRouter } from 'next/navigation';

export default function ServiceDegradationBanner() {
  const [systemHealth, setSystemHealth] = useState(serviceDegradationManager.getSystemHealth());
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check system health periodically
    const checkHealth = () => {
      const health = serviceDegradationManager.getSystemHealth();
      setSystemHealth(health);
      
      // Show banner if system is degraded and not dismissed
      if (health.overallHealth !== 'healthy' && !isDismissed) {
        setIsVisible(true);
      } else if (health.overallHealth === 'healthy') {
        setIsVisible(false);
        setIsDismissed(false); // Reset dismissal when system is healthy
      }
    };

    // Initial check
    checkHealth();

    // Set up periodic health checks
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    // Listen for service status changes
    const unsubscribers = [
      'enhanced-analysis',
      'vector-search', 
      'scin-dataset',
      'google-vision'
    ].map(service => 
      serviceDegradationManager.onServiceStatusChange(service, checkHealth)
    );

    return () => {
      clearInterval(interval);
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [isDismissed]);

  const handleDismiss = () => {
    setIsDismissed(true);
    setIsVisible(false);
  };

  const handleRetryServices = () => {
    // Reset all services to trigger retry
    serviceDegradationManager.resetAllServices();
    setIsDismissed(false);
  };

  const handleUseLegacy = () => {
    router.push('/skin-analysis');
  };

  if (!isVisible || systemHealth.overallHealth === 'healthy') {
    return null;
  }

  const getBannerConfig = () => {
    switch (systemHealth.overallHealth) {
      case 'critical':
        return {
          variant: 'destructive' as const,
          icon: AlertTriangle,
          title: 'Critical Service Issues',
          description: `Most enhanced features are currently unavailable (${systemHealth.unavailableServices.length}/${systemHealth.totalServices} services down). Standard analysis is still available.`,
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-800'
        };
      case 'degraded':
        return {
          variant: 'default' as const,
          icon: AlertTriangle,
          title: 'Some Services Unavailable',
          description: `Some enhanced features are temporarily unavailable (${systemHealth.unavailableServices.length}/${systemHealth.totalServices} services affected). Analysis will automatically use available features.`,
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-800'
        };
      default:
        return null;
    }
  };

  const config = getBannerConfig();
  if (!config) return null;

  return (
    <div className={`${config.bgColor} ${config.borderColor} border-b`}>
      <div className="container mx-auto px-4 py-3">
        <Alert className="border-0 bg-transparent p-0">
          <div className="flex items-start gap-3">
            <config.icon className={`h-5 w-5 ${config.textColor} mt-0.5 flex-shrink-0`} />
            
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <h4 className={`font-medium ${config.textColor} mb-1`}>
                    {config.title}
                  </h4>
                  <AlertDescription className={`${config.textColor} text-sm mb-3`}>
                    {config.description}
                  </AlertDescription>
                  
                  {/* Affected Services */}
                  {systemHealth.unavailableServices.length > 0 && (
                    <div className="mb-3">
                      <p className={`text-xs ${config.textColor} mb-1 font-medium`}>
                        Affected services:
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {systemHealth.unavailableServices.map(service => (
                          <span 
                            key={service}
                            className={`text-xs px-2 py-1 rounded ${config.textColor} bg-white/50 border`}
                          >
                            {service.replace('-', ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleRetryServices}
                    className="text-xs"
                  >
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Retry
                  </Button>
                  
                  {systemHealth.overallHealth === 'critical' && (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={handleUseLegacy}
                      className="text-xs"
                    >
                      <ArrowRight className="h-3 w-3 mr-1" />
                      Use Standard Analysis
                    </Button>
                  )}
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleDismiss}
                    className="text-xs p-1"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </Alert>
      </div>
    </div>
  );
}