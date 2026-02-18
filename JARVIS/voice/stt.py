"""Speech-to-Text using faster-whisper."""

import io
import time as time_module
from pathlib import Path
from typing import Any, BinaryIO

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    webrtcvad = None  # type: ignore

from ..core.config import MODEL_CONFIG
from ..core.logger import get_logger

logger = get_logger(__name__)

# Type alias for VAD
try:
    if WEBRTCVAD_AVAILABLE and webrtcvad is not None:
        VadType = webrtcvad.Vad
    else:
        VadType = Any
except NameError:
    VadType = Any


class SpeechToText:
    """Speech-to-Text using faster-whisper with VAD-based recording."""
    
    def __init__(self) -> None:
        """Initialize the STT engine with faster-whisper."""
        self.model_size = MODEL_CONFIG.whisper_model
        self.device = MODEL_CONFIG.device
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        self._model = None
        self._vad = None
        
        # Audio parameters
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # VAD parameters
        self.vad_aggressiveness = 3
        self.silence_timeout = 2.0  # Seconds of silence before stopping
        self.min_speech_duration = 0.5  # Minimum seconds of speech required
        self.max_duration = 30.0  # Maximum recording duration
        
        logger.info(f"SpeechToText initialized (model: {self.model_size}, device: {self.device})")
    
    def _load_model(self) -> None:
        """Load the Whisper model if not already loaded."""
        if self._model is not None:
            return
        
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}") from e
    
    def _init_vad(self) -> None:
        """Initialize the Voice Activity Detector."""
        if self._vad is not None:
            return
        
        if not WEBRTCVAD_AVAILABLE or webrtcvad is None:
            raise RuntimeError("webrtcvad not installed. Run: pip install webrtcvad-wheels")
        
        try:
            self._vad = webrtcvad.Vad(self.vad_aggressiveness)
            logger.debug("VAD initialized")
        except Exception as e:
            logger.error(f"Failed to initialize VAD: {e}")
            raise RuntimeError(f"Failed to initialize VAD: {e}") from e
    
    def _is_speech(self, audio_frame: bytes) -> bool:
        """Check if audio frame contains speech.
        
        Args:
            audio_frame: Audio frame bytes
            
        Returns:
            True if speech detected, False otherwise
        """
        if self._vad is None:
            return False
        
        try:
            return self._vad.is_speech(audio_frame, self.sample_rate)
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def record_and_transcribe(self, duration: float | None = None) -> str:
        """Record audio until silence detected, then transcribe.
        
        Args:
            duration: Maximum recording duration in seconds (None for VAD-based)
            
        Returns:
            Transcribed text
        """
        try:
            self._load_model()
            self._init_vad()
            
            max_duration = duration or self.max_duration
            
            logger.info("Recording audio...")
            audio_data = self._record_with_vad(max_duration)
            
            if len(audio_data) == 0:
                logger.warning("No audio recorded")
                return ""
            
            logger.info(f"Recorded {len(audio_data) / self.sample_rate:.2f} seconds of audio")
            
            # Transcribe the recorded audio
            return self._transcribe_audio(audio_data)
            
        except Exception as e:
            logger.error(f"Error in record_and_transcribe: {e}")
            return ""
    
    def _record_with_vad(self, max_duration: float) -> np.ndarray:
        """Record audio using Voice Activity Detection.
        
        Args:
            max_duration: Maximum recording duration in seconds
            
        Returns:
            Recorded audio as numpy array
        """
        frames: list[bytes] = []
        recording = False
        silence_start = 0.0
        speech_start = 0.0
        start_time = 0.0
        
        def callback(indata: np.ndarray, frame_count: int, 
                    time_info: Any, status: sd.CallbackFlags) -> None:
            nonlocal recording, silence_start, speech_start, start_time
            
            if status:
                logger.warning(f"Audio stream status: {status}")
            
            # Convert to int16 for VAD
            audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
            frame_bytes = audio_int16.tobytes()
            
            is_speech = self._is_speech(frame_bytes)
            # time_info is a CFFI struct, access attributes directly
            try:
                current_time = float(time_info.input_buffer_adc_time)
            except (AttributeError, TypeError):
                # Fallback if time_info doesn't have expected field
                current_time = time_module.time()
            
            if start_time == 0.0:
                start_time = current_time
            
            elapsed = current_time - start_time
            
            if elapsed > max_duration:
                raise sd.CallbackStop()
            
            if is_speech:
                if not recording:
                    recording = True
                    speech_start = current_time
                    logger.debug("Speech detected, starting recording")
                silence_start = current_time
                frames.append(frame_bytes)
            elif recording:
                # Continue recording during short pauses
                frames.append(frame_bytes)
                
                # Check silence timeout
                if current_time - silence_start > self.silence_timeout:
                    speech_duration = current_time - speech_start
                    if speech_duration >= self.min_speech_duration:
                        logger.debug(f"Silence detected after {speech_duration:.2f}s of speech")
                        raise sd.CallbackStop()
                    else:
                        # Not enough speech, reset
                        logger.debug("Not enough speech, resetting")
                        recording = False
                        frames.clear()
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.frame_size,
                channels=1,
                dtype=np.float32,
                callback=callback
            ):
                # Wait for recording to complete
                import time
                time.sleep(max_duration + 1.0)
        except sd.CallbackStop:
            pass
        except Exception as e:
            logger.error(f"Recording error: {e}")
        
        # Convert frames back to float32 array
        if not frames:
            return np.array([], dtype=np.float32)
        
        audio_int16 = np.frombuffer(b"".join(frames), dtype=np.int16)
        return audio_int16.astype(np.float32) / 32767.0
    
    def _transcribe_audio(self, audio_data: np.ndarray) -> str:
        """Transcribe audio data using Whisper.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Transcribed text
        """
        if self._model is None:
            logger.error("Whisper model not loaded")
            return ""
        
        if len(audio_data) == 0:
            logger.warning("Empty audio data provided for transcription")
            return ""
        
        try:
            logger.info("Transcribing audio...")
            
            # Transcribe
            segments, info = self._model.transcribe(
                audio_data,
                language="en",
                task="transcribe",
                vad_filter=True
            )
            
            # Collect all segments
            text_parts: list[str] = []
            for segment in segments:
                text_parts.append(segment.text.strip())
            
            text = " ".join(text_parts).strip()
            
            logger.info(f"Transcription complete: '{text}'")
            logger.debug(f"Detected language: {info.language}, Probability: {info.language_probability:.2f}")
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def transcribe_file(self, path: str | Path) -> str:
        """Transcribe an audio file.
        
        Args:
            path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            self._load_model()
            
            if self._model is None:
                logger.error("Whisper model failed to load")
                return ""
            
            file_path = Path(path)
            if not file_path.exists():
                logger.error(f"Audio file not found: {file_path}")
                return ""
            
            logger.info(f"Transcribing file: {file_path}")
            
            # Transcribe file directly
            segments, info = self._model.transcribe(
                str(file_path),
                language="en",
                task="transcribe",
                vad_filter=True
            )
            
            # Collect all segments
            text_parts: list[str] = []
            for segment in segments:
                text_parts.append(segment.text.strip())
            
            text = " ".join(text_parts).strip()
            
            logger.info(f"File transcription complete: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return ""
