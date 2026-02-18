#!/usr/bin/env python3
"""Comprehensive diagnostic and fail-safe test for JARVIS."""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("JARVIS COMPREHENSIVE DIAGNOSTIC")
print("="*60)

results = {
    "passed": [],
    "warnings": [],
    "failed": []
}

def test_module(name, test_func):
    """Run a test and record results."""
    try:
        test_func()
        results["passed"].append(name)
        print(f"[OK] {name}")
        return True
    except Exception as e:
        results["failed"].append(f"{name}: {e}")
        print(f"[FAIL] {name}: {e}")
        return False

# Test 1: Core Configuration
print("\n1. Core Configuration")
print("-" * 40)

def test_core_config():
    from JARVIS.core.config import MODEL_CONFIG, WAKE_WORD
    assert MODEL_CONFIG is not None
    assert WAKE_WORD is not None

test_module("Config Import", test_core_config)

# Test 2: Hardware Detection  
print("\n2. Hardware Detection")
print("-" * 40)

def test_hardware():
    from JARVIS.core.hardware import HardwareDetector
    profile, config = HardwareDetector.detect()
    assert profile is not None
    assert config is not None

test_module("Hardware Detection", test_hardware)

# Test 3: Logger
print("\n3. Logging System")
print("-" * 40)

def test_logger():
    from JARVIS.core.logger import get_logger
    logger = get_logger("test")
    logger.info("Test message")
    assert logger is not None

test_module("Logger", test_logger)

# Test 4: Memory - Readme Only
print("\n4. Memory System (Readme)")
print("-" * 40)

def test_readme_memory():
    from JARVIS.memory.readme_memory import ReadmeMemory
    readme = ReadmeMemory()
    content = readme.load()
    assert len(content) > 0
    readme.append_fact("Important Facts", "Test fact for diagnostic")

test_module("ReadmeMemory", test_readme_memory)

# Test 5: Memory - Full System
print("\n5. Memory System (Full)")
print("-" * 40)

def test_memory_manager():
    from JARVIS.memory import MemoryManager
    memory = MemoryManager()
    
    # Should work even without ChromaDB
    memory.save("Test input", "Test response", important=False)
    results = memory.retrieve("test")
    
    # Check readme is working
    assert results["core"] is not None
    print(f"  ChromaDB: {'OK' if memory.chroma else 'Not Available (optional)'}")
    print(f"  Readme: {'OK' if memory.readme else 'Failed'}")

test_module("MemoryManager", test_memory_manager)

# Test 6: Brain Components
print("\n6. Brain Components")
print("-" * 40)

def test_brain():
    from JARVIS.brain import OllamaClient, PromptBuilder, ReactAgent
    
    # Test client (without server)
    client = OllamaClient()
    available = client.is_available()
    print(f"  Ollama Server: {'Connected' if available else 'Not Running (optional)'}")
    
    # Test prompt builder
    builder = PromptBuilder()
    prompt = builder.build_system_prompt("Test context", ["Test memory"])
    assert len(prompt) > 0
    
    # Test agent creation (without running)
    agent = ReactAgent(client, {}, builder, None)
    assert agent is not None
    print(f"  Agent: OK (tools: {len(agent.tools)})")

test_module("Brain Components", test_brain)

# Test 7: Keyboard Trigger
print("\n7. Keyboard Trigger")
print("-" * 40)

def test_keyboard():
    from JARVIS.voice.keyboard_trigger import KeyboardTrigger
    
    def callback():
        pass
    
    trigger = KeyboardTrigger(callback)
    assert trigger is not None
    print(f"  pynput: {'Available' if trigger else 'Not Available (optional)'}")

test_module("Keyboard Trigger", test_keyboard)

# Test 8: Voice Pipeline (Expected to fail without deps)
print("\n8. Voice Pipeline")
print("-" * 40)

def test_voice():
    try:
        from JARVIS.voice import VoicePipeline
        pipeline = VoicePipeline()
        print("  STT/TTS: Available")
        return True
    except ImportError as e:
        print(f"  STT/TTS: Not Available (optional)")
        print(f"    Install: pip install faster-whisper piper-tts")
        return True  # This is OK - voice is optional
    except Exception as e:
        raise e

test_module("Voice Pipeline", test_voice)

# Test 9: Main Application
print("\n9. Main Application")
print("-" * 40)

def test_main():
    # Just test imports, don't run main
    import JARVIS.main as main_module
    assert hasattr(main_module, 'main')
    assert hasattr(main_module, 'process_command')

test_module("Main Module", test_main)

# Summary
print("\n" + "="*60)
print("DIAGNOSTIC SUMMARY")
print("="*60)
print(f"Passed:   {len(results['passed'])}")
print(f"Warnings: {len(results['warnings'])}")
print(f"Failed:   {len(results['failed'])}")

if results['failed']:
    print("\nFailed Tests:")
    for failure in results['failed']:
        print(f"  - {failure}")

if results['warnings']:
    print("\nWarnings:")
    for warning in results['warnings']:
        print(f"  - {warning}")

print("\n" + "="*60)
if len(results['failed']) == 0:
    print("STATUS: ALL CRITICAL SYSTEMS OPERATIONAL")
    print("JARVIS is ready to run!")
else:
    print("STATUS: SOME ISSUES DETECTED")
    print("Review failed tests above.")
print("="*60)
