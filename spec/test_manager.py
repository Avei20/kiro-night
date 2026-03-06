"""Tests for TaskManager class."""

import pytest
from task_assistant.manager import TaskManager
from task_assistant.store import TaskStore


def test_task_manager_initialization():
    """Test TaskManager accepts and stores TaskStore instance."""
    # Arrange
    task_store = TaskStore("test_tasks.md")
    
    # Act
    task_manager = TaskManager(task_store)
    
    # Assert
    assert task_manager.task_store is task_store
    assert isinstance(task_manager.task_store, TaskStore)
    assert task_manager.task_store.file_path == "test_tasks.md"


def test_task_manager_stores_task_store_reference():
    """Test TaskManager maintains reference to the same TaskStore instance."""
    # Arrange
    task_store = TaskStore("another_test.md")
    
    # Act
    task_manager = TaskManager(task_store)
    
    # Assert
    assert task_manager.task_store.file_path == "another_test.md"


def test_create_task_first_task(tmp_path):
    """Test creating the first task generates task-001 ID."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Act
    task = task_manager.create_task("Buy groceries")
    
    # Assert
    assert task.id == "task-001"
    assert task.description == "Buy groceries"
    assert task.completed is False
    
    # Verify task was persisted
    tasks = task_store.read_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == "task-001"
    assert tasks[0].description == "Buy groceries"


def test_create_task_increments_id(tmp_path):
    """Test creating multiple tasks increments ID correctly."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Act
    task1 = task_manager.create_task("First task")
    task2 = task_manager.create_task("Second task")
    task3 = task_manager.create_task("Third task")
    
    # Assert
    assert task1.id == "task-001"
    assert task2.id == "task-002"
    assert task3.id == "task-003"
    
    # Verify all tasks were persisted
    tasks = task_store.read_tasks()
    assert len(tasks) == 3
    assert tasks[0].id == "task-001"
    assert tasks[1].id == "task-002"
    assert tasks[2].id == "task-003"


def test_create_task_returns_task_object(tmp_path):
    """Test create_task returns a Task object with correct attributes."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Act
    task = task_manager.create_task("Test task")
    
    # Assert
    from task_assistant.models import Task
    assert isinstance(task, Task)
    assert task.description == "Test task"
    assert task.completed is False
    assert task.created_at is not None


def test_get_all_tasks_empty_store(tmp_path):
    """Test get_all_tasks returns empty list when no tasks exist."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Act
    tasks = task_manager.get_all_tasks()
    
    # Assert
    assert tasks == []
    assert isinstance(tasks, list)


def test_get_all_tasks_returns_all_tasks(tmp_path):
    """Test get_all_tasks returns all tasks from storage."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create multiple tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    task_manager.create_task("Third task")
    
    # Act
    tasks = task_manager.get_all_tasks()
    
    # Assert
    assert len(tasks) == 3
    assert tasks[0].description == "First task"
    assert tasks[1].description == "Second task"
    assert tasks[2].description == "Third task"


def test_get_all_tasks_returns_task_objects(tmp_path):
    """Test get_all_tasks returns proper Task objects."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    task_manager.create_task("Test task")
    
    # Act
    tasks = task_manager.get_all_tasks()
    
    # Assert
    from task_assistant.models import Task
    assert len(tasks) == 1
    assert isinstance(tasks[0], Task)
    assert tasks[0].id == "task-001"
    assert tasks[0].description == "Test task"
    assert tasks[0].completed is False


def test_find_task_existing_task(tmp_path):
    """Test find_task returns task when ID exists."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    task_manager.create_task("Third task")
    
    # Act
    found_task = task_manager.find_task("task-002")
    
    # Assert
    assert found_task is not None
    assert found_task.id == "task-002"
    assert found_task.description == "Second task"


def test_find_task_nonexistent_task(tmp_path):
    """Test find_task returns None when ID doesn't exist."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    
    # Act
    found_task = task_manager.find_task("task-999")
    
    # Assert
    assert found_task is None


def test_find_task_empty_store(tmp_path):
    """Test find_task returns None when store is empty."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Act
    found_task = task_manager.find_task("task-001")
    
    # Assert
    assert found_task is None


def test_update_task_description(tmp_path):
    """Test updating a task's description."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Original description")
    
    # Act
    updated_task = task_manager.update_task("task-001", description="Updated description")
    
    # Assert
    assert updated_task.id == "task-001"
    assert updated_task.description == "Updated description"
    assert updated_task.completed is False
    
    # Verify persistence
    tasks = task_store.read_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Updated description"


