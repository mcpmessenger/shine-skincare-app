// Service Degradation Handler
// Manages fallback strategies when enhanced features are unavailable

interface ServiceStatus {
  isAvailable: boolean;
  lastChecked: number;
  failureCount: number;
  nextRetryTime: number;
}

interface DegradationConfig {
  maxFailures: number;
  retryDelay: number;
  healthCheckInterval: number;
}

class ServiceDegradationManager {
  private services: Map<string, ServiceStatus> = new Map();
  private config: DegradationConfig;
  private listeners: Map<string, ((status: boolean) => void)[]> = new Map();

  constructor(config: Partial<DegradationConfig> = {}) {
    this.config = {
      maxFailures: 3,
      retryDelay: 30000, // 30 seconds
      healthCheckInterval: 60000, // 1 minute
      ...config
    };
  }

  // Register a service for monitoring
  registerService(serviceName: string): void {
    if (!this.services.has(serviceName)) {
      this.services.set(serviceName, {
        isAvailable: true,
        lastChecked: Date.now(),
        failureCount: 0,
        nextRetryTime: 0
      });
    }
  }

  // Record a service failure
  recordFailure(serviceName: string): void {
    const service = this.services.get(serviceName);
    if (!service) return;

    service.failureCount++;
    service.lastChecked = Date.now();

    if (service.failureCount >= this.config.maxFailures) {
      service.isAvailable = false;
      service.nextRetryTime = Date.now() + this.config.retryDelay;
      this.notifyListeners(serviceName, false);
    }
  }

  // Record a service success
  recordSuccess(serviceName: string): void {
    const service = this.services.get(serviceName);
    if (!service) return;

    const wasUnavailable = !service.isAvailable;
    service.isAvailable = true;
    service.failureCount = 0;
    service.lastChecked = Date.now();
    service.nextRetryTime = 0;

    if (wasUnavailable) {
      this.notifyListeners(serviceName, true);
    }
  }

  // Check if a service is available
  isServiceAvailable(serviceName: string): boolean {
    const service = this.services.get(serviceName);
    if (!service) return true; // Assume available if not registered

    // Check if it's time to retry
    if (!service.isAvailable && Date.now() >= service.nextRetryTime) {
      service.isAvailable = true;
      service.failureCount = 0;
    }

    return service.isAvailable;
  }

  // Get service status
  getServiceStatus(serviceName: string): ServiceStatus | null {
    return this.services.get(serviceName) || null;
  }

  // Subscribe to service status changes
  onServiceStatusChange(serviceName: string, callback: (isAvailable: boolean) => void): () => void {
    if (!this.listeners.has(serviceName)) {
      this.listeners.set(serviceName, []);
    }
    
    this.listeners.get(serviceName)!.push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(serviceName);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  // Notify listeners of status changes
  private notifyListeners(serviceName: string, isAvailable: boolean): void {
    const callbacks = this.listeners.get(serviceName);
    if (callbacks) {
      callbacks.forEach(callback => callback(isAvailable));
    }
  }

  // Get degradation recommendations
  getDegradationStrategy(serviceName: string): {
    shouldFallback: boolean;
    fallbackMessage: string;
    retryAvailable: boolean;
    nextRetryIn?: number;
  } {
    const service = this.services.get(serviceName);
    
    if (!service || service.isAvailable) {
      return {
        shouldFallback: false,
        fallbackMessage: '',
        retryAvailable: false
      };
    }

    const nextRetryIn = Math.max(0, service.nextRetryTime - Date.now());
    
    return {
      shouldFallback: true,
      fallbackMessage: this.getFallbackMessage(serviceName),
      retryAvailable: nextRetryIn <= 0,
      nextRetryIn: nextRetryIn > 0 ? nextRetryIn : undefined
    };
  }

  private getFallbackMessage(serviceName: string): string {
    const messages: Record<string, string> = {
      'enhanced-analysis': 'Enhanced analysis is temporarily unavailable. You can use our standard analysis or try again later.',
      'vector-search': 'Vector-based recommendations are temporarily unavailable. Standard recommendations are still available.',
      'scin-dataset': 'Advanced demographic matching is temporarily unavailable. Basic analysis is still available.',
      'google-vision': 'Advanced image processing is temporarily unavailable. Basic analysis is still available.'
    };

    return messages[serviceName] || 'This service is temporarily unavailable. Please try again later.';
  }

  // Reset all services (useful for testing or manual recovery)
  resetAllServices(): void {
    this.services.forEach((service, serviceName) => {
      service.isAvailable = true;
      service.failureCount = 0;
      service.nextRetryTime = 0;
      this.notifyListeners(serviceName, true);
    });
  }

  // Get overall system health
  getSystemHealth(): {
    overallHealth: 'healthy' | 'degraded' | 'critical';
    availableServices: string[];
    unavailableServices: string[];
    totalServices: number;
  } {
    const availableServices: string[] = [];
    const unavailableServices: string[] = [];

    this.services.forEach((service, serviceName) => {
      if (service.isAvailable) {
        availableServices.push(serviceName);
      } else {
        unavailableServices.push(serviceName);
      }
    });

    const totalServices = this.services.size;
    const availableCount = availableServices.length;
    
    let overallHealth: 'healthy' | 'degraded' | 'critical';
    if (availableCount === totalServices) {
      overallHealth = 'healthy';
    } else if (availableCount >= totalServices / 2) {
      overallHealth = 'degraded';
    } else {
      overallHealth = 'critical';
    }

    return {
      overallHealth,
      availableServices,
      unavailableServices,
      totalServices
    };
  }
}

// Create singleton instance
export const serviceDegradationManager = new ServiceDegradationManager();

// Register known services
serviceDegradationManager.registerService('enhanced-analysis');
serviceDegradationManager.registerService('vector-search');
serviceDegradationManager.registerService('scin-dataset');
serviceDegradationManager.registerService('google-vision');

export default serviceDegradationManager;