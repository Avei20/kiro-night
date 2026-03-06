"""Data models for tasks."""

from datetime import datetime
from pydantic import BaseModel, Field
import re


class Task(BaseModel):
    """Represents a single task with markdown serialization support."""
    
    id: str = Field(..., description="Unique task identifier")
    description: str = Field(..., min_length=1, description="Task description")
    completed: bool = Field(default=False, description="Task completion status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    def to_markdown(self) -> str:
        """Convert task to markdown list item.
        
        Returns:
            Markdown formatted string like: "- [ ] Task description (ID: task-001)"
        """
        checkbox = "[x]" if self.completed else "[ ]"
        return f"- {checkbox} {self.description} (ID: {self.id})"
    
    @classmethod
    def from_markdown(cls, line: str) -> "Task":
        """Parse task from markdown list item.
        
        Args:
            line: Markdown formatted task line
            
        Returns:
            Task object parsed from the markdown line
            
        Raises:
            ValueError: If the line format is invalid
        """
        # Expected format: "- [ ] Task description (ID: task-001)"
        # or: "- [x] Task description (ID: task-001)"
        
        # Match markdown checkbox list item with ID
        pattern = r'^-\s+\[([ x])\]\s+(.+?)\s+\(ID:\s+([^)]+)\)$'
        match = re.match(pattern, line.strip())
        
        if not match:
            raise ValueError(f"Invalid markdown task format: {line}")
        
        checkbox, description, task_id = match.groups()
        completed = checkbox.lower() == 'x'
        
        # Create task with current timestamp (we don't persist created_at in markdown)
        return cls(
            id=task_id,
            description=description,
            completed=completed
        )
