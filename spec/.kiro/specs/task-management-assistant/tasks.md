# Implementation Plan: Task Management Assistant

## Overview

This plan implements a conversational AI task management assistant using the Strands Python library with OpenRouter integration. The system stores tasks in a markdown file and provides natural language interaction through a CLI interface. Implementation follows a bottom-up approach, building core components first and integrating them into the agent system.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create pyproject.toml with UV package manager configuration
  - Add dependencies: strands, pydantic, pydantic-settings, python-dotenv
  - Create .env.example file with required environment variables
  - Create main project directory structure
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 2. Implement configuration management
  - [x] 2.1 Create Settings model with Pydantic
    - Define Settings class with openrouter_api_key, task_file_path, and default_model fields
    - Configure SettingsConfigDict for .env file loading
    - Add field validation and default values
    - _Requirements: 1.1, 1.2, 9.1_
  
  - [x] 2.2 Implement load_config function
    - Create function to instantiate and return Settings
    - Handle ValidationError with descriptive error messages
    - _Requirements: 1.1, 1.4, 9.4_

- [x] 3. Implement Task data model
  - Create Task class with Pydantic BaseModel
  - Add fields: id, description, completed, created_at
  - Implement to_markdown() method for serialization
  - Implement from_markdown() classmethod for parsing
  - Add field validators for description (min_length=1)
  - _Requirements: 10.1, 10.2, 10.3, 10.5_

- [ ] 4. Implement Task Store
  - [x] 4.1 Create TaskStore class initialization
    - Accept file_path parameter in __init__
    - Store file path as instance variable
    - _Requirements: 2.1, 9.3_
  
  - [x] 4.2 Implement ensure_file_exists method
    - Check if markdown file exists
    - Create file with header if it doesn't exist
    - Handle file system errors gracefully
    - _Requirements: 9.3_
  
  - [x] 4.3 Implement read_tasks method
    - Read markdown file content
    - Parse each line using Task.from_markdown()
    - Return list of Task objects
    - Handle empty files and malformed lines
    - _Requirements: 2.1, 4.1, 4.2, 4.4, 10.5_
  
  - [x] 4.4 Implement write_tasks method
    - Accept list of Task objects
    - Convert each task to markdown using to_markdown()
    - Write to file with proper formatting
    - Ensure atomic write operation
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 5. Implement Task Manager
  - [x] 5.1 Create TaskManager class initialization
    - Accept TaskStore instance in __init__
    - Store task_store as instance variable
    - _Requirements: 3.4, 4.1_
  
  - [x] 5.2 Implement create_task method
    - Generate unique task ID (e.g., task-001, task-002)
    - Create Task object with provided description
    - Load existing tasks, append new task, write back
    - Return created Task object
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.3 Implement get_all_tasks method
    - Call task_store.read_tasks()
    - Return list of all tasks
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 5.4 Implement find_task method
    - Accept task_id parameter
    - Search through tasks for matching ID
    - Return Task object or None
    - _Requirements: 5.1, 6.1_
  
  - [x] 5.5 Implement update_task method
    - Find task by ID using find_task
    - Raise TaskNotFoundError if not found
    - Update specified task attributes
    - Write updated task list back to storage
    - Return updated Task object
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 5.6 Implement delete_task method
    - Find task by ID
    - Raise TaskNotFoundError if not found
    - Remove task from list
    - Write updated task list back to storage
    - Return True on success
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6. Checkpoint - Verify core components
  - Ensure all core classes are implemented correctly
  - Verify TaskStore can read/write markdown files
  - Verify TaskManager CRUD operations work
  - Ask the user if questions arise

- [ ] 7. Implement Strands agent tools
  - [x] 7.1 Create create_task_tool function
    - Define tool function that accepts description parameter
    - Call task_manager.create_task()
    - Return success message with task ID
    - Handle errors and return error messages
    - _Requirements: 3.1, 3.2, 3.5, 8.5_
  
  - [x] 7.2 Create list_tasks_tool function
    - Define tool function with no parameters
    - Call task_manager.get_all_tasks()
    - Format tasks for display
    - Handle empty task list case
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 7.3 Create update_task_tool function
    - Define tool function with task_id and optional update parameters
    - Call task_manager.update_task()
    - Return success message
    - Handle TaskNotFoundError and return appropriate message
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.5_
  
  - [x] 7.4 Create delete_task_tool function
    - Define tool function with task_id parameter
    - Call task_manager.delete_task()
    - Return success message
    - Handle TaskNotFoundError and return appropriate message
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 8.5_

- [ ] 8. Implement agent initialization
  - [x] 8.1 Create create_agent function
    - Accept Settings and TaskManager parameters
    - Initialize OpenRouter provider with API key and model
    - Create Strands Agent with system prompt
    - Register all tool functions with the agent
    - Return configured Agent instance
    - _Requirements: 1.2, 1.3, 8.2, 9.2_
  
  - [x] 8.2 Create run_agent function
    - Accept Agent instance
    - Start agent's interactive conversation loop
    - Handle user interrupts (Ctrl+C) gracefully
    - _Requirements: 8.1, 8.3_

- [ ] 9. Implement CLI interface
  - [x] 9.1 Create main function
    - Load configuration using load_config()
    - Initialize TaskStore with config.task_file_path
    - Call task_store.ensure_file_exists()
    - Initialize TaskManager with TaskStore
    - Create agent using create_agent()
    - Call run_agent() to start interactive loop
    - _Requirements: 9.1, 9.2, 9.3, 9.5_
  
  - [x] 9.2 Add error handling to main function
    - Catch ConfigurationError and display helpful message
    - Catch other exceptions and log errors
    - Ensure graceful exit on all error paths
    - _Requirements: 9.4, 8.5_
  
  - [x] 9.3 Add __main__ entry point
    - Create if __name__ == "__main__" block
    - Call main() function
    - _Requirements: 9.5_

- [x] 10. Create example files and documentation
  - Create .env.example with OPENROUTER_API_KEY placeholder
  - Create README.md with setup and usage instructions
  - Document how to install dependencies with UV
  - Document how to run the application
  - _Requirements: 1.1, 7.1, 8.1_

- [x] 11. Final checkpoint - Integration verification
  - Ensure all components are wired together correctly
  - Verify agent can perform all CRUD operations
  - Verify error handling works throughout the system
  - Ask the user if questions arise

## Notes

- Implementation uses Python 3.11+ with type hints throughout
- UV package manager is used for dependency management
- All configuration is loaded from .env file using Pydantic
- Tasks are stored in markdown format for human readability
- Natural language interaction is handled by Strands + OpenRouter
- Error handling provides descriptive messages at all layers
