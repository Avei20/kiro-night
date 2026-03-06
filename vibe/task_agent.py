"""Task Management Assistant using Strands SDK with OpenRouter

This agent helps manage tasks stored in a markdown file (tasks.md).

Features:
- Add tasks with priority levels (high, medium, low)
- List all tasks
- Mark tasks as completed
- Delete tasks
- Clear completed tasks

Usage:
    uv run python task_agent.py

The agent uses:
- Strands SDK for AI agent capabilities
- OpenRouter as the AI provider (OpenAI-compatible API)
- Pydantic Settings for environment variable management
- tasks.md as the single source of truth for task storage
"""

import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings
from strands import Agent, tool
from strands.models.openai import OpenAIModel


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    openrouter_api_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Load settings
settings = Settings()

# Task file path
TASKS_FILE = Path("tasks.md")


def ensure_tasks_file():
    """Ensure tasks.md exists"""
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("# Tasks\n\n")


@tool
def list_tasks() -> str:
    """List all tasks from the tasks file.
    
    Returns:
        String containing all tasks
    """
    ensure_tasks_file()
    return TASKS_FILE.read_text()


@tool
def add_task(task: str, priority: Literal["high", "medium", "low"] = "medium") -> str:
    """Add a new task to the tasks file.
    
    Args:
        task: The task description
        priority: Task priority (high, medium, or low)
    
    Returns:
        Confirmation message
    """
    ensure_tasks_file()
    content = TASKS_FILE.read_text()
    
    # Add task with priority
    new_task = f"- [ ] **[{priority.upper()}]** {task}\n"
    
    # Append to file
    if content.strip().endswith("# Tasks"):
        content += "\n" + new_task
    else:
        content += new_task
    
    TASKS_FILE.write_text(content)
    return f"Task added: {task} (Priority: {priority})"


@tool
def complete_task(task_number: int) -> str:
    """Mark a task as completed.
    
    Args:
        task_number: The task number to complete (1-based index)
    
    Returns:
        Confirmation message
    """
    ensure_tasks_file()
    content = TASKS_FILE.read_text()
    lines = content.split("\n")
    
    # Find task lines
    task_lines = [i for i, line in enumerate(lines) if line.strip().startswith("- [ ]")]
    
    if task_number < 1 or task_number > len(task_lines):
        return f"Invalid task number. There are {len(task_lines)} tasks."
    
    # Mark as complete
    task_idx = task_lines[task_number - 1]
    lines[task_idx] = lines[task_idx].replace("- [ ]", "- [x]")
    
    TASKS_FILE.write_text("\n".join(lines))
    return f"Task {task_number} marked as completed!"


@tool
def delete_task(task_number: int) -> str:
    """Delete a task from the tasks file.
    
    Args:
        task_number: The task number to delete (1-based index)
    
    Returns:
        Confirmation message
    """
    ensure_tasks_file()
    content = TASKS_FILE.read_text()
    lines = content.split("\n")
    
    # Find all task lines (both completed and incomplete)
    task_lines = [i for i, line in enumerate(lines) 
                  if line.strip().startswith("- [ ]") or line.strip().startswith("- [x]")]
    
    if task_number < 1 or task_number > len(task_lines):
        return f"Invalid task number. There are {len(task_lines)} tasks."
    
    # Remove the task
    task_idx = task_lines[task_number - 1]
    deleted_task = lines[task_idx]
    del lines[task_idx]
    
    TASKS_FILE.write_text("\n".join(lines))
    return f"Task {task_number} deleted: {deleted_task}"


@tool
def clear_completed_tasks() -> str:
    """Remove all completed tasks from the tasks file.
    
    Returns:
        Confirmation message with count of removed tasks
    """
    ensure_tasks_file()
    content = TASKS_FILE.read_text()
    lines = content.split("\n")
    
    # Filter out completed tasks
    completed_count = sum(1 for line in lines if line.strip().startswith("- [x]"))
    filtered_lines = [line for line in lines if not line.strip().startswith("- [x]")]
    
    TASKS_FILE.write_text("\n".join(filtered_lines))
    return f"Cleared {completed_count} completed task(s)"


# Create the agent with OpenRouter (using OpenAI-compatible API)
model = OpenAIModel(
    client_args={
        "api_key": settings.openrouter_api_key,
        "base_url": "https://openrouter.ai/api/v1"
    },
    model_id="openrouter/free",  # Uses free models automatically
)

agent = Agent(
    model=model,
    tools=[list_tasks, add_task, complete_task, delete_task, clear_completed_tasks],
    system_prompt="""You are a helpful Task Management Assistant. You help users manage their tasks stored in a markdown file.

Your capabilities:
- List all tasks
- Add new tasks with priority levels (high, medium, low)
- Mark tasks as completed
- Delete tasks
- Clear all completed tasks

Be friendly, concise, and proactive. When users ask to add tasks, suggest appropriate priority levels if not specified.
Always confirm actions and provide clear feedback.""",
)


def main():
    """Interactive task management assistant"""
    print("🤖 Task Management Assistant")
    print("=" * 50)
    print("I can help you manage your tasks!")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\n👋 Goodbye! Your tasks are saved in tasks.md")
                break
            
            if not user_input:
                continue
            
            # Get response from agent
            response = agent(user_input)
            print(f"\nAssistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your tasks are saved in tasks.md")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
