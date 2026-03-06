# Task Management Assistant

An AI-powered task management assistant built with Strands Python library and OpenRouter.

## Features

- Natural language task management through conversational AI
- Simple markdown file storage for tasks
- Create, read, update, and delete tasks via conversation
- Powered by OpenRouter's AI models

## Setup

### Prerequisites

- Python 3.11 or higher
- UV package manager
- OpenRouter API key

### Installation

1. Clone the repository
2. Install dependencies using UV:
   ```bash
   uv sync
   ```

3. Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the assistant:
```bash
python main.py
```

Then interact with the assistant using natural language:
- "Create a task to buy groceries"
- "Show me all my tasks"
- "Mark task-001 as complete"
- "Delete the grocery task"

## Project Structure

```
task-management-assistant/
├── task_assistant/          # Main package
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── models.py           # Task data models
│   ├── store.py            # Markdown file storage
│   ├── manager.py          # Task CRUD operations
│   ├── agent.py            # Strands agent and tools
│   └── exceptions.py       # Custom exceptions
├── main.py                 # CLI entry point
├── tasks.md                # Task storage (created automatically)
├── .env                    # Environment variables (not in git)
└── .env.example            # Example environment file
```

## Configuration

Configuration is managed through environment variables in the `.env` file:

- `OPENROUTER_API_KEY` (required): Your OpenRouter API key
- `TASK_FILE_PATH` (optional): Path to task storage file (default: tasks.md)
- `DEFAULT_MODEL` (optional): OpenRouter model to use (default: openrouter/free)

## License

MIT
