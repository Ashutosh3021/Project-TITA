"""
Voice Pipeline Testing Guide
============================

## Quick Test (After installing dependencies)

```bash
# Install all voice dependencies
pip install -r requirements.txt

# Run full integration test
python tests/test_voice_integration.py
```

## Individual Component Tests

### 1. Test Text-to-Speech (Easiest)
```bash
python tests/test_voice_components.py --test tts
```

### 2. Test Speech-to-Text
```bash
python tests/test_voice_components.py --test stt
```

### 3. Test Wake Word Detection
```bash
python tests/test_voice_components.py --test wake
```

### 4. Test Full Pipeline
```bash
python tests/test_voice_components.py --test all
```

## Manual Testing Steps

### Step 1: Check Audio Devices
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Step 2: Test TTS Only
```python
from JARVIS.voice import TextToSpeech
tts = TextToSpeech()
tts.speak("Hello, this is a test.")
```

### Step 3: Test STT Only
```python
from JARVIS.voice import SpeechToText
stt = SpeechToText()
text = stt.record_and_transcribe()
print(f"You said: {text}")
```

### Step 4: Test Full Pipeline
```python
from JARVIS.voice import VoicePipeline

def callback(text):
    print(f"Heard: {text}")
    return f"I heard you say: {text}"

pipeline = VoicePipeline()
pipeline.listen_and_respond(callback)
```

## Expected Behavior

1. **TTS Test**: You should hear "Hello, testing voice synthesis"
2. **STT Test**: Speak for 3 seconds, see transcription printed
3. **Wake Word Test**: Say "Tita", hear beep, then speak
4. **Full Pipeline**: Say "Tita", hear beep, speak, hear response

## Troubleshooting

### No Audio Output
- Check default output device: `python -c "import sounddevice as sd; print(sd.default.device[1])"`
- Test with: `python -c "import sounddevice as sd; import numpy as np; sd.play(np.sin(2*np.pi*440*np.linspace(0,1,44100)), 44100); sd.wait()"`

### No Audio Input
- Check default input device: `python -c "import sounddevice as sd; print(sd.default.device[0])"`
- Check microphone permissions (Windows: Settings > Privacy > Microphone)

### Model Loading Errors
- CPU mode should work out of the box
- GPU mode requires CUDA: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

### Import Errors
```bash
pip install faster-whisper openwakeword webrtcvad-wheels
```

### Piper Voice Not Found
If you see: `Unable to find voice: en_US-lessac-medium`

**Option 1: Download Piper voices (Recommended for better quality)**
```bash
python scripts/setup_voices.py
# Or manually:
python -m piper.download --model en_US-lessac-medium
```

**Option 2: Use Windows TTS fallback (Automatic)**
The system will automatically fall back to Windows built-in TTS if Piper voices aren't available. No additional setup needed!

## Debug Mode

Set log level to DEBUG for verbose output:
```python
import os
os.environ["LOG_LEVEL"] = "DEBUG"

from JARVIS.voice import VoicePipeline
# ... rest of code
```

## Windows TTS Fallback

On Windows, the voice pipeline now automatically falls back to Windows SAPI (built-in text-to-speech) if:
- Piper TTS is not installed
- Piper voice models are not downloaded
- Piper encounters any errors

This ensures the voice pipeline works out-of-the-box on Windows without additional voice downloads!
