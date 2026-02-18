"""Test script for multi-mode wake word detection."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("Multi-Mode Wake Word Test")
print("="*60)
print()
print("This detector supports 3 wake methods:")
print("  1. TWO CLAPS - Clap your hands twice")
print("  2. 'WAKE UP BOY' - Say the phrase clearly")
print("  3. 'JARVIS' - Say the name")
print()
print("Any of these will trigger the wake word!")
print("="*60)

def on_wake():
    print("\n>>> WAKE WORD DETECTED! <<<")
    print("You can now speak your command...")

try:
    # Import the detector
    from JARVIS.voice.wake_word import MultiWakeWordDetector
    
    print("\nInitializing wake word detector...")
    detector = MultiWakeWordDetector(on_wake)
    
    print("Starting detection (10 seconds)...")
    print("Try one of these methods:")
    print("  - Clap twice")
    print("  - Say 'wake up boy'")
    print("  - Say 'Jarvis'")
    print("\nPress Ctrl+C to stop early")
    
    detector.start()
    
    # Run for 10 seconds
    for i in range(10):
        time.sleep(1)
        print(f"  {i+1}s...", end="\r")
    
    detector.stop()
    print("\n\nTest complete!")
    
except KeyboardInterrupt:
    print("\n\nStopped by user")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
