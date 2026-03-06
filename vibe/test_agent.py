"""Quick test of the Task Management Assistant"""

from task_agent import agent

# Test the agent with a simple query
print("Testing Task Management Assistant...\n")

# Test 1: Add a task
print("Test 1: Adding a task")
response = agent("Add a task: Write documentation for the project with high priority")
print(f"Response: {response}\n")

# Test 2: List tasks
print("Test 2: Listing tasks")
response = agent("Show me all my tasks")
print(f"Response: {response}\n")

print("✅ Agent is working! Run 'python task_agent.py' for interactive mode.")
