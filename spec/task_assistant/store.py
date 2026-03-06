"""Task storage implementation using markdown files."""


class TaskStore:
    """Handles reading and writing tasks to markdown file."""
    
    def __init__(self, file_path: str):
        """Initialize with path to markdown file.
        
        Args:
            file_path: Path to the markdown file for task storage
        """
        self.file_path = file_path

    def ensure_file_exists(self) -> None:
        """Create markdown file with header if it doesn't exist.

        Creates the file with a '# Tasks' header if the file doesn't exist.
        Handles file system errors gracefully by raising TaskStoreError.

        Raises:
            TaskStoreError: If file creation fails due to permissions or other IO errors
        """
        import os
        from pathlib import Path
        from .exceptions import TaskStoreError

        try:
            file = Path(self.file_path)

            # Check if file exists
            if not file.exists():
                # Create parent directories if they don't exist
                file.parent.mkdir(parents=True, exist_ok=True)

                # Create file with header
                file.write_text("# Tasks\n\n", encoding="utf-8")
        except (OSError, IOError, PermissionError) as e:
            raise TaskStoreError(f"Failed to create task file at {self.file_path}: {e}") from e
    def read_tasks(self) -> list:
        """Parse markdown file and return list of tasks.

        Reads the markdown file, parses each line that contains a task,
        and returns a list of Task objects. Handles empty files and
        malformed lines gracefully.

        Returns:
            List of Task objects parsed from the markdown file

        Raises:
            TaskStoreError: If file reading fails or file doesn't exist
        """
        from pathlib import Path
        from .models import Task
        from .exceptions import TaskStoreError

        try:
            file = Path(self.file_path)

            # If file doesn't exist, return empty list
            if not file.exists():
                return []

            # Read file content
            content = file.read_text(encoding="utf-8")

            # Parse tasks from content
            tasks = []
            for line in content.splitlines():
                line = line.strip()

                # Skip empty lines and header lines
                if not line or line.startswith("#"):
                    continue

                # Try to parse as task
                if line.startswith("- ["):
                    try:
                        task = Task.from_markdown(line)
                        tasks.append(task)
                    except ValueError:
                        # Skip malformed lines silently
                        continue

            return tasks

        except (OSError, IOError, PermissionError) as e:
            raise TaskStoreError(f"Failed to read tasks from {self.file_path}: {e}") from e

    def write_tasks(self, tasks: list) -> None:
        """Write tasks to markdown file, replacing existing content.

        Converts each task to markdown format and writes them to the file
        with proper formatting. Uses atomic write operation to prevent
        data corruption.

        Args:
            tasks: List of Task objects to write to file

        Raises:
            TaskStoreError: If file writing fails due to permissions or other IO errors
        """
        from pathlib import Path
        from .exceptions import TaskStoreError
        import tempfile
        import os

        try:
            # Build markdown content
            lines = ["# Tasks\n\n"]

            for task in tasks:
                lines.append(task.to_markdown() + "\n")

            content = "".join(lines)

            # Atomic write: write to temp file, then rename
            file = Path(self.file_path)

            # Create parent directories if they don't exist
            file.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file in the same directory
            temp_fd, temp_path = tempfile.mkstemp(
                dir=file.parent,
                prefix=f".{file.name}.",
                suffix=".tmp"
            )

            try:
                # Write content to temp file
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
                    temp_file.write(content)

                # Atomically replace the original file
                os.replace(temp_path, self.file_path)

            except Exception:
                # Clean up temp file if something goes wrong
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise

        except (OSError, IOError, PermissionError) as e:
            raise TaskStoreError(f"Failed to write tasks to {self.file_path}: {e}") from e
