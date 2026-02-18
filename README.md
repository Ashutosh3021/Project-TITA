# JARVIS - Intelligent Voice Assistant

A locally-running, privacy-first voice assistant with ReAct-based agent capabilities, supporting keyboard/voice activation, web search, browser automation, email/calendar integration, and contextual memory.

## Quick Start

**Run JARVIS:**
```bash
python Jarvis.py
```

That's it! JARVIS will start and show you the system status.

## Activation

### Current Mode: SPACE Bar
Press **SPACE** to activate JARVIS, then speak/type your command.

### Available Commands
- **"Hello"** or **"Hi"** - Greeting
- **"What time is it?"** - Current time  
- **"What is today's date?"** - Current date
- **"What is your name?"** - Introduction
- **"Help"** - Show available commands
- **"Goodbye"** or **"Exit"** - Quit

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 4 cores | 6+ cores |
| **RAM** | 8 GB | 16 GB |
| **GPU** | None (CPU mode) | 4+ GB VRAM |
| **Storage** | 5 GB | 20 GB |

## Installation

### 1. Basic Setup
```bash
# Clone repository
git clone <repository-url>
cd jarvis

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install core dependencies
pip install -r requirements.txt
```

### 2. Optional Features

**For Voice Features:**
```bash
pip install faster-whisper webrtcvad-wheels piper-tts
```

**For Full Memory:**
```bash
pip install chromadb langchain-community sentence-transformers
```

**For AI Brain (Ollama):**
```bash
# Install from https://ollama.ai
ollama serve
ollama pull phi3:mini
```

### 3. Configuration

Copy `.env.example` to `.env` and configure:
```bash
# Optional: Google OAuth for Gmail
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Optional: Microsoft for Outlook/Calendar
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id
```

## Project Structure

```
jarvis/
├── Jarvis.py              # ⭐ MAIN ENTRY POINT - Run this!
├── JARVIS/                # Source code
│   ├── main.py           # Application logic
│   ├── core/             # Config, hardware, logger
│   ├── voice/            # STT, TTS, keyboard trigger
│   ├── brain/            # LLM, agent, prompts
│   ├── memory/           # ChromaDB + MEMORY.md
│   └── tools/            # Web, email, calendar
├── memory/               # Memory storage
│   └── MEMORY.md         # Human-readable facts
├── data/                 # Data storage
│   ├── chroma_db/        # Vector database
│   └── logs/             # Application logs
└── tests/                # Test suite
```

## Usage Examples

### Basic Usage
```bash
python Jarvis.py

# Then press SPACE and speak!
```

### With Voice (Optional)
```bash
pip install faster-whisper piper-tts
python Jarvis.py

# Press SPACE, speak clearly
```

### With AI Brain (Optional)
```bash
ollama serve
python Jarvis.py

# Press SPACE, ask questions
```

## Troubleshooting

### "No input method available"
```bash
pip install pynput
```

### "STT not available"
```bash
pip install faster-whisper webrtcvad-wheels
```

### "Ollama not connected"
```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull phi3:mini
```

### Check System Status
```bash
python tests/test_full_diagnostic.py
```

### View Logs
```bash
type data\logs\jarvis.log  # Windows
cat data/logs/jarvis.log   # Linux/Mac
```

## Development

```bash
# Run tests
python tests/test_full_diagnostic.py

# Run specific test
python tests/test_memory.py

# Check syntax
python -m py_compile JARVIS/main.py
```

## Features

- ✅ **Keyboard Activation** - Press SPACE to activate
- ✅ **Voice Interface** - Optional STT/TTS (with dependencies)
- ✅ **Memory System** - Two-tier (file-based + ChromaDB)
- ✅ **AI Brain** - ReAct agent with Ollama integration
- ✅ **Fail-Safes** - Graceful degradation for all components
- ✅ **Local-First** - Privacy-focused, runs offline
- ⚠️ **Web Integration** - Gmail/Calendar (requires OAuth setup)

## Architecture

JARVIS uses a modular architecture with fail-safes:

```
User presses SPACE
        ↓
VoicePipeline / KeyboardTrigger
        ↓
Speech-to-Text (or typed input)
        ↓
ReactAgent (with MemoryManager)
        ↓
LLM (Ollama) or Simple Commands
        ↓
Text-to-Speech (or text output)
        ↓
User hears/sees response
```

**Fail-Safe Flow:**
- Voice missing → Falls back to keyboard
- ChromaDB missing → Uses file-based memory
- Ollama missing → Uses simple responses
- Any error → Logs and continues

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, check:
1. `DIAGNOSTIC_REPORT.md` - System diagnostics
2. `data/logs/jarvis.log` - Application logs  
3. `tests/test_full_diagnostic.py` - Run diagnostics
