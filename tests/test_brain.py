"""Test script for JARVIS brain layer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("JARVIS Brain Layer Test")
print("="*60)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from JARVIS.brain import OllamaClient, PromptBuilder, ReactAgent
    print("   [OK] All imports successful")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 2: OllamaClient
print("\n2. Testing OllamaClient...")
try:
    client = OllamaClient()
    print(f"   Model: {client.model}")
    print(f"   URL: {client.base_url}")
    
    # Check availability (will fail if Ollama not running - that's OK)
    available = client.is_available()
    print(f"   Available: {available}")
    if not available:
        print("   [INFO] Ollama not running - this is OK for testing")
    print("   [OK] OllamaClient initialized")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 3: PromptBuilder
print("\n3. Testing PromptBuilder...")
try:
    builder = PromptBuilder()
    
    # Test system prompt building
    prompt = builder.build_system_prompt(
        memory_context="Boss name is Ashutosh",
        retrieved_memories=["Boss prefers tea over coffee"]
    )
    print(f"   Prompt length: {len(prompt)} chars")
    print("   [OK] PromptBuilder working")
    
    # Test tool formatting
    def sample_tool(query: str) -> str:
        """Search the web for information."""
        return f"Results for: {query}"
    
    tools = {"search": sample_tool}
    tool_text = builder.format_tool_list(tools)
    print(f"   Tool list formatted: {len(tool_text)} chars")
    
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Test 4: ReactAgent
print("\n4. Testing ReactAgent...")
try:
    def dummy_tool(query: str) -> str:
        """A dummy tool for testing."""
        return f"Dummy result: {query}"
    
    tools = {"dummy": dummy_tool}
    agent = ReactAgent(client, tools, builder, memory=None)
    
    print(f"   Tools: {list(agent.tools.keys())}")
    print(f"   Max iterations: {agent.max_iterations}")
    
    # Test action parsing
    test_response = """
    Thought: I need to search for this.
    Action: dummy("hello world")
    """
    action = agent.parse_action(test_response)
    if action:
        print(f"   Parsed action: {action[0]}({action[1]})")
    
    print("   [OK] ReactAgent initialized")
    
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Brain layer test complete!")
print("="*60)
print("\nTo use the brain layer:")
print("  from JARVIS.brain import OllamaClient, PromptBuilder, ReactAgent")
print("\nExample usage:")
print("  client = OllamaClient()")
print("  prompt_builder = PromptBuilder()")
print("  agent = ReactAgent(client, tools, prompt_builder, memory)")
print("  response = agent.run('What is the weather?')")
