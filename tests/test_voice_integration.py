"""Quick integration test for voice pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Run quick integration tests."""
    print("="*60)
    print("JARVIS Voice Pipeline - Quick Integration Test")
    print("="*60)
    
    # Test 1: Import all components
    print("\n1. Testing imports...")
    try:
        from JARVIS.voice import VoicePipeline, SpeechToText, TextToSpeech, WakeWordDetector
        from JARVIS.core.config import MODEL_CONFIG, WAKE_WORD
        print("   OK  All imports successful")
    except Exception as e:
        print(f"   ERROR  Import failed: {e}")
        return 1
    
    # Test 2: Configuration
    print("\n2. Testing configuration...")
    try:
        print(f"   Wake word: {WAKE_WORD}")
        print(f"   STT Model: {MODEL_CONFIG.whisper_model}")
        print(f"   TTS Engine: {MODEL_CONFIG.tts_engine}")
        print(f"   Device: {MODEL_CONFIG.device}")
        print("   OK  Configuration loaded")
    except Exception as e:
        print(f"   ERROR  Configuration error: {e}")
        return 1
    
    # Test 3: Initialize components
    print("\n3. Testing component initialization...")
    try:
        tts = TextToSpeech()
        print(f"   OK  TTS initialized ({tts.engine})")
        
        stt = SpeechToText()
        print(f"   OK  STT initialized ({stt.model_size})")
        
        # Wake word detector needs a callback
        def dummy_callback():
            pass
        
        wake = WakeWordDetector(dummy_callback)
        print(f"   OK  Wake word detector initialized ({wake.wake_word})")
        
        pipeline = VoicePipeline()
        print("   OK  Voice pipeline initialized")
        
    except Exception as e:
        print(f"   ERROR  Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 4: Quick TTS test
    print("\n4. Testing TTS (you should hear audio)...")
    try:
        tts.speak("Voice test successful")
        print("   OK  TTS working")
    except Exception as e:
        print(f"   ERROR  TTS failed: {e}")
        return 1
    
    print("\n" + "="*60)
    print("OK  All integration tests passed!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Run full component tests: python tests/test_voice_components.py --test all")
    print("  2. Try the example: python examples/voice_example.py")
    print("  3. Or run a quick STT test: python tests/test_voice_components.py --test stt")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
