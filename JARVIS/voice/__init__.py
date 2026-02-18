"""Voice pipeline for JARVIS - prototype version with keyboard trigger."""

import threading
from typing import Callable

import numpy as np
import sounddevice as sd

from ..core.logger import get_logger
from .keyboard_trigger import KeyboardTrigger

logger = get_logger(__name__)

# Try to import STT and TTS, but don't fail if dependencies are missing
try:
    from .stt import SpeechToText
    STT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"STT not available: {e}")
    STT_AVAILABLE = False
    SpeechToText = None

try:
    from .tts import TextToSpeech
    TTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"TTS not available: {e}")
    TTS_AVAILABLE = False
    TextToSpeech = None


class VoicePipeline:
    """Prototype voice pipeline using SPACE bar trigger."""
    
    def __init__(self) -> None:
        """Initialize the voice pipeline components."""
        if not STT_AVAILABLE or SpeechToText is None:
            raise RuntimeError("SpeechToText not available. Install: pip install faster-whisper webrtcvad-wheels")
        if not TTS_AVAILABLE or TextToSpeech is None:
            raise RuntimeError("TextToSpeech not available. Install: pip install piper-tts pyttsx3")
            
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.trigger: KeyboardTrigger | None = None
        
        self._is_listening = False
        self._callback: Callable[[str], str] | None = None
        self._confirmation_tone_duration = 0.1
        self._confirmation_tone_freq = 880
        
        logger.info("VoicePipeline initialized (PROTOTYPE - Press SPACE to activate)")
    
    def _play_confirmation_tone(self) -> None:
        """Play a short beep to confirm activation."""
        try:
            sample_rate = 44100
            t = np.linspace(
                0, 
                self._confirmation_tone_duration, 
                int(sample_rate * self._confirmation_tone_duration),
                False
            )
            tone = 0.1 * np.sin(2 * np.pi * self._confirmation_tone_freq * t)
            
            fade_samples = int(0.01 * sample_rate)
            tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
            tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            sd.play(tone, sample_rate)
            sd.wait()
            
            import time
            time.sleep(0.2)
            
        except Exception as e:
            logger.error(f"Failed to play confirmation tone: {e}")
    
    def _on_trigger(self) -> None:
        """Handle SPACE bar trigger."""
        try:
            logger.info("SPACE pressed - starting interaction")
            
            # Play confirmation tone
            self._play_confirmation_tone()
            
            # Record and transcribe
            transcribed_text = self.stt.record_and_transcribe()
            
            if not transcribed_text:
                logger.warning("No speech detected")
                self.tts.speak("I didn't catch that. Please try again.")
                return
            
            logger.info(f"User said: '{transcribed_text}'")
            
            # Call the user's callback
            if self._callback is not None:
                try:
                    response = self._callback(transcribed_text)
                    
                    # Speak the response
                    if response:
                        self.tts.speak(response)
                    
                except Exception as e:
                    logger.error(f"Callback error: {e}")
                    self.tts.speak("Sorry, I encountered an error processing your request.")
            else:
                logger.warning("No callback registered")
                self.tts.speak("I'm not sure how to respond to that.")
                
        except Exception as e:
            logger.error(f"Error in trigger handler: {e}")
            self.tts.speak("Sorry, something went wrong.")
    
    def listen_and_respond(self, callback: Callable[[str], str]) -> None:
        """Start listening for SPACE bar and respond to speech.
        
        Press SPACE to activate, then speak your command.
        
        Args:
            callback: Function that takes transcribed text and returns response text
        """
        if self._is_listening:
            logger.warning("Voice pipeline already listening")
            return
        
        try:
            logger.info("="*60)
            logger.info("JARVIS PROTOTYPE MODE")
            logger.info("="*60)
            logger.info("Press SPACE to activate, then speak your command")
            logger.info("Press Ctrl+C to stop")
            logger.info("="*60)
            
            self._callback = callback
            self._is_listening = True
            
            # Create and start keyboard trigger
            self.trigger = KeyboardTrigger(self._on_trigger)
            self.trigger.start()
            
            # Keep the main thread alive
            while self._is_listening and self.trigger.is_running():
                import time
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Voice pipeline interrupted by user")
        except Exception as e:
            logger.error(f"Voice pipeline error: {e}")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the voice pipeline."""
        logger.info("Stopping voice pipeline...")
        self._is_listening = False
        
        if self.trigger is not None:
            try:
                self.trigger.stop()
                self.trigger = None
            except Exception as e:
                logger.error(f"Error stopping trigger: {e}")
        
        logger.info("Voice pipeline stopped")
    
    def is_listening(self) -> bool:
        """Check if the voice pipeline is currently listening."""
        return self._is_listening
