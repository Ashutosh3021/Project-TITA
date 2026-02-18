"""Setup script for downloading voice models and dependencies."""

import subprocess
import sys

def download_piper_voices():
    """Download default Piper voice models."""
    print("Downloading Piper voice models...")
    
    voices = [
        "en_US-lessac-medium"
    ]
    
    for voice in voices:
        print(f"  Downloading {voice}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "piper.download", "--model", voice],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print(f"    ✓ {voice} downloaded")
            else:
                print(f"    ✗ Failed to download {voice}")
                print(f"      Error: {result.stderr}")
        except Exception as e:
            print(f"    ✗ Error downloading {voice}: {e}")
    
    print("\nVoice download complete!")
    print("\nTo use Piper TTS:")
    print("  1. Make sure voices are downloaded (run this script)")
    print("  2. Test with: python -c \"from JARVIS.voice import TextToSpeech; t=TextToSpeech(); t.speak('Hello')\"")

def check_installation():
    """Check if all dependencies are installed."""
    print("Checking installation...")
    
    deps = [
        "faster-whisper",
        "openwakeword",
        "piper-tts",
        "sounddevice",
        "soundfile",
        "numpy",
    ]
    
    all_ok = True
    for dep in deps:
        try:
            __import__(dep.replace("-", "_"))
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} - Run: pip install {dep}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    if not check_installation():
        print("\n⚠ Some dependencies are missing. Install them first:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    download_piper_voices()
