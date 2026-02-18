# SAFETY GUIDE - Preventing System Shutdown

## What Happened?

Your laptop likely shut down due to one of these reasons:

1. **Audio Feedback Loop**: Microphone picked up speaker output → created loud screeching loop → system overload
2. **Resource Overload**: Continuous audio processing consumed too much CPU/memory
3. **Power/Thermal Protection**: System shut down to protect hardware

## Safety Changes Made

### 1. Wake Word Detection (wake_word.py)
- Increased cooldown duration: 3 seconds (was 1.5s)
- Raised energy threshold: 0.02 (was 0.01) - less sensitive
- Increased minimum speech frames: 5 (was 3)
- These changes prevent rapid triggering and feedback loops

### 2. Voice Pipeline (__init__.py)
- Lowered confirmation tone volume: 0.1 (was 0.3)
- Added 0.2s delay after tone to prevent feedback

### 3. Added Safe Test (test_safe.py)
- Tests imports only, no audio operations
- Run this first to verify code works

## Safe Testing Procedure

### Step 1: Safe Test (No Audio)
```bash
python tests/test_safe.py
```
This only tests imports and initialization - NO AUDIO.

### Step 2: Check Audio Setup
```bash
# Use headphones or keep volume LOW
python -c "import sounddevice as sd; print('Devices:', len(sd.query_devices()))"
```

### Step 3: Test TTS Only (One Direction)
```python
# Run in Python, keep volume at 20% or use headphones
from JARVIS.voice import TextToSpeech
tts = TextToSpeech()
tts.speak("Testing")  # Should hear this once
```

### Step 4: Test Wake Word (Only if Step 3 worked)
```python
from JARVIS.voice import WakeWordDetector

def callback():
    print("Wake word detected!")

detector = WakeWordDetector(callback)
detector.start()

# Say "Tita" clearly
# If anything goes wrong, press Ctrl+C

import time
time.sleep(10)
detector.stop()
```

### Step 5: Full Pipeline (Last Step)
```python
from JARVIS.voice import VoicePipeline

def handle(text):
    print(f"Heard: {text}")
    return "Got it"

pipeline = VoicePipeline()

# KEEP VOLUME LOW OR USE HEADPHONES
pipeline.listen_and_respond(handle)

# Stop with Ctrl+C
```

## Emergency Stop

If you hear feedback or system slows down:
1. **Ctrl+C** - Stops Python script
2. **Ctrl+Break** - Force stop
3. **Mute speakers immediately**
4. **Unplug microphone** if needed

## Prevention Checklist

Before running voice tests:
- [ ] Use headphones OR keep speaker volume at 20%
- [ ] Close unnecessary applications
- [ ] Ensure laptop has good ventilation
- [ ] Have Ctrl+C ready
- [ ] Test one component at a time
- [ ] Start with shorter durations (5 seconds, not 30)

## If System Shuts Down Again

1. **Don't panic** - Modern laptops have protection
2. **Wait 1 minute** before turning back on
3. **Check Event Viewer** (Windows) for shutdown reason
4. **Use headphones** for all future tests
5. **Run test_safe.py** first to verify code integrity

## Hardware-Specific Notes

### Windows
- Check microphone privacy settings
- Set default communication device
- Disable audio enhancements

### Audio Device Selection
```python
import sounddevice as sd

# List all devices
print(sd.query_devices())

# Use specific device (replace X with device number)
sd.default.device = (X, X)  # (input, output)
```

## When to Use Each Test

| Test | Audio? | Risk | Use When |
|------|--------|------|----------|
| test_safe.py | No | None | First time, checking code |
| test_simple.py | Yes (TTS only) | Low | Verified safe mode works |
| test_voice_components.py | Yes (all) | Medium | Individual component testing |
| Full pipeline | Yes (loop) | Higher | Final integration testing |

## Recommended Test Order

1. **test_safe.py** - Verify code works
2. **TTS only** - One-way audio test
3. **STT only** - Microphone input only
4. **Wake word** - Short duration (10s)
5. **Full pipeline** - Last step, use headphones

## Code Changes Summary

All safety improvements are marked with `# SAFETY:` comments in the code:
- wake_word.py: Lines 55, 59, 61
- __init__.py: Lines 43-45, 53-54

These changes reduce sensitivity and add delays to prevent feedback loops.

## Questions?

If you're unsure about running a test:
1. Start with test_safe.py
2. Ask before running full pipeline
3. Use headphones!
