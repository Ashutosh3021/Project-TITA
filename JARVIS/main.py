#!/usr/bin/env python3
"""
JARVIS - Prototype Main Entry Point

Press SPACE to activate JARVIS
Simple voice assistant with keyboard trigger
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path("data/logs/jarvis.log"), encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)


def process_command(text: str) -> str:
    """Process user command and return response."""
    text_lower = text.lower()
    
    # Simple command handling for prototype
    if "hello" in text_lower or "hi" in text_lower:
        return "Hello Boss! How can I help you today?"
    
    elif "time" in text_lower:
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%I:%M %p')}"
    
    elif "date" in text_lower:
        from datetime import datetime
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    
    elif "your name" in text_lower or "who are you" in text_lower:
        return "I am JARVIS, your personal voice assistant."
    
    elif "quit" in text_lower or "exit" in text_lower or "goodbye" in text_lower:
        return "Goodbye Boss! Have a great day!"
    
    else:
        return f"I heard you say: {text}. I'm a prototype, so my capabilities are limited."


def main() -> None:
    """Main entry point for JARVIS prototype."""
    logger.info("=" * 60)
    logger.info("JARVIS PROTOTYPE")
    logger.info("=" * 60)
    
    print("\n" + "=" * 60)
    print("JARVIS VOICE ASSISTANT - PROTOTYPE")
    print("=" * 60)
    print()
    print("Activation: Press SPACE bar")
    print()
    print("How to use:")
    print("1. Press SPACE to activate")
    print("2. Wait for beep")
    print("3. Speak your command")
    print("4. JARVIS will respond")
    print("5. Press SPACE again for next command")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    try:
        # Import and initialize voice pipeline
        from JARVIS.voice import VoicePipeline
        
        logger.info("Initializing voice pipeline...")
        pipeline = VoicePipeline()
        
        logger.info("JARVIS ready! Press SPACE to activate.")
        print("✓ JARVIS is ready!")
        print("Press SPACE to start...\n")
        
        # Start listening
        pipeline.listen_and_respond(process_command)
        
    except KeyboardInterrupt:
        print("\n\nShutting down JARVIS...")
        logger.info("Shutdown by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
