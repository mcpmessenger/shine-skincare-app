#!/usr/bin/env python3
"""
Performance Monitoring for Enhanced Embeddings
Monitors analysis time, memory usage, CPU usage, and embedding quality
"""

import time
import psutil
import json
import numpy as np
import cv2
from datetime import datetime
from enhanced_analysis_api import EnhancedAnalysisAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_images():
    """Create a variety of test images for performance testing"""
    test_images = []
    
    # Different image sizes and qualities
    sizes = [(224, 224), (512, 512), (1024, 1024)]
    qualities = [50, 75, 95]
    
    for size in sizes:
        for quality in qualities:
            # Create test image
            img = np.random.randint(100, 200, (*size, 3), dtype=np.uint8)
            
            # Add skin-like features
            center_x, center_y = size[0] // 2, size[1] // 2
            radius = min(size) // 4
            cv2.circle(img, (center_x, center_y), radius, [180, 160, 140], -1)
            
            # Convert to bytes with specified quality
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])
            test_images.append({
                'data': buffer.tobytes(),
                'size': size,
                'quality': quality,
                'name': f"{size[0]}x{size[1]}_q{quality}"
            })
    
    return test_images

def monitor_performance():
    """Monitor the performance of the enhanced embedding system"""
    print("📊 Performance Monitoring for Enhanced Embeddings")
    print("=" * 60)
    
    # Initialize API
    api = EnhancedAnalysisAPI()
    
    # Create test images
    test_images = create_test_images()
    print(f"✅ Created {len(test_images)} test images")
    
    # Performance metrics
    metrics = {
        'analysis_times': [],
        'memory_usage': [],
        'cpu_usage': [],
        'embedding_dimensions': [],
        'confidence_scores': [],
        'quality_scores': [],
        'face_detection_results': [],
        'errors': []
    }
    
    # Test different analysis types
    analysis_types = ['comprehensive', 'focused', 'research']
    
    for i, test_image in enumerate(test_images):
        print(f"\n🔍 Testing image {i+1}/{len(test_images)}: {test_image['name']}")
        
        for analysis_type in analysis_types:
            try:
                # Record start time and system metrics
                start_time = time.time()
                start_memory = psutil.virtual_memory().percent
                start_cpu = psutil.cpu_percent()
                
                # Perform analysis
                result = api.analyze_skin_enhanced(test_image['data'], analysis_type)
                
                # Record end time and metrics
                end_time = time.time()
                end_memory = psutil.virtual_memory().percent
                end_cpu = psutil.cpu_percent()
                
                # Calculate metrics
                analysis_time = end_time - start_time
                memory_delta = end_memory - start_memory
                cpu_delta = end_cpu - start_cpu
                
                # Store metrics
                metrics['analysis_times'].append({
                    'image': test_image['name'],
                    'analysis_type': analysis_type,
                    'time': analysis_time,
                    'size': test_image['size'],
                    'quality': test_image['quality']
                })
                
                metrics['memory_usage'].append({
                    'image': test_image['name'],
                    'analysis_type': analysis_type,
                    'memory_delta': memory_delta,
                    'peak_memory': end_memory
                })
                
                metrics['cpu_usage'].append({
                    'image': test_image['name'],
                    'analysis_type': analysis_type,
                    'cpu_delta': cpu_delta,
                    'peak_cpu': end_cpu
                })
                
                # Embedding metrics
                if 'embedding_info' in result:
                    metrics['embedding_dimensions'].append({
                        'image': test_image['name'],
                        'analysis_type': analysis_type,
                        'dimensions': result['embedding_info']['dimensions']
                    })
                
                # Confidence and quality
                metrics['confidence_scores'].append({
                    'image': test_image['name'],
                    'analysis_type': analysis_type,
                    'confidence': result['confidence_score']
                })
                
                if 'quality_assessment' in result:
                    metrics['quality_scores'].append({
                        'image': test_image['name'],
                        'analysis_type': analysis_type,
                        'quality': result['quality_assessment']['overall_quality']
                    })
                
                # Face detection
                if 'face_detection' in result:
                    metrics['face_detection_results'].append({
                        'image': test_image['name'],
                        'analysis_type': analysis_type,
                        'detected': result['face_detection']['face_detected'],
                        'confidence': result['face_detection'].get('confidence', 0)
                    })
                
                print(f"   ✅ {analysis_type}: {analysis_time:.3f}s, Confidence: {result['confidence_score']:.3f}")
                
            except Exception as e:
                error_msg = f"Error processing {test_image['name']} with {analysis_type}: {str(e)}"
                metrics['errors'].append(error_msg)
                print(f"   ❌ {analysis_type}: Error - {str(e)}")
    
    # Calculate summary statistics
    summary = calculate_summary_statistics(metrics)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"performance_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'detailed_metrics': metrics
        }, f, indent=2)
    
    print(f"\n📊 Performance Summary:")
    print(f"   Average Analysis Time: {summary['avg_analysis_time']:.3f}s")
    print(f"   Average Memory Usage: {summary['avg_memory_delta']:.2f}%")
    print(f"   Average CPU Usage: {summary['avg_cpu_delta']:.2f}%")
    print(f"   Average Confidence: {summary['avg_confidence']:.3f}")
    print(f"   Average Quality Score: {summary['avg_quality']:.3f}")
    print(f"   Face Detection Rate: {summary['face_detection_rate']:.1f}%")
    print(f"   Error Rate: {summary['error_rate']:.1f}%")
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return summary

