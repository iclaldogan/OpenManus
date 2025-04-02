"""Tools for task persistence and resumption."""
import os
from typing import Dict, List, Optional

from app.agent.task_persistence import TaskPersistenceManager
from app.logger import logger
from app.tool.base import BaseTool, ToolResult


class SaveTask(BaseTool):
    """Tool for saving the current task state."""
    
    name: str = "save_task"
    description: str = "Save the current task state for later resumption"
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "Optional task ID. If not provided, a new ID will be generated."
            },
            "description": {
                "type": "string",
                "description": "Optional description of the task for easier identification."
            }
        },
        "required": []
    }
    
    def __init__(self):
        super().__init__()
        self.persistence_manager = TaskPersistenceManager()
        
    async def execute(
        self, task_id: Optional[str] = None, description: Optional[str] = None
    ) -> ToolResult:
        """Save the current task state.
        
        Args:
            task_id: Optional task ID
            description: Optional task description
            
        Returns:
            ToolResult with the task ID
        """
        try:
            # Get the agent from the context
            from app.agent.manus import Manus
            agent = Manus()
            
            # Add description to metadata if provided
            if description:
                agent.description = description
                
            # Save the task
            saved_task_id = self.persistence_manager.save_task(agent, task_id)
            
            return ToolResult(
                output=f"Task saved successfully with ID: {saved_task_id}"
            )
        except Exception as e:
            logger.error(f"Error saving task: {str(e)}")
            return ToolResult(
                output=f"Error saving task: {str(e)}"
            )


class ListTasks(BaseTool):
    """Tool for listing saved tasks."""
    
    name: str = "list_tasks"
    description: str = "List all saved tasks that can be resumed"
    
    parameters: Dict = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    def __init__(self):
        super().__init__()
        self.persistence_manager = TaskPersistenceManager()
        
    async def execute(self) -> ToolResult:
        """List all saved tasks.
        
        Returns:
            ToolResult with the list of tasks
        """
        try:
            tasks = self.persistence_manager.list_tasks()
            
            if not tasks:
                return ToolResult(
                    output="No saved tasks found."
                )
                
            # Format the output
            output = "Saved tasks:\n\n"
            for i, task in enumerate(tasks, 1):
                output += f"{i}. Task ID: {task['task_id']}\n"
                output += f"   Created: {task['timestamp']}\n"
                output += f"   Agent: {task['agent_name']}\n"
                output += f"   Messages: {task['messages']}\n"
                output += f"   State: {task['state']}\n\n"
                
            return ToolResult(
                output=output
            )
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return ToolResult(
                output=f"Error listing tasks: {str(e)}"
            )


class ResumeTask(BaseTool):
    """Tool for resuming a saved task."""
    
    name: str = "resume_task"
    description: str = "Resume a previously saved task"
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to resume"
            }
        },
        "required": ["task_id"]
    }
    
    def __init__(self):
        super().__init__()
        self.persistence_manager = TaskPersistenceManager()
        
    async def execute(self, task_id: str) -> ToolResult:
        """Resume a saved task.
        
        Args:
            task_id: The ID of the task to resume
            
        Returns:
            ToolResult with the result of the operation
        """
        try:
            # Get the agent from the context
            from app.agent.manus import Manus
            agent = Manus()
            
            # Load the task
            success = self.persistence_manager.load_task(task_id, agent)
            
            if success:
                return ToolResult(
                    output=f"Task {task_id} resumed successfully. You can continue where you left off."
                )
            else:
                return ToolResult(
                    output=f"Failed to resume task {task_id}."
                )
        except Exception as e:
            logger.error(f"Error resuming task: {str(e)}")
            return ToolResult(
                output=f"Error resuming task: {str(e)}"
            )


class DeleteTask(BaseTool):
    """Tool for deleting a saved task."""
    
    name: str = "delete_task"
    description: str = "Delete a previously saved task"
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to delete"
            }
        },
        "required": ["task_id"]
    }
    
    def __init__(self):
        super().__init__()
        self.persistence_manager = TaskPersistenceManager()
        
    async def execute(self, task_id: str) -> ToolResult:
        """Delete a saved task.
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            ToolResult with the result of the operation
        """
        try:
            success = self.persistence_manager.delete_task(task_id)
            
            if success:
                return ToolResult(
                    output=f"Task {task_id} deleted successfully."
                )
            else:
                return ToolResult(
                    output=f"Failed to delete task {task_id}."
                )
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            return ToolResult(
                output=f"Error deleting task: {str(e)}"
            )