"""Tests for agent tools."""

import pytest
from task_assistant.agent import create_task_tool
from task_assistant.manager import TaskManager
from task_assistant.store import TaskStore


def test_create_task_tool_success(tmp_path):
    """Test create_task_tool returns success message with task ID."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create the tool
    tool = create_task_tool(task_manager)
    
    # Act
    result = tool("Buy groceries")
    
    # Assert
    assert "Task created successfully" in result
    assert "task-001" in result
    
    # Verify task was actually created
    tasks = task_manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Buy groceries"


def test_create_task_tool_multiple_tasks(tmp_path):
    """Test create_task_tool can create multiple tasks."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create the tool
    tool = create_task_tool(task_manager)
    
    # Act
    result1 = tool("First task")
    result2 = tool("Second task")
    result3 = tool("Third task")
    
    # Assert
    assert "task-001" in result1
    assert "task-002" in result2
    assert "task-003" in result3
    
    # Verify all tasks were created
    tasks = task_manager.get_all_tasks()
    assert len(tasks) == 3


def test_create_task_tool_returns_string(tmp_path):
    """Test create_task_tool returns a string message."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create the tool
    tool = create_task_tool(task_manager)
    
    # Act
    result = tool("Test task")
    
    # Assert
    assert isinstance(result, str)
    assert len(result) > 0



def test_list_tasks_tool_empty_list(tmp_path):
    """Test list_tasks_tool handles empty task list."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    from task_assistant.agent import list_tasks_tool
    tool = list_tasks_tool(task_manager)

    # Act
    result = tool()

    # Assert
    assert "No tasks found" in result
    assert "empty" in result.lower()


def test_list_tasks_tool_with_tasks(tmp_path):
    """Test list_tasks_tool displays all tasks."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    # Create some tasks
    task_manager.create_task("Buy groceries")
    task_manager.create_task("Write code")
    task_manager.create_task("Read book")

    from task_assistant.agent import list_tasks_tool
    tool = list_tasks_tool(task_manager)

    # Act
    result = tool()

    # Assert
    assert "Found 3 task(s)" in result
    assert "Buy groceries" in result
    assert "Write code" in result
    assert "Read book" in result
    assert "task-001" in result
    assert "task-002" in result
    assert "task-003" in result


def test_list_tasks_tool_shows_completion_status(tmp_path):
    """Test list_tasks_tool shows task completion status."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    # Create tasks with different completion status
    task_manager.create_task("Incomplete task")
    task_manager.create_task("Complete task")
    task_manager.update_task("task-002", completed=True)

    from task_assistant.agent import list_tasks_tool
    tool = list_tasks_tool(task_manager)

    # Act
    result = tool()

    # Assert
    assert "Found 2 task(s)" in result
    # Check for status indicators (○ for incomplete, ✓ for complete)
    assert "○" in result or "✓" in result
    assert "Incomplete task" in result
    assert "Complete task" in result


def test_list_tasks_tool_returns_string(tmp_path):
    """Test list_tasks_tool returns a string message."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    from task_assistant.agent import list_tasks_tool
    tool = list_tasks_tool(task_manager)

    # Act
    result = tool()

    # Assert
    assert isinstance(result, str)
    assert len(result) > 0



def test_update_task_tool_description(tmp_path):
    """Test update_task_tool can update task description."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Original description")
    
    from task_assistant.agent import update_task_tool
    tool = update_task_tool(task_manager)
    
    # Act
    result = tool("task-001", description="Updated description")
    
    # Assert
    assert "Task updated successfully" in result
    assert "Updated description" in result
    assert "task-001" in result
    
    # Verify task was actually updated
    tasks = task_manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Updated description"


def test_update_task_tool_completed_status(tmp_path):
    """Test update_task_tool can update task completion status."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    from task_assistant.agent import update_task_tool
    tool = update_task_tool(task_manager)
    
    # Act
    result = tool("task-001", completed=True)
    
    # Assert
    assert "Task updated successfully" in result
    assert "✓" in result  # Completed status indicator
    
    # Verify task was actually updated
    tasks = task_manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].completed is True


def test_update_task_tool_both_fields(tmp_path):
    """Test update_task_tool can update both description and completion status."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Original task")
    
    from task_assistant.agent import update_task_tool
    tool = update_task_tool(task_manager)
    
    # Act
    result = tool("task-001", description="Updated task", completed=True)
    
    # Assert
    assert "Task updated successfully" in result
    assert "Updated task" in result
    assert "✓" in result
    
    # Verify both fields were updated
    tasks = task_manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Updated task"
    assert tasks[0].completed is True


