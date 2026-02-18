"""Human-readable MEMORY.md management for JARVIS."""

import re
from pathlib import Path
from typing import Any

from ..core.config import MEMORY_FILE_PATH
from ..core.logger import get_logger

logger = get_logger(__name__)


class ReadmeMemory:
    """Manages human-readable MEMORY.md file with structured sections."""
    
    # Standard sections in MEMORY.md
    SECTIONS = [
        "User Profile",
        "Preferences", 
        "Important Facts",
        "Ongoing Tasks"
    ]
    
    def __init__(self, file_path: Path = MEMORY_FILE_PATH) -> None:
        """Initialize ReadmeMemory.
        
        Args:
            file_path: Path to MEMORY.md file
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self.file_path.exists():
            self._create_template()
        
        logger.info(f"ReadmeMemory initialized at {self.file_path}")
    
    def _create_template(self) -> None:
        """Create template MEMORY.md file with standard sections."""
        template = """# JARVIS CORE MEMORY

## User Profile
- Name: 
- Location: 
- Occupation: 
- Other: 

## Preferences
- Communication style: 
- Topics of interest: 
- Preferred times: 

## Important Facts
(No important facts recorded yet)

## Ongoing Tasks
(No ongoing tasks)
"""
        try:
            self.file_path.write_text(template, encoding="utf-8")
            logger.info(f"Created MEMORY.md template at {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise RuntimeError(f"Failed to create MEMORY.md template: {e}") from e
    
    def load(self) -> str:
        """Load full content of MEMORY.md.
        
        Returns:
            Full file content as string
        """
        try:
            content = self.file_path.read_text(encoding="utf-8")
            logger.debug(f"Loaded {len(content)} characters from MEMORY.md")
            return content
        except Exception as e:
            logger.error(f"Failed to load MEMORY.md: {e}")
            # Return empty string if file can't be read
            return ""
    
    def get_section(self, section: str) -> str:
        """Get content of a specific section.
        
        Args:
            section: Section name (e.g., "User Profile")
            
        Returns:
            Section content as string
        """
        try:
            content = self.load()
            
            # Find section heading
            pattern = rf"## {re.escape(section)}\n(.*?)(?=## |\Z)"
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                section_content = match.group(1).strip()
                logger.debug(f"Retrieved section '{section}': {len(section_content)} chars")
                return section_content
            else:
                logger.warning(f"Section '{section}' not found")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to get section '{section}': {e}")
            return ""
    
    def update_section(self, section: str, content: str) -> None:
        """Replace entire content of a section.
        
        Args:
            section: Section name
            content: New section content
        """
        try:
            full_content = self.load()
            
            # Find and replace section
            pattern = rf"(## {re.escape(section)}\n).*?(?=## |\Z)"
            replacement = rf"\1{content}\n\n"
            
            new_content = re.sub(pattern, replacement, full_content, flags=re.DOTALL)
            
            # Write back
            self.file_path.write_text(new_content, encoding="utf-8")
            logger.info(f"Updated section '{section}'")
            
        except Exception as e:
            logger.error(f"Failed to update section '{section}': {e}")
            raise RuntimeError(f"Failed to update section: {e}") from e
    
    def append_fact(self, section: str, fact: str) -> None:
        """Append a fact to a section.
        
        Args:
            section: Section name
            fact: Fact text to add
        """
        try:
            current_content = self.get_section(section)
            
            # Add fact as bullet point
            timestamp = self._get_timestamp()
            new_entry = f"- {fact} [{timestamp}]"
            
            if current_content and not current_content.endswith("\n"):
                current_content += "\n"
            
            updated_content = current_content + new_entry + "\n"
            
            self.update_section(section, updated_content)
            logger.info(f"Added fact to '{section}': {fact[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to append fact: {e}")
            raise RuntimeError(f"Failed to append fact: {e}") from e
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def update_user_profile(self, **kwargs: Any) -> None:
        """Update user profile section.
        
        Args:
            **kwargs: Profile fields (name, location, occupation, etc.)
        """
        try:
            profile_content = self.get_section("User Profile")
            
            # Update each field
            for key, value in kwargs.items():
                # Capitalize first letter of key
                field_name = key.capitalize()
                
                # Check if field exists
                pattern = rf"(- {re.escape(field_name)}: ).*"
                if re.search(pattern, profile_content):
                    # Update existing field
                    profile_content = re.sub(
                        pattern,
                        rf"\1{value}",
                        profile_content
                    )
                else:
                    # Add new field
                    if not profile_content.endswith("\n"):
                        profile_content += "\n"
                    profile_content += f"- {field_name}: {value}\n"
            
            self.update_section("User Profile", profile_content)
            logger.info("Updated user profile")
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise RuntimeError(f"Failed to update profile: {e}") from e
    
    def add_task(self, task: str, status: str = "active") -> None:
        """Add a task to ongoing tasks.
        
        Args:
            task: Task description
            status: Task status (active, completed, etc.)
        """
        try:
            timestamp = self._get_timestamp()
            task_entry = f"- [ ] {task} (Status: {status}) [{timestamp}]"
            
            self.append_fact("Ongoing Tasks", task_entry)
            logger.info(f"Added task: {task}")
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            raise RuntimeError(f"Failed to add task: {e}") from e
    
    def complete_task(self, task_pattern: str) -> bool:
        """Mark a task as completed.
        
        Args:
            task_pattern: Pattern to match task
            
        Returns:
            True if task was found and updated
        """
        try:
            content = self.get_section("Ongoing Tasks")
            
            # Find and update task
            pattern = rf"(- \[ )()(.*?{re.escape(task_pattern)}.*?)(\n)"
            if re.search(pattern, content, re.IGNORECASE):
                updated = re.sub(
                    pattern,
                    rf"\1x\3\4",
                    content,
                    flags=re.IGNORECASE
                )
                self.update_section("Ongoing Tasks", updated)
                logger.info(f"Marked task as completed: {task_pattern}")
                return True
            else:
                logger.warning(f"Task not found: {task_pattern}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    def get_all_facts(self) -> list[str]:
        """Get all facts from Important Facts section.
        
        Returns:
            List of fact strings
        """
        try:
            content = self.get_section("Important Facts")
            
            # Extract bullet points
            facts = []
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    # Remove bullet and timestamp
                    fact = re.sub(r"\s*\[\d{4}-\d{2}-\d{2}\]\s*$", "", line[2:])
                    facts.append(fact)
            
            return facts
            
        except Exception as e:
            logger.error(f"Failed to get facts: {e}")
            return []
