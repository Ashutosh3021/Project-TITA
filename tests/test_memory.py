"""Test script for JARVIS memory system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("JARVIS Memory System Test")
print("="*60)

# Test 1: ReadmeMemory (doesn't require heavy dependencies)
print("\n1. Testing ReadmeMemory...")
try:
    from JARVIS.memory.readme_memory import ReadmeMemory
    
    readme = ReadmeMemory()
    print("   OK  ReadmeMemory initialized")
    
    # Load content
    content = readme.load()
    print(f"   OK  Loaded {len(content)} characters")
    
    # Get section
    profile = readme.get_section("User Profile")
    print(f"   OK  User Profile section: {len(profile)} chars")
    
    # Append fact
    readme.append_fact("Important Facts", "Boss prefers morning meetings")
    print("   OK  Added fact to Important Facts")
    
    print("\n   OK  ReadmeMemory test passed!")
    
except Exception as e:
    print(f"   FAIL  ReadmeMemory test failed: {e}")

# Test 2: ChromaMemory (requires langchain and chromadb)
print("\n2. Testing ChromaMemory...")
try:
    from JARVIS.memory.chroma import ChromaMemory
    
    chroma = ChromaMemory()
    print("   OK  ChromaMemory initialized")
    
    # Add conversation
    chroma.add_conversation(
        user_input="Hello JARVIS",
        assistant_response="Hello Boss! How can I help?"
    )
    print("   OK  Added conversation")
    
    # Add fact
    chroma.add_fact("Boss prefers concise answers", category="preferences")
    print("   OK  Added fact")
    
    # Retrieve
    results = chroma.retrieve_relevant("preferences", n_results=3)
    print(f"   OK  Retrieved {len(results)} relevant items")
    
    # Stats
    stats = chroma.get_stats()
    print(f"   OK  Stats: {stats}")
    
    print("\n   OK  ChromaMemory test passed!")
    
except ImportError as e:
    print(f"   WARN  ChromaMemory requires dependencies: {e}")
    print("      Install: pip install langchain-community chromadb sentence-transformers")
except Exception as e:
    print(f"   FAIL  ChromaMemory test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: MemoryManager
print("\n3. Testing MemoryManager...")
try:
    from JARVIS.memory import MemoryManager
    
    memory = MemoryManager()
    print("   OK  MemoryManager initialized")
    
    if memory.is_ready():
        print("   OK  Both backends ready")
        
        # Save conversation
        memory.save(
            user_input="What's the time?",
            assistant_response="It's 3:00 PM",
            important=True
        )
        print("   OK  Saved conversation")
        
        # Retrieve
        results = memory.retrieve("time", n_results=3)
        print(f"   OK  Retrieved {len(results['relevant'])} relevant memories")
        
        # Learn fact
        memory.learn_fact("Boss works from 9 AM to 5 PM", "User Profile")
        print("   OK  Learned new fact")
    else:
        print("   WARN  MemoryManager partially initialized")
        if memory.readme:
            print("      - ReadmeMemory: OK")
        else:
            print("      - ReadmeMemory: Failed")
        if memory.chroma:
            print("      - ChromaMemory: OK")
        else:
            print("      - ChromaMemory: Failed")
    
    print("\n   OK  MemoryManager test passed!")
    
except Exception as e:
    print(f"   FAIL  MemoryManager test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Memory System Test Complete!")
print("="*60)
