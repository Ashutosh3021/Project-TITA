"""Quick STT test with fixed time_info access."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("STT Quick Test - Fixed time_info access")
print("="*60)

from JARVIS.voice import SpeechToText

stt = SpeechToText()
print(f"Initialized: {stt.model_size} model on {stt.device}")
print("\nSpeak for 3 seconds...")

text = stt.record_and_transcribe(duration=3.0)

if text:
    print(f"\nOK  Transcribed: '{text}'")
else:
    print("\nWARN  No speech detected")
