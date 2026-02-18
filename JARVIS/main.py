#!/usr/bin/env python3
"""
JARVIS - Production-Ready Main Entry Point with Fail-Safes

This version includes comprehensive error handling and graceful degradation.
"""

import logging
import os
import sys
import traceback
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


def check_dependencies() -> dict[str, bool]:
    """Check which optional dependencies are available.
    
    Returns:
        Dictionary of dependency name -> available
    """
    deps = {
        "voice": False,
        "memory_full": False,
        "ollama": False,
        "keyboard": False
    }
    
    # Check voice dependencies
    try:
        from JARVIS.voice import VoicePipeline
        # Try to create instance to ensure STT/TTS are available
        test_pipeline = VoicePipeline()
        deps["voice"] = True
    except (ImportError, RuntimeError):
        pass
    except Exception:
        pass
    
    # Check memory dependencies
    try:
        from JARVIS.memory.chroma import ChromaMemory
        deps["memory_full"] = True
    except ImportError:
        pass
    
    # Check keyboard
    try:
        import pynput
        deps["keyboard"] = True
    except ImportError:
        pass
    
    return deps


def print_startup_banner(deps: dict[str, bool]) -> None:
    """Print startup banner with dependency status."""
    print("\n" + "="*60)
    print("JARVIS VOICE ASSISTANT")
    print("="*60)
    print()
    print("SYSTEM STATUS:")
    
    if deps["voice"]:
        print("  [OK] Voice Pipeline (STT/TTS)")
    else:
        print("  [MISSING] Voice Pipeline - Install: pip install faster-whisper piper-tts")
    
    if deps["memory_full"]:
        print("  [OK] Full Memory (ChromaDB)")
    else:
        print("  [PARTIAL] Memory - Using file mode (ChromaDB optional)")
    
    if deps["keyboard"]:
        print("  [OK] Keyboard Control")
    else:
        print("  [MISSING] Keyboard - Install: pip install pynput")
    
    print()
    print("ACTIVATION:")
    if deps["keyboard"]:
        print("  Press SPACE to activate JARVIS")
    else:
        print("  Type 'go' + ENTER to activate")
    
    print()
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")


def process_command(text: str) -> str:
    """Process user command and return response."""
    text_lower = text.lower()
    
    # Simple command handling for prototype
    if any(word in text_lower for word in ["hello", "hi", "hey"]):
        return "Hello Boss! How can I help you today?"
    
    elif "time" in text_lower:
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%I:%M %p')}"
    
    elif "date" in text_lower:
        from datetime import datetime
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    
    elif any(word in text_lower for word in ["your name", "who are you"]):
        return "I am JARVIS, your personal voice assistant."
    
    elif any(word in text_lower for word in ["quit", "exit", "goodbye", "bye"]):
        return "Goodbye Boss! Have a great day!"
    
    elif "help" in text_lower:
        return """Available commands:
- Hello / Hi
- What time is it?
- What is today's date?
- What is your name?
- Help
- Goodbye / Exit"""
    
    else:
        return f"I heard you say: {text}. Try saying 'help' for available commands."


def main() -> int:
    """Main entry point for JARVIS with comprehensive error handling.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger.info("=" * 60)
    logger.info("JARVIS Starting...")
    logger.info("=" * 60)
    
    try:
        # Check dependencies
        deps = check_dependencies()
        print_startup_banner(deps)
        
        # Validate minimum requirements
        if not deps["keyboard"] and not deps["voice"]:
            print("ERROR: No input method available!")
            print("Install at least one:")
            print("  pip install pynput          (keyboard control)")
            print("  pip install faster-whisper  (voice control)")
            return 1
        
        # Initialize components
        print("Initializing components...")
        
        # Initialize variables for fail-safe operation
        pipeline = None
        agent = None
        use_brain = False
        memory = None
        
        # Try voice pipeline if available
        if deps["voice"]:
            try:
                from JARVIS.voice import VoicePipeline
                pipeline = VoicePipeline()
                logger.info("Voice pipeline initialized")
                print("✓ Voice pipeline ready")
            except Exception as e:
                logger.error(f"Voice pipeline failed: {e}")
                print(f"⚠ Voice pipeline failed: {e}")
                print("  Falling back to keyboard input...")
                deps["voice"] = False
        
        # Use keyboard trigger if voice unavailable or as primary
        if not deps["voice"]:
            print("Using keyboard input mode...")
        
        # Initialize memory (optional)
        try:
            from JARVIS.memory import MemoryManager
            memory = MemoryManager()
            if memory.is_ready():
                logger.info("Memory system fully initialized")
                print("✓ Memory system ready")
            else:
                logger.info("Memory system partially initialized")
                print("⚠ Memory system partial (file mode)")
        except Exception as e:
            logger.warning(f"Memory system unavailable: {e}")
            print(f"⚠ Memory system unavailable: {e}")
            memory = None
        
        # Initialize brain (optional - can work without)
        try:
            from JARVIS.brain import OllamaClient, PromptBuilder, ReactAgent
            llm = OllamaClient()
            prompt_builder = PromptBuilder()
            
            if llm.is_available():
                logger.info("Ollama connected")
                print("✓ AI Brain connected")
                agent = ReactAgent(llm, {}, prompt_builder, memory)
                use_brain = True
            else:
                logger.warning("Ollama not available - using simple responses")
                print("⚠ AI Brain offline (simple mode)")
                use_brain = False
        except Exception as e:
            logger.warning(f"Brain initialization failed: {e}")
            print(f"⚠ AI features unavailable: {e}")
            use_brain = False
        
        # Define callback
        def callback(text: str) -> str:
            """Process user input with fail-safes."""
            try:
                if use_brain:
                    return agent.run(text)
                else:
                    return process_command(text)
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                return "I'm sorry, I encountered an error processing your request."
        
        print("\n✓ JARVIS is ready!")
        print()
        
        # Start listening
        if deps["voice"]:
            print("Press SPACE to speak...")
            pipeline.listen_and_respond(callback)
        else:
            # Manual mode
            print("Type your command (or 'quit' to exit):")
            while True:
                try:
                    user_input = input("> ").strip()
                    if user_input.lower() in ["quit", "exit", "bye"]:
                        print("Goodbye Boss!")
                        break
                    if user_input:
                        response = callback(user_input)
                        print(f"JARVIS: {response}")
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        
        logger.info("JARVIS shutdown complete")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user.")
        logger.info("Shutdown by user (KeyboardInterrupt)")
        return 0
        
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print("\n" + "="*60)
        print("FATAL ERROR")
        print("="*60)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check logs: data/logs/jarvis.log")
        print("2. Verify Python version: python --version (need 3.11+)")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Check configuration: .env file")
        print()
        print("Stack trace:")
        traceback.print_exc()
        print("="*60)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
