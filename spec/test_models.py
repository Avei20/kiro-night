"""Unit tests for Task data model."""

import pytest
from datetime import datetime
from task_assistant.models import Task


def test_task_creation():
    """Test creating a task with required fields."""
    task = Task(id="task-001", description="Test task")
    
    assert task.id == "task-001"
    assert task.description == "Test task"
    assert task.completed is False
    assert isinstance(task.created_at, datetime)


def test_task_with_completed_status():
    """Test creating a completed task."""
    task = Task(id="task-002", description="Completed task", completed=True)
    
    assert task.completed is True


def test_task_description_validation():
    """Test that empty description is rejected."""
    with pytest.raises(ValueError):
        Task(id="task-003", description="")


def test_to_markdown_incomplete():
    """Test markdown serialization for incomplete task."""
    task = Task(id="task-001", description="Buy groceries")
    markdown = task.to_markdown()
    
    assert markdown == "- [ ] Buy groceries (ID: task-001)"


def test_to_markdown_completed():
    """Test markdown serialization for completed task."""
    task = Task(id="task-002", description="Finish homework", completed=True)
    markdown = task.to_markdown()
    
    assert markdown == "- [x] Finish homework (ID: task-002)"


def test_from_markdown_incomplete():
    """Test parsing incomplete task from markdown."""
    line = "- [ ] Write documentation (ID: task-003)"
    task = Task.from_markdown(line)
    
    assert task.id == "task-003"
    assert task.description == "Write documentation"
    assert task.completed is False


def test_from_markdown_completed():
    """Test parsing completed task from markdown."""
    line = "- [x] Review code (ID: task-004)"
    task = Task.from_markdown(line)
    
    assert task.id == "task-004"
    assert task.description == "Review code"
    assert task.completed is True


def test_from_markdown_invalid_format():
    """Test that invalid markdown format raises error."""
    with pytest.raises(ValueError, match="Invalid markdown task format"):
        Task.from_markdown("Invalid task format")


def test_round_trip_serialization():
    """Test that task can be serialized and deserialized correctly."""
    original = Task(id="task-005", description="Test round trip", completed=False)
    markdown = original.to_markdown()
    restored = Task.from_markdown(markdown)
    
    assert restored.id == original.id
    assert restored.description == original.description
    assert restored.completed == original.completed
