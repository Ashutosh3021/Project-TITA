"""Text-to-Speech using Piper TTS or Higgs Audio V2."""

import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

# Optional imports with fallback
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore

try:
    from transformers import AutoModel, AutoProcessor
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoModel = None  # type: ignore
    AutoProcessor = None  # type: ignore

from ..core.config import MODEL_CONFIG
from ..core.logger import get_logger

logger = get_logger(__name__)


class TextToSpeech:
    """Text-to-Speech using Piper TTS or Higgs Audio V2."""
    
    def __init__(self) -> None:
        """Initialize the TTS engine based on MODEL_CONFIG."""
        self.engine = MODEL_CONFIG.tts_engine
        self.device = MODEL_CONFIG.device
        
        # Piper TTS settings
        self.piper_model = "en_US-lessac-medium"
        self.piper_voice_path: Path | None = None
        self._piper_voice_downloaded = False
        
        # Higgs Audio V2 settings
        self._higgs_model = None
        self._higgs_processor = None
        self.higgs_model_name = "openbmb/MiniCPM-o-2_6"  # Higgs Audio V2 base
        
        # Audio playback settings
        self.sample_rate = 24000
        
        logger.info(f"TextToSpeech initialized (engine: {self.engine}, device: {self.device})")
    
    def _load_higgs_model(self) -> None:
        """Load Higgs Audio V2 model if not already loaded."""
        if self._higgs_model is not None:
            return
        
        if not TRANSFORMERS_AVAILABLE or not TORCH_AVAILABLE:
            logger.error("transformers or torch not installed. Cannot use Higgs Audio V2.")
            self.engine = "piper"
            return
        
        try:
            logger.info("Loading Higgs Audio V2 model...")
            
            if AutoProcessor is None or AutoModel is None or torch is None:
                raise RuntimeError("Required libraries not available")
            
            self._higgs_processor = AutoProcessor.from_pretrained(
                self.higgs_model_name,
                trust_remote_code=True
            )
            self._higgs_model = AutoModel.from_pretrained(
                self.higgs_model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            if self.device == "cuda":
                self._higgs_model = self._higgs_model.to("cuda")
            
            self._higgs_model.eval()
            
            logger.info("Higgs Audio V2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Higgs Audio V2: {e}")
            # Fallback to Piper
            logger.warning("Falling back to Piper TTS")
            self.engine = "piper"
    
    def _ensure_piper_voice(self) -> bool:
        """Check if Piper voice model is available.
        
        Returns:
            True if voice is available, False otherwise
        """
        if self._piper_voice_downloaded:
            return True
        
        # For now, skip auto-download and use fallback
        # Piper voice download requires: python -m piper.download
        # which may not be available in all installations
        return False
    
    def _synthesize_windows_tts(self, text: str) -> np.ndarray:
        """Fallback Windows TTS using pyttsx3 or win32com.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as numpy array (or empty if unavailable)
        """
        try:
            # Try pyttsx3 first (more reliable)
            try:
                import pyttsx3
                logger.info("Using pyttsx3 TTS fallback - speaking now...")
                
                engine = pyttsx3.init()
                engine.setProperty('rate', 175)
                engine.setProperty('volume', 0.9)
                
                # Get available voices and set a good one
                voices = engine.getProperty('voices')
                if voices:
                    # Try to find an English voice
                    for voice in voices:
                        if 'english' in voice.name.lower() or 'en-us' in voice.id.lower():
                            engine.setProperty('voice', voice.id)
                            break
                
                # Speak immediately (blocking)
                engine.say(text)
                engine.runAndWait()
                
                logger.info("Windows TTS playback completed")
                # Return small silence to indicate success
                return np.zeros(int(self.sample_rate * 0.1), dtype=np.float32)
                
            except ImportError:
                pass  # Try win32com next
            
            # Try win32com as second option
            try:
                import win32com.client
                logger.info("Using Windows SAPI TTS fallback - speaking now...")
                
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Volume = 90
                speaker.Rate = 0
                speaker.Speak(text)
                
                logger.info("Windows SAPI TTS playback completed")
                # Return small silence to indicate success
                return np.zeros(int(self.sample_rate * 0.1), dtype=np.float32)
                
            except ImportError:
                logger.debug("Windows TTS not available (pywin32/pyttsx3 not installed)")
                return np.array([], dtype=np.float32)
                
        except Exception as e:
            logger.error(f"Windows TTS error: {e}")
            import traceback
            traceback.print_exc()
            return np.array([], dtype=np.float32)
    
    def _generate_beep(self, duration: float = 0.1, frequency: float = 880) -> np.ndarray:
        """Generate a simple beep tone.
        
        Args:
            duration: Duration in seconds
            frequency: Frequency in Hz
            
        Returns:
            Audio data as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Fade in/out
        fade_samples = int(0.01 * self.sample_rate)
        tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
        tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return tone.astype(np.float32)
    
    def _synthesize_piper(self, text: str) -> tuple[np.ndarray, bool]:
        """Synthesize speech using Piper TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Tuple of (audio_data, played_externally). 
            If played_externally is True, audio was played via Windows TTS and audio_data will be empty.
        """
        # Try to download voice if needed
        if not self._ensure_piper_voice():
            logger.warning("Piper voice not available, trying Windows TTS fallback")
            result = self._synthesize_windows_tts(text)
            # Windows TTS plays directly, so return empty with flag
            return result, len(result) == 0
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            try:
                # Run Piper TTS
                cmd = [
                    "piper",
                    "--model", self.piper_model,
                    "--output_file", temp_wav_path
                ]
                
                # Pass text via stdin
                process = subprocess.run(
                    cmd,
                    input=text.encode("utf-8"),
                    capture_output=True,
                    timeout=30
                )
                
                if process.returncode != 0:
                    error_msg = process.stderr.decode()
                    if "Unable to find voice" in error_msg or "not found" in error_msg.lower():
                        logger.warning("Piper voice not found, trying Windows TTS fallback")
                        result = self._synthesize_windows_tts(text)
                        return result, len(result) == 0
                    raise RuntimeError(f"Piper TTS failed: {error_msg}")
                
                # Load generated audio
                audio_data, sample_rate = sf.read(temp_wav_path, dtype="float32")
                
                # Resample if needed
                if sample_rate != self.sample_rate:
                    try:
                        import librosa
                        audio_data = librosa.resample(
                            y=audio_data,
                            orig_sr=sample_rate,
                            target_sr=self.sample_rate
                        )
                    except ImportError:
                        logger.warning("librosa not available, using original sample rate")
                        self.sample_rate = sample_rate
                
                return audio_data, False
                
            finally:
                # Cleanup temp file
                Path(temp_wav_path).unlink(missing_ok=True)
                
        except FileNotFoundError:
            logger.error("Piper TTS not found. Please install: pip install piper-tts")
            logger.warning("Trying Windows TTS fallback")
            result = self._synthesize_windows_tts(text)
            return result, len(result) == 0
        except Exception as e:
            logger.error(f"Piper TTS synthesis error: {e}")
            logger.warning("Trying Windows TTS fallback")
            result = self._synthesize_windows_tts(text)
            return result, len(result) == 0
    
    def _synthesize_higgs(self, text: str) -> np.ndarray:
        """Synthesize speech using Higgs Audio V2.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as numpy array
        """
        try:
            if self._higgs_model is None:
                self._load_higgs_model()
            
            logger.info("Synthesizing with Higgs Audio V2...")
            
            if self._higgs_processor is None or self._higgs_model is None or not TORCH_AVAILABLE or torch is None:
                raise RuntimeError("Higgs model not properly loaded")
            
            # Prepare inputs
            processor = self._higgs_processor
            model = self._higgs_model
            
            inputs = processor(
                text=text,
                return_tensors="pt"
            )
            
            if self.device == "cuda":
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate speech
            with torch.no_grad():
                outputs = model.generate(**inputs)
            
            # Convert to numpy
            audio_data = outputs.cpu().numpy().squeeze()
            
            # Ensure float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Higgs Audio V2 synthesis error: {e}")
            # Fallback to Piper
            logger.warning("Falling back to Piper TTS")
            return self._synthesize_piper(text)
    
    def _play_audio(self, audio_data: np.ndarray) -> None:
        """Play audio through speakers.
        
        Args:
            audio_data: Audio data as numpy array
        """
        try:
            if len(audio_data) == 0:
                logger.warning("Empty audio data, nothing to play")
                return
            
            # Ensure correct shape
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(-1, 1)
            
            logger.debug(f"Playing audio: {len(audio_data)} samples at {self.sample_rate}Hz")
            
            sd.play(audio_data, self.sample_rate)
            sd.wait()
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
    
    def speak(self, text: str) -> None:
        """Synthesize and play text (blocking).
        
        Args:
            text: Text to speak
        """
        if not text.strip():
            logger.warning("Empty text provided, nothing to speak")
            return
        
        try:
            logger.info(f"Speaking: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # Synthesize based on engine
            if self.engine == "higgs":
                audio_data = self._synthesize_higgs(text)
                self._play_audio(audio_data)
            else:
                audio_data, played_externally = self._synthesize_piper(text)
                # Only play audio if it wasn't already played by Windows TTS
                if not played_externally:
                    self._play_audio(audio_data)
            
            logger.info("Speech playback complete")
            
        except Exception as e:
            logger.error(f"Speech error: {e}")
    
    def speak_async(self, text: str) -> threading.Thread:
        """Synthesize and play text (non-blocking).
        
        Args:
            text: Text to speak
            
        Returns:
            Thread object for the speaking task
        """
        if not text.strip():
            logger.warning("Empty text provided, nothing to speak")
            # Return a dummy thread
            dummy = threading.Thread(target=lambda: None)
            dummy.start()
            return dummy
        
        logger.info(f"Speaking async: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        def _speak_worker():
            try:
                self.speak(text)
            except Exception as e:
                logger.error(f"Async speech error: {e}")
        
        thread = threading.Thread(target=_speak_worker, daemon=True)
        thread.start()
        
        return thread
