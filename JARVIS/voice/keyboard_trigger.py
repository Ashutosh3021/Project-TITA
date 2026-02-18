"""Keyboard trigger for JARVIS prototype - press SPACE to activate."""

import threading
import time
from typing import Callable

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    keyboard = None

from ..core.logger import get_logger

logger = get_logger(__name__)


class KeyboardTrigger:
    """Simple keyboard trigger - press SPACE to activate JARVIS."""
    
    def __init__(self, callback: Callable[[], None]) -> None:
        """Initialize keyboard trigger.
        
        Args:
            callback: Function to call when SPACE is pressed
        """
        self.callback = callback
        self._running = False
        self._listener = None
        
        if not PYNPUT_AVAILABLE or keyboard is None:
            logger.warning("pynput not installed. Install with: pip install pynput")
            logger.warning("Falling back to manual input mode")
        
        logger.info("KeyboardTrigger initialized - Press SPACE to activate")
    
    def _on_press(self, key) -> bool:
        """Handle key press events.
        
        Args:
            key: The key that was pressed
            
        Returns:
            False to stop listener (if needed)
        """
        try:
            if key == keyboard.Key.space:
                logger.info("SPACE pressed - activating JARVIS")
                self.callback()
        except AttributeError:
            pass
        return True
    
    def start(self) -> None:
        """Start listening for keyboard events."""
        if self._running:
            logger.warning("Keyboard trigger already running")
            return
        
        if not PYNPUT_AVAILABLE or keyboard is None:
            logger.warning("pynput not available - starting manual input mode")
            self._start_manual_mode()
            return
        
        try:
            self._running = True
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.start()
            logger.info("Keyboard trigger started - Press SPACE to activate JARVIS")
            logger.info("Press ESC to stop")
            
        except Exception as e:
            self._running = False
            logger.error(f"Failed to start keyboard trigger: {e}")
            raise RuntimeError(f"Keyboard trigger error: {e}") from e
    
    def _start_manual_mode(self) -> None:
        """Fallback mode - use input() if pynput not available."""
        self._running = True
        logger.info("=== MANUAL MODE ===")
        logger.info("Type 'go' and press ENTER to activate JARVIS")
        logger.info("Type 'quit' to stop")
        
        def manual_loop():
            while self._running:
                try:
                    user_input = input("> ").strip().lower()
                    if user_input == 'go':
                        logger.info("Activating JARVIS...")
                        self.callback()
                    elif user_input == 'quit':
                        logger.info("Stopping...")
                        self.stop()
                        break
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        
        thread = threading.Thread(target=manual_loop, daemon=True)
        thread.start()
    
    def stop(self) -> None:
        """Stop the keyboard trigger."""
        if not self._running:
            return
        
        logger.info("Stopping keyboard trigger...")
        self._running = False
        
        if self._listener is not None:
            try:
                self._listener.stop()
                self._listener = None
            except Exception as e:
                logger.error(f"Error stopping keyboard listener: {e}")
        
        logger.info("Keyboard trigger stopped")
    
    def is_running(self) -> bool:
        """Check if trigger is running."""
        return self._running
