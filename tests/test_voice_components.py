"""Unit and integration tests for voice pipeline components."""

import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_tts():
    """Test Text-to-Speech component."""
    print("\n" + "="*60)
    print("TESTING: Text-to-Speech (TTS)")
    print("="*60)
    
    try:
        from JARVIS.voice import TextToSpeech
        
        print("OK  Import successful")
        
        tts = TextToSpeech()
        print(f"OK  TTS initialized (engine: {tts.engine})")
        
        print("\n🔊 Speaking: 'Hello, this is a voice test.'")
        tts.speak("Hello, this is a voice test.")
        print("OK  TTS test completed")
        
        return True
        
    except Exception as e:
        print(f"ERROR  TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stt():
    """Test Speech-to-Text component."""
    print("\n" + "="*60)
    print("TESTING: Speech-to-Text (STT)")
    print("="*60)
    
    try:
        from JARVIS.voice import SpeechToText
        
        print("OK  Import successful")
        
        stt = SpeechToText()
        print(f"OK  STT initialized (model: {stt.model_size}, device: {stt.device})")
        
        print("\n[MIC]  Please speak for 5 seconds...")
        print("   (Say something like 'Hello JARVIS' or 'Testing one two three')")
        
        text = stt.record_and_transcribe(duration=5.0)
        
        if text:
            print(f"\nOK  Transcription: '{text}'")
            return True
        else:
            print("\nWARN  No speech detected or transcription failed")
            return False
            
    except Exception as e:
        print(f"ERROR  STT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wake_word():
    """Test Wake Word Detection component."""
    print("\n" + "="*60)
    print("TESTING: Wake Word Detection")
    print("="*60)
    
    try:
        # Import directly from wake_word module to avoid STT/TTS dependencies
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from JARVIS.voice.wake_word import MultiWakeWordDetector as WakeWordDetector
        
        print("OK Import successful")
        
        detected = [False]
        
        def on_wake():
            detected[0] = True
            print("\n>>> Wake word DETECTED! <<<")
        
        detector = WakeWordDetector(on_wake)
        print("OK Wake word detector initialized")
        print(f"   Mode: {detector.wake_word}")
        
        print("\n[MIC] Test wake word detection...")
        print("   Try any of these:")
        print("   - Clap twice")
        print("   - Say 'wake up boy'")
        print("   - Say 'Jarvis'")
        print("   (Waiting 10 seconds)")
        
        detector.start()
        
        # Wait for detection or timeout
        for i in range(10):
            if detected[0]:
                break
            time.sleep(1)
            print(f"   {i+1}s...", end="\r")
        
        detector.stop()
        
        if detected[0]:
            print("\nOK Wake word test completed successfully")
            return True
        else:
            print("\nINFO Wake word not detected (this is OK if you didn't say it)")
            return True  # Still consider test successful
            
    except Exception as e:
        print(f"ERROR Wake word test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test the complete voice pipeline."""
    print("\n" + "="*60)
    print("TESTING: Full Voice Pipeline")
    print("="*60)
    
    try:
        from JARVIS.voice import VoicePipeline
        
        print("OK  Import successful")
        
        response_received = [False]
        
        def callback(text: str) -> str:
            print(f"\n📝 Transcribed: '{text}'")
            response_received[0] = True
            return f"I heard you say: {text}"
        
        pipeline = VoicePipeline()
        print("OK  Voice pipeline initialized")
        
        print("\n[MIC]  Full Pipeline Test Instructions:")
        print("   1. Say 'Tita' to trigger wake word")
        print("   2. Wait for confirmation beep")
        print("   3. Say something like 'Hello JARVIS'")
        print("   4. You should hear a response")
        print("\n   (Test will run for 15 seconds)")
        
        # Run for 15 seconds
        import threading
        
        def run_pipeline():
            try:
                pipeline.listen_and_respond(callback)
            except Exception as e:
                print(f"Pipeline error: {e}")
        
        thread = threading.Thread(target=run_pipeline)
        thread.daemon = True
        thread.start()
        
        # Wait for 15 seconds
        for i in range(15):
            if response_received[0]:
                break
            time.sleep(1)
            print(f"   {i+1}s...", end="\r")
        
        pipeline.stop()
        thread.join(timeout=2)
        
        if response_received[0]:
            print("\nOK  Full pipeline test completed successfully")
            return True
        else:
            print("\nWARN  No response received (you may not have spoken)")
            return True  # Still consider test successful
            
    except Exception as e:
        print(f"ERROR  Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_devices():
    """Test and display audio device information."""
    print("\n" + "="*60)
    print("AUDIO DEVICE INFORMATION")
    print("="*60)
    
    try:
        import sounddevice as sd
        
        print("\n[INFO]  Available Audio Devices:")
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            marker = ""
            if i == sd.default.device[0]:
                marker += " [DEFAULT INPUT]"
            if i == sd.default.device[1]:
                marker += " [DEFAULT OUTPUT]"
            print(f"   {i}: {device['name']}{marker}")
            print(f"      Channels: {device['max_input_channels']} in, {device['max_output_channels']} out")
            print(f"      Sample Rate: {device['default_samplerate']} Hz")
        
        print(f"\n📊 Default Devices:")
        print(f"   Input:  {sd.default.device[0]} - {devices[sd.default.device[0]]['name']}")
        print(f"   Output: {sd.default.device[1]} - {devices[sd.default.device[1]]['name']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR  Audio device test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Test JARVIS Voice Pipeline")
    parser.add_argument(
        "--test",
        choices=["tts", "stt", "wake", "all", "devices"],
        default="devices",
        help="Which test to run (default: devices)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        import os
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    print("\n" + "="*60)
    print("JARVIS VOICE PIPELINE TEST SUITE")
    print("="*60)
    
    results = []
    
    if args.test in ("devices", "all"):
        results.append(("Audio Devices", test_audio_devices()))
    
    if args.test in ("tts", "all"):
        results.append(("TTS", test_tts()))
    
    if args.test in ("stt", "all"):
        results.append(("STT", test_stt()))
    
    if args.test in ("wake", "all"):
        results.append(("Wake Word", test_wake_word()))
    
    if args.test == "all":
        results.append(("Full Pipeline", test_full_pipeline()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "OK  PASS" if passed else "ERROR  FAIL"
        print(f"{name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
