import asyncio
import argparse
import sys
from pathlib import Path

from app.agent.manus import Manus
from app.agent.task_persistence import TaskPersistenceManager
from app.logger import logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Manus AI Assistant")
    
    # Add task management arguments
    task_group = parser.add_argument_group("Task Management")
    task_group.add_argument("--resume", metavar="TASK_ID", help="Resume a previously saved task")
    task_group.add_argument("--list-tasks", action="store_true", help="List all saved tasks")
    task_group.add_argument("--delete-task", metavar="TASK_ID", help="Delete a saved task")
    
    return parser.parse_args()


async def list_tasks():
    """List all saved tasks."""
    persistence_manager = TaskPersistenceManager()
    tasks = persistence_manager.list_tasks()
    
    if not tasks:
        print("No saved tasks found.")
        return
    
    print("Saved Tasks:")
    print("-" * 80)
    for i, task in enumerate(tasks, 1):
        print(f"{i}. Task ID: {task['task_id']}")
        print(f"   Created: {task['timestamp']}")
        print(f"   Agent: {task['agent_name']}")
        print(f"   Messages: {task['messages']}")
        print(f"   State: {task['state']}")
        print("-" * 80)


async def delete_task(task_id):
    """Delete a saved task."""
    persistence_manager = TaskPersistenceManager()
    success = persistence_manager.delete_task(task_id)
    
    if success:
        print(f"Task {task_id} deleted successfully.")
    else:
        print(f"Failed to delete task {task_id}.")


async def resume_task(task_id):
    """Resume a previously saved task."""
    agent = Manus()
    persistence_manager = TaskPersistenceManager()
    
    success = persistence_manager.load_task(task_id, agent)
    if not success:
        print(f"Failed to resume task {task_id}.")
        return
    
    print(f"Resumed task {task_id}. Continuing where you left off...")
    
    # Continue with the interactive loop
    await interactive_loop(agent)


async def interactive_loop(agent=None):
    """Run the interactive command loop."""
    if agent is None:
        agent = Manus()
        
    while True:
        try:
            prompt = input("Enter your prompt (or 'exit'/'quit' to quit): ")
            prompt_lower = prompt.lower()
            
            if prompt_lower in ["exit", "quit"]:
                logger.info("Goodbye!")
                break
                
            if not prompt.strip():
                logger.warning("Skipping empty prompt.")
                continue
                
            # Check for special commands
            if prompt_lower.startswith("save task"):
                # Extract task ID if provided
                parts = prompt_lower.split(maxsplit=2)
                task_id = parts[2] if len(parts) > 2 else None
                
                # Save the task
                persistence_manager = TaskPersistenceManager()
                saved_task_id = persistence_manager.save_task(agent, task_id)
                print(f"Task saved with ID: {saved_task_id}")
                continue
                
            if prompt_lower == "list tasks":
                await list_tasks()
                continue
                
            if prompt_lower.startswith("resume task"):
                # Extract task ID
                parts = prompt_lower.split(maxsplit=2)
                if len(parts) < 3:
                    print("Please specify a task ID to resume.")
                    continue
                    
                task_id = parts[2]
                await resume_task(task_id)
                break  # Break out of this loop as resume_task will start a new loop
                
            if prompt_lower.startswith("delete task"):
                # Extract task ID
                parts = prompt_lower.split(maxsplit=2)
                if len(parts) < 3:
                    print("Please specify a task ID to delete.")
                    continue
                    
                task_id = parts[2]
                await delete_task(task_id)
                continue
                
            # Process normal prompt
            logger.warning("Processing your request...")
            await agent.run(prompt)
            
        except KeyboardInterrupt:
            logger.warning("Goodbye!")
            break


async def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Handle command line arguments
    if args.list_tasks:
        await list_tasks()
        return
        
    if args.delete_task:
        await delete_task(args.delete_task)
        return
        
    if args.resume:
        await resume_task(args.resume)
        return
    
    # No special arguments, run the interactive loop
    await interactive_loop()


if __name__ == "__main__":
    asyncio.run(main())