def test_update_task_tool_task_not_found(tmp_path):
    """Test update_task_tool handles non-existent task ID."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    from task_assistant.agent import update_task_tool
    tool = update_task_tool(task_manager)
    
    # Act
    result = tool("task-999", description="New description")
    
    # Assert
    assert "Task not found" in result
    assert "task-999" in result


def test_update_task_tool_no_updates_provided(tmp_path):
    """Test update_task_tool handles case when no updates are provided."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    from task_assistant.agent import update_task_tool
    tool = update_task_tool(task_manager)
    
    # Act
    result = tool("task-001")
    
    # Assert
    assert "No updates provided" in result


def test_update_task_tool_returns_string(tmp_path):
    """Test update_task_tool returns a string message."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)
    
    # Create a task
    task_manager.create_task("Test task")
    
    from task_assistant.agent import update_task_tool
    tool = update_task_tool(task_manager)
    
    # Act
    result = tool("task-001", description="Updated")
    
    # Assert
    assert isinstance(result, str)
    assert len(result) > 0



def test_delete_task_tool_success(tmp_path):
    """Test delete_task_tool successfully deletes a task."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    # Create a task
    task_manager.create_task("Task to delete")

    from task_assistant.agent import delete_task_tool
    tool = delete_task_tool(task_manager)

    # Act
    result = tool("task-001")

    # Assert
    assert "deleted successfully" in result
    assert "task-001" in result

    # Verify task was actually deleted
    tasks = task_manager.get_all_tasks()
    assert len(tasks) == 0


def test_delete_task_tool_task_not_found(tmp_path):
    """Test delete_task_tool handles non-existent task ID."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    from task_assistant.agent import delete_task_tool
    tool = delete_task_tool(task_manager)

    # Act
    result = tool("task-999")

    # Assert
    assert "Task not found" in result
    assert "task-999" in result


def test_delete_task_tool_deletes_correct_task(tmp_path):
    """Test delete_task_tool deletes only the specified task."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    # Create multiple tasks
    task_manager.create_task("First task")
    task_manager.create_task("Second task")
    task_manager.create_task("Third task")

    from task_assistant.agent import delete_task_tool
    tool = delete_task_tool(task_manager)

    # Act
    result = tool("task-002")

    # Assert
    assert "deleted successfully" in result

    # Verify only the second task was deleted
    tasks = task_manager.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].id == "task-001"
    assert tasks[0].description == "First task"
    assert tasks[1].id == "task-003"
    assert tasks[1].description == "Third task"


def test_delete_task_tool_returns_string(tmp_path):
    """Test delete_task_tool returns a string message."""
    # Arrange
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    # Create a task
    task_manager.create_task("Test task")

    from task_assistant.agent import delete_task_tool
    tool = delete_task_tool(task_manager)

    # Act
    result = tool("task-001")

    # Assert
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_agent_initialization(tmp_path, monkeypatch):
    """Test create_agent function initializes agent correctly."""
    # Arrange
    from task_assistant.agent import create_agent
    from task_assistant.config import Settings
    from task_assistant.store import TaskStore
    from task_assistant.manager import TaskManager
    from strands import Agent

    # Mock the API key
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")

    # Create task manager
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    # Load settings
    settings = Settings()

    # Act
    agent = create_agent(settings, task_manager)

    # Assert
    assert agent is not None
    assert isinstance(agent, Agent)
    assert hasattr(agent, 'model')
    # Verify agent has model configured
    assert agent.model is not None


def test_create_agent_with_custom_model(tmp_path, monkeypatch):
    """Test create_agent respects custom model configuration."""
    # Arrange
    from task_assistant.agent import create_agent
    from task_assistant.config import Settings
    from task_assistant.store import TaskStore
    from task_assistant.manager import TaskManager

    # Mock the API key and custom model
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("DEFAULT_MODEL", "openrouter/custom-model")

    # Create task manager
    task_file = tmp_path / "tasks.md"
    task_store = TaskStore(str(task_file))
    task_store.ensure_file_exists()
    task_manager = TaskManager(task_store)

    # Load settings
    settings = Settings()

    # Act
    agent = create_agent(settings, task_manager)

    # Assert
    assert agent is not None
    assert agent.model is not None
    # Verify settings were loaded correctly
    assert settings.default_model == "openrouter/custom-model"

