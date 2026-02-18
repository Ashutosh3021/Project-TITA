# Voice Pipeline Testing Guide

## Quick Start

### 1. Check if everything is installed
```bash
python tests/test_voice_integration.py
```

This will:
- ✓ Test all imports
- ✓ Verify configuration
- ✓ Initialize components
- ✓ Play a test audio (via Windows TTS fallback if Piper voice not available)

### 2. Test Individual Components

**Audio Devices:**
```bash
python tests/test_voice_components.py --test devices
```

**Text-to-Speech only:**
```bash
python tests/test_voice_components.py --test tts
```

**Speech-to-Text only:**
```bash
python tests/test_voice_components.py --test stt
```

**Wake Word:**
```bash
python tests/test_voice_components.py --test wake
```

**All tests:**
```bash
python tests/test_voice_components.py --test all
```

### 3. Manual Python Testing

```python
# Quick TTS test
from JARVIS.voice import TextToSpeech
tts = TextToSpeech()
tts.speak("Hello from JARVIS")

# Quick STT test
from JARVIS.voice import SpeechToText
stt = SpeechToText()
text = stt.record_and_transcribe(duration=5)  # Speak for 5 seconds
print(f"You said: {text}")
```

## Troubleshooting

### Piper Voice Not Found
If you see: `Unable to find voice: en_US-lessac-medium`

**Solution 1: Download Piper voices (Recommended)**
```bash
python scripts/setup_voices.py
# Or manually:
python -m piper.download --model en_US-lessac-medium
```

**Solution 2: Use Windows TTS fallback (automatic)**
The code now automatically falls back to Windows built-in TTS if Piper voices aren't available.

### No Audio Output
1. Check default playback device:
```python
import sounddevice as sd
print(sd.query_devices())
print(f"Default output: {sd.default.device[1]}")
```

2. Test audio system:
```bash
python -c "import sounddevice as sd; import numpy as np; sd.play(np.sin(2*np.pi*440*np.linspace(0,1,44100)), 44100); sd.wait()"
```

### No Audio Input
1. Check default recording device:
```python
import sounddevice as sd
print(f"Default input: {sd.default.device[0]}")
```

2. Check Windows microphone permissions:
   - Settings → Privacy → Microphone
   - Enable "Allow apps to access your microphone"

### Model Loading Errors
**CPU Mode:** Should work out of the box

**GPU Mode:** Install CUDA-enabled PyTorch:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Import Errors
```bash
pip install faster-whisper openwakeword webrtcvad-wheels pywin32
```

## Voice Models

### Piper TTS Voices
Download additional voices from: https://github.com/rhasspy/piper/releases/tag/v1.2.0

Available voices:
- `en_US-lessac-medium` (default, ~50MB)
- `en_US-lessac-high` (better quality, ~100MB)
- `en_US-amy-medium` (female voice)
- `en_US-ryan-medium` (male voice)

### Whisper Models (STT)
Auto-selected based on hardware:
- `tiny` (~39MB) - CPU
- `small` (~466MB) - Low GPU
- `medium` (~1.5GB) - Mid GPU
- `large-v3` (~2.9GB) - High GPU

## Debug Mode

Set environment variable for verbose logging:
```bash
set LOG_LEVEL=DEBUG
python tests/test_voice_integration.py
```

## Full Example

```bash
# Install dependencies
pip install -r requirements.txt

# Download Piper voices (optional - has fallback)
python scripts/setup_voices.py

# Run integration test
python tests/test_voice_integration.py

# Run full pipeline test
python tests/test_voice_components.py --test all

# Try the interactive example
python examples/voice_example.py
```

## Expected Behavior

1. **TTS Test:** You should hear "Voice test successful" (Windows TTS or Piper)
2. **STT Test:** Speak for 3 seconds, see your text printed
3. **Wake Word Test:** Say "Tita", wait for beep confirmation
4. **Full Pipeline:** Say "Tita" → hear beep → speak → hear response

## Test Files

- `tests/test_voice_integration.py` - Quick smoke test
- `tests/test_voice_components.py` - Detailed component tests
- `tests/VOICE_TESTING.md` - This guide
- `scripts/setup_voices.py` - Download Piper voices
- `examples/voice_example.py` - Full usage example

## Windows-Specific Notes

On Windows, the voice pipeline will:
1. Try Piper TTS first (if voices downloaded)
2. Fall back to Windows SAPI (built-in) if Piper not available
3. Use Windows default audio devices

No additional setup required - just run the tests!
