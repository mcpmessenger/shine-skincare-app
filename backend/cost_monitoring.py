#!/usr/bin/env python3
"""
Cost Monitoring System
Tracks Google Cloud API usage and calculates savings from hybrid approach
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CostMonitor:
    """Monitor costs for Google Cloud APIs"""
    
    def __init__(self):
        """Initialize cost monitor"""
        self.cost_file = "api_costs.json"
        self.load_costs()
    
    def load_costs(self):
        """Load existing cost data"""
        try:
            if os.path.exists(self.cost_file):
                with open(self.cost_file, 'r') as f:
                    self.costs = json.load(f)
            else:
                self.costs = {
                    'total_requests': 0,
                    'google_vision_requests': 0,
                    'local_detection_requests': 0,
                    'total_cost': 0.0,
                    'savings': 0.0,
                    'daily_usage': {},
                    'monthly_usage': {}
                }
        except Exception as e:
            logger.error(f"❌ Error loading costs: {e}")
            self.costs = {
                'total_requests': 0,
                'google_vision_requests': 0,
                'local_detection_requests': 0,
                'total_cost': 0.0,
                'savings': 0.0,
                'daily_usage': {},
                'monthly_usage': {}
            }
    
    def save_costs(self):
        """Save cost data to file"""
        try:
            with open(self.cost_file, 'w') as f:
                json.dump(self.costs, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving costs: {e}")
    
    def record_request(self, method: str, success: bool = True):
        """
        Record an API request
        
        Args:
            method: 'google_vision' or 'local_detection'
            success: Whether the request was successful
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            month = datetime.now().strftime('%Y-%m')
            
            # Update total requests
            self.costs['total_requests'] += 1
            
            # Update method-specific requests
            if method == 'google_vision':
                self.costs['google_vision_requests'] += 1
                cost_per_request = 0.0015  # $1.50 per 1000 requests
            else:  # local_detection
                self.costs['local_detection_requests'] += 1
                cost_per_request = 0.0  # FREE
            
            # Calculate costs
            current_cost = cost_per_request
            self.costs['total_cost'] += current_cost
            
            # Calculate savings (vs full Google Vision)
            if method == 'local_detection':
                saved_cost = 0.0015  # What we would have paid for Google Vision
                self.costs['savings'] += saved_cost
            
            # Update daily usage
            if today not in self.costs['daily_usage']:
                self.costs['daily_usage'][today] = {
                    'google_vision': 0,
                    'local_detection': 0,
                    'total_cost': 0.0,
                    'savings': 0.0
                }
            
            self.costs['daily_usage'][today][method] += 1
            self.costs['daily_usage'][today]['total_cost'] += current_cost
            if method == 'local_detection':
                self.costs['daily_usage'][today]['savings'] += 0.0015
            
            # Update monthly usage
            if month not in self.costs['monthly_usage']:
                self.costs['monthly_usage'][month] = {
                    'google_vision': 0,
                    'local_detection': 0,
                    'total_cost': 0.0,
                    'savings': 0.0
                }
            
            self.costs['monthly_usage'][month][method] += 1
            self.costs['monthly_usage'][month]['total_cost'] += current_cost
            if method == 'local_detection':
                self.costs['monthly_usage'][month]['savings'] += 0.0015
            
            # Save updated costs
            self.save_costs()
            
            logger.info(f"📊 Recorded {method} request - Cost: ${current_cost:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Error recording request: {e}")
    
    def get_cost_summary(self) -> Dict:
        """Get cost summary"""
        try:
            total_requests = self.costs['total_requests']
            google_requests = self.costs['google_vision_requests']
            local_requests = self.costs['local_detection_requests']
            total_cost = self.costs['total_cost']
            total_savings = self.costs['savings']
            
            # Calculate percentages
            google_percentage = (google_requests / total_requests * 100) if total_requests > 0 else 0
            local_percentage = (local_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Calculate what full Google Vision would cost
            full_google_cost = total_requests * 0.0015
            savings_percentage = (total_savings / full_google_cost * 100) if full_google_cost > 0 else 0
            
            return {
                'total_requests': total_requests,
                'google_vision_requests': google_requests,
                'local_detection_requests': local_requests,
                'google_percentage': round(google_percentage, 1),
                'local_percentage': round(local_percentage, 1),
                'total_cost': round(total_cost, 4),
                'total_savings': round(total_savings, 4),
                'full_google_cost': round(full_google_cost, 4),
                'savings_percentage': round(savings_percentage, 1),
                'cost_per_request': {
                    'google_vision': '$0.0015',
                    'local_detection': 'FREE'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting cost summary: {e}")
            return {}
    
    def get_daily_usage(self, days: int = 7) -> List[Dict]:
        """Get daily usage for last N days"""
        try:
            daily_data = []
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                if date in self.costs['daily_usage']:
                    daily_data.append({
                        'date': date,
                        **self.costs['daily_usage'][date]
                    })
                else:
                    daily_data.append({
                        'date': date,
                        'google_vision': 0,
                        'local_detection': 0,
                        'total_cost': 0.0,
                        'savings': 0.0
                    })
            
            return list(reversed(daily_data))
            
        except Exception as e:
            logger.error(f"❌ Error getting daily usage: {e}")
            return []
    
    def get_monthly_usage(self, months: int = 3) -> List[Dict]:
        """Get monthly usage for last N months"""
        try:
            monthly_data = []
            for i in range(months):
                month = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
                if month in self.costs['monthly_usage']:
                    monthly_data.append({
                        'month': month,
                        **self.costs['monthly_usage'][month]
                    })
                else:
                    monthly_data.append({
                        'month': month,
                        'google_vision': 0,
                        'local_detection': 0,
                        'total_cost': 0.0,
                        'savings': 0.0
                    })
            
            return list(reversed(monthly_data))
            
        except Exception as e:
            logger.error(f"❌ Error getting monthly usage: {e}")
            return []
    
    def generate_report(self) -> str:
        """Generate a cost report"""
        try:
            summary = self.get_cost_summary()
            daily_usage = self.get_daily_usage(7)
            monthly_usage = self.get_monthly_usage(3)
            
            report = f"""
💰 Cost Monitoring Report
========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Summary:
  Total Requests: {summary.get('total_requests', 0)}
  Google Vision: {summary.get('google_vision_requests', 0)} ({summary.get('google_percentage', 0)}%)
  Local Detection: {summary.get('local_detection_requests', 0)} ({summary.get('local_percentage', 0)}%)

💰 Costs:
  Total Cost: ${summary.get('total_cost', 0):.4f}
  Total Savings: ${summary.get('total_savings', 0):.4f}
  Full Google Cost: ${summary.get('full_google_cost', 0):.4f}
  Savings Percentage: {summary.get('savings_percentage', 0)}%

📈 Daily Usage (Last 7 Days):
"""
            
            for day in daily_usage:
                report += f"  {day['date']}: G={day['google_vision']}, L={day['local_detection']}, Cost=${day['total_cost']:.4f}, Saved=${day['savings']:.4f}\n"
            
            report += f"""
📊 Monthly Usage (Last 3 Months):
"""
            
            for month in monthly_usage:
                report += f"  {month['month']}: G={month['google_vision']}, L={month['local_detection']}, Cost=${month['total_cost']:.4f}, Saved=${month['savings']:.4f}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return f"Error generating report: {e}"

def main():
    """Test cost monitoring"""
    monitor = CostMonitor()
    
    # Simulate some requests
    logger.info("🧪 Testing cost monitoring...")
    
    # Record some test requests
    monitor.record_request('local_detection')  # FREE
    monitor.record_request('local_detection')  # FREE
    monitor.record_request('google_vision')    # $0.0015
    monitor.record_request('local_detection')  # FREE
    monitor.record_request('google_vision')    # $0.0015
    
    # Generate report
    report = monitor.generate_report()
    logger.info(report)
    
    # Save report to file
    with open('cost_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info("✅ Cost monitoring test completed!")

if __name__ == "__main__":
    main() 