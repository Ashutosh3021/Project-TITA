"""Central configuration module for JARVIS."""

import os
from pathlib import Path

from dotenv import load_dotenv

from .hardware import ModelConfig, get_hardware_config

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

WAKE_WORD: str = os.getenv("WAKE_WORD", "multi-mode")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")

MICROSOFT_CLIENT_ID: str | None = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET: str | None = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_TENANT_ID: str | None = os.getenv("MICROSOFT_TENANT_ID")

_hardware_profile, MODEL_CONFIG = get_hardware_config()

MEMORY_FILE_PATH: Path = Path("memory/MEMORY.md")
CHROMA_PATH: Path = Path("data/chroma_db")
LOG_PATH: Path = Path("data/logs")

for path in [MEMORY_FILE_PATH.parent, CHROMA_PATH, LOG_PATH]:
    path.mkdir(parents=True, exist_ok=True)
