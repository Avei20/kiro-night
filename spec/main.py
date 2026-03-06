"""Task Management Assistant - CLI Entry Point."""

import sys
import logging

from task_assistant.config import load_config
from task_assistant.store import TaskStore
from task_assistant.manager import TaskManager
from task_assistant.agent import create_agent, run_agent
from task_assistant.exceptions import ConfigurationError

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the Task Management Assistant.
    
    Initializes all components and starts the interactive agent loop:
    1. Loads configuration from environment
    2. Initializes task store and ensures file exists
    3. Creates task manager with the store
    4. Creates and configures the Strands agent
    5. Starts the interactive conversation loop
    
    Handles errors gracefully with helpful messages and ensures clean exit.
    """
    try:
        # Load configuration
        config = load_config()
        
        # Initialize task store
        task_store = TaskStore(config.task_file_path)
        task_store.ensure_file_exists()
        
        # Initialize task manager
        task_manager = TaskManager(task_store)
        
        # Create agent
        agent = create_agent(config, task_manager)
        
        # Start interactive loop
        run_agent(agent)
        
    except ConfigurationError as e:
        # Handle configuration errors with helpful message
        print(f"\n❌ Configuration Error:\n{e}\n", file=sys.stderr)
        sys.exit(1)
        
    except KeyboardInterrupt:
        # Handle user interruption gracefully
        print("\n\n👋 Goodbye! Your tasks have been saved.", file=sys.stderr)
        sys.exit(0)
        
    except Exception as e:
        # Handle unexpected errors with logging
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
        print(
            f"\n❌ An unexpected error occurred: {e}\n"
            f"Please check the logs for more details.\n",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

