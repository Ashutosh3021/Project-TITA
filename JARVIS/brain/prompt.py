"""Prompt builder for constructing system prompts with memory and tool context."""

from ..core.config import MEMORY_FILE_PATH
from ..core.logger import get_logger

logger = get_logger(__name__)


class PromptBuilder:
    """Builds system prompts with memory context and tool definitions."""
    
    def __init__(self) -> None:
        """Initialize the prompt builder."""
        logger.info("PromptBuilder initialized")
    
    def build_system_prompt(
        self, 
        memory_context: str = "", 
        retrieved_memories: list[str] | None = None
    ) -> str:
        """Build a comprehensive system prompt for JARVIS.
        
        Args:
            memory_context: Content from MEMORY.md (core knowledge)
            retrieved_memories: List of relevant memories from ChromaDB
            
        Returns:
            Complete system prompt string
        """
        # Base personality and role definition
        base_prompt = """You are JARVIS (Just A Rather Very Intelligent System), a helpful AI assistant for your Boss.

PERSONALITY:
- You are helpful, concise, and direct in your responses
- You address the user as "Boss" 
- You maintain a professional yet friendly tone
- You are proactive in offering assistance
- You admit when you don't know something rather than making up answers

CORE CAPABILITIES:
- Answer questions using your knowledge
- Execute tools and commands when needed
- Remember important information about your Boss
- Learn from past interactions

REASONING PROCESS (ReAct Pattern):
When solving problems, use this format:
1. Thought: Analyze the situation and plan your approach
2. Action: If you need to use a tool, specify it as "Action: tool_name(args)"
3. Observation: Review the result of the action
4. Final Answer: Provide your response to the Boss

You can iterate through multiple Thought/Action/Observation cycles before giving the Final Answer.

RULES:
- Always think step-by-step for complex tasks
- Use tools when they can help accomplish a task
- Be concise but thorough in your final answers
- If a tool fails, try an alternative approach or explain the issue
"""
        
        # Add core knowledge from MEMORY.md
        if memory_context:
            base_prompt += f"""

CORE KNOWLEDGE (from long-term memory):
{memory_context}
"""
        
        # Add retrieved relevant memories
        if retrieved_memories:
            memories_text = "\n".join(f"- {memory}" for memory in retrieved_memories)
            base_prompt += f"""

RELEVANT CONTEXT (from recent memory):
{memories_text}
"""
        
        logger.debug(f"Built system prompt ({len(base_prompt)} chars)")
        return base_prompt.strip()
    
    def format_tool_list(self, tools: dict[str, callable]) -> str:
        """Format available tools for inclusion in prompt.
        
        Args:
            tools: Dictionary mapping tool names to callable functions
            
        Returns:
            Formatted tool list string
        """
        if not tools:
            return "No tools currently available."
        
        tool_descriptions = []
        
        for name, func in tools.items():
            # Get docstring if available
            doc = func.__doc__ or "No description available"
            # Take first line of docstring
            description = doc.strip().split("\n")[0]
            tool_descriptions.append(f"- {name}: {description}")
        
        tools_text = "\n".join(tool_descriptions)
        
        formatted = f"""AVAILABLE TOOLS:
{tools_text}

TOOL USAGE FORMAT:
When you need to use a tool, respond with:
Action: tool_name(arguments)

The system will execute the tool and return an observation.
You can then continue reasoning or provide your final answer.
"""
        
        return formatted
    
    def build_react_prompt(
        self,
        user_input: str,
        conversation_history: list[dict[str, str]] | None = None,
        memory_context: str = "",
        retrieved_memories: list[str] | None = None,
        tools: dict[str, callable] | None = None
    ) -> list[dict[str, str]]:
        """Build complete message list for ReAct agent.
        
        Args:
            user_input: The user's current input
            conversation_history: Previous messages in the conversation
            memory_context: Core knowledge from MEMORY.md
            retrieved_memories: Relevant memories from ChromaDB
            tools: Available tools dictionary
            
        Returns:
            List of message dictionaries for LLM
        """
        messages = []
        
        # System message with full context
        system_prompt = self.build_system_prompt(memory_context, retrieved_memories)
        
        # Add tools if available
        if tools:
            system_prompt += "\n\n" + self.format_tool_list(tools)
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        logger.debug(f"Built ReAct prompt with {len(messages)} messages")
        return messages
    
    def read_memory_file(self) -> str:
        """Read core knowledge from MEMORY.md file.
        
        Returns:
            Content of MEMORY.md or empty string if not found
        """
        try:
            if MEMORY_FILE_PATH.exists():
                content = MEMORY_FILE_PATH.read_text(encoding="utf-8")
                logger.debug(f"Read {len(content)} chars from MEMORY.md")
                return content
            else:
                logger.warning(f"MEMORY.md not found at {MEMORY_FILE_PATH}")
                return ""
        except (IOError, OSError) as e:
            logger.error(f"Error reading MEMORY.md: {e}")
            return ""
