"""Tests for TaskStore class."""

import pytest
from pathlib import Path
import tempfile
import os
from task_assistant.store import TaskStore
from task_assistant.exceptions import TaskStoreError


class TestEnsureFileExists:
    """Tests for TaskStore.ensure_file_exists method."""
    
    def test_creates_file_if_not_exists(self):
        """Test that ensure_file_exists creates a new file with header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            store = TaskStore(file_path)
            
            # Verify file doesn't exist yet
            assert not Path(file_path).exists()
            
            # Call ensure_file_exists
            store.ensure_file_exists()
            
            # Verify file was created
            assert Path(file_path).exists()
            
            # Verify file has correct header
            content = Path(file_path).read_text(encoding="utf-8")
            assert content == "# Tasks\n\n"
    
    def test_does_not_overwrite_existing_file(self):
        """Test that ensure_file_exists doesn't overwrite existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create file with existing content
            existing_content = "# Tasks\n\n- [ ] Existing task (ID: task-001)\n"
            Path(file_path).write_text(existing_content, encoding="utf-8")
            
            store = TaskStore(file_path)
            store.ensure_file_exists()
            
            # Verify content wasn't changed
            content = Path(file_path).read_text(encoding="utf-8")
            assert content == existing_content
    
    def test_creates_parent_directories(self):
        """Test that ensure_file_exists creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "subdir", "nested", "tasks.md")
            store = TaskStore(file_path)
            
            # Verify parent directories don't exist
            assert not Path(file_path).parent.exists()
            
            # Call ensure_file_exists
            store.ensure_file_exists()
            
            # Verify file and parent directories were created
            assert Path(file_path).exists()
            assert Path(file_path).parent.exists()
            
            # Verify file has correct header
            content = Path(file_path).read_text(encoding="utf-8")
            assert content == "# Tasks\n\n"
    
    def test_raises_error_on_permission_denied(self):
        """Test that ensure_file_exists raises TaskStoreError on permission errors."""
        # Create a read-only directory
        with tempfile.TemporaryDirectory() as tmpdir:
            readonly_dir = os.path.join(tmpdir, "readonly")
            os.mkdir(readonly_dir)
            os.chmod(readonly_dir, 0o444)  # Read-only
            
            file_path = os.path.join(readonly_dir, "tasks.md")
            store = TaskStore(file_path)
            
            try:
                # Should raise TaskStoreError
                with pytest.raises(TaskStoreError) as exc_info:
                    store.ensure_file_exists()
                
                # Verify error message contains file path
                assert file_path in str(exc_info.value)
            finally:
                # Cleanup: restore permissions
                os.chmod(readonly_dir, 0o755)


class TestReadTasks:
    """Tests for TaskStore.read_tasks method."""
    
    def test_reads_tasks_from_file(self):
        """Test that read_tasks correctly parses tasks from markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create file with tasks
            content = """# Tasks

- [ ] First task (ID: task-001)
- [x] Second task (ID: task-002)
- [ ] Third task (ID: task-003)
"""
            Path(file_path).write_text(content, encoding="utf-8")
            
            store = TaskStore(file_path)
            tasks = store.read_tasks()
            
            # Verify correct number of tasks
            assert len(tasks) == 3
            
            # Verify first task
            assert tasks[0].id == "task-001"
            assert tasks[0].description == "First task"
            assert tasks[0].completed is False
            
            # Verify second task
            assert tasks[1].id == "task-002"
            assert tasks[1].description == "Second task"
            assert tasks[1].completed is True
            
            # Verify third task
            assert tasks[2].id == "task-003"
            assert tasks[2].description == "Third task"
            assert tasks[2].completed is False
    
    def test_returns_empty_list_for_empty_file(self):
        """Test that read_tasks returns empty list for empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create empty file
            Path(file_path).write_text("# Tasks\n\n", encoding="utf-8")
            
            store = TaskStore(file_path)
            tasks = store.read_tasks()
            
            assert tasks == []
    
    def test_returns_empty_list_for_nonexistent_file(self):
        """Test that read_tasks returns empty list if file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nonexistent.md")
            
            store = TaskStore(file_path)
            tasks = store.read_tasks()
            
            assert tasks == []
    
    def test_skips_malformed_lines(self):
        """Test that read_tasks skips malformed task lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create file with valid and malformed tasks
            content = """# Tasks

