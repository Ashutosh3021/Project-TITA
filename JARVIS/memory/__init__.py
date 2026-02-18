"""Unified memory management for JARVIS - composes ChromaDB and README memory."""

from pathlib import Path
from typing import Any

from ..core.config import CHROMA_PATH, MEMORY_FILE_PATH
from ..core.logger import get_logger
from .chroma import ChromaMemory
from .readme_memory import ReadmeMemory

logger = get_logger(__name__)


class MemoryManager:
    """Unified memory manager combining ChromaDB vector storage and human-readable MEMORY.md.
    
    This class provides a high-level interface for JARVIS to:
    - Save conversations and facts
    - Retrieve relevant context
    - Manage important information in human-readable format
    """
    
    def __init__(
        self,
        chroma_path: Path = CHROMA_PATH,
        memory_file_path: Path = MEMORY_FILE_PATH
    ) -> None:
        """Initialize memory manager with both storage backends.
        
        Args:
            chroma_path: Directory for ChromaDB storage
            memory_file_path: Path to MEMORY.md file
        """
        try:
            self.chroma = ChromaMemory(chroma_path)
            logger.info("ChromaMemory initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaMemory: {e}")
            self.chroma = None
        
        try:
            self.readme = ReadmeMemory(memory_file_path)
            logger.info("ReadmeMemory initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ReadmeMemory: {e}")
            self.readme = None
        
        logger.info("MemoryManager initialized")
    
    def save(
        self,
        user_input: str,
        assistant_response: str,
        important: bool = False,
        session_id: str | None = None
    ) -> None:
        """Save a conversation exchange.
        
        Always saves to ChromaDB. If important=True, also appends to MEMORY.md.
        
        Args:
            user_input: User's input text
            assistant_response: Assistant's response text
            important: Whether this is important enough for MEMORY.md
            session_id: Optional session identifier
        """
        # Always save to ChromaDB
        if self.chroma:
            try:
                metadata = {}
                if session_id:
                    metadata["session_id"] = session_id
                
                self.chroma.add_conversation(
                    user_input=user_input,
                    assistant_response=assistant_response,
                    metadata=metadata
                )
                logger.debug("Saved to ChromaDB")
            except Exception as e:
                logger.error(f"Failed to save to ChromaDB: {e}")
        
        # If important, also save to MEMORY.md
        if important and self.readme:
            try:
                # Determine section based on content
                fact = f"User asked: {user_input} | Assistant responded: {assistant_response}"
                self.readme.append_fact("Important Facts", fact)
                logger.info("Saved important fact to MEMORY.md")
            except Exception as e:
                logger.error(f"Failed to save to MEMORY.md: {e}")
    
    def retrieve(self, query: str, n_results: int = 5) -> dict[str, Any]:
        """Retrieve relevant memories.
        
        Returns both core memory (from MEMORY.md) and relevant ChromaDB results.
        
        Args:
            query: Search query
            n_results: Number of ChromaDB results to return
            
        Returns:
            Dictionary with keys:
            - "core": Full MEMORY.md content (str)
            - "relevant": List of relevant text chunks from ChromaDB (list[str])
        """
        result = {
            "core": "",
            "relevant": []
        }
        
        # Get core memory from MEMORY.md
        if self.readme:
            try:
                result["core"] = self.readme.load()
                logger.debug("Retrieved core memory from MEMORY.md")
            except Exception as e:
                logger.error(f"Failed to retrieve core memory: {e}")
        
        # Get relevant memories from ChromaDB
        if self.chroma:
            try:
                result["relevant"] = self.chroma.retrieve_relevant(query, n_results)
                logger.debug(f"Retrieved {len(result['relevant'])} relevant memories from ChromaDB")
            except Exception as e:
                logger.error(f"Failed to retrieve from ChromaDB: {e}")
        
        return result
    
    def learn_fact(self, fact: str, section: str = "Important Facts") -> None:
        """Learn and store a new fact.
        
        Stores in both ChromaDB (for vector search) and MEMORY.md (for human readability).
        
        Args:
            fact: The fact to learn
            section: Section in MEMORY.md (default: "Important Facts")
        """
        # Save to ChromaDB for vector search
        if self.chroma:
            try:
                self.chroma.add_fact(fact, category=section)
                logger.debug(f"Added fact to ChromaDB: {fact[:50]}...")
            except Exception as e:
                logger.error(f"Failed to add fact to ChromaDB: {e}")
        
        # Save to MEMORY.md for human readability
        if self.readme:
            try:
                self.readme.append_fact(section, fact)
                logger.info(f"Learned fact in {section}: {fact[:50]}...")
            except Exception as e:
                logger.error(f"Failed to add fact to MEMORY.md: {e}")
    
    def update_user_profile(self, **kwargs: Any) -> None:
        """Update user profile information.
        
        Args:
            **kwargs: Profile fields (name, location, occupation, etc.)
        """
        if self.readme:
            try:
                self.readme.update_user_profile(**kwargs)
                logger.info("Updated user profile")
            except Exception as e:
                logger.error(f"Failed to update user profile: {e}")
    
    def add_task(self, task: str, status: str = "active") -> None:
        """Add a new ongoing task.
        
        Args:
            task: Task description
            status: Task status
        """
        if self.readme:
            try:
                self.readme.add_task(task, status)
                logger.info(f"Added task: {task}")
            except Exception as e:
                logger.error(f"Failed to add task: {e}")
    
    def complete_task(self, task_pattern: str) -> bool:
        """Mark a task as completed.
        
        Args:
            task_pattern: Pattern to match the task
            
        Returns:
            True if task was found and marked complete
        """
        if self.readme:
            try:
                result = self.readme.complete_task(task_pattern)
                if result:
                    logger.info(f"Completed task: {task_pattern}")
                return result
            except Exception as e:
                logger.error(f"Failed to complete task: {e}")
        return False
    
    def cleanup(self, days: int = 30) -> int:
        """Clean up old conversations.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of items cleaned up
        """
        if self.chroma:
            try:
                count = self.chroma.clear_old_conversations(days)
                logger.info(f"Cleaned up {count} old conversations")
                return count
            except Exception as e:
                logger.error(f"Failed to cleanup: {e}")
        return 0
    
    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        stats = {
            "chroma": {"initialized": self.chroma is not None},
            "readme": {"initialized": self.readme is not None}
        }
        
        if self.chroma:
            try:
                chroma_stats = self.chroma.get_stats()
                for key, value in chroma_stats.items():
                    stats["chroma"][key] = value
            except Exception as e:
                logger.error(f"Failed to get ChromaDB stats: {e}")
        
        return stats
    
    def is_ready(self) -> bool:
        """Check if memory system is fully initialized.
        
        Returns:
            True if both backends are ready
        """
        return self.chroma is not None and self.readme is not None
