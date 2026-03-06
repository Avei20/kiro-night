# Task Management Assistant

An AI-powered task management assistant built with Strands SDK and OpenRouter.

## Features

- 📝 Add tasks with priority levels (high, medium, low)
- ✅ Mark tasks as completed
- 🗑️ Delete individual tasks
- 🧹 Clear all completed tasks
- 📋 List all tasks
- 💾 Single markdown file as source of truth (`tasks.md`)

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure your OpenRouter API key in `.env`:
```
OPENROUTER_API_KEY=your_key_here
```

Get your API key at: https://openrouter.ai/keys

Note: The included key has reached its limit. You'll need to add your own key to use the AI agent.

## Usage

### Interactive AI Assistant

Run the interactive assistant (requires valid API key):
```bash
uv run python task_agent.py
```

### Demo Mode (No API Required)

Test the task management tools without API calls:
```bash
uv run python demo_tools.py
```

### Example Commands

When using the AI assistant, you can say:
- "Add a task to review the project documentation with high priority"
- "Show me all my tasks"
- "Mark task 1 as completed"
- "Delete task 3"
- "Clear all completed tasks"

## How It Works

The assistant uses:
- **Strands SDK**: For building the AI agent with tool-calling capabilities
- **OpenRouter**: As the AI provider (OpenAI-compatible API)
- **Pydantic Settings**: For loading API keys from `.env` file
- **tasks.md**: Single markdown file storing all tasks

All tasks are stored in `tasks.md` in a simple markdown checklist format with priority tags.

## Project Structure

```
.
├── task_agent.py      # Main AI agent with interactive mode
├── demo_tools.py      # Demo script to test tools without API
├── test_agent.py      # Simple agent test script
├── tasks.md           # Task storage (auto-generated)
├── .env               # API key configuration
└── pyproject.toml     # Project dependencies
```
