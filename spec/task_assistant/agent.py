"""Strands agent implementation and tools."""

from strands import tool
from .manager import TaskManager
from .exceptions import TaskStoreError, TaskNotFoundError


def create_task_tool(task_manager: TaskManager):
    """Create a tool function for creating tasks.

    Args:
        task_manager: TaskManager instance to use for task operations

    Returns:
        A tool function that can be registered with the Strands agent
    """
    @tool
    def create_task(description: str) -> str:
        """Create a new task with the given description.

        Args:
            description: The task description

        Returns:
            Success message with task ID or error message
        """
        try:
            task = task_manager.create_task(description)
            return f"Task created successfully with ID: {task.id}"
        except TaskStoreError as e:
            return f"Error creating task: {str(e)}"
        except Exception as e:
            return f"Unexpected error creating task: {str(e)}"

    return create_task


def list_tasks_tool(task_manager: TaskManager):
    """Create a tool function for listing all tasks.

    Args:
        task_manager: TaskManager instance to use for task operations

    Returns:
        A tool function that can be registered with the Strands agent
    """
    @tool
    def list_tasks() -> str:
        """List all tasks in the task store.

        Returns:
            Formatted list of all tasks or message if no tasks exist
        """
        try:
            tasks = task_manager.get_all_tasks()

            if not tasks:
                return "No tasks found. Your task list is empty."

            # Format tasks for display
            result = f"Found {len(tasks)} task(s):\n\n"
            for task in tasks:
                status = "✓" if task.completed else "○"
                result += f"{status} [{task.id}] {task.description}\n"

            return result.strip()
        except TaskStoreError as e:
            return f"Error reading tasks: {str(e)}"
        except Exception as e:
            return f"Unexpected error listing tasks: {str(e)}"

    return list_tasks



def update_task_tool(task_manager: TaskManager):
    """Create a tool function for updating tasks.

    Args:
        task_manager: TaskManager instance to use for task operations

    Returns:
        A tool function that can be registered with the Strands agent
    """
    @tool
    def update_task(task_id: str, description: str = None, completed: bool = None) -> str:
        """Update an existing task's attributes.

        Args:
            task_id: The ID of the task to update
            description: Optional new description for the task
            completed: Optional completion status (True/False)

        Returns:
            Success message with updated task details or error message
        """
        try:
            # Build updates dictionary with only provided parameters
            updates = {}
            if description is not None:
                updates['description'] = description
            if completed is not None:
                updates['completed'] = completed

            # Check if any updates were provided
            if not updates:
                return "No updates provided. Please specify description or completed status."

            # Update the task
            updated_task = task_manager.update_task(task_id, **updates)

            # Format success message
            status = "✓" if updated_task.completed else "○"
            return f"Task updated successfully:\n{status} [{updated_task.id}] {updated_task.description}"

        except TaskNotFoundError as e:
            return f"Task not found: {str(e)}"
        except TaskStoreError as e:
            return f"Error updating task: {str(e)}"
        except Exception as e:
            return f"Unexpected error updating task: {str(e)}"

    return update_task



def delete_task_tool(task_manager: TaskManager):
    """Create a tool function for deleting tasks.

    Args:
        task_manager: TaskManager instance to use for task operations

    Returns:
        A tool function that can be registered with the Strands agent
    """
    @tool
    def delete_task(task_id: str) -> str:
        """Delete a task by its ID.

        Args:
            task_id: The ID of the task to delete

        Returns:
            Success message or error message
        """
        try:
            task_manager.delete_task(task_id)
            return f"Task '{task_id}' deleted successfully."
        except TaskNotFoundError as e:
            return f"Task not found: {str(e)}"
        except TaskStoreError as e:
            return f"Error deleting task: {str(e)}"
        except Exception as e:
            return f"Unexpected error deleting task: {str(e)}"

    return delete_task

def create_agent(settings, task_manager):
    """Create and configure Strands agent with OpenRouter via LiteLLM.

    Args:
        settings: Settings instance with OpenRouter API key and model configuration
        task_manager: TaskManager instance for task operations

    Returns:
        Configured Agent instance ready for interaction
    """
    from strands import Agent
    # from strands.models.litellm import LiteLLMModel
    from strands.models.openai import OpenAIModel

    # Initialize LiteLLM model with OpenRouter
    # model = LiteLLMModel(
    #     client_args={
    #         "api_key": settings.openrouter_api_key,
    #         "api_base": "https://openrouter.ai/api/v1"
    #     },
    #     model_id=settings.default_model,
    #     params={
    #         "max_tokens": 2048,
    #         "temperature": 0.7
    #     }
    # )
    model = OpenAIModel(
        client_args={
            "api_key": settings.openrouter_api_key,
            "base_url": "https://openrouter.ai/api/v1"
        },
        model_id="openrouter/free",  # Uses free models automatically
    )

    # Create tool instances
    tools = [
        create_task_tool(task_manager),
        list_tasks_tool(task_manager),
        update_task_tool(task_manager),
        delete_task_tool(task_manager)
    ]

    # System prompt for the agent
    system_prompt = """You are a helpful task management assistant. You help users manage their tasks through natural conversation.

You can:
- Create new tasks when users describe what they need to do
- List all tasks to show what's on the user's plate
- Update tasks to change descriptions or mark them complete
- Delete tasks that are no longer needed

Be conversational and helpful. When users ask ambiguous questions, ask for clarification. Always confirm actions you take."""

    # Create and return the agent
    agent = Agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )

    return agent


def run_agent(agent):
    """Run the agent's interactive conversation loop.

    Args:
        agent: Configured Agent instance ready for interaction

    The function runs an interactive loop where:
    - User input is read from stdin
    - Agent processes the input and responds
    - Conversation history is maintained automatically by the agent
    - Ctrl+C gracefully exits the loop
    """
    print("Task Management Assistant")
    print("Type your requests in natural language. Press Ctrl+C to exit.\n")

    try:
        while True:
            try:
                # Get user input
                user_input = input("> ").strip()

                # Skip empty input
                if not user_input:
                    continue

                # Call the agent with user input
                response = agent(user_input)

                # Print the agent's response
                print(f"\n{response}\n")

            except EOFError:
                # Handle EOF (Ctrl+D on Unix, Ctrl+Z on Windows)
                print("\nGoodbye!")
                break

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\nGoodbye!")

