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
        self.total_active_seconds = 0
        self.total_idle_seconds = 0
        self.last_activity_time = datetime.now()
        self.start_time = datetime.now()
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
        self._last_tick_time = time.time()
        
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
                now_ts = time.time()
                elapsed = now_ts - self._last_tick_time
                self._last_tick_time = now_ts
                
                with self._lock:
                    time_since_activity = (current_time - self.last_activity_time).total_seconds()
                    
                    # Accumulate time based on activity
                    if time_since_activity > self.idle_threshold:
                        self.total_idle_seconds += elapsed
                    else:
                        self.total_active_seconds += elapsed
                        
                    mouse_clicks = self.mouse_clicks
                    keyboard_presses = self.keyboard_presses
                
                activity_data = {
                    'timestamp': current_time.isoformat(),
                    'mouse_clicks': mouse_clicks,
                    'keyboard_presses': keyboard_presses,
                    'idle_time': time_since_activity,
                    'is_idle': time_since_activity > self.idle_threshold,
                    'screen_time': int(self.total_active_seconds)
                }
                
                self.activity_buffer.append(activity_data)
                logger.debug(f"Activity Tick: {mouse_clicks} clicks, {keyboard_presses} keys, Active: {int(self.total_active_seconds)}s")
                
                # Wait for the interval or stop event
                self._stop_event.wait(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def get_activity_summary(self) -> Dict:
        """Get activity summary for the current period with thread safety"""
        with self._lock:
            # Use total active seconds as a basis for screen time
            screen_time = int(self.total_active_seconds)
            total_clicks = self.mouse_clicks
            total_presses = self.keyboard_presses
            time_since_activity = (datetime.now() - self.last_activity_time).total_seconds()
            
            # Diagnostics
            mouse_status = "ok" if self._mouse_listener and self._mouse_listener.is_alive() else "stopped"
            kb_status = "ok" if self._keyboard_listener and self._keyboard_listener.is_alive() else "stopped"
            
            return {
                'mouse_clicks': total_clicks,
                'keyboard_presses': total_presses,
                'idle_time': int(time_since_activity),
                'is_idle': time_since_activity > self.idle_threshold,
                'activity_level': self._calculate_activity_level(total_clicks, total_presses),
                'last_activity': self.last_activity_time.isoformat(),
                'screen_time': screen_time,
                'buffer_size': len(self.activity_buffer),
                'diagnostics': {
                    'mouse_listener': mouse_status,
                    'keyboard_listener': kb_status
                }
            }
    
    def _calculate_activity_level(self, clicks: int, presses: int) -> float:
        """Calculate activity level (0-1) based on actions per minute"""
        total_actions = clicks + presses
        uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60.0
        
        if uptime_minutes < 0.1:  # Avoid division by zero
            return 0.0
            
        actions_per_minute = total_actions / uptime_minutes
        # Normalize: 50 actions per minute is considered 100% active
        activity_level = min(1.0, actions_per_minute / 50.0)
        return activity_level
    
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
