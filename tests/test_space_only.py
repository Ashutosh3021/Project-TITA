"""Quick test of keyboard trigger without voice dependencies."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("KEYBOARD TRIGGER TEST")
print("="*60)
print()
print("Testing SPACE bar activation...")
print("Press SPACE 3 times to test (Ctrl+C to stop)")
print()

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from JARVIS.voice.keyboard_trigger import KeyboardTrigger
    
    trigger_count = [0]
    
    def on_space():
        trigger_count[0] += 1
        print(f">>> SPACE pressed! (count: {trigger_count[0]})")
        if trigger_count[0] >= 3:
            print("\nTest complete! Keyboard trigger works!")
            # Stop after 3 presses
            import os
            os._exit(0)
    
    trigger = KeyboardTrigger(on_space)
    trigger.start()
    
    print("Listening for SPACE bar...")
    print("(Press SPACE 3 times)")
    
    # Run for 30 seconds max
    for i in range(30):
        time.sleep(1)
        if not trigger.is_running():
            break
    
    if trigger_count[0] == 0:
        print("\nNo SPACE presses detected - test incomplete")
    else:
        print(f"\nDetected {trigger_count[0]} SPACE presses")
    
    trigger.stop()
    
except KeyboardInterrupt:
    print("\n\nTest stopped by user")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
