#!/usr/bin/env python3
"""
Enhanced Analysis Feedback System
Provides detailed customer feedback and clearly labels sample data
"""

import json
import random
from typing import Dict, List, Optional
from datetime import datetime

class EnhancedFeedbackSystem:
    def __init__(self):
        self.sample_data_indicators = [
            "SAMPLE DATA - FOR TESTING",
            "DEMO ANALYSIS - NOT MEDICAL ADVICE",
            "TEST IMAGE - EDUCATIONAL PURPOSE",
            "SAMPLE SKIN CONDITION - DEMO ONLY"
        ]
        
        self.confidence_levels = {
            'high': (80, 100),
            'medium': (50, 79),
            'low': (20, 49),
            'very_low': (0, 19)
        }
        
        self.condition_descriptions = {
            'melanoma': {
                'name': 'Melanoma',
                'description': 'A serious form of skin cancer that develops from melanocytes',
                'symptoms': ['Asymmetric shape', 'Irregular borders', 'Varied colors', 'Diameter > 6mm', 'Evolving appearance'],
                'urgency': 'HIGH - Requires immediate medical attention',
                'recommendations': [
                    'Schedule dermatologist appointment immediately',
                    'Document changes with photos',
                    'Avoid sun exposure',
                    'Use broad-spectrum sunscreen'
                ]
            },
            'nevus': {
                'name': 'Nevus (Mole)',
                'description': 'A common benign growth of melanocytes',
                'symptoms': ['Symmetrical shape', 'Regular borders', 'Uniform color', 'Stable appearance'],
                'urgency': 'LOW - Monitor for changes',
                'recommendations': [
                    'Regular self-examination',
                    'Document any changes',
                    'Use sunscreen',
                    'Annual skin check'
                ]
            },
            'basal_cell_carcinoma': {
                'name': 'Basal Cell Carcinoma',
                'description': 'A common, slow-growing skin cancer',
                'symptoms': ['Pearly appearance', 'Pink or red patch', 'Slow-growing', 'May bleed or crust'],
                'urgency': 'MEDIUM - Schedule dermatologist visit',
                'recommendations': [
                    'Schedule dermatologist appointment',
                    'Protect from sun exposure',
                    'Monitor for changes',
                    'Use protective clothing'
                ]
            },
            'actinic_keratosis': {
                'name': 'Actinic Keratosis',
                'description': 'Pre-cancerous skin growth from sun damage',
                'symptoms': ['Rough, scaly patches', 'Pink or red base', 'May be tender', 'Sun-exposed areas'],
                'urgency': 'MEDIUM - Medical evaluation recommended',
                'recommendations': [
                    'Schedule dermatologist appointment',
                    'Sun protection essential',
                    'Regular skin monitoring',
                    'Consider treatment options'
                ]
            },
            'benign_keratosis': {
                'name': 'Benign Keratosis',
                'description': 'A harmless skin growth common with aging',
                'symptoms': ['Waxy appearance', 'Stuck-on look', 'Light brown to black', 'No symptoms'],
                'urgency': 'LOW - Usually harmless',
                'recommendations': [
                    'Monitor for changes',
                    'No treatment usually needed',
                    'Regular skin checks',
                    'Sun protection'
                ]
            },
            'normal': {
                'name': 'Normal Skin',
                'description': 'Healthy skin with no concerning features',
                'symptoms': ['Even color', 'Smooth texture', 'No unusual growths'],
                'urgency': 'NONE - Continue good skin care',
                'recommendations': [
                    'Maintain good skin care routine',
                    'Use sunscreen daily',
                    'Regular skin self-exams',
                    'Annual dermatologist visit'
                ]
            }
        }
    
    def generate_sample_data_warning(self) -> str:
        """Generate a clear warning about sample data"""
        return f"""
⚠️ **SAMPLE DATA ANALYSIS**
This analysis uses sample/demo images for testing purposes.
**This is NOT real medical analysis and should NOT be used for medical decisions.**

🔬 **What this means:**
- Images are generated for testing
- Results are simulated
- Not based on real medical data
- For demonstration purposes only

📋 **For real analysis:**
- Upload actual photos of your skin
- Consult healthcare professionals
- Use for educational purposes only
"""
    
    def calculate_confidence_score(self, condition: str, features_detected: int) -> Dict:
        """Calculate confidence score based on detected features"""
        base_confidence = random.randint(60, 95)
        
        # Adjust based on condition and features
        if condition == 'melanoma':
            base_confidence = min(85, base_confidence + 10)
        elif condition == 'normal':
            base_confidence = max(70, base_confidence - 5)
        
        # Determine confidence level
        confidence_level = 'medium'
        for level, (min_val, max_val) in self.confidence_levels.items():
            if min_val <= base_confidence <= max_val:
                confidence_level = level
                break
        
        return {
            'score': base_confidence,
            'level': confidence_level,
            'features_detected': features_detected,
            'reliability': 'sample_data'  # Clearly indicate this is sample data
        }
    
    def generate_detailed_analysis(self, condition: str, confidence: Dict) -> Dict:
        """Generate detailed analysis with customer-friendly feedback"""
        condition_info = self.condition_descriptions.get(condition, self.condition_descriptions['normal'])
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'sample_data_warning': True,
            'condition': {
                'name': condition_info['name'],
                'description': condition_info['description'],
                'symptoms': condition_info['symptoms'],
                'urgency': condition_info['urgency']
            },
            'confidence': confidence,
            'recommendations': condition_info['recommendations'],
            'educational_info': {
                'what_to_look_for': condition_info['symptoms'],
                'when_to_seek_help': 'Any changes in size, shape, or color',
                'prevention_tips': [
                    'Use broad-spectrum sunscreen (SPF 30+)',
                    'Avoid peak sun hours (10 AM - 4 PM)',
                    'Wear protective clothing',
                    'Regular skin self-examinations'
                ]
            },
            'disclaimer': {
                'medical_advice': 'This analysis is for educational purposes only and does not constitute medical advice.',
                'sample_data': 'This analysis uses sample data for demonstration purposes.',
                'consultation': 'Always consult with a qualified healthcare professional for medical concerns.',
                'emergency': 'If you have concerns about your skin, seek immediate medical attention.'
            }
        }
        
        return analysis
    
    def format_customer_feedback(self, analysis: Dict) -> str:
        """Format analysis into customer-friendly feedback"""
        condition = analysis['condition']
        confidence = analysis['confidence']
        
        feedback = f"""
🔍 **SKIN ANALYSIS RESULTS**

📋 **Condition Detected:** {condition['name']}
📝 **Description:** {condition['description']}

🎯 **Confidence Level:** {confidence['level'].upper()} ({confidence['score']}%)
⚠️ **Sample Data Analysis** - For demonstration purposes only

🚨 **Urgency Level:** {condition['urgency']}

📋 **Key Symptoms to Watch For:**
"""
        
        for symptom in condition['symptoms']:
            feedback += f"• {symptom}\n"
        
        feedback += f"""
💡 **Recommendations:**
"""
        
        # Get recommendations from the analysis, not the condition
        for rec in analysis.get('recommendations', []):
            feedback += f"• {rec}\n"
        
        feedback += f"""
📚 **Educational Information:**
• **What to Look For:** {', '.join(condition['symptoms'][:3])}
• **When to Seek Help:** Any changes in size, shape, or color
• **Prevention:** Use sunscreen, avoid peak sun hours, regular checks

⚠️ **Important Disclaimers:**
• This is sample data analysis for demonstration
• Not real medical advice
• Always consult healthcare professionals
• For educational purposes only

🆘 **Emergency:** If you have skin concerns, seek immediate medical attention.
"""
        
        return feedback
    
    def create_sample_data_report(self, condition: str) -> Dict:
        """Create a comprehensive sample data report"""
        confidence = self.calculate_confidence_score(condition, random.randint(3, 8))
        analysis = self.generate_detailed_analysis(condition, confidence)
        
        return {
            'analysis': analysis,
            'customer_feedback': self.format_customer_feedback(analysis),
            'sample_data_warning': self.generate_sample_data_warning(),
            'metadata': {
                'data_type': 'sample_generated',
                'purpose': 'demonstration',
                'medical_validity': 'none',
                'educational_only': True
            }
        }

def main():
    """Test the enhanced feedback system"""
    feedback_system = EnhancedFeedbackSystem()
    
    # Test with different conditions
    conditions = ['melanoma', 'nevus', 'basal_cell_carcinoma', 'normal']
    
    print("🧪 Testing Enhanced Feedback System")
    print("=" * 50)
    
    for condition in conditions:
        print(f"\n📊 Testing {condition.upper()} analysis:")
        report = feedback_system.create_sample_data_report(condition)
        
        print(f"Condition: {report['analysis']['condition']['name']}")
        print(f"Confidence: {report['analysis']['confidence']['level']} ({report['analysis']['confidence']['score']}%)")
        print(f"Urgency: {report['analysis']['condition']['urgency']}")
        print(f"Sample Data: {report['metadata']['data_type']}")
    
    print("\n✅ Enhanced feedback system ready!")
    print("📋 Sample data clearly labeled")
    print("🎯 Customer-friendly feedback generated")

if __name__ == "__main__":
    main() 