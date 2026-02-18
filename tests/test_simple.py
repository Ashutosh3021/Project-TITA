"""Simple voice test without unicode characters."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("JARVIS Voice Pipeline - Simple Test")
print("="*60)

# Test 1: Import
print("\n1. Testing imports...")
try:
    from JARVIS.voice import VoicePipeline, SpeechToText, TextToSpeech, WakeWordDetector
    print("   [OK] All imports successful")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: TTS
print("\n2. Testing TTS (you should hear audio)...")
try:
    tts = TextToSpeech()
    tts.speak("Voice test successful. TTS is working.")
    print("   [OK] TTS working")
except Exception as e:
    print(f"   [FAIL] TTS failed: {e}")

# Test 3: Audio Devices
print("\n3. Checking audio devices...")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    print(f"   Found {len(devices)} audio devices")
    print(f"   Default input: {sd.default.device[0]}")
    print(f"   Default output: {sd.default.device[1]}")
    print("   [OK] Audio devices available")
except Exception as e:
    print(f"   [FAIL] Audio check failed: {e}")

print("\n" + "="*60)
print("Test complete!")
print("="*60)
print("\nTo test STT, run: python tests/test_voice_components.py --test stt")
print("To test wake word, run: python tests/test_voice_components.py --test wake")
