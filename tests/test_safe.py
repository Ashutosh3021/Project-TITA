"""Simple safe test - no audio, just imports and initialization."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("SAFE TEST - No Audio Operations")
print("="*60)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from JARVIS.voice import VoicePipeline, SpeechToText, TextToSpeech, WakeWordDetector
    from JARVIS.core.config import MODEL_CONFIG, WAKE_WORD
    print("   [OK] All imports successful")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 2: Configuration
print("\n2. Testing configuration...")
print(f"   Wake word: {WAKE_WORD}")
print(f"   STT Model: {MODEL_CONFIG.whisper_model}")
print(f"   TTS Engine: {MODEL_CONFIG.tts_engine}")
print(f"   Device: {MODEL_CONFIG.device}")
print("   [OK] Configuration loaded")

# Test 3: Initialize components (no audio)
print("\n3. Testing component initialization...")
try:
    tts = TextToSpeech()
    print(f"   [OK] TTS initialized ({tts.engine})")
    
    stt = SpeechToText()
    print(f"   [OK] STT initialized ({stt.model_size})")
    
    def dummy():
        pass
    
    wake = WakeWordDetector(dummy)
    print(f"   [OK] Wake word detector initialized ({wake.wake_word})")
    
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Test 4: Audio devices check (safe read-only)
print("\n4. Checking audio devices (read-only)...")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    print(f"   Found {len(devices)} audio devices")
    print(f"   Default input: {sd.default.device[0]}")
    print(f"   Default output: {sd.default.device[1]}")
    print("   [OK] Audio devices found")
except Exception as e:
    print(f"   [WARN] {e}")

print("\n" + "="*60)
print("SAFE TEST COMPLETE")
print("="*60)
print("\nTo test with audio, run:")
print("  python tests/test_simple.py")
print("\nIMPORTANT SAFETY NOTES:")
print("  - Keep speaker volume low during testing")
print("  - Use headphones to prevent feedback loops")
print("  - Press Ctrl+C immediately if you hear feedback")
print("  - Test one component at a time")
