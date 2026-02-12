"""
Module 2: AI-Based Fatigue Detection (Enhanced with Groq AI)
Intelligently detects fatigue using activity data and optional webcam input
"""

import cv2
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional
from config.config import FATIGUE_CONFIG, ML_CONFIG
import threading
import time
from modules.groq_ai_integration import get_groq_ai
from modules.activity_monitor import get_activity_monitor

logger = logging.getLogger(__name__)


class FatigueDetector:
    """Detects user fatigue using AI and optional computer vision with thread safety"""
    
    def __init__(self):
        self.use_ai_analysis = ML_CONFIG.get('enable_ai_fatigue_detection', True)
        self.use_webcam = FATIGUE_CONFIG.get('use_webcam', False)
        self.webcam_index = FATIGUE_CONFIG.get('webcam_index', 0)
        self.detection_interval = FATIGUE_CONFIG.get('detection_interval', 10)
        self.ai_analysis_interval = 60  # Run AI analysis every 60 seconds instead of every 10
        self.min_fatigue_score = FATIGUE_CONFIG.get('min_fatigue_score_for_break', 0.6)
        
        self.cap = None
        self.is_running = False
        self.detection_thread = None
        
        # Thread safety
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Current metrics
        self.current_fatigue_score = 0.0
        self.eye_strain_level = 0
        self.posture_score = 1.0
        self.blink_rate = 18.0
        self.facial_expression = 'neutral'
        self.fatigue_trend = 'stable'
        
        # Historical data for trend analysis
        self.fatigue_history = []
        self.max_history = 20
        
        # AI analysis timing
        self.last_ai_analysis = 0
        
        # Load cascade classifiers if using webcam
        self.face_cascade = None
        self.eye_cascade = None
        
        if self.use_webcam:
            try:
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                self.eye_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_eye.xml'
                )
                logger.info("[OK] Cascade classifiers loaded")
            except Exception as e:
                logger.error(f"[ERROR] Error loading cascades: {e}")
                self.use_webcam = False
        
        # Get Groq AI integration
        self.groq_ai = get_groq_ai() if self.use_ai_analysis else None
    
    def initialize_webcam(self) -> bool:
        """Initialize webcam for fatigue detection"""
        if not self.use_webcam:
            logger.info("Webcam disabled - using activity-based detection")
            return True
        
        try:
            self.cap = cv2.VideoCapture(self.webcam_index)
            if not self.cap.isOpened():
                logger.warning("Could not open webcam - falling back to activity-based detection")
                self.use_webcam = False
                return True
            
            logger.info("[OK] Webcam initialized successfully")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Error initializing webcam: {e}")
            self.use_webcam = False
            return True
    
    def start_detection(self):
        """Start fatigue detection with thread safety"""
        with self._lock:
            if self.is_running:
                logger.warning("Fatigue detection already started")
                return True
        
        logger.info("Starting fatigue detection...")
        
        if not self.initialize_webcam():
            logger.error("Failed to initialize detection")
            return False
        
        try:
            # Reset stop event
            self._stop_event.clear()
            
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            
            with self._lock:
                self.is_running = True
            
            logger.info("[OK] Fatigue detection started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start fatigue detection: {e}")
            self._cleanup_resources()
            return False
    
    def stop_detection(self):
        """Stop fatigue detection with proper cleanup"""
        with self._lock:
            if not self.is_running:
                logger.warning("Fatigue detection not running")
                return
        
        logger.info("Stopping fatigue detection...")
        
        # Signal stop
        self._stop_event.set()
        
        with self._lock:
            self.is_running = False
        
        # Clean up resources
        self._cleanup_resources()
        
        logger.info("Fatigue detection stopped")
    
    def _cleanup_resources(self):
        """Clean up webcam and other resources"""
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
                self.cap = None
        except Exception as e:
            logger.warning(f"Error cleaning up webcam: {e}")
        logger.info("Stopping fatigue detection...")
        self.is_running = False
        
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        logger.info("[OK] Fatigue detection stopped")
    
    def _detection_loop(self):
        """Main detection loop with stop event"""
        while not self._stop_event.is_set():
            try:
                current_time = time.time()
                
                if self.use_webcam and self.cap and self.cap.isOpened():
                    self._detect_from_webcam()
                else:
                    # Activity-based detection
                    self._detect_from_activity()
                
                # Use AI to analyze metrics periodically (every 60 seconds instead of every 10)
                if (self.use_ai_analysis and self.groq_ai and self.groq_ai.client and 
                    current_time - self.last_ai_analysis > self.ai_analysis_interval):
                    try:
                        self._ai_analysis()
                        self.last_ai_analysis = current_time
                    except Exception as ai_error:
                        logger.warning(f"AI analysis failed: {ai_error}")
                        # Don't let AI analysis failures stop the detection loop
                
                # Wait for the interval or stop event
                self._stop_event.wait(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(1)
    
    def _detect_from_webcam(self):
        """Detect fatigue from webcam frames"""
        ret, frame = self.cap.read()
        if not ret:
            return
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            # Detect eyes for blink rate and eye strain
            x, y, w, h = faces[0]
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            # Update metrics
            if len(eyes) >= 2:
                self.eye_strain_level = min(10, max(0, self._calculate_eye_strain(eyes)))
            
            # Estimate posture from face detection
            self.posture_score = self._estimate_posture(faces[0], frame.shape)
            
            # Calculate blink rate (simulated - would need proper blink detection)
            self.blink_rate = 18.0 + np.random.normal(0, 2)
            self.blink_rate = max(5, min(30, self.blink_rate))
            
            # Estimate facial expression
            self.facial_expression = self._estimate_expression(gray[y:y+h, x:x+w])
    
    def _detect_from_activity(self):
        """Calculate fatigue detection based on activity patterns from activity monitor"""
        try:
            activity_monitor = get_activity_monitor()
            if not activity_monitor:
                return
            
            # Get current activity data
            activity_data = activity_monitor.get_activity_summary()
            
            with self._lock:
                # Extract activity metrics
                mouse_clicks = activity_data.get('mouse_clicks', 0)
                keyboard_presses = activity_data.get('keyboard_presses', 0)
                idle_time = activity_data.get('idle_time', 0)
                is_idle = activity_data.get('is_idle', False)
                
                # Calculate fatigue based on activity
                # High idle time = high fatigue
                # Low activity = high fatigue
                total_actions = mouse_clicks + keyboard_presses
                
                # Fatigue score calculation (0-1 scale)
                if idle_time > 300:  # Idle for more than 5 minutes
                    self.current_fatigue_score = 0.8
                elif idle_time > 60:  # Idle for more than 1 minute
                    self.current_fatigue_score = 0.6
                elif idle_time > 30:  # Idle for more than 30 seconds
                    self.current_fatigue_score = 0.4
                elif total_actions < 5:  # Very low activity
                    self.current_fatigue_score = 0.5
                else:
                    # Normal activity means lower fatigue
                    self.current_fatigue_score = max(0.1, min(1.0, 0.3 + idle_time / 600))
                
                # Eye strain level (0-100 scale) - based on activity intensity
                intensity = min(100, (total_actions / 10 * 10))  # Activity as percentage
                self.eye_strain_level = max(0, min(100, 50 - intensity + idle_time / 10))
                
                # Posture score (0-1 scale) - assume good posture if active
                if is_idle:
                    self.posture_score = max(0.5, 1.0 - idle_time / 600)
                else:
                    self.posture_score = min(1.0, 0.7 + total_actions / 100)
                
                # Blink rate simulation (15-30 blinks per minute) - lower when fatigued
                base_blink = 18.0
                fatigue_impact = self.current_fatigue_score * 5
                self.blink_rate = max(12, base_blink - fatigue_impact + np.random.normal(0, 1))
                
                # Facial expression based on activity
                if is_idle:
                    self.facial_expression = 'neutral'
                elif self.current_fatigue_score > 0.7:
                    self.facial_expression = 'tired'
                else:
                    self.facial_expression = 'focused'
                
                # Trend analysis
                self.fatigue_history.append(self.current_fatigue_score)
                if len(self.fatigue_history) > self.max_history:
                    self.fatigue_history.pop(0)
                
                if len(self.fatigue_history) > 1:
                    recent_trend = self.current_fatigue_score - self.fatigue_history[0]
                    if recent_trend > 0.2:
                        self.fatigue_trend = 'increasing'
                    elif recent_trend < -0.2:
                        self.fatigue_trend = 'decreasing'
                    else:
                        self.fatigue_trend = 'stable'
                        
        except Exception as e:
            logger.debug(f"Error in activity-based detection: {e}")
            # Keep the existing metrics on error
    
    def _calculate_eye_strain(self, eyes) -> float:
        """Calculate eye strain level"""
        if len(eyes) == 0:
            return 5.0
        
        # Higher strain if eyes are detected but might indicate stress
        eye_spacing = np.mean([e[2] for e in eyes])  # Average eye width
        
        # Normalize to 0-10 scale
        strain = 5.0  # Base level
        if eye_spacing < 15:
            strain += 2  # Squinting
        if eye_spacing > 40:
            strain -= 1  # Wide eyes (alertness)
        
        return max(0, min(10, strain))
    
    def _estimate_posture(self, face_rect: Tuple, frame_shape: Tuple) -> float:
        """Estimate posture quality from face position"""
        x, y, w, h = face_rect
        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        
        # Ideal face should be centered
        face_center_y = y + h / 2
        ideal_position = frame_height / 2
        
        deviation = abs(face_center_y - ideal_position) / ideal_position
        
        # Convert to 0-1 score (lower deviation = higher score)
        posture_score = 1.0 - min(deviation, 1.0)
        return max(0.0, min(1.0, posture_score))
    
    def _estimate_expression(self, face_roi) -> str:
        """Estimate facial expression"""
        # Simplified expression detection
        expressions = ['alert', 'neutral', 'tired', 'stressed']
        variation = np.std(face_roi)
        
        if variation < 20:
            return 'drowsy'
        elif variation < 30:
            return 'tired'
        elif variation < 50:
            return 'neutral'
        else:
            return 'alert'
    
    def _ai_analysis(self):
        """Use Groq AI to analyze current metrics"""
        try:
            metrics = {
                'fatigue_score': self.current_fatigue_score,
                'eye_strain': self.eye_strain_level,
                'posture_quality': self.posture_score,
                'blink_rate': self.blink_rate,
                'facial_expression': self.facial_expression,
                'trend': self.fatigue_trend
            }
            
            # Let AI enhance fatigue score
            analysis = self.groq_ai.analyze_activity_and_fatigue(
                user_id=1,  # Would come from session
                activity_data={'activity_level': 0.5, 'idle_time': 0},
                fatigue_metrics=metrics
            )
            
            if analysis.get('status') == 'success':
                # Update fatigue level based on AI analysis
                urgency = analysis.get('BREAK_URGENCY', 'Optional')
                if urgency == 'Immediate':
                    self.current_fatigue_score = 0.9
                elif urgency == 'Soon':
                    self.current_fatigue_score = max(0.75, self.current_fatigue_score)
                elif urgency == 'Optional':
                    self.current_fatigue_score = max(0.5, self.current_fatigue_score)
        except Exception as e:
            logger.debug(f"AI analysis skipped: {e}")
    
    def update_metrics_from_activity(self, activity_data: Dict):
        """Update fatigue metrics based on activity data"""
        try:
            idle_time = activity_data.get('idle_time', 0)
            activity_level = activity_data.get('activity_level', 0.5)
            session_duration = activity_data.get('session_duration', 0)
            
            # Calculate fatigue based on activity patterns
            base_fatigue = 0.2  # Base fatigue
            
            # Idle time increases fatigue
            idle_factor = min(1.0, idle_time / 3600)  # Max impact at 1 hour idle
            base_fatigue += idle_factor * 0.3
            
            # Low activity increases fatigue
            if activity_level < 0.3:
                base_fatigue += 0.2
            elif activity_level > 0.8:
                base_fatigue += 0.15  # High stress
            
            # Long sessions increase fatigue
            session_factor = min(1.0, session_duration / 7200)  # Max impact at 2 hours
            base_fatigue += session_factor * 0.3
            
            self.current_fatigue_score = min(1.0, base_fatigue)
            
            # Update trend
            self.fatigue_history.append(self.current_fatigue_score)
            if len(self.fatigue_history) > self.max_history:
                self.fatigue_history.pop(0)
            
            if len(self.fatigue_history) > 1:
                if self.current_fatigue_score > self.fatigue_history[-2]:
                    self.fatigue_trend = 'increasing'
                elif self.current_fatigue_score < self.fatigue_history[-2]:
                    self.fatigue_trend = 'decreasing'
                else:
                    self.fatigue_trend = 'stable'
        except Exception as e:
            logger.debug(f"Error updating metrics: {e}")
    
    def get_fatigue_status(self) -> Dict:
        """Get current fatigue status with thread safety"""
        with self._lock:
            return {
                'fatigue_score': self.current_fatigue_score,
                'eye_strain_level': self.eye_strain_level,
                'posture_score': self.posture_score,
                'blink_rate': self.blink_rate,
                'facial_expression': self.facial_expression,
                'fatigue_trend': self.fatigue_trend,
                'webcam_data_used': self.use_webcam and self.cap is not None,
                'alert_generated': self.current_fatigue_score > self.min_fatigue_score,
                'timestamp': datetime.now().isoformat()
            }

    def get_recommendations_for_fatigue(self) -> List[Dict]:
        """Get break recommendations based on current fatigue level"""
        status = self.get_fatigue_status()
        fatigue_score = status.get('fatigue_score', 0)
        
        recs = []
        if fatigue_score > 0.8:
            recs = [
                {'activity': 'Short Walk', 'duration': 10, 'reason': 'High fatigue detected'},
                {'activity': 'Power Nap', 'duration': 15, 'reason': 'Critical fatigue level'}
            ]
        elif fatigue_score > 0.6:
            recs = [
                {'activity': 'Stretching', 'duration': 5, 'reason': 'Moderate fatigue detected'},
                {'activity': 'Deep Breathing', 'duration': 3, 'reason': 'Refocusing needed'}
            ]
        else:
            recs = [
                {'activity': 'Eye Exercise', 'duration': 1, 'reason': 'Preventative maintenance'},
                {'activity': 'Hydration', 'duration': 2, 'reason': 'Keep energy levels up'}
            ]
        return recs

    def reset_metrics(self):
        """Reset fatigue metrics (e.g., after a break)"""
        self.current_fatigue_score = max(0.0, self.current_fatigue_score - 0.3)
        self.eye_strain_level = max(0, self.eye_strain_level - 2)
        self.fatigue_trend = 'decreasing'
        logger.info("[OK] Fatigue metrics reset after break")


# Global instance
fatigue_detector = None


def get_fatigue_detector() -> FatigueDetector:
    """Get or create fatigue detector instance"""
    global fatigue_detector
    if fatigue_detector is None:
        fatigue_detector = FatigueDetector()
    return fatigue_detector
