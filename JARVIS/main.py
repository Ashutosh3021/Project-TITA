#!/usr/bin/env python3
"""
JARVIS - Main Entry Point

Wake word: "Tita"
Intelligent voice assistant with ReAct-based agent capabilities.
"""

import asyncio
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


async def main() -> None:
    """Main entry point for JARVIS."""
    logger.info("=" * 60)
    logger.info("JARVIS Voice Assistant Starting...")
    logger.info("Wake word: 'Tita'")
    logger.info("=" * 60)
    
    # TODO: Initialize core components
    # - Hardware detection
    # - Wake word engine
    # - Voice pipeline (STT/TTS)
    # - LLM brain
    # - Memory system
    # - Tools
    
    logger.info("JARVIS ready! Say 'Tita' to activate.")
    
    # Main loop placeholder
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down JARVIS...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Fatal error in main loop")
        sys.exit(1)
