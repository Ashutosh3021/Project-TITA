"""Multi-mode wake word detection supporting claps and voice phrases."""

import threading
import time
from collections import deque
from typing import Callable

import numpy as np
import sounddevice as sd

try:
    from openwakeword.model import Model
    OPENWAKEWORD_AVAILABLE = True
except ImportError:
    OPENWAKEWORD_AVAILABLE = False
    Model = None

try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    webrtcvad = None

from ..core.config import MODEL_CONFIG
from ..core.logger import get_logger

logger = get_logger(__name__)


class MultiWakeWordDetector:
    """Detects multiple wake words: 2 claps, 'wake up boy', or 'Jarvis'.
    
    Detection priority:
    1. 2 Claps (audio pattern detection)
    2. Voice phrases (using VAD + keyword spotting)
    3. General speech (VAD fallback)
    """
    
    def __init__(self, callback: Callable[[], None]) -> None:
        """Initialize the multi-mode wake word detector.
        
        Args:
            callback: Function to call when wake word is detected
        """
        self.callback = callback
        self._running = False
        self._thread: threading.Thread | None = None
        self._stream: sd.InputStream | None = None
        
        # Audio parameters - must be valid VAD frame size (10, 20, or 30ms)
        self.sample_rate = 16000
        self.chunk_size = 480  # 30ms at 16kHz (valid for webrtcvad)
        
        # Detection state
        self._detection_buffer: deque[np.ndarray] = deque(maxlen=20)
        self._cooldown_end = 0.0
        self._cooldown_duration = 3.0  # 3 seconds between detections
        
        # Clap detection parameters - INCREASED THRESHOLDS to reduce false positives
        self._clap_threshold = 0.25  # Energy threshold for clap (increased from 0.15)
        self._clap_max_duration = 0.3  # Max duration of a clap (seconds)
        self._clap_min_duration = 0.05  # Min duration of a clap (seconds)
        self._max_clap_gap = 1.0  # Max time between two claps (seconds)
        self._clap_history: list[float] = []
        self._in_clap = False
        self._clap_start_time = 0.0
        
        # Phrase detection
        self._target_phrases = ["wake up boy", "jarvis"]
        self._phrase_buffer = ""  # Accumulated speech text (simplified)
        self._speech_frames = 0
        
        # VAD parameters - INCREASED THRESHOLDS to reduce false positives
        self._vad = None
        self._energy_threshold = 0.04  # Increased from 0.02
        self._consecutive_speech_frames = 0
        self._min_speech_frames = 10  # Increased from 5 (requires more sustained speech)
        
        # Backward compatibility property
        self.wake_word = "Multi-Mode (claps/voice)"
        
        logger.info(f"MultiWakeWordDetector initialized")
        logger.info(f"Supported wake words: 2 claps, 'wake up boy', 'Jarvis'")
    
    def _init_vad(self) -> None:
        """Initialize VAD for speech detection."""
        if WEBRTCVAD_AVAILABLE and webrtcvad is not None:
            try:
                self._vad = webrtcvad.Vad(2)
                logger.info("VAD initialized for speech detection")
            except (RuntimeError, AttributeError) as e:
                logger.warning(f"Could not initialize VAD: {e}")
                self._vad = None
        else:
            logger.info("VAD not available, using energy-based detection only")
    
    def _detect_claps(self, audio_data: np.ndarray, current_time: float) -> bool:
        """Detect 2 claps pattern.
        
        Args:
            audio_data: Audio chunk
            current_time: Current timestamp
            
        Returns:
            True if 2 claps detected
        """
        # Calculate peak energy
        peak_energy = np.max(np.abs(audio_data))
        
        # Check if we're in a clap event
        if peak_energy > self._clap_threshold:
            if not self._in_clap:
                # Start of potential clap
                self._in_clap = True
                self._clap_start_time = current_time
            # Still in clap, continue tracking
            return False
        else:
            if self._in_clap:
                # End of clap event
                clap_duration = current_time - self._clap_start_time
                self._in_clap = False
                
                # Validate clap duration
                if self._clap_min_duration <= clap_duration <= self._clap_max_duration:
                    logger.debug(f"Clap detected! Duration: {clap_duration:.3f}s")
                    self._clap_history.append(current_time)
                    
                    # Clean old claps outside time window
                    cutoff_time = current_time - self._max_clap_gap
                    self._clap_history = [t for t in self._clap_history if t > cutoff_time]
                    
                    # Check for exactly 2 claps
                    if len(self._clap_history) >= 2:
                        clap_gap = self._clap_history[1] - self._clap_history[0]
                        logger.info(f"2 CLAPS DETECTED! Gap: {clap_gap:.3f}s")
                        self._clap_history.clear()  # Reset after detection
                        return True
            
            return False
    
    def _detect_phrase(self, audio_data: np.ndarray) -> bool:
        """Simple phrase detection using energy patterns.
        
        This is a simplified version - in production, you'd use proper
        speech recognition or keyword spotting.
        
        Args:
            audio_data: Audio chunk
            
        Returns:
            True if speech pattern detected (simplified phrase detection)
        """
        # Convert to int16 for analysis
        audio_int16 = (audio_data * 32767).astype(np.int16)
        frame_bytes = audio_int16.tobytes()
        
        # Check for speech using VAD or energy
        is_speech = False
        if self._vad is not None:
            try:
                is_speech = self._vad.is_speech(frame_bytes, self.sample_rate)
            except (RuntimeError, ValueError) as e:
                logger.debug(f"VAD processing error: {e}")
                is_speech = False
            except Exception as e:
                # Catch any other VAD-related errors (including webrtcvad.Error)
                logger.debug(f"VAD error: {e}")
                is_speech = False
        
        if not is_speech:
            # Fallback to energy detection
            energy = np.sqrt(np.mean(audio_int16.astype(np.float32) ** 2))
            is_speech = energy > (self._energy_threshold * 32767)
        
        if is_speech:
            self._consecutive_speech_frames += 1
            self._speech_frames += 1
            
            # If we have sustained speech, consider it as potential phrase
            if self._consecutive_speech_frames >= self._min_speech_frames:
                # Require MORE sustained speech to reduce false positives
                if self._speech_frames >= 20:  # ~600ms of continuous speech (increased from 10)
                    logger.info("Sustained speech detected - triggering wake word")
                    return True
        else:
            self._consecutive_speech_frames = 0
            # REMOVED: Short speech burst detection - too sensitive
            # Only trigger on sustained speech now
            self._speech_frames = 0
        
        return False
    
    def _audio_callback(self, indata: np.ndarray, frames: int, 
                       time_info: any, status: sd.CallbackFlags) -> None:
        """Process audio chunks for wake word detection."""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        if not self._running:
            return
        
        try:
            # Convert to mono if stereo
            if indata.shape[1] > 1:
                audio_data = np.mean(indata, axis=1)
            else:
                audio_data = indata[:, 0]
            
            # Add to buffer
            self._detection_buffer.append(audio_data)
            
            # Check cooldown
            current_time = time.time()
            if current_time < self._cooldown_end:
                remaining = self._cooldown_end - current_time
                if int(remaining) != int(self._cooldown_end - current_time - 0.1):  # Log once per second
                    logger.debug(f"In cooldown period: {remaining:.1f}s remaining")
                return
            
            # Detection priority:
            # 1. Try clap detection first
            if self._detect_claps(audio_data, current_time):
                self._cooldown_end = current_time + self._cooldown_duration
                self._trigger_detection("2 claps")
                return
            
            # 2. Try phrase/speech detection
            if self._detect_phrase(audio_data):
                self._cooldown_end = current_time + self._cooldown_duration
                self._consecutive_speech_frames = 0
                self._speech_frames = 0
                self._trigger_detection("voice phrase")
                return
                
        except (RuntimeError, ValueError) as e:
            logger.error(f"Error in audio callback: {e}")
    
    def _trigger_detection(self, method: str) -> None:
        """Trigger the wake word callback.
        
        Args:
            method: Detection method that triggered (claps/phrase/etc)
        """
        try:
            logger.info(f"Wake word detected via {method}! Triggering callback...")
            self.callback()
        except (RuntimeError, TypeError) as e:
            logger.error(f"Error in wake word callback: {e}")
    
    def start(self) -> None:
        """Start the wake word detection in a background thread."""
        if self._running:
            logger.warning("Wake word detector already running")
            return
        
        try:
            logger.info("Starting multi-mode wake word detector...")
            self._init_vad()
            
            self._running = True
            
            # Create and start audio stream
            try:
                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    blocksize=self.chunk_size,
                    channels=1,
                    dtype=np.float32,
                    callback=self._audio_callback
                )
                self._stream.start()
            except (RuntimeError, OSError) as e:
                self._running = False
                logger.error(f"Failed to open audio input stream: {e}")
                logger.error("Please check your microphone settings and permissions")
                raise RuntimeError(f"Audio input error: {e}") from e
            
            # Start processing thread
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            
            logger.info("Wake word detector started")
            logger.info("Listening for: 2 claps, 'wake up boy', or 'Jarvis'")
            
        except RuntimeError:
            raise
        except (RuntimeError, OSError) as e:
            self._running = False
            logger.error(f"Failed to start wake word detector: {e}")
            raise RuntimeError(f"Failed to start wake word detector: {e}") from e
    
    def _run(self) -> None:
        """Main loop for the wake word detection thread."""
        logger.info("Wake word detection thread running")
        
        while self._running:
            try:
                time.sleep(0.01)
            except (RuntimeError, OSError) as e:
                logger.error(f"Error in wake word detection loop: {e}")
    
    def stop(self) -> None:
        """Stop the wake word detection."""
        if not self._running:
            logger.warning("Wake word detector not running")
            return
        
        logger.info("Stopping wake word detector...")
        self._running = False
        
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            except (RuntimeError, OSError) as e:
                logger.error(f"Error stopping audio stream: {e}")
        
        if self._thread is not None:
            try:
                self._thread.join(timeout=2.0)
                self._thread = None
            except (RuntimeError, OSError) as e:
                logger.error(f"Error joining detection thread: {e}")
        
        logger.info("Wake word detector stopped")
    
    def is_running(self) -> bool:
        """Check if the detector is currently running."""
        return self._running


# Keep old class name for backward compatibility
WakeWordDetector = MultiWakeWordDetector
