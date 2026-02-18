"""
Voice Pipeline Example Usage
============================

This demonstrates how to use the JARVIS Voice Pipeline.
"""

from JARVIS.voice import VoicePipeline


def process_command(text: str) -> str:
    """Example callback that processes user voice commands.
    
    Args:
        text: Transcribed user speech
        
    Returns:
        Response to speak back to the user
    """
    # This is where you'd integrate with your brain/LLM logic
    print(f"User said: {text}")
    
    # Example responses
    if "hello" in text.lower():
        return "Hello! How can I help you today?"
    elif "time" in text.lower():
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%I:%M %p')}"
    elif "quit" in text.lower() or "exit" in text.lower():
        return "Goodbye!"
    else:
        return f"I heard you say: {text}"


def main():
    """Run the voice pipeline."""
    # Initialize the voice pipeline
    pipeline = VoicePipeline()
    
    try:
        # Start listening - this will:
        # 1. Wait for wake word "Tita"
        # 2. Play confirmation tone
        # 3. Record and transcribe speech
        # 4. Call our callback with the transcribed text
        # 5. Speak the response
        print("Starting JARVIS Voice Assistant...")
        print("Say 'Tita' to wake me up!")
        print("Press Ctrl+C to stop")
        
        pipeline.listen_and_respond(process_command)
        
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        pipeline.stop()


if __name__ == "__main__":
    main()
