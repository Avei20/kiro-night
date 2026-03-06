"""Task manager for CRUD operations."""

from .store import TaskStore


class TaskManager:
    """Manages task operations with markdown persistence."""
    
    def __init__(self, task_store: TaskStore):
        """Initialize with task store instance.
        
        Args:
            task_store: TaskStore instance for task persistence
        """
        self.task_store = task_store


    def create_task(self, description: str):
        """Create a new task with unique ID.

        Generates a unique task ID (e.g., task-001, task-002), creates a Task
        object with the provided description, loads existing tasks, appends the
        new task, and writes back to storage.

        Args:
            description: The task description

        Returns:
            The created Task object

        Raises:
            TaskStoreError: If reading or writing tasks fails
        """
        from .models import Task

        # Load existing tasks
        tasks = self.task_store.read_tasks()

        # Generate unique task ID
        if not tasks:
            # First task
            task_id = "task-001"
        else:
            # Find the highest task number and increment
            max_num = 0
            for task in tasks:
                # Extract number from task ID (e.g., "task-001" -> 1)
                if task.id.startswith("task-"):
                    try:
                        num = int(task.id.split("-")[1])
                        max_num = max(max_num, num)
                    except (IndexError, ValueError):
                        # Skip malformed task IDs
                        continue

            # Generate next ID
            task_id = f"task-{max_num + 1:03d}"

        # Create new task
        new_task = Task(id=task_id, description=description)

        # Append to task list
        tasks.append(new_task)

        # Write back to storage
        self.task_store.write_tasks(tasks)

        return new_task
    def get_all_tasks(self):
        """Retrieve all tasks from storage.

        Reads all tasks from the task store and returns them as a list.

        Returns:
            List of Task objects

        Raises:
            TaskStoreError: If reading tasks fails
        """
        return self.task_store.read_tasks()
    def find_task(self, task_id: str):
        """Find task by ID.

        Searches through all tasks for a task with the matching ID.

        Args:
            task_id: The task ID to search for

        Returns:
            Task object if found, None otherwise

        Raises:
            TaskStoreError: If reading tasks fails
        """
        tasks = self.task_store.read_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: str, **updates):
        """Update task attributes by ID.

        Finds a task by its ID, updates the specified attributes, and persists
        the changes to storage.

        Args:
            task_id: The ID of the task to update
            **updates: Keyword arguments for attributes to update (e.g., description, completed)

        Returns:
            The updated Task object

        Raises:
            TaskNotFoundError: If the task with the given ID is not found
            TaskStoreError: If reading or writing tasks fails
        """
        from .exceptions import TaskNotFoundError

        # Find the task
        task = self.find_task(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with ID '{task_id}' not found")

        # Load all tasks
        tasks = self.task_store.read_tasks()

        # Find and update the task in the list
        for i, t in enumerate(tasks):
            if t.id == task_id:
                # Create updated task with new attributes
                task_dict = t.model_dump()
                task_dict.update(updates)

                # Create new Task instance with updated values
                from .models import Task
                updated_task = Task(**task_dict)

                # Replace in list
                tasks[i] = updated_task

                # Write back to storage
                self.task_store.write_tasks(tasks)

                return updated_task

        # This should not happen since find_task already verified existence
        raise TaskNotFoundError(f"Task with ID '{task_id}' not found")

    def delete_task(self, task_id: str) -> bool:
        """Delete task by ID, return success status.

        Finds a task by its ID, removes it from the task list, and persists
        the changes to storage.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True on successful deletion

        Raises:
            TaskNotFoundError: If the task with the given ID is not found
            TaskStoreError: If reading or writing tasks fails
        """
        from .exceptions import TaskNotFoundError

        # Find the task to verify it exists
        task = self.find_task(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with ID '{task_id}' not found")

        # Load all tasks
        tasks = self.task_store.read_tasks()

        # Remove the task from the list
        tasks = [t for t in tasks if t.id != task_id]

        # Write updated list back to storage
        self.task_store.write_tasks(tasks)

        return True




