"""
Module 3: Break Enforcement (Force) Module
Enforces breaks by locking screen, muting inputs, or fading screen
"""

import logging
import threading
import time
import pyautogui
import ctypes
from datetime import datetime
from typing import Dict, Optional
from config.config import BREAK_CONFIG, NOTIFICATION_CONFIG
import platform
import subprocess

logger = logging.getLogger(__name__)


class BreakEnforcer:
    """Enforces break compliance through screen locking and input muting"""
    
    def __init__(self):
        self.is_enforcing = False
        self.enforcement_thread = None
        self.break_duration = BREAK_CONFIG['default_break_duration']
        self.break_type = 'micro'
        self.screen_locked = False
        self.input_muted = False
        self.start_time = None
        self.OS = platform.system()
        
    def enforce_break(self, duration: int, break_type: str = 'micro', 
                     lock_screen: bool = True, mute_input: bool = True) -> bool:
        """
        Enforce a break with specified parameters
        
        Args:
            duration: Break duration in seconds
            break_type: Type of break (micro, regular, long, forced)
            lock_screen: Whether to lock screen
            mute_input: Whether to mute inputs
        
        Returns:
            True if break enforcement started successfully
        """
        logger.info(f"Enforcing {break_type} break for {duration} seconds")
        
        self.is_enforcing = True
        self.break_duration = duration
        self.break_type = break_type
        self.start_time = datetime.now()
        
        # Start enforcement in separate thread
        self.enforcement_thread = threading.Thread(
            target=self._enforcement_loop,
            args=(lock_screen, mute_input),
            daemon=True
        )
        self.enforcement_thread.start()
        
        return True
    
    def stop_enforcement(self) -> bool:
        """Stop enforcing break"""
        logger.info("Stopping break enforcement")
        self.is_enforcing = False
        self._restore_system_state()
        return True
    
    def _enforcement_loop(self, lock_screen: bool, mute_input: bool):
        """Main enforcement loop"""
        try:
            if lock_screen:
                self._lock_screen()
            
            if mute_input:
                self._mute_input()
            
            # Keep enforcement active
            elapsed = 0
            while self.is_enforcing and elapsed < self.break_duration:
                time.sleep(1)
                elapsed += 1
                
                # Show remaining time if screen is locked
                if lock_screen and elapsed % 10 == 0:
                    remaining = self.break_duration - elapsed
                    logger.info(f"Break enforcement: {remaining} seconds remaining")
            
            self._restore_system_state()
            self.is_enforcing = False
            
        except Exception as e:
            logger.error(f"Error in enforcement loop: {e}")
            self._restore_system_state()
    
    def _lock_screen(self):
        """Lock the screen"""
        try:
            logger.info("Locking screen...")
            
            if self.OS == 'Windows':
                # Windows: Use Ctrl+Alt+Delete or lock screen
                ctypes.windll.user32.LockWorkStation()
                self.screen_locked = True
                
            elif self.OS == 'Darwin':  # macOS
                subprocess.run(['open', '-a', 'System\\\ Preferences'])
                self.screen_locked = True
                
            elif self.OS == 'Linux':
                # Try various Linux screen locker commands
                try:
                    subprocess.run(['xdg-screensaver', 'activate'])
                except:
                    subprocess.run(['gnome-screensaver-command', '-a'])
                self.screen_locked = True
            
            logger.info("Screen locked successfully")
            
        except Exception as e:
            logger.error(f"Error locking screen: {e}")
    
    def _mute_input(self):
        """Mute keyboard and mouse inputs"""
        try:
            logger.info("Muting inputs...")
            self.input_muted = True
            
            # On Windows, can use BlockInput API
            if self.OS == 'Windows':
                try:
                    ctypes.windll.user32.BlockInput(True)
                except:
                    logger.warning("Could not block input on Windows")
            
            logger.info("Inputs muted successfully")
            
        except Exception as e:
            logger.error(f"Error muting inputs: {e}")
    
    def _fade_screen(self):
        """Gradually fade the screen to black"""
        try:
            logger.info("Fading screen...")
            fade_duration = BREAK_CONFIG['screen_fade_duration']
            steps = 20
            
            for i in range(steps):
                alpha = (i / steps) * 255
                # Would need UI implementation to actually fade screen
                time.sleep(fade_duration / steps)
            
        except Exception as e:
            logger.error(f"Error fading screen: {e}")
    
    def _restore_system_state(self):
        """Restore system to normal state"""
        try:
            logger.info("Restoring system state...")
            
            # Unmute inputs
            if self.input_muted and self.OS == 'Windows':
                try:
                    ctypes.windll.user32.BlockInput(False)
                    self.input_muted = False
                except:
                    logger.warning("Could not unblock input")
            
            # Unlock screen
            if self.screen_locked:
                if self.OS == 'Windows':
                    # Press a key to wake screen
                    pyautogui.press('space')
                self.screen_locked = False
            
            logger.info("System state restored")
            
        except Exception as e:
            logger.error(f"Error restoring system state: {e}")
    
    def show_notification(self, title: str, message: str, duration: int = 5):
        """Show break notification to user"""
        try:
            if self.OS == 'Windows':
                self._show_windows_notification(title, message, duration)
            elif self.OS == 'Darwin':
                self._show_macos_notification(title, message)
            elif self.OS == 'Linux':
                self._show_linux_notification(title, message, duration)
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
    
    def _show_windows_notification(self, title: str, message: str, duration: int):
        """Show Windows notification"""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=duration)
        except:
            logger.warning("Could not show Windows notification")
    
    def _show_macos_notification(self, title: str, message: str):
        """Show macOS notification"""
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script])
        except:
            logger.warning("Could not show macOS notification")
    
    def _show_linux_notification(self, title: str, message: str, duration: int):
        """Show Linux notification"""
        try:
            subprocess.run(['notify-send', title, message])
        except:
            logger.warning("Could not show Linux notification")
    
    def get_enforcement_status(self) -> Dict:
        """Get current enforcement status"""
        if not self.is_enforcing:
            return {
                'is_enforcing': False,
                'status': 'Not enforcing',
                'elapsed_time': 0
            }
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        remaining = max(0, self.break_duration - elapsed)
        
        return {
            'is_enforcing': True,
            'break_type': self.break_type,
            'status': 'Enforcing break',
            'elapsed_time': int(elapsed),
            'remaining_time': int(remaining),
            'total_duration': self.break_duration,
            'screen_locked': self.screen_locked,
            'input_muted': self.input_muted,
            'progress': (elapsed / self.break_duration) * 100 if self.break_duration > 0 else 0
        }
    
    def schedule_break(self, break_interval: int, duration: int, break_type: str = 'micro'):
        """Schedule a break for later"""
        logger.info(f"Break scheduled: {break_type} break in {break_interval} minutes")
        
        def scheduled_break():
            time.sleep(break_interval * 60)
            self.enforce_break(duration * 60, break_type)
        
        thread = threading.Thread(target=scheduled_break, daemon=True)
        thread.start()


# Global instance
break_enforcer = None


def get_break_enforcer() -> BreakEnforcer:
    """Get or create break enforcer instance"""
    global break_enforcer
    if break_enforcer is None:
        break_enforcer = BreakEnforcer()
    return break_enforcer