def test_update_task_completed_status(tmp_path):
    """Test updating a task's completed status."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    # Act
    updated_task = task_manager.update_task("task-001", completed=True)
    
    # Assert
    assert updated_task.id == "task-001"
    assert updated_task.description == "Test task"
    assert updated_task.completed is True
    
    # Verify persistence
    tasks = task_store.read_tasks()
    assert len(tasks) == 1
    assert tasks[0].completed is True


def test_update_task_multiple_attributes(tmp_path):
    """Test updating multiple task attributes at once."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Original task")
    
    # Act
    updated_task = task_manager.update_task(
        "task-001",
        description="Updated task",
        completed=True
    )
    
    # Assert
    assert updated_task.id == "task-001"
    assert updated_task.description == "Updated task"
    assert updated_task.completed is True
    
    # Verify persistence
    tasks = task_store.read_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Updated task"
    assert tasks[0].completed is True


def test_update_task_nonexistent_raises_error(tmp_path):
    """Test updating a nonexistent task raises TaskNotFoundError."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    # Act & Assert
    from task_assistant.exceptions import TaskNotFoundError
    with pytest.raises(TaskNotFoundError) as exc_info:
        task_manager.update_task("task-999", description="Updated")
    
    assert "task-999" in str(exc_info.value)


def test_update_task_preserves_other_tasks(tmp_path):
    """Test updating one task doesn't affect other tasks."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create multiple tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    task_manager.create_task("Third task")
    
    # Act
    task_manager.update_task("task-002", description="Updated second task", completed=True)
    
    # Assert
    tasks = task_store.read_tasks()
    assert len(tasks) == 3
    assert tasks[0].id == "task-001"
    assert tasks[0].description == "First task"
    assert tasks[0].completed is False
    assert tasks[1].id == "task-002"
    assert tasks[1].description == "Updated second task"
    assert tasks[1].completed is True
    assert tasks[2].id == "task-003"
    assert tasks[2].description == "Third task"
    assert tasks[2].completed is False


def test_update_task_returns_task_object(tmp_path):
    """Test update_task returns a Task object."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    # Act
    updated_task = task_manager.update_task("task-001", description="Updated")
    
    # Assert
    from task_assistant.models import Task
    assert isinstance(updated_task, Task)
    assert updated_task.id == "task-001"
    assert updated_task.description == "Updated"


def test_delete_task_existing_task(tmp_path):
    """Test deleting an existing task."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    task_manager.create_task("Third task")
    
    # Act
    result = task_manager.delete_task("task-002")
    
    # Assert
    assert result is True
    
    # Verify task was removed
    tasks = task_store.read_tasks()
    assert len(tasks) == 2
    assert tasks[0].id == "task-001"
    assert tasks[1].id == "task-003"


def test_delete_task_nonexistent_raises_error(tmp_path):
    """Test deleting a nonexistent task raises TaskNotFoundError."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    # Act & Assert
    from task_assistant.exceptions import TaskNotFoundError
    with pytest.raises(TaskNotFoundError) as exc_info:
        task_manager.delete_task("task-999")
    
    assert "task-999" in str(exc_info.value)


def test_delete_task_empty_store_raises_error(tmp_path):
    """Test deleting from empty store raises TaskNotFoundError."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Act & Assert
    from task_assistant.exceptions import TaskNotFoundError
    with pytest.raises(TaskNotFoundError) as exc_info:
        task_manager.delete_task("task-001")
    
    assert "task-001" in str(exc_info.value)


def test_delete_task_returns_true(tmp_path):
    """Test delete_task returns True on success."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    # Act
    result = task_manager.delete_task("task-001")
    
    # Assert
    assert result is True
    assert isinstance(result, bool)


def test_delete_task_persists_changes(tmp_path):
    """Test delete_task persists changes to storage."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    
    # Act
    task_manager.delete_task("task-001")
    
    # Assert - verify by reading from storage again
    tasks = task_store.read_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == "task-002"
    assert tasks[0].description == "Second task"


def test_delete_task_only_deletes_specified_task(tmp_path):
    """Test delete_task only removes the specified task."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create multiple tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    task_manager.create_task("Third task")
    task_manager.create_task("Fourth task")
    
    # Act
    task_manager.delete_task("task-003")
    
    # Assert
    tasks = task_store.read_tasks()
    assert len(tasks) == 3
    assert tasks[0].id == "task-001"
    assert tasks[1].id == "task-002"
    assert tasks[2].id == "task-004"
    
    # Verify task-003 is not in the list
    task_ids = [t.id for t in tasks]
    assert "task-003" not in task_ids
