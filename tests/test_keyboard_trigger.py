"""Test script for keyboard trigger prototype."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("JARVIS PROTOTYPE - Keyboard Trigger Test")
print("="*60)
print()
print("This is a simple prototype using SPACE bar activation")
print()
print("INSTRUCTIONS:")
print("1. Press SPACE to activate JARVIS")
print("2. Wait for confirmation beep")
print("3. Speak your command")
print("4. JARVIS will respond")
print("5. Press SPACE again for next command")
print()
print("Press Ctrl+C to stop")
print("="*60)
print()

def process_command(text):
    """Simple callback - just echo for testing."""
    print(f"\n>>> You said: '{text}'")
    
    # Simple responses for testing
    text_lower = text.lower()
    if "hello" in text_lower:
        return "Hello Boss! How can I help you?"
    elif "time" in text_lower:
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%I:%M %p')}"
    elif "quit" in text_lower or "exit" in text_lower:
        return "Goodbye Boss!"
    else:
        return f"I heard you say: {text}"

try:
    from JARVIS.voice import VoicePipeline
    
    print("Initializing voice pipeline...")
    pipeline = VoicePipeline()
    
    print("\nReady! Press SPACE to start...\n")
    
    pipeline.listen_and_respond(process_command)
    
except KeyboardInterrupt:
    print("\n\nStopped by user")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
