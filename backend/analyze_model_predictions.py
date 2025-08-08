#!/usr/bin/env python3
"""
Model Prediction Analyzer for Shine Skincare App
Analyzes why some categories show 0% accuracy and provides insights
"""

import os
import json
import logging
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelPredictionAnalyzer:
    def __init__(self):
        self.data_dir = Path("data/comprehensive_dataset")
        self.splits_dir = self.data_dir / "processed" / "splits"
        self.models_dir = Path("models")
        self.results_dir = Path("results")
        
        # Load the trained model
        self.model_path = self.models_dir / "comprehensive_model_final.h5"
        
    def load_model_and_data(self):
        """Load the trained model and test data"""
        logger.info("Loading model and test data...")
        
        # Load model
        if self.model_path.exists():
            self.model = load_model(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
        else:
            logger.error(f"Model not found at {self.model_path}")
            return False
        
        # Load test data
        test_datagen = ImageDataGenerator(rescale=1./255)
        self.test_generator = test_datagen.flow_from_directory(
            self.splits_dir / "test",
            target_size=(224, 224),
            batch_size=1,  # One image at a time for detailed analysis
            class_mode='categorical',
            shuffle=False
        )
        
        logger.info(f"Test samples: {self.test_generator.samples}")
        logger.info(f"Class indices: {self.test_generator.class_indices}")
        
        return True
    
    def analyze_predictions(self):
        """Analyze model predictions in detail"""
        logger.info("Analyzing model predictions...")
        
        # Reset generator
        self.test_generator.reset()
        
        # Get predictions
        predictions = self.model.predict(self.test_generator, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = self.test_generator.classes
        confidence_scores = np.max(predictions, axis=1)
        
        # Get class names
        class_names = list(self.test_generator.class_indices.keys())
        
        # Analyze each prediction
        analysis_results = []
        
        for i in range(len(predictions)):
            true_class_idx = true_classes[i]
            predicted_class_idx = predicted_classes[i]
            confidence = confidence_scores[i]
            
            true_class_name = class_names[true_class_idx]
            predicted_class_name = class_names[predicted_class_idx]
            
            is_correct = true_class_idx == predicted_class_idx
            
            # Get all prediction probabilities
            all_probs = predictions[i]
            
            analysis_results.append({
                'sample_index': i,
                'true_class': true_class_name,
                'predicted_class': predicted_class_name,
                'confidence': confidence,
                'is_correct': is_correct,
                'all_probabilities': all_probs.tolist(),
                'true_class_prob': all_probs[true_class_idx]
            })
        
        return analysis_results, class_names
    
    def print_detailed_analysis(self, analysis_results, class_names):
        """Print detailed analysis of predictions"""
        print("\n" + "="*80)
        print("DETAILED MODEL PREDICTION ANALYSIS")
        print("="*80)
        
        # Group by true class
        class_analysis = {}
        for result in analysis_results:
            true_class = result['true_class']
            if true_class not in class_analysis:
                class_analysis[true_class] = []
            class_analysis[true_class].append(result)
        
        # Analyze each class
        for class_name in class_names:
            if class_name in class_analysis:
                samples = class_analysis[class_name]
                correct_count = sum(1 for s in samples if s['is_correct'])
                total_count = len(samples)
                accuracy = correct_count / total_count if total_count > 0 else 0
                
                print(f"\n📊 {class_name.upper()} ANALYSIS:")
                print(f"   Accuracy: {correct_count}/{total_count} = {accuracy:.1%}")
                
                for i, sample in enumerate(samples):
                    status = "✅ CORRECT" if sample['is_correct'] else "❌ WRONG"
                    print(f"   Sample {i+1}: {status}")
                    print(f"     True: {sample['true_class']}")
                    print(f"     Predicted: {sample['predicted_class']}")
                    print(f"     Confidence: {sample['confidence']:.3f}")
                    print(f"     True class probability: {sample['true_class_prob']:.3f}")
        
        # Overall statistics
        total_correct = sum(1 for r in analysis_results if r['is_correct'])
        total_samples = len(analysis_results)
        overall_accuracy = total_correct / total_samples if total_samples > 0 else 0
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Total samples: {total_samples}")
        print(f"   Correct predictions: {total_correct}")
        print(f"   Overall accuracy: {overall_accuracy:.1%}")
        
        # Confidence analysis
        confidences = [r['confidence'] for r in analysis_results]
        avg_confidence = np.mean(confidences)
        print(f"   Average confidence: {avg_confidence:.3f}")
        
        # Find most confused classes
        confusion_matrix = {}
        for result in analysis_results:
            true_class = result['true_class']
            pred_class = result['predicted_class']
            key = (true_class, pred_class)
            confusion_matrix[key] = confusion_matrix.get(key, 0) + 1
        
        print(f"\n🔍 CONFUSION ANALYSIS:")
        for (true_class, pred_class), count in confusion_matrix.items():
            if true_class != pred_class:
                print(f"   {true_class} → {pred_class}: {count} times")
    
    def suggest_improvements(self, analysis_results):
        """Suggest improvements based on analysis"""
        print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
        
        # Check for low confidence predictions
        low_confidence = [r for r in analysis_results if r['confidence'] < 0.5]
        if low_confidence:
            print(f"   ⚠️  {len(low_confidence)} predictions have low confidence (<50%)")
            print(f"      Consider: Increase training data, adjust model architecture")
        
        # Check for class imbalance in predictions
        pred_counts = {}
        for result in analysis_results:
            pred_class = result['predicted_class']
            pred_counts[pred_class] = pred_counts.get(pred_class, 0) + 1
        
        print(f"   📊 Prediction distribution:")
        for class_name, count in pred_counts.items():
            percentage = (count / len(analysis_results)) * 100
            print(f"      {class_name}: {count} predictions ({percentage:.1f}%)")
        
        # Check for specific class issues
        class_accuracy = {}
        for result in analysis_results:
            true_class = result['true_class']
            if true_class not in class_accuracy:
                class_accuracy[true_class] = {'correct': 0, 'total': 0}
            class_accuracy[true_class]['total'] += 1
            if result['is_correct']:
                class_accuracy[true_class]['correct'] += 1
        
        print(f"   🎯 Per-class accuracy:")
        for class_name, stats in class_accuracy.items():
            accuracy = stats['correct'] / stats['total']
            print(f"      {class_name}: {stats['correct']}/{stats['total']} = {accuracy:.1%}")
            
            if accuracy == 0:
                print(f"         ⚠️  {class_name} needs more training data!")
            elif accuracy < 0.5:
                print(f"         ⚠️  {class_name} needs improvement")
    
    def create_visualization(self, analysis_results, class_names):
        """Create visualization of prediction analysis"""
        logger.info("Creating prediction analysis visualization...")
        
        # Prepare data for visualization
        true_classes = [r['true_class'] for r in analysis_results]
        predicted_classes = [r['predicted_class'] for r in analysis_results]
        confidences = [r['confidence'] for r in analysis_results]
        is_correct = [r['is_correct'] for r in analysis_results]
        
        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Confidence distribution
        axes[0, 0].hist(confidences, bins=20, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('Prediction Confidence Distribution')
        axes[0, 0].set_xlabel('Confidence Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Per-class accuracy
        class_accuracy = {}
        for result in analysis_results:
            true_class = result['true_class']
            if true_class not in class_accuracy:
                class_accuracy[true_class] = {'correct': 0, 'total': 0}
            class_accuracy[true_class]['total'] += 1
            if result['is_correct']:
                class_accuracy[true_class]['correct'] += 1
        
        classes = list(class_accuracy.keys())
        accuracies = [class_accuracy[c]['correct'] / class_accuracy[c]['total'] for c in classes]
        
        bars = axes[0, 1].bar(classes, accuracies, color=['green' if a > 0.5 else 'red' for a in accuracies])
        axes[0, 1].set_title('Per-Class Accuracy')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].set_ylim(0, 1)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                           f'{acc:.1%}', ha='center', va='bottom')
        
        # 3. Confusion matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(true_classes, predicted_classes, labels=class_names)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1, 0])
        axes[1, 0].set_title('Confusion Matrix')
        axes[1, 0].set_xlabel('Predicted')
        axes[1, 0].set_ylabel('True')
        
        # 4. Confidence vs correctness
        correct_confidences = [conf for conf, correct in zip(confidences, is_correct) if correct]
        incorrect_confidences = [conf for conf, correct in zip(confidences, is_correct) if not correct]
        
        axes[1, 1].hist(correct_confidences, bins=10, alpha=0.7, label='Correct', color='green')
        axes[1, 1].hist(incorrect_confidences, bins=10, alpha=0.7, label='Incorrect', color='red')
        axes[1, 1].set_title('Confidence Distribution by Correctness')
        axes[1, 1].set_xlabel('Confidence Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'prediction_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualization saved to {self.results_dir / 'prediction_analysis.png'}")
    
    def run_analysis(self):
        """Run the complete prediction analysis"""
        logger.info("Starting model prediction analysis...")
        
        try:
            # Load model and data
            if not self.load_model_and_data():
                return False
            
            # Analyze predictions
            analysis_results, class_names = self.analyze_predictions()
            
            # Print detailed analysis
            self.print_detailed_analysis(analysis_results, class_names)
            
            # Suggest improvements
            self.suggest_improvements(analysis_results)
            
            # Create visualization
            self.create_visualization(analysis_results, class_names)
            
            # Save analysis results
            analysis_file = self.results_dir / 'prediction_analysis.json'
            with open(analysis_file, 'w') as f:
                json.dump({
                    'analysis_results': analysis_results,
                    'class_names': class_names,
                    'summary': {
                        'total_samples': len(analysis_results),
                        'correct_predictions': sum(1 for r in analysis_results if r['is_correct']),
                        'average_confidence': np.mean([r['confidence'] for r in analysis_results])
                    }
                }, f, indent=2)
            
            logger.info(f"Analysis results saved to {analysis_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Prediction analysis failed: {e}")
            return False

def main():
    """Main function"""
    print("="*70)
    print("Shine Skincare App - Model Prediction Analyzer")
    print("="*70)
    print("This analyzes why some categories show 0% accuracy")
    print("and provides detailed insights for improvement.")
    print("="*70)
    
    # Create analyzer
    analyzer = ModelPredictionAnalyzer()
    
    # Run analysis
    success = analyzer.run_analysis()
    
    if success:
        print("\n✅ Prediction analysis completed successfully!")
        print("📊 Check the detailed analysis above for insights")
        print("📈 Visualization saved to: results/prediction_analysis.png")
        print("📋 Results saved to: results/prediction_analysis.json")
    else:
        print("\n❌ Prediction analysis failed. Check logs for details.")

if __name__ == "__main__":
    main()
