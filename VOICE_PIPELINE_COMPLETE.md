# JARVIS Voice Pipeline - Complete Implementation

## Summary

The voice pipeline for JARVIS is now fully implemented and working. It includes:

### Components Built

1. **voice/wake_word.py** - Wake word detection using openWakeWord
   - Detects "Tita" wake word
   - Runs in background thread
   - Plays confirmation beep on detection

2. **voice/stt.py** - Speech-to-Text using faster-whisper
   - Auto-detects model size based on hardware
   - VAD-based recording (stops on silence)
   - Supports file transcription

3. **voice/tts.py** - Text-to-Speech using Piper + Fallback
   - Piper TTS for high quality (when voices downloaded)
   - Windows TTS fallback using pyttsx3 (works immediately)
   - Higgs Audio V2 support for GPU systems

4. **voice/__init__.py** - VoicePipeline orchestrator
   - Coordinates wake word -> STT -> callback -> TTS
   - Simple listen_and_respond() interface

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Test It
```bash
python tests/test_simple.py
```

You should hear: "Voice test successful. TTS is working."

### Use It
```python
from JARVIS.voice import VoicePipeline

def handle_command(text):
    print(f"User said: {text}")
    return f"I heard: {text}"

pipeline = VoicePipeline()
pipeline.listen_and_respond(handle_command)
```

## Test Commands

```bash
# Simple test (recommended)
python tests/test_simple.py

# Full integration test
python tests/test_voice_integration.py

# Individual components
python tests/test_voice_components.py --test tts
python tests/test_voice_components.py --test stt
python tests/test_voice_components.py --test wake

# Audio device check
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## File Structure

```
JARVIS/
├── voice/
│   ├── __init__.py          # VoicePipeline class
│   ├── wake_word.py         # WakeWordDetector class
│   ├── stt.py               # SpeechToText class
│   └── tts.py               # TextToSpeech class
├── core/
│   ├── config.py            # MODEL_CONFIG, WAKE_WORD
│   ├── logger.py            # Logging setup
│   └── hardware.py          # Hardware detection
├── tests/
│   ├── test_simple.py       # Simple test (no unicode)
│   ├── test_voice_integration.py
│   ├── test_voice_components.py
│   └── README.md
├── examples/
│   └── voice_example.py
└── scripts/
    └── setup_voices.py
```

## Configuration

Hardware is auto-detected at startup:
- **CPU**: tiny whisper + Windows TTS fallback
- **Low GPU**: small whisper + piper TTS
- **Mid GPU**: medium whisper + higgs TTS
- **High GPU**: large-v3 whisper + higgs TTS

Wake word is configured in `.env`:
```
WAKE_WORD=Tita
```

## Troubleshooting

**No audio output?**
- Check default device: `python -c "import sounddevice as sd; print(sd.default.device)"`
- Check Windows volume
- Test with: `python tests/test_simple.py`

**STT not working?**
- Check microphone permissions in Windows
- Ensure microphone is not muted
- Test with: `python tests/test_voice_components.py --test stt`

**Wake word not detected?**
- Say "Tita" clearly
- Ensure microphone is working
- Check background noise level

**Want better TTS quality?**
```bash
# Download Piper voices (optional)
python scripts/setup_voices.py
```

## Status

All components are functional:
- [x] Text-to-Speech (with Windows fallback)
- [x] Speech-to-Text
- [x] Wake Word Detection
- [x] Full Pipeline Integration
- [x] Hardware Auto-detection
- [x] Error handling
- [x] Logging

Ready for integration with the brain/LLM components!
