"""Test script for task persistence functionality."""
import asyncio
import os
from pathlib import Path

from app.agent.manus import Manus
from app.agent.task_persistence import TaskPersistenceManager
from app.logger import logger


async def test_save_and_resume():
    """Test saving and resuming a task."""
    # Create tasks directory if it doesn't exist
    tasks_dir = Path("tasks")
    tasks_dir.mkdir(exist_ok=True)
    
    # Create a new agent
    agent = Manus()
    
    # Run a simple task
    logger.info("Running initial task...")
    await agent.run("What is the current time?")
    
    # Save the task
    persistence_manager = TaskPersistenceManager()
    task_id = persistence_manager.save_task(agent)
    logger.info(f"Task saved with ID: {task_id}")
    
    # Create a new agent
    new_agent = Manus()
    
    # Resume the task
    logger.info(f"Resuming task with ID: {task_id}")
    success = persistence_manager.load_task(task_id, new_agent)
    
    if success:
        logger.info("Task resumed successfully!")
        logger.info(f"Agent has {len(new_agent.messages)} messages in memory")
        
        # Continue the task
        logger.info("Continuing the task...")
        await new_agent.run("What is the weather like today?")
    else:
        logger.error("Failed to resume task!")


async def test_list_tasks():
    """Test listing saved tasks."""
    persistence_manager = TaskPersistenceManager()
    tasks = persistence_manager.list_tasks()
    
    logger.info(f"Found {len(tasks)} saved tasks:")
    for i, task in enumerate(tasks, 1):
        logger.info(f"{i}. Task ID: {task['task_id']}")
        logger.info(f"   Created: {task['timestamp']}")
        logger.info(f"   Agent: {task['agent_name']}")
        logger.info(f"   Messages: {task['messages']}")
        logger.info(f"   State: {task['state']}")


async def main():
    """Run the tests."""
    logger.info("Testing task persistence functionality...")
    
    # Test saving and resuming a task
    await test_save_and_resume()
    
    # Test listing tasks
    await test_list_tasks()
    
    logger.info("Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())