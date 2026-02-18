"""ReAct agent for reasoning and tool execution."""

import json
import re
from typing import Any

from ..core.logger import get_logger
from .llm import OllamaClient
from .prompt import PromptBuilder

logger = get_logger(__name__)


class ReactAgent:
    """ReAct (Reasoning + Acting) agent for JARVIS."""
    
    def __init__(
        self,
        llm: OllamaClient,
        tools: dict[str, callable],
        prompt_builder: PromptBuilder,
        memory: Any | None = None
    ) -> None:
        """Initialize the ReAct agent.
        
        Args:
            llm: Ollama LLM client
            tools: Dictionary mapping tool names to callable functions
            prompt_builder: Prompt builder for constructing prompts
            memory: Memory manager for retrieving and saving memories
        """
        self.llm = llm
        self.tools = tools
        self.prompt_builder = prompt_builder
        self.memory = memory
        
        self.max_iterations = 5
        
        logger.info(f"ReactAgent initialized with {len(tools)} tools")
    
    def run(self, user_input: str) -> str:
        """Execute ReAct loop to process user input.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Final answer from the agent
        """
        logger.info(f"Starting ReAct loop for input: '{user_input[:50]}...'")
        
        # Step 1: Retrieve relevant memories
        retrieved_memories = []
        if self.memory:
            try:
                retrieved_memories = self.memory.retrieve(user_input, top_k=3)
                logger.info(f"Retrieved {len(retrieved_memories)} relevant memories")
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.error(f"Error retrieving memories: {e}")
        
        # Step 2: Read core knowledge from MEMORY.md
        memory_context = self.prompt_builder.read_memory_file()
        
        # Step 3: Build initial messages
        messages = self.prompt_builder.build_react_prompt(
            user_input=user_input,
            memory_context=memory_context,
            retrieved_memories=retrieved_memories,
            tools=self.tools
        )
        
        # Step 4: ReAct loop
        conversation_log = []
        final_answer = ""
        
        for iteration in range(self.max_iterations):
            logger.info(f"ReAct iteration {iteration + 1}/{self.max_iterations}")
            
            try:
                # Get LLM response
                response = self.llm.chat(messages, stream=False)
                logger.debug(f"LLM response: {response[:200]}...")
                
                # Check for Final Answer
                if "Final Answer:" in response:
                    final_answer = self._extract_final_answer(response)
                    logger.info("Final answer received")
                    break
                
                # Check for Action
                action_result = self.parse_action(response)
                if action_result:
                    tool_name, tool_args = action_result
                    
                    # Log the thought
                    thought = self._extract_thought(response)
                    if thought:
                        logger.info(f"Thought: {thought}")
                        conversation_log.append(f"Thought: {thought}")
                    
                    logger.info(f"Action: {tool_name}({tool_args})")
                    conversation_log.append(f"Action: {tool_name}({tool_args})")
                    
                    # Execute tool
                    observation = self._execute_tool(tool_name, tool_args)
                    logger.info(f"Observation: {observation}")
                    conversation_log.append(f"Observation: {observation}")
                    
                    # Add to messages for next iteration
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "system", 
                        "content": f"Observation: {observation}"
                    })
                else:
                    # No action found, treat as final response
                    final_answer = response
                    logger.info("No action detected, using response as final answer")
                    break
                    
            except (RuntimeError, ValueError, TypeError) as e:
                logger.error(f"Error in ReAct iteration {iteration + 1}: {e}")
                final_answer = f"I encountered an error while processing your request: {e}"
                break
        
        # If max iterations reached without final answer
        if not final_answer and conversation_log:
            final_answer = "I reached the maximum number of reasoning steps. Here's what I found:\n\n" + "\n".join(conversation_log)
        elif not final_answer:
            final_answer = "I'm sorry, I wasn't able to complete the task."
        
        # Step 5: Save to memory
        if self.memory:
            try:
                self.memory.save(f"User: {user_input}\nAssistant: {final_answer}")
                logger.info("Conversation saved to memory")
            except (AttributeError, IOError, RuntimeError) as e:
                logger.error(f"Error saving to memory: {e}")
        
        return final_answer
    
    def parse_action(self, text: str) -> tuple[str, str] | None:
        """Parse action from LLM response.
        
        Args:
            text: LLM response text
            
        Returns:
            Tuple of (tool_name, tool_args) or None if no action found
        """
        # Look for Action: pattern
        action_match = re.search(r'Action:\s*(\w+)\s*\(([^)]*)\)', text, re.IGNORECASE)
        
        if action_match:
            tool_name = action_match.group(1).strip()
            tool_args = action_match.group(2).strip()
            
            # Validate tool exists
            if tool_name in self.tools:
                return (tool_name, tool_args)
            else:
                logger.warning(f"Tool '{tool_name}' not found in available tools")
        
        # Alternative format: Action: tool_name args (without parentheses)
        action_match_alt = re.search(r'Action:\s*(\w+)\s+(.+?)(?:\n|$)', text, re.IGNORECASE)
        if action_match_alt:
            tool_name = action_match_alt.group(1).strip()
            tool_args = action_match_alt.group(2).strip()
            
            if tool_name in self.tools:
                return (tool_name, tool_args)
        
        return None
    
    def _extract_thought(self, text: str) -> str:
        """Extract thought from LLM response.
        
        Args:
            text: LLM response text
            
        Returns:
            Thought text or empty string
        """
        # Look for Thought: pattern
        thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|Final Answer:|$)', text, re.DOTALL | re.IGNORECASE)
        
        if thought_match:
            return thought_match.group(1).strip()
        
        return ""
    
    def _extract_final_answer(self, text: str) -> str:
        """Extract final answer from LLM response.
        
        Args:
            text: LLM response text
            
        Returns:
            Final answer text
        """
        # Look for Final Answer: pattern
        answer_match = re.search(r'Final Answer:\s*(.+)', text, re.DOTALL | re.IGNORECASE)
        
        if answer_match:
            return answer_match.group(1).strip()
        
        # If no Final Answer marker, return the whole text
        return text.strip()
    
    def _execute_tool(self, tool_name: str, tool_args: str) -> str:
        """Execute a tool and return the observation.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Observation from tool execution
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        tool_func = self.tools[tool_name]
        
        try:
            # Try to parse args as JSON
            if tool_args.strip():
                try:
                    args = json.loads(tool_args)
                    if isinstance(args, dict):
                        result = tool_func(**args)
                    else:
                        result = tool_func(args)
                except json.JSONDecodeError:
                    # Not JSON, pass as string
                    result = tool_func(tool_args)
            else:
                # No args
                result = tool_func()
            
            # Convert result to string
            if isinstance(result, dict):
                return json.dumps(result, indent=2)
            else:
                return str(result)
                
        except (TypeError, ValueError, RuntimeError) as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return f"Error executing {tool_name}: {e}"