- [ ] Valid task (ID: task-001)
- This is not a valid task
- [ ] Missing ID
- [x] Another valid task (ID: task-002)
Some random text
"""
            Path(file_path).write_text(content, encoding="utf-8")
            
            store = TaskStore(file_path)
            tasks = store.read_tasks()
            
            # Should only parse the two valid tasks
            assert len(tasks) == 2
            assert tasks[0].id == "task-001"
            assert tasks[1].id == "task-002"
    
    def test_skips_header_lines(self):
        """Test that read_tasks skips markdown header lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create file with multiple headers
            content = """# Tasks

## Section 1

- [ ] Task in section 1 (ID: task-001)

## Section 2

- [ ] Task in section 2 (ID: task-002)
"""
            Path(file_path).write_text(content, encoding="utf-8")
            
            store = TaskStore(file_path)
            tasks = store.read_tasks()
            
            # Should parse both tasks, skipping headers
            assert len(tasks) == 2
            assert tasks[0].id == "task-001"
            assert tasks[1].id == "task-002"
    
    def test_raises_error_on_read_permission_denied(self):
        """Test that read_tasks raises TaskStoreError on permission errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create file
            Path(file_path).write_text("# Tasks\n\n- [ ] Task (ID: task-001)\n", encoding="utf-8")
            
            # Make file unreadable
            os.chmod(file_path, 0o000)
            
            store = TaskStore(file_path)
            
            try:
                # Should raise TaskStoreError
                with pytest.raises(TaskStoreError) as exc_info:
                    store.read_tasks()
                
                # Verify error message contains file path
                assert file_path in str(exc_info.value)
            finally:
                # Cleanup: restore permissions
                os.chmod(file_path, 0o644)


class TestWriteTasks:
    """Tests for TaskStore.write_tasks method."""
    
    def test_writes_tasks_to_file(self):
        """Test that write_tasks correctly writes tasks to markdown file."""
        from task_assistant.models import Task
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            store = TaskStore(file_path)
            
            # Create tasks
            tasks = [
                Task(id="task-001", description="First task", completed=False),
                Task(id="task-002", description="Second task", completed=True),
                Task(id="task-003", description="Third task", completed=False),
            ]
            
            # Write tasks
            store.write_tasks(tasks)
            
            # Verify file was created
            assert Path(file_path).exists()
            
            # Verify content
            content = Path(file_path).read_text(encoding="utf-8")
            expected = """# Tasks

- [ ] First task (ID: task-001)
- [x] Second task (ID: task-002)
- [ ] Third task (ID: task-003)
"""
            assert content == expected
    
    def test_writes_empty_task_list(self):
        """Test that write_tasks handles empty task list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            store = TaskStore(file_path)
            
            # Write empty list
            store.write_tasks([])
            
            # Verify file was created with just header
            assert Path(file_path).exists()
            content = Path(file_path).read_text(encoding="utf-8")
            assert content == "# Tasks\n\n"
    
    def test_overwrites_existing_file(self):
        """Test that write_tasks replaces existing content."""
        from task_assistant.models import Task
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create file with existing content
            existing_content = "# Tasks\n\n- [ ] Old task (ID: task-999)\n"
            Path(file_path).write_text(existing_content, encoding="utf-8")
            
            store = TaskStore(file_path)
            
            # Write new tasks
            tasks = [
                Task(id="task-001", description="New task", completed=False),
            ]
            store.write_tasks(tasks)
            
            # Verify old content was replaced
            content = Path(file_path).read_text(encoding="utf-8")
            assert "task-999" not in content
            assert "task-001" in content
            assert "New task" in content
    
    def test_creates_parent_directories(self):
        """Test that write_tasks creates parent directories if needed."""
        from task_assistant.models import Task
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "subdir", "nested", "tasks.md")
            store = TaskStore(file_path)
            
            # Verify parent directories don't exist
            assert not Path(file_path).parent.exists()
            
            # Write tasks
            tasks = [Task(id="task-001", description="Test task", completed=False)]
            store.write_tasks(tasks)
            
            # Verify file and parent directories were created
            assert Path(file_path).exists()
            assert Path(file_path).parent.exists()
    
    def test_atomic_write_operation(self):
        """Test that write_tasks uses atomic write operation."""
        from task_assistant.models import Task
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            
            # Create initial file
            initial_content = "# Tasks\n\n- [ ] Initial task (ID: task-001)\n"
            Path(file_path).write_text(initial_content, encoding="utf-8")
            
            store = TaskStore(file_path)
            
            # Write new tasks
            tasks = [
                Task(id="task-002", description="Updated task", completed=False),
            ]
            store.write_tasks(tasks)
            
            # Verify no temporary files left behind
            temp_files = list(Path(tmpdir).glob(".tasks.md.*.tmp"))
            assert len(temp_files) == 0
            
            # Verify content was updated
            content = Path(file_path).read_text(encoding="utf-8")
            assert "Updated task" in content
    
    def test_raises_error_on_write_permission_denied(self):
        """Test that write_tasks raises TaskStoreError on permission errors."""
        from task_assistant.models import Task
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a read-only directory
            readonly_dir = os.path.join(tmpdir, "readonly")
            os.mkdir(readonly_dir)
            os.chmod(readonly_dir, 0o444)  # Read-only
            
            file_path = os.path.join(readonly_dir, "tasks.md")
            store = TaskStore(file_path)
            
            tasks = [Task(id="task-001", description="Test task", completed=False)]
            
            try:
                # Should raise TaskStoreError
                with pytest.raises(TaskStoreError) as exc_info:
                    store.write_tasks(tasks)
                
                # Verify error message contains file path
                assert file_path in str(exc_info.value)
            finally:
                # Cleanup: restore permissions
                os.chmod(readonly_dir, 0o755)
    
    def test_round_trip_read_write(self):
        """Test that tasks can be read and written back without data loss."""
        from task_assistant.models import Task
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "tasks.md")
            store = TaskStore(file_path)
            
            # Create original tasks
            original_tasks = [
                Task(id="task-001", description="First task", completed=False),
                Task(id="task-002", description="Second task", completed=True),
                Task(id="task-003", description="Third task with special chars: @#$%", completed=False),
            ]
            
            # Write tasks
            store.write_tasks(original_tasks)
            
            # Read tasks back
            read_tasks = store.read_tasks()
            
            # Verify all tasks were preserved (ignoring created_at timestamp)
            assert len(read_tasks) == len(original_tasks)
            for original, read in zip(original_tasks, read_tasks):
                assert read.id == original.id
                assert read.description == original.description
                assert read.completed == original.completed
