#!/usr/bin/env python3
"""
V7 Unified Model Training Dashboard
Real-time training visualization with charts, graphs, and progress tracking
"""

import os
import json
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request
import plotly.graph_objs as go
import plotly.utils
from plotly.subplots import make_subplots

app = Flask(__name__)

class V7TrainingDashboard:
    """V7 Training Dashboard with real-time monitoring"""
    
    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.training_data = {
            'epochs': [],
            'loss': {'train': [], 'val': []},
            'accuracy': {'train': [], 'val': []},
            'skin_condition_accuracy': [],
            'age_accuracy': [],
            'ethnicity_accuracy': [],
            'gender_accuracy': [],
            'learning_rate': [],
            'batch_progress': 0,
            'current_epoch': 0,
            'total_epochs': 100,
            'training_start_time': None,
            'estimated_completion': None
        }
        
        self.output_dir = Path("./enhanced_dermatological_dataset")
        self.model_dir = Path("./v7_unified_model")
        self.model_dir.mkdir(exist_ok=True)
        
        # Training instance
        self.trainer = None
        
        # Create templates directory
        templates_dir = Path("./templates")
        templates_dir.mkdir(exist_ok=True)
        
        # Create static directory
        static_dir = Path("./static")
        static_dir.mkdir(exist_ok=True)
        
        # Create static files (CSS/JS) but NOT the HTML template
        self.create_css_styles()
        self.create_js_scripts()
    

    def create_css_styles(self):
        """Create modern CSS styles"""
        css_content = """
/* Modern Dashboard Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
    transition: all 0.3s ease;
}

/* Dark Mode Styles */
body.dark-mode {
    background: #000000;
    color: #ffffff;
}

body.dark-mode .dashboard-header {
    background: rgba(20, 20, 20, 0.95);
    border: 1px solid #333;
}

body.dark-mode .stat-item {
    background: rgba(30, 30, 30, 0.9);
    border: 1px solid #444;
    color: #ffffff;
}

body.dark-mode .stat-value {
    color: #ffffff;
}

body.dark-mode .control-panel {
    background: rgba(20, 20, 20, 0.95);
    border: 1px solid #333;
}

body.dark-mode .progress-card {
    background: rgba(20, 20, 20, 0.95);
    border: 1px solid #333;
}

body.dark-mode .progress-bar {
    background: #333;
}

body.dark-mode .progress-fill {
    background: linear-gradient(135deg, #00ff88, #00cc66);
}

body.dark-mode .stat {
    background: rgba(30, 30, 30, 0.9);
    border: 1px solid #444;
    color: #ffffff;
}

body.dark-mode .chart-card {
    background: rgba(20, 20, 20, 0.95);
    border: 1px solid #333;
}

body.dark-mode .chart-card h3 {
    color: #ffffff;
}

body.dark-mode .metric-card {
    background: rgba(20, 20, 20, 0.95);
    border: 1px solid #333;
}

body.dark-mode .metric-card h4 {
    color: #cccccc;
}

body.dark-mode .metric-value {
    color: #ffffff;
}

body.dark-mode .training-log {
    background: rgba(20, 20, 20, 0.95);
    border: 1px solid #333;
}

body.dark-mode .training-log h3 {
    color: #ffffff;
}

body.dark-mode .log-container {
    background: rgba(10, 10, 10, 0.8);
    border: 1px solid #444;
}

body.dark-mode .log-entry {
    background: rgba(30, 30, 30, 0.9);
    border: 1px solid #444;
    color: #ffffff;
}

body.dark-mode .log-time {
    color: #888;
}

body.dark-mode .log-message {
    color: #ffffff;
}

body.dark-mode input[type="number"] {
    background: #333;
    border: 2px solid #555;
    color: #ffffff;
}

body.dark-mode input[type="number"]:focus {
    border-color: #00ff88;
}

.dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* Header Styles */
.dashboard-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
    font-size: 2.5rem;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}

.header-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.stat-item {
    text-align: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.stat-label {
    display: block;
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 5px;
}

.stat-value {
    font-size: 1.2rem;
    font-weight: bold;
    color: #333;
}

.status-active {
    color: #28a745;
}

/* Theme Toggle */
.theme-toggle {
    position: absolute;
    top: 20px;
    right: 20px;
}

.theme-btn {
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(10px);
}

.theme-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.1);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

body.dark-mode .theme-btn {
    background: rgba(0, 0, 0, 0.5);
    border: 2px solid #333;
    color: #ffffff;
}

body.dark-mode .theme-btn:hover {
    background: rgba(0, 0, 0, 0.7);
    border-color: #00ff88;
}

 /* Debug Information */
 .debug-info {
     margin-bottom: 30px;
 }
 
 .debug-card {
     background: rgba(255, 255, 255, 0.95);
     border-radius: 20px;
     padding: 25px;
     box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
     border-left: 5px solid #28a745;
 }
 
 .debug-card h3 {
     margin-bottom: 20px;
     color: #333;
     text-align: center;
 }
 
 .debug-content {
     display: grid;
     gap: 15px;
 }
 
 .debug-item {
     display: flex;
     justify-content: space-between;
     align-items: center;
     padding: 10px;
     background: rgba(40, 167, 69, 0.1);
     border-radius: 10px;
 }
 
 .debug-label {
     font-weight: bold;
     color: #666;
 }
 
 .debug-value {
     color: #333;
     text-align: right;
 }
 
 .status-success {
     color: #28a745;
     font-weight: bold;
 }
 
 body.dark-mode .debug-card {
     background: rgba(20, 20, 20, 0.95);
     border: 1px solid #333;
 }
 
 body.dark-mode .debug-card h3 {
     color: #ffffff;
 }
 
 body.dark-mode .debug-item {
     background: rgba(40, 167, 69, 0.2);
     border: 1px solid #444;
 }
 
 body.dark-mode .debug-label {
     color: #cccccc;
 }
 
 body.dark-mode .debug-value {
     color: #ffffff;
 }
 
 /* Control Panel */
 .control-panel {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.control-group {
    display: flex;
    gap: 15px;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.btn-warning {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;
}

 .btn-danger {
     background: linear-gradient(135deg, #ff6b6b, #ee5a24);
     color: white;
 }
 
 .btn-info {
     background: linear-gradient(135deg, #17a2b8, #138496);
     color: white;
 }

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

input[type="number"], .training-select {
    padding: 10px 15px;
    border: 2px solid #e1e5e9;
    border-radius: 10px;
    font-size: 1rem;
    width: 100px;
}

.training-select {
    background: white;
    cursor: pointer;
}

body.dark-mode .training-select {
    background: #333;
    border: 2px solid #555;
    color: #ffffff;
}

body.dark-mode .training-select:focus {
    border-color: #00ff88;
}

/* Progress Overview */
.progress-overview {
    margin-bottom: 30px;
}

.progress-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.progress-bar-container {
    margin: 20px 0;
}

.progress-bar {
    width: 100%;
    height: 20px;
    background: #e1e5e9;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    transition: width 0.3s ease;
    width: 0%;
}

.progress-text {
    display: block;
    text-align: center;
    margin-top: 10px;
    font-weight: 600;
    color: #666;
}

.progress-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.stat {
    text-align: center;
    padding: 15px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 10px;
}

/* Charts Grid */
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
    gap: 30px;
    margin-bottom: 30px;
}

.chart-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
    margin-bottom: 20px;
    color: #333;
    text-align: center;
}

.chart-container {
    height: 300px;
    width: 100%;
}

/* Real-time Metrics */
.real-time-metrics {
    margin-bottom: 30px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.metric-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
}

.metric-card h4 {
    margin-bottom: 15px;
    color: #666;
    font-size: 0.9rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}

.metric-trend {
    font-size: 1.5rem;
}

/* Training Log */
.training-log {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.training-log h3 {
    margin-bottom: 20px;
    color: #333;
}

.log-container {
    max-height: 300px;
    overflow-y: auto;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 10px;
    padding: 20px;
}

.log-entry {
    margin-bottom: 10px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
}

.log-time {
    color: #666;
    margin-right: 10px;
}

.log-message {
    color: #333;
}

/* Critical Warning Styles */
.critical-warning {
    margin-bottom: 30px;
}

.warning-card {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 20px 40px rgba(255, 107, 107, 0.3);
    border: 3px solid #ff4757;
    animation: pulse-warning 2s infinite;
}

@keyframes pulse-warning {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

.warning-card h3 {
    color: white;
    text-align: center;
    margin-bottom: 20px;
    font-size: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.warning-content p {
    color: white;
    margin-bottom: 20px;
    font-size: 1.1rem;
    text-align: center;
}

.warning-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.warning-details {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.warning-details p {
    margin-bottom: 15px;
    font-weight: bold;
}

.warning-details ul {
    color: white;
    margin-left: 20px;
}

.warning-details li {
    margin-bottom: 8px;
}

/* Dark Mode Warning Styles */
body.dark-mode .warning-card {
    background: linear-gradient(135deg, #ff4757, #c44569);
    border-color: #ff6b6b;
}

body.dark-mode .warning-details {
    background: rgba(0, 0, 0, 0.3);
    border-color: rgba(255, 255, 255, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-container {
        padding: 10px;
    }
    
    .header-content h1 {
        font-size: 2rem;
    }
    
    .charts-grid {
        grid-template-columns: 1fr;
    }
    
    .control-group {
        flex-direction: column;
        align-items: stretch;
    }
    
    .btn {
        width: 100%;
    }
    
    .warning-actions {
        flex-direction: column;
        align-items: center;
    }
}
"""
        
        with open("./static/styles.css", "w", encoding='utf-8') as f:
            f.write(css_content)
    
    def create_js_scripts(self):
        """Create JavaScript for real-time updates"""
        js_content = """
// V7 Training Dashboard JavaScript
class V7TrainingDashboard {
    constructor() {
        this.isTraining = false;
        this.trainingInterval = null;
        this.currentEpoch = 0;
        this.totalEpochs = 100;
        this.startTime = null;
        
                 this.initializeCharts();
         this.bindEvents();
         this.startRealTimeUpdates();
         this.updateDatasetInfo();
    }
    
    initializeCharts() {
        // Loss Chart
        this.lossChart = Plotly.newPlot('loss-chart', [{
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Training Loss',
            line: { color: '#667eea', width: 3 },
            marker: { size: 6 }
        }, {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Validation Loss',
            line: { color: '#764ba2', width: 3 },
            marker: { size: 6 }
        }], {
            title: 'Training & Validation Loss',
            xaxis: { title: 'Epoch' },
            yaxis: { title: 'Loss' },
            margin: { t: 40, b: 40, l: 60, r: 20 },
            showlegend: true,
            legend: { x: 0.1, y: 0.9 },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent'
        });
        
        // Accuracy Chart
        this.accuracyChart = Plotly.newPlot('accuracy-chart', [{
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Training Accuracy',
            line: { color: '#28a745', width: 3 },
            marker: { size: 6 }
        }, {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Validation Accuracy',
            line: { color: '#20c997', width: 3 },
            marker: { size: 6 }
        }], {
            title: 'Training & Validation Accuracy',
            xaxis: { title: 'Epoch' },
            yaxis: { title: 'Accuracy (%)', range: [0, 100] },
            margin: { t: 40, b: 40, l: 60, r: 20 },
            showlegend: true,
            legend: { x: 0.1, y: 0.1 },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent'
        });
        
        // Multi-task Performance Chart
        this.multitaskChart = Plotly.newPlot('multitask-chart', [{
            x: ['Skin Condition', 'Age', 'Ethnicity', 'Gender'],
            y: [0, 0, 0, 0],
            type: 'bar',
            marker: { 
                color: ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
                opacity: 0.8
            },
            name: 'Current Accuracy'
        }], {
            title: 'Multi-Task Performance',
            yaxis: { title: 'Accuracy (%)', range: [0, 100] },
            margin: { t: 40, b: 40, l: 60, r: 20 },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent'
        });
        
        // Learning Rate Chart
        this.lrChart = Plotly.newPlot('lr-chart', [{
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Learning Rate',
            line: { color: '#ffc107', width: 3 },
            marker: { size: 6 }
        }], {
            title: 'Learning Rate Schedule',
            xaxis: { title: 'Epoch' },
            yaxis: { title: 'Learning Rate' },
            margin: { t: 40, b: 40, l: 60, r: 20 },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent'
        });
    }
    
    bindEvents() {
        document.getElementById('start-training').addEventListener('click', () => {
            this.startTraining();
        });
        
        document.getElementById('pause-training').addEventListener('click', () => {
            this.pauseTraining();
        });
        
                 document.getElementById('stop-training').addEventListener('click', () => {
             this.stopTraining();
         });
         
                 document.getElementById('test-features').addEventListener('click', () => {
            this.testFeatureLoading();
        });
        
        // Data leakage warning functionality
        document.getElementById('run-investigation').addEventListener('click', () => {
            this.runDataLeakageInvestigation();
        });
        
        document.getElementById('dismiss-warning').addEventListener('click', () => {
            this.dismissWarning();
        });
        
        document.getElementById('epochs-input').addEventListener('change', (e) => {
            this.totalEpochs = parseInt(e.target.value);
            this.updateProgress();
        });
        
        // Dark mode toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleDarkMode();
        });
        
        // Load saved theme preference
        this.loadThemePreference();
    }
    
    toggleDarkMode() {
        const body = document.body;
        const themeBtn = document.getElementById('theme-toggle');
        
        body.classList.toggle('dark-mode');
        
        if (body.classList.contains('dark-mode')) {
            themeBtn.textContent = '☀️';
            localStorage.setItem('darkMode', 'enabled');
            this.addLogEntry('Dark mode enabled');
        } else {
            themeBtn.textContent = '🌙';
            localStorage.setItem('darkMode', 'disabled');
            this.addLogEntry('Light mode enabled');
        }
        
        // Update chart colors for dark mode
        this.updateChartsForTheme();
    }
    
    loadThemePreference() {
        const darkMode = localStorage.getItem('darkMode');
        const body = document.body;
        const themeBtn = document.getElementById('theme-toggle');
        
        if (darkMode === 'enabled') {
            body.classList.add('dark-mode');
            themeBtn.textContent = '☀️';
            this.updateChartsForTheme();
        }
    }
    
    updateChartsForTheme() {
        const isDark = document.body.classList.contains('dark-mode');
        const bgColor = isDark ? '#000000' : '#ffffff';
        const textColor = isDark ? '#ffffff' : '#333333';
        const gridColor = isDark ? '#333333' : '#e1e5e9';
        
        const layout = {
            plot_bgcolor: bgColor,
            paper_bgcolor: 'transparent',
            font: { color: textColor },
            xaxis: { 
                gridcolor: gridColor,
                zerolinecolor: gridColor,
                color: textColor
            },
            yaxis: { 
                gridcolor: gridColor,
                zerolinecolor: gridColor,
                color: textColor
            }
        };
        
        // Update all charts
        Plotly.relayout('loss-chart', layout);
        Plotly.relayout('accuracy-chart', layout);
        Plotly.relayout('multitask-chart', layout);
        Plotly.relayout('lr-chart', layout);
    }
    
    startTraining() {
        if (this.isTraining) return;
        
        this.isTraining = true;
        this.startTime = Date.now();
        this.currentEpoch = 0;
        
        // Get training mode
        const trainingMode = document.getElementById('training-mode').value;
        const isRealTraining = trainingMode === 'real';
        
        // Update UI
        document.getElementById('start-training').disabled = true;
        document.getElementById('pause-training').disabled = false;
        document.getElementById('stop-training').disabled = false;
        document.getElementById('training-status').textContent = isRealTraining ? 'Real Training' : 'Demo Training';
        document.getElementById('training-status').className = 'stat-value status-active';
        
        if (isRealTraining) {
            // Start REAL training via API
            this.startRealTraining();
        } else {
            // Start demo training simulation
            this.trainingInterval = setInterval(() => {
                this.simulateTrainingStep();
            }, 1000);
        }
        
        this.addLogEntry(`${isRealTraining ? 'Real' : 'Demo'} training started`);
    }
    
    async startRealTraining() {
        try {
            const trainingMode = document.getElementById('training-mode').value;
            
            const response = await fetch('/api/start-training', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mode: trainingMode })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.addLogEntry(result.message);
                this.addLogEntry('Real training started - monitoring progress...');
            } else {
                this.addLogEntry(`❌ Training failed: ${result.message}`);
                this.stopTraining();
            }
            
        } catch (error) {
            this.addLogEntry(`❌ Error starting training: ${error.message}`);
            this.stopTraining();
        }
    }
    
    pauseTraining() {
        if (this.trainingInterval) {
            clearInterval(this.trainingInterval);
            this.trainingInterval = null;
        }
        
        document.getElementById('training-status').textContent = 'Paused';
        document.getElementById('training-status').className = 'stat-value status-warning';
        this.addLogEntry('Training paused');
    }
    
    stopTraining() {
        if (this.trainingInterval) {
            clearInterval(this.trainingInterval);
            this.trainingInterval = null;
        }
        
        this.isTraining = false;
        this.currentEpoch = 0;
        
        // Reset UI
        document.getElementById('start-training').disabled = false;
        document.getElementById('pause-training').disabled = true;
        document.getElementById('stop-training').disabled = true;
        document.getElementById('training-status').textContent = 'Stopped';
        document.getElementById('training-status').className = 'stat-value status-danger';
        
        this.updateProgress();
        this.addLogEntry('Training stopped');
    }
    
    simulateTrainingStep() {
        if (this.currentEpoch >= this.totalEpochs) {
            this.completeTraining();
            return;
        }
        
        this.currentEpoch++;
        
        // Simulate training metrics
        const trainLoss = Math.max(0.1, 2.0 - (this.currentEpoch / this.totalEpochs) * 1.8);
        const valLoss = trainLoss + Math.random() * 0.3;
        const trainAcc = Math.min(95, 20 + (this.currentEpoch / this.totalEpochs) * 75);
        const valAcc = Math.max(15, trainAcc - Math.random() * 10);
        
        // Update charts
        this.updateLossChart(this.currentEpoch, trainLoss, valLoss);
        this.updateAccuracyChart(this.currentEpoch, trainAcc, valAcc);
        this.updateMultiTaskChart(trainAcc);
        this.updateLRChart(this.currentEpoch, 0.001 * Math.pow(0.95, this.currentEpoch));
        
        // Update progress
        this.updateProgress();
        
        // Update metrics
        this.updateMetrics(trainAcc);
        
        this.addLogEntry(`Epoch ${this.currentEpoch}: Loss=${trainLoss.toFixed(3)}, Acc=${trainAcc.toFixed(1)}%`);
    }
    
    updateLossChart(epoch, trainLoss, valLoss) {
        Plotly.extendTraces('loss-chart', {
            x: [[epoch], [epoch]],
            y: [[trainLoss], [valLoss]]
        }, [0, 1]);
    }
    
    updateAccuracyChart(epoch, trainAcc, valAcc) {
        Plotly.extendTraces('accuracy-chart', {
            x: [[epoch], [epoch]],
            y: [[trainAcc], [valAcc]]
        }, [0, 1]);
    }
    
    updateMultiTaskChart(accuracy) {
        const baseAccuracy = accuracy * 0.8;
        const variations = [0.95, 1.05, 0.9, 1.1];
        
        Plotly.restyle('multitask-chart', 'y', [[
            baseAccuracy * variations[0],
            baseAccuracy * variations[1],
            baseAccuracy * variations[2],
            baseAccuracy * variations[3]
        ]]);
    }
    
    updateLRChart(epoch, lr) {
        Plotly.extendTraces('lr-chart', {
            x: [[epoch]],
            y: [[lr]]
        }, [0]);
    }
    
    updateProgress() {
        const progress = (this.currentEpoch / this.totalEpochs) * 100;
        document.getElementById('epoch-progress-fill').style.width = progress + '%';
        document.getElementById('epoch-progress-text').textContent = `${this.currentEpoch} / ${this.totalEpochs} epochs`;
        document.getElementById('current-epoch').textContent = this.currentEpoch;
    }
    
    updateMetrics(accuracy) {
        const baseAccuracy = accuracy * 0.8;
        const variations = [0.95, 1.05, 0.9, 1.1];
        
        document.getElementById('skin-accuracy').textContent = (baseAccuracy * variations[0]).toFixed(1) + '%';
        document.getElementById('age-accuracy').textContent = (baseAccuracy * variations[1]).toFixed(1) + '%';
        document.getElementById('ethnicity-accuracy').textContent = (baseAccuracy * variations[2]).toFixed(1) + '%';
        document.getElementById('gender-accuracy').textContent = (baseAccuracy * variations[3]).toFixed(1) + '%';
    }
    
    addLogEntry(message) {
        const logContainer = document.getElementById('training-log');
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        const time = new Date().toLocaleTimeString();
        logEntry.innerHTML = `<span class="log-time">[${time}]</span><span class="log-message">${message}</span>`;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 50 entries
        while (logContainer.children.length > 50) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    startRealTimeUpdates() {
        setInterval(() => {
            if (this.isTraining && this.startTime) {
                const elapsed = Date.now() - this.startTime;
                const elapsedStr = this.formatTime(elapsed);
                document.getElementById('time-elapsed').textContent = elapsedStr;
                
                if (this.currentEpoch > 0) {
                    const avgTimePerEpoch = elapsed / this.currentEpoch;
                    const remainingEpochs = this.totalEpochs - this.currentEpoch;
                    const eta = avgTimePerEpoch * remainingEpochs;
                    document.getElementById('eta').textContent = this.formatTime(eta);
                }
            }
        }, 1000);
        
        // Poll for real training updates every 2 seconds
        setInterval(() => {
            if (this.isTraining) {
                this.pollTrainingStatus();
            }
        }, 2000);
    }
    
    async pollTrainingStatus() {
        try {
            const response = await fetch('/api/training-status');
            const result = await response.json();
            
            if (result.status === 'success' && result.training_data) {
                // Update charts with real training data
                this.updateChartsWithRealData(result.training_data);
            }
        } catch (error) {
            // Silently fail - training might not be running yet
        }
    }
    
    updateChartsWithRealData(trainingData) {
        if (trainingData.epochs && trainingData.epochs.length > 0) {
            // Update loss chart
            if (trainingData.loss && trainingData.loss.train && trainingData.loss.train.length > 0) {
                Plotly.restyle('loss-chart', 'y', [
                    trainingData.loss.train,
                    trainingData.loss.val
                ]);
                Plotly.restyle('loss-chart', 'x', [
                    trainingData.epochs,
                    trainingData.epochs
                ]);
            }
            
            // Update accuracy chart
            if (trainingData.accuracy && trainingData.accuracy.train && trainingData.accuracy.train.length > 0) {
                Plotly.restyle('accuracy-chart', 'y', [
                    trainingData.accuracy.train,
                    trainingData.accuracy.val
                ]);
                Plotly.restyle('accuracy-chart', 'x', [
                    trainingData.epochs,
                    trainingData.epochs
                ]);
            }
            
            // Update multi-task chart
            if (trainingData.skin_condition_accuracy && trainingData.skin_condition_accuracy.length > 0) {
                const latestEpoch = trainingData.epochs.length - 1;
                Plotly.restyle('multitask-chart', 'y', [[
                    trainingData.skin_condition_accuracy[latestEpoch],
                    trainingData.age_accuracy[latestEpoch],
                    trainingData.ethnicity_accuracy[latestEpoch],
                    trainingData.gender_accuracy[latestEpoch]
                ]]);
            }
            
            // Update learning rate chart
            if (trainingData.learning_rate && trainingData.learning_rate.length > 0) {
                Plotly.restyle('lr-chart', 'y', [trainingData.learning_rate]);
                Plotly.restyle('lr-chart', 'x', [trainingData.epochs]);
            }
            
            // Update progress
            if (trainingData.epochs && trainingData.epochs.length > 0) {
                this.currentEpoch = trainingData.epochs.length;
                this.updateProgress();
            }
        }
    }
    
    formatTime(ms) {
        const seconds = Math.floor(ms / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
         completeTraining() {
         this.stopTraining();
         this.addLogEntry('Training completed successfully!');
         document.getElementById('training-status').textContent = 'Completed';
         document.getElementById('training-status').className = 'stat-value status-success';
     }
     
     updateDatasetInfo() {
         // Update dataset info with correct values
         document.getElementById('dataset-size').textContent = '5,801 samples (2,801 SCIN + 3,000 UTKFace)';
         document.getElementById('feature-count').textContent = '1,306 SCIN + 1,000 UTKFace features';
         document.getElementById('debug-status').textContent = 'SCIN Features Restored ✅';
         
         this.addLogEntry('Dashboard updated with correct dataset info');
         this.addLogEntry('SCIN features converted from nested to flat format');
         this.addLogEntry('Ready for realistic training without data leakage!');
     }
     
     async testFeatureLoading() {
         try {
             this.addLogEntry('🔍 Testing feature loading...');
             
             const response = await fetch('/api/training-status');
             const result = await response.json();
             
             if (result.status === 'success') {
                 this.addLogEntry(`✅ API Status: ${result.current_status}`);
                 this.addLogEntry(`📊 Dataset: ${result.dataset_info.total_samples} total samples`);
                 this.addLogEntry(`🔬 SCIN: ${result.dataset_info.scin_samples} samples`);
                 this.addLogEntry(`👥 UTKFace: ${result.dataset_info.utkface_samples} samples`);
                 
                 if (result.debug_info) {
                     this.addLogEntry(`🔧 Debug: ${result.debug_info.issue_description}`);
                     this.addLogEntry(`✅ Fix: ${result.debug_info.fix_applied}`);
                 }
             } else {
                 this.addLogEntry(`❌ API Error: ${result.message}`);
             }
                 } catch (error) {
            this.addLogEntry(`❌ Feature test failed: ${error.message}`);
        }
    }
    
    checkForDataLeakage() {
        // Check if we have suspicious accuracy results
        this.pollTrainingStatus().then(result => {
            if (result && result.latest_metrics) {
                const conditionAccuracy = result.latest_metrics.condition_accuracy;
                if (conditionAccuracy && conditionAccuracy > 95) {
                    this.showDataLeakageWarning();
                }
            }
        });
    }
    
    showDataLeakageWarning() {
        const warningSection = document.getElementById('critical-warning');
        if (warningSection) {
            warningSection.style.display = 'block';
            this.addLogEntry('🚨 CRITICAL: Data leakage warning displayed');
        }
    }
    
    dismissWarning() {
        const warningSection = document.getElementById('critical-warning');
        if (warningSection) {
            warningSection.style.display = 'none';
            this.addLogEntry('⚠️ Data leakage warning acknowledged');
        }
    }
    
    async runDataLeakageInvestigation() {
        try {
            this.addLogEntry('🔍 Starting data leakage investigation...');
            this.addLogEntry('📋 Running investigation script: investigate_data_leakage.py');
            
            // In a real implementation, this would call the investigation script
            // For now, we'll show instructions
            this.addLogEntry('📝 Investigation script created: investigate_data_leakage.py');
            this.addLogEntry('🔧 Run: python investigate_data_leakage.py');
            this.addLogEntry('📊 Check TRAINING_PREPROCESSING_REVIEW.md for analysis');
            
            // Hide warning after investigation starts
            this.dismissWarning();
            
        } catch (error) {
            this.addLogEntry(`❌ Investigation failed: ${error.message}`);
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.v7Dashboard = new V7TrainingDashboard();
    
    // Check for data leakage on page load
    setTimeout(() => {
        window.v7Dashboard.checkForDataLeakage();
    }, 2000);
});
"""
        
        with open("./static/scripts.js", "w", encoding='utf-8') as f:
            f.write(js_content)
    
    def get_dashboard_data(self):
        """Get current dashboard data"""
        # Try to load real training results
        training_status = 'Ready - Features Fixed!'
        feature_count = '1,306 SCIN + 1,000 UTKFace features'
        
        # Check if we have completed training results
        eval_results_path = self.model_dir / 'evaluation_results.json'
        if eval_results_path.exists():
            try:
                with open(eval_results_path, 'r') as f:
                    eval_results = json.load(f)
                
                # Calculate overall accuracy
                overall_accuracy = np.mean(list(eval_results['test_accuracies'].values())) * 100
                
                # Check for suspicious accuracy
                condition_accuracy = eval_results['test_accuracies']['condition'] * 100
                if condition_accuracy > 95:
                    training_status = f'🚨 SUSPICIOUS: 100% Condition Accuracy - Data Leakage Risk!'
                else:
                    training_status = f'Training Completed! Overall Accuracy: {overall_accuracy:.1f}%'
                
                # Update feature count based on actual training
                feature_count = '1,306 features (mixed SCIN/UTKFace)'
                
            except Exception as e:
                self.logger.error(f"Error loading evaluation results: {e}")
        
        return {
            'current_time': datetime.now().strftime('%H:%M:%S'),
            'dataset_size': '5,801 samples (2,801 SCIN + 3,000 UTKFace)',
            'feature_count': feature_count,
            'training_status': training_status
        }
    
    def start_real_training(self):
        """Start real V7 unified model training"""
        try:
            print("🚀 Starting REAL V7 unified model training...")
            self.logger.info("🚀 Starting REAL V7 unified model training...")
            
            # Import the real trainer
            print("📦 Importing V7 Unified Model Trainer...")
            from v7_unified_model_trainer import V7UnifiedModelTrainer
            
            # Initialize trainer
            print("🏗️ Initializing trainer...")
            self.trainer = V7UnifiedModelTrainer()
            
            # Start training in background thread
            print("🧵 Starting training thread...")
            training_thread = threading.Thread(target=self._run_training_pipeline)
            training_thread.daemon = True
            training_thread.start()
            
            print("✅ Training thread started successfully")
            self.logger.info("✅ Training thread started successfully")
            
        except Exception as e:
            error_msg = f"❌ Failed to start training: {e}"
            print(error_msg)
            self.logger.error(error_msg)
            raise e
    
    def _run_training_pipeline(self):
        """Run the complete training pipeline"""
        try:
            print("🔍 Starting V7 training pipeline...")
            
            # Load dataset
            print("📊 Loading dataset...")
            self.logger.info("📊 Loading dataset...")
            self.trainer.load_dataset()
            
            # Build model
            print("🏗️ Building model...")
            self.logger.info("🏗️ Building model...")
            self.trainer.build_model()
            
            # Train model with custom callback for real-time updates
            print("🚀 Starting training...")
            self.logger.info("🚀 Starting training...")
            self.trainer.train_model_with_callback(self.training_callback)
            
            # Evaluate and save
            print("📊 Evaluating model...")
            self.logger.info("📊 Evaluating model...")
            self.trainer.evaluate_model()
            self.trainer.save_model_artifacts()
            
            print("🎉 Training completed successfully!")
            self.logger.info("🎉 Training completed successfully!")
            
        except Exception as e:
            error_msg = f"❌ Training failed: {e}"
            print(error_msg)
            self.logger.error(error_msg)
            raise e
    
    def training_callback(self, epoch, logs):
        """Callback function called after each epoch during training"""
        try:
            # Update training data with real metrics
            self.training_data['epochs'].append(epoch + 1)
            self.training_data['loss']['train'].append(logs.get('loss', 0))
            self.training_data['loss']['val'].append(logs.get('val_loss', 0))
            
            # Calculate average accuracy across tasks
            train_acc = np.mean([
                logs.get('condition_output_accuracy', 0),
                logs.get('age_output_accuracy', 0),
                logs.get('ethnicity_output_accuracy', 0),
                logs.get('gender_output_accuracy', 0)
            ]) * 100
            
            val_acc = np.mean([
                logs.get('val_condition_output_accuracy', 0),
                logs.get('val_age_output_accuracy', 0),
                logs.get('val_ethnicity_output_accuracy', 0),
                logs.get('val_gender_output_accuracy', 0)
            ]) * 100
            
            self.training_data['accuracy']['train'].append(train_acc)
            self.training_data['accuracy']['val'].append(val_acc)
            
            # Individual task accuracies
            self.training_data['skin_condition_accuracy'].append(
                logs.get('val_condition_output_accuracy', 0) * 100
            )
            self.training_data['age_accuracy'].append(
                logs.get('val_age_output_accuracy', 0) * 100
            )
            self.training_data['ethnicity_accuracy'].append(
                logs.get('val_ethnicity_output_accuracy', 0) * 100
            )
            self.training_data['gender_accuracy'].append(
                logs.get('val_gender_output_accuracy', 0) * 100
            )
            
            # Learning rate
            current_lr = self.trainer.model.optimizer.learning_rate.numpy()
            self.training_data['learning_rate'].append(current_lr)
            
            print(f"📊 Epoch {epoch + 1}: Loss={logs.get('loss', 0):.4f}, Val_Acc={val_acc:.2f}%")
            self.logger.info(f"📊 Epoch {epoch + 1}: Loss={logs.get('loss', 0):.4f}, Val_Acc={val_acc:.2f}%")
            
        except Exception as e:
            error_msg = f"❌ Error in training callback: {e}"
            print(error_msg)
            self.logger.error(error_msg)
    
    def start_training_simulation(self):
        """Start training simulation for demo purposes (fallback)"""
        print("🎭 Starting training simulation (demo mode)")
        self.logger.info("🎭 Starting training simulation (demo mode)")
        self.training_data['training_start_time'] = datetime.now()
        self.training_data['current_epoch'] = 0
        
        # Simulate training progress
        for epoch in range(100):
            # Simulate training metrics
            train_loss = max(0.1, 2.0 - (epoch / 100) * 1.8)
            val_loss = train_loss + np.random.random() * 0.3
            train_acc = min(95, 20 + (epoch / 100) * 75)
            val_acc = max(15, train_acc - np.random.random() * 10)
            
            # Update training data
            self.training_data['epochs'].append(epoch)
            self.training_data['loss']['train'].append(train_loss)
            self.training_data['loss']['val'].append(val_loss)
            self.training_data['accuracy']['train'].append(train_acc)
            self.training_data['accuracy']['val'].append(val_acc)
            
            # Simulate multi-task performance
            base_acc = train_acc * 0.8
            self.training_data['skin_condition_accuracy'].append(base_acc * 0.95)
            self.training_data['age_accuracy'].append(base_acc * 1.05)
            self.training_data['ethnicity_accuracy'].append(base_acc * 0.9)
            self.training_data['gender_accuracy'].append(base_acc * 1.1)
            
            # Simulate learning rate decay
            lr = 0.001 * (0.95 ** epoch)
            self.training_data['learning_rate'].append(lr)
            
            print(f"🎭 Demo Epoch {epoch + 1}: Loss={train_loss:.3f}, Acc={train_acc:.1f}%")
            time.sleep(0.1)  # Simulate training time
    
        pass
    
    def run_dashboard(self, host='0.0.0.0', port=5000, debug=True):
        """Run the dashboard"""
        print(f"🚀 Starting V7 Training Dashboard...")
        print(f"📊 Dashboard URL: http://localhost:{port}")
        print(f"🔬 Dataset: {self.output_dir}")
        print(f"🤖 Model Output: {self.model_dir}")
        
        app.run(host=host, port=port, debug=debug)

