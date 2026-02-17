# JARVIS - Intelligent Voice Assistant

Wake word: **"Tita"**

A locally-running, privacy-first voice assistant with ReAct-based agent capabilities, supporting web search, browser automation, email/calendar integration, and contextual memory.

## Features

- **Voice Interface**: Wake word detection, speech-to-text (faster-whisper), text-to-speech (Piper/Higgs)
- **Local LLM**: Powered by Ollama with hardware-adaptive model selection
- **Memory System**: ChromaDB vector store + human-readable MEMORY.md
- **Web Capabilities**: DuckDuckGo search + Playwright browser automation
- **Productivity**: Gmail and Microsoft 365 calendar/email integration
- **Agent Pattern**: ReAct loop for reasoning and action

## Hardware Requirements

| Profile | CPU | RAM | GPU | Use Case |
|---------|-----|-----|-----|----------|
| **Low** | 4 cores | 8 GB | None | Basic functionality with tiny models |
| **Medium** | 6 cores | 16 GB | 4 GB VRAM | Good performance with small/medium models |
| **High** | 8+ cores | 32 GB | 8+ GB VRAM | Full features with large models |

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd jarvis
python setup.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Download Playwright browsers
- Create necessary directories
- Copy `.env.example` to `.env`

### 2. Configure Environment

Edit `.env` with your API credentials:

```bash
# Required: Google OAuth2 for Gmail
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Required: Microsoft Graph API for Outlook/Calendar
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id
```

### 3. Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com)

```bash
# Pull recommended models
ollama pull llama3.2:3b      # Low hardware
ollama pull llama3:8b        # Medium hardware
ollama pull llama3:70b       # High hardware (if VRAM permits)
```

### 4. Run the Assistant

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start the assistant
python -m JARVIS.main
```

Say **"Tita"** to wake the assistant!

## Project Structure

```
JARVIS/
├── core/          # Main orchestration and ReAct loop
├── voice/         # STT, TTS, and wake word detection
├── brain/         # LLM integration with Ollama
├── memory/        # ChromaDB and MEMORY.md management
├── tools/         # Web search, browser, email, calendar
├── ui/            # FastAPI backend + React frontend
└── main.py        # Entry point

data/
├── chroma_db/     # Vector database files
├── models/        # Downloaded models (whisper, piper, openwakeword)
└── logs/          # Application logs

tests/             # Unit and integration tests
```

## Development

```bash
# Run tests
pytest

# Run linting
ruff check .

# Type checking
mypy JARVIS/
```

## License

MIT License - See LICENSE file for details
