"""
Module 1: User Activity Monitoring
Monitors mouse, keyboard, screen interaction, and idle periods
"""

import time
import logging
from datetime import datetime
from typing import Dict, Tuple
from pynput import mouse, keyboard
import psutil
import threading
from collections import deque
from config.config import ACTIVITY_CONFIG

logger = logging.getLogger(__name__)


class ActivityMonitor:
    """Monitors user activity patterns with thread safety"""
    
    def __init__(self):
        self.mouse_clicks = 0
        self.keyboard_presses = 0
        self.screen_time = 0
        self.idle_time = 0
        self.last_activity_time = datetime.now()
        self.is_monitoring = False
        self.activity_buffer = deque(maxlen=ACTIVITY_CONFIG['activity_buffer_size'])
        self.listener_thread = None
        self.monitor_interval = ACTIVITY_CONFIG['monitor_interval']
        self.idle_threshold = ACTIVITY_CONFIG['idle_threshold']
        
        # Thread safety
        self._lock = threading.Lock()
        self._mouse_listener = None
        self._keyboard_listener = None
        self._stop_event = threading.Event()
        
    def _on_move(self, x, y):
        """Callback for mouse movement"""
        with self._lock:
            self.last_activity_time = datetime.now()
        
    def _on_click(self, x, y, button, pressed):
        """Callback for mouse click"""
        if pressed:
            with self._lock:
                self.mouse_clicks += 1
                self.last_activity_time = datetime.now()
    
    def _on_scroll(self, x, y, dx, dy):
        """Callback for mouse scroll"""
        with self._lock:
            self.last_activity_time = datetime.now()
    
    def _on_press(self, key):
        """Callback for keyboard press"""
        try:
            with self._lock:
                self.keyboard_presses += 1
                self.last_activity_time = datetime.now()
        except AttributeError:
            pass
    
    def start_monitoring(self):
        """Start monitoring user activity with thread safety"""
        with self._lock:
            if self.is_monitoring:
                logger.warning("Activity monitoring already started")
                return True
        
        logger.info("Starting activity monitoring...")
        
        try:
            # Reset stop event
            self._stop_event.clear()
            
            # Set up mouse and keyboard listeners
            self._mouse_listener = mouse.Listener(
                on_move=self._on_move,
                on_click=self._on_click,
                on_scroll=self._on_scroll
            )
            self._mouse_listener.start()
            
            self._keyboard_listener = keyboard.Listener(on_press=self._on_press)
            self._keyboard_listener.start()
            
            # Start monitoring thread
            self.listener_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.listener_thread.start()
            
            with self._lock:
                self.is_monitoring = True
            
            logger.info("Activity monitoring started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start activity monitoring: {e}")
            self._cleanup_listeners()
            return False
        
    def stop_monitoring(self):
        """Stop monitoring user activity with proper cleanup"""
        with self._lock:
            if not self.is_monitoring:
                logger.warning("Activity monitoring not running")
                return
        
        logger.info("Stopping activity monitoring...")
        
        # Signal stop
        self._stop_event.set()
        
        with self._lock:
            self.is_monitoring = False
        
        # Clean up listeners
        self._cleanup_listeners()
        
        logger.info("Activity monitoring stopped")
    
    def _cleanup_listeners(self):
        """Clean up mouse and keyboard listeners"""
        try:
            if self._mouse_listener:
                self._mouse_listener.stop()
                self._mouse_listener = None
        except Exception as e:
            logger.warning(f"Error stopping mouse listener: {e}")
        
        try:
            if self._keyboard_listener:
                self._keyboard_listener.stop()
                self._keyboard_listener = None
        except Exception as e:
            logger.warning(f"Error stopping keyboard listener: {e}")
        
    def _monitor_loop(self):
        """Main monitoring loop with stop event"""
        while not self._stop_event.is_set():
            try:
                current_time = datetime.now()
                
                with self._lock:
                    time_since_activity = (current_time - self.last_activity_time).total_seconds()
                    mouse_clicks = self.mouse_clicks
                    keyboard_presses = self.keyboard_presses
                
                activity_data = {
                    'timestamp': current_time.isoformat(),
                    'mouse_clicks': mouse_clicks,
                    'keyboard_presses': keyboard_presses,
                    'idle_time': time_since_activity,
                    'is_idle': time_since_activity > self.idle_threshold,
                    'screen_time': self._get_screen_time()
                }
                
                self.activity_buffer.append(activity_data)
                
                # Wait for the interval or stop event
                self._stop_event.wait(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)  # Brief pause before continuing
    
    def get_activity_summary(self) -> Dict:
        """Get activity summary for the current period with thread safety"""
        with self._lock:
            if not self.activity_buffer:
                return self._get_empty_summary()
            
            total_clicks = self.mouse_clicks
            total_presses = self.keyboard_presses
            time_since_activity = (datetime.now() - self.last_activity_time).total_seconds()
            
            return {
                'mouse_clicks': total_clicks,
                'keyboard_presses': total_presses,
                'idle_time': time_since_activity,
                'is_idle': time_since_activity > self.idle_threshold,
                'activity_level': self._calculate_activity_level(total_clicks, total_presses),
                'last_activity': self.last_activity_time.isoformat(),
                'buffer_size': len(self.activity_buffer)
            }
    
    def _calculate_activity_level(self, clicks: int, presses: int) -> float:
        """Calculate activity level (0-1)"""
        total_actions = clicks + presses
        # Normalize to 0-1 range (assuming max 200 actions in monitoring period)
        activity_level = min(1.0, total_actions / 200.0)
        return activity_level
    
    def _get_screen_time(self) -> int:
        """Get screen on time in seconds (Windows specific)"""
        try:
            # Get screen time from Windows Event Viewer or system metrics
            # This is a simplified version
            return 0
        except Exception as e:
            logger.warning(f"Could not get screen time: {e}")
            return 0
    
    def reset_counters(self):
        """Reset activity counters with thread safety"""
        with self._lock:
            self.mouse_clicks = 0
            self.keyboard_presses = 0
            self.last_activity_time = datetime.now()
    
    def _get_empty_summary(self) -> Dict:
        """Get empty activity summary"""
        return {
            'mouse_clicks': 0,
            'keyboard_presses': 0,
            'idle_time': 0,
            'is_idle': False,
            'activity_level': 0.0,
            'last_activity': datetime.now().isoformat(),
            'buffer_size': 0
        }
    
    def get_keystroke_dynamics(self) -> Dict:
        """Get keystroke dynamics for pattern analysis"""
        return {
            'total_keystrokes': self.keyboard_presses,
            'keystroke_pattern': 'normal' if self.keyboard_presses > ACTIVITY_CONFIG['low_activity_threshold'] else 'low',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_mouse_dynamics(self) -> Dict:
        """Get mouse dynamics for pattern analysis"""
        return {
            'total_clicks': self.mouse_clicks,
            'click_pattern': 'normal' if self.mouse_clicks > 10 else 'low',
            'timestamp': datetime.now().isoformat()
        }


# Global instance
activity_monitor = None


def get_activity_monitor() -> ActivityMonitor:
    """Get or create activity monitor instance"""
    global activity_monitor
    if activity_monitor is None:
        activity_monitor = ActivityMonitor()
    return activity_monitor
