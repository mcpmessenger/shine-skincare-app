#!/usr/bin/env python3
"""
Railway Deployment Monitor
Monitors Railway deployment health and performance
"""

import requests
import time
import json
from datetime import datetime

def monitor_railway_app(base_url, interval=60):
    """Monitor Railway app continuously"""
    
    print(f"Starting Railway monitoring for: {base_url}")
    print(f"Check interval: {interval} seconds")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Health check
            start_time = time.time()
            response = requests.get(f"{base_url}/api/health", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get('status', 'unknown')
                mode = health_data.get('mode', 'unknown')
                
                print(f"[{timestamp}] ✅ Status: {status} | Mode: {mode} | Response: {response_time:.0f}ms")
                
                # Enhanced health check
                try:
                    enhanced_response = requests.get(f"{base_url}/api/enhanced/health/enhanced", timeout=5)
                    if enhanced_response.status_code == 200:
                        enhanced_data = enhanced_response.json()
                        services = enhanced_data.get('services', {})
                        service_status = []
                        for service, status in services.items():
                            service_status.append(f"{service}:{'✅' if status else '❌'}")
                        print(f"                    Services: {' | '.join(service_status)}")
                except:
                    print(f"                    Enhanced health check failed")
                    
            else:
                print(f"[{timestamp}] ❌ HTTP {response.status_code} | Response: {response_time:.0f}ms")
                
        except requests.exceptions.Timeout:
            print(f"[{timestamp}] ⏰ Request timeout")
        except requests.exceptions.ConnectionError:
            print(f"[{timestamp}] 🔌 Connection error")
        except Exception as e:
            print(f"[{timestamp}] ❌ Error: {e}")
        
        time.sleep(interval)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python railway_monitor.py <railway_url> [interval_seconds]")
        print("Example: python railway_monitor.py https://your-app.railway.app 30")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    try:
        monitor_railway_app(base_url, interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()