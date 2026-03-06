"""Integration tests for core components working together."""

import pytest
import tempfile
import os
from pathlib import Path
from task_assistant.models import Task
from task_assistant.store import TaskStore
from task_assistant.manager import TaskManager
from task_assistant.exceptions import TaskNotFoundError


def test_full_crud_workflow():
    """Test complete CRUD workflow with all components."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        task_file = os.path.join(tmpdir, "tasks.md")
        task_store = TaskStore(task_file)
        task_store.ensure_file_exists()
        task_manager = TaskManager(task_store)
        
        # Verify file was created
        assert Path(task_file).exists()
        
        # CREATE: Add some tasks
        task1 = task_manager.create_task("Buy groceries")
        task2 = task_manager.create_task("Write documentation")
        task3 = task_manager.create_task("Review pull requests")
        
        assert task1.id == "task-001"
        assert task2.id == "task-002"
        assert task3.id == "task-003"
        
        # READ: Get all tasks
        all_tasks = task_manager.get_all_tasks()
        assert len(all_tasks) == 3
        assert all_tasks[0].description == "Buy groceries"
        assert all_tasks[1].description == "Write documentation"
        assert all_tasks[2].description == "Review pull requests"
        
        # READ: Find specific task
        found_task = task_manager.find_task("task-002")
        assert found_task is not None
        assert found_task.description == "Write documentation"
        assert found_task.completed is False
        
        # UPDATE: Mark task as completed
        updated_task = task_manager.update_task("task-002", completed=True)
        assert updated_task.completed is True
        
        # Verify update persisted
        all_tasks = task_manager.get_all_tasks()
        assert all_tasks[1].completed is True
        
        # UPDATE: Change description
        updated_task = task_manager.update_task(
            "task-001",
            description="Buy groceries and cook dinner"
        )
        assert updated_task.description == "Buy groceries and cook dinner"
        
        # Verify update persisted
        all_tasks = task_manager.get_all_tasks()
        assert all_tasks[0].description == "Buy groceries and cook dinner"
        
        # DELETE: Remove a task
        result = task_manager.delete_task("task-003")
        assert result is True
        
        # Verify deletion persisted
        all_tasks = task_manager.get_all_tasks()
        assert len(all_tasks) == 2
        assert all_tasks[0].id == "task-001"
        assert all_tasks[1].id == "task-002"
        
        # Verify deleted task cannot be found
        found_task = task_manager.find_task("task-003")
        assert found_task is None


def test_markdown_file_format():
    """Test that markdown file maintains correct format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        task_file = os.path.join(tmpdir, "tasks.md")
        task_store = TaskStore(task_file)
        task_store.ensure_file_exists()
        task_manager = TaskManager(task_store)
        
        # Create tasks
        task_manager.create_task("First task")
        task_manager.create_task("Second task")
        task_manager.update_task("task-002", completed=True)
        
        # Read raw markdown file
        content = Path(task_file).read_text(encoding="utf-8")
        
        # Verify format
        assert "# Tasks" in content
        assert "- [ ] First task (ID: task-001)" in content
        assert "- [x] Second task (ID: task-002)" in content


def test_persistence_across_instances():
    """Test that data persists across different TaskManager instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        task_file = os.path.join(tmpdir, "tasks.md")
        
        # First instance: create tasks
        task_store1 = TaskStore(task_file)
        task_store1.ensure_file_exists()
        task_manager1 = TaskManager(task_store1)
        
        task_manager1.create_task("Persistent task 1")
        task_manager1.create_task("Persistent task 2")
        task_manager1.update_task("task-001", completed=True)
        
        # Second instance: read tasks
        task_store2 = TaskStore(task_file)
        task_manager2 = TaskManager(task_store2)
        
        tasks = task_manager2.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].id == "task-001"
        assert tasks[0].description == "Persistent task 1"
        assert tasks[0].completed is True
        assert tasks[1].id == "task-002"
        assert tasks[1].description == "Persistent task 2"
        assert tasks[1].completed is False


def test_error_handling():
    """Test error handling for invalid operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        task_file = os.path.join(tmpdir, "tasks.md")
        task_store = TaskStore(task_file)
        task_store.ensure_file_exists()
        task_manager = TaskManager(task_store)
        
        # Create a task
        task_manager.create_task("Test task")
        
        # Try to update non-existent task
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_manager.update_task("task-999", description="Updated")
        assert "task-999" in str(exc_info.value)
        
        # Try to delete non-existent task
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_manager.delete_task("task-999")
        assert "task-999" in str(exc_info.value)
        
        # Verify original task is still intact
        tasks = task_manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == "task-001"


def test_task_id_generation():
    """Test that task IDs are generated correctly and sequentially."""
    with tempfile.TemporaryDirectory() as tmpdir:
        task_file = os.path.join(tmpdir, "tasks.md")
        task_store = TaskStore(task_file)
        task_store.ensure_file_exists()
        task_manager = TaskManager(task_store)
        
        # Create multiple tasks
        for i in range(1, 11):
            task = task_manager.create_task(f"Task {i}")
            expected_id = f"task-{i:03d}"
            assert task.id == expected_id
        
        # Delete a task in the middle
        task_manager.delete_task("task-005")
        
        # Create a new task - should continue from highest ID
        new_task = task_manager.create_task("New task")
        assert new_task.id == "task-011"
        
        # Verify total count
        tasks = task_manager.get_all_tasks()
        assert len(tasks) == 10  # 10 created, 1 deleted = 9 + 1 new = 10