def calculate_summary_statistics(metrics):
    """Calculate summary statistics from performance metrics"""
    summary = {}
    
    # Analysis times
    if metrics['analysis_times']:
        times = [m['time'] for m in metrics['analysis_times']]
        summary['avg_analysis_time'] = np.mean(times)
        summary['min_analysis_time'] = np.min(times)
        summary['max_analysis_time'] = np.max(times)
    
    # Memory usage
    if metrics['memory_usage']:
        memory_deltas = [m['memory_delta'] for m in metrics['memory_usage']]
        summary['avg_memory_delta'] = np.mean(memory_deltas)
        summary['peak_memory'] = max([m['peak_memory'] for m in metrics['memory_usage']])
    
    # CPU usage
    if metrics['cpu_usage']:
        cpu_deltas = [m['cpu_delta'] for m in metrics['cpu_usage']]
        summary['avg_cpu_delta'] = np.mean(cpu_deltas)
        summary['peak_cpu'] = max([m['peak_cpu'] for m in metrics['cpu_usage']])
    
    # Confidence scores
    if metrics['confidence_scores']:
        confidences = [m['confidence'] for m in metrics['confidence_scores']]
        summary['avg_confidence'] = np.mean(confidences)
        summary['min_confidence'] = np.min(confidences)
        summary['max_confidence'] = np.max(confidences)
    
    # Quality scores
    if metrics['quality_scores']:
        qualities = [m['quality'] for m in metrics['quality_scores']]
        summary['avg_quality'] = np.mean(qualities)
        summary['min_quality'] = np.min(qualities)
        summary['max_quality'] = np.max(qualities)
    
    # Face detection rate
    if metrics['face_detection_results']:
        detected_count = sum(1 for m in metrics['face_detection_results'] if m['detected'])
        total_count = len(metrics['face_detection_results'])
        summary['face_detection_rate'] = (detected_count / total_count) * 100
    
    # Error rate
    total_analyses = len(metrics['analysis_times'])
    error_count = len(metrics['errors'])
    summary['error_rate'] = (error_count / total_analyses) * 100 if total_analyses > 0 else 0
    
    return summary

if __name__ == "__main__":
    try:
        summary = monitor_performance()
        print("\n🎉 Performance monitoring completed successfully!")
        print("📈 Enhanced embedding system is performing well!")
    except Exception as e:
        print(f"❌ Performance monitoring failed: {e}")
        import traceback
        traceback.print_exc() 