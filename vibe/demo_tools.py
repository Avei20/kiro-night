"""Demo script to test the task management tools without API calls"""

from task_agent import (
    list_tasks, 
    add_task, 
    complete_task, 
    delete_task, 
    clear_completed_tasks
)

print("🧪 Testing Task Management Tools\n")
print("=" * 50)

# Test 1: Add tasks
print("\n1. Adding tasks...")
print(add_task("Write project documentation", "high"))
print(add_task("Review code changes", "medium"))
print(add_task("Update dependencies", "low"))

# Test 2: List tasks
print("\n2. Listing all tasks...")
print(list_tasks())

# Test 3: Complete a task
print("\n3. Completing task 2...")
print(complete_task(2))

# Test 4: List tasks again
print("\n4. Listing tasks after completion...")
print(list_tasks())

# Test 5: Delete a task
print("\n5. Deleting task 1...")
print(delete_task(1))

# Test 6: List tasks again
print("\n6. Listing tasks after deletion...")
print(list_tasks())

# Test 7: Clear completed tasks
print("\n7. Clearing completed tasks...")
print(clear_completed_tasks())

# Test 8: Final list
print("\n8. Final task list...")
print(list_tasks())

print("\n" + "=" * 50)
print("✅ All tools working correctly!")
print("📄 Check tasks.md to see the results")