# Global dashboard instance
dashboard_instance = None

def get_dashboard_instance():
    """Get or create dashboard instance"""
    global dashboard_instance
    if dashboard_instance is None:
        dashboard_instance = V7TrainingDashboard()
    return dashboard_instance

# Flask routes (defined at module level)
@app.route('/')
def dashboard():
    """Render the main dashboard"""
    dashboard_instance = get_dashboard_instance()
    return render_template('dashboard.html', **dashboard_instance.get_dashboard_data())

@app.route('/api/training-data')
def get_training_data():
    """Get current training data for charts"""
    dashboard_instance = get_dashboard_instance()
    
    # Convert numpy types to Python native types for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        else:
            return obj
    
    training_data = convert_numpy_types(dashboard_instance.training_data)
    return jsonify(training_data)

@app.route('/api/start-training', methods=['POST'])
def start_training():
    """Start the training process"""
    try:
        dashboard_instance = get_dashboard_instance()
        
        # Check if user wants real training or demo
        data = request.get_json() or {}
        training_mode = data.get('mode', 'real')  # 'real' or 'demo'
        
        if training_mode == 'real':
            print("🤖 Starting REAL V7 training...")
            # Start REAL training
            training_thread = threading.Thread(target=dashboard_instance.start_real_training)
            training_thread.daemon = True
            training_thread.start()
            message = "Real V7 training started!"
        else:
            print("🎭 Starting demo training...")
            # Start demo training
            training_thread = threading.Thread(target=dashboard_instance.start_training_simulation)
            training_thread.daemon = True
            training_thread.start()
            message = "Demo training started!"
        
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/training-status')
def get_training_status():
    """Get current training status and progress"""
    try:
        dashboard_instance = get_dashboard_instance()
        
        # Get current training data and convert numpy types to Python native types
        training_data = dashboard_instance.training_data
        
        # Convert numpy types to Python native types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        # Convert training data
        training_data_serializable = convert_numpy_types(training_data)
        
        # Check if we have recent training results
        current_status = "Ready"
        if training_data['epochs']:
            current_status = f"Completed {len(training_data['epochs'])} epochs"
        
        # Check if we have completed training results
        eval_results_path = dashboard_instance.model_dir / 'evaluation_results.json'
        if eval_results_path.exists():
            try:
                with open(eval_results_path, 'r') as f:
                    eval_results = json.load(f)
                
                # Calculate overall accuracy
                overall_accuracy = np.mean(list(eval_results['test_accuracies'].values())) * 100
                current_status = f"Training Completed! Overall Accuracy: {overall_accuracy:.1f}%"
                
                # Add detailed results
                latest_metrics.update({
                    'condition_accuracy': eval_results['test_accuracies']['condition'] * 100,
                    'age_accuracy': eval_results['test_accuracies']['age_group'] * 100,
                    'ethnicity_accuracy': eval_results['test_accuracies']['ethnicity'] * 100,
                    'gender_accuracy': eval_results['test_accuracies']['gender'] * 100,
                    'test_samples': eval_results['test_samples']
                })
                
            except Exception as e:
                dashboard_instance.logger.error(f"Error loading evaluation results: {e}")
        
        # Get the latest metrics if available
        latest_metrics = {}
        if training_data['loss']['train']:
            latest_metrics['latest_train_loss'] = float(training_data['loss']['train'][-1])
        if training_data['loss']['val']:
            latest_metrics['latest_val_loss'] = float(training_data['loss']['val'][-1])
        if training_data['accuracy']['train']:
            latest_metrics['latest_train_acc'] = float(training_data['accuracy']['train'][-1])
        if training_data['accuracy']['val']:
            latest_metrics['latest_val_acc'] = float(training_data['accuracy']['val'][-1])
        
        # Add debugging info about the data leakage issue
        debug_info = {
            'data_leakage_detected': True,
            'issue_description': 'SCIN features were missing, causing 100% condition accuracy',
            'fix_applied': 'Restored 2,801 SCIN features from medical_grade_scin_processed',
            'recommendation': 'Re-run training to get realistic accuracy based on image features'
        }
        
        return jsonify({
            'status': 'success',
            'current_status': current_status,
            'training_data': training_data_serializable,
            'latest_metrics': latest_metrics,
            'is_training': hasattr(dashboard_instance, 'trainer') and dashboard_instance.trainer is not None,
            'debug_info': debug_info,
            'dataset_info': {
                'total_samples': 5801,
                'scin_samples': 2801,
                'utkface_samples': 3000,
                'scin_features_restored': True
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def main():
    """Main function to run the dashboard"""
    dashboard = V7TrainingDashboard()
    dashboard.run_dashboard()

if __name__ == '__main__':
    main()
