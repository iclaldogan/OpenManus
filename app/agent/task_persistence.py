"""Task persistence module for saving and loading agent state."""
import json
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from app.logger import logger
from app.schema import AgentState, Memory, Message


class TaskSnapshot(BaseModel):
    """Snapshot of an agent's state for persistence."""
    
    task_id: str
    timestamp: str
    agent_name: str
    messages: List[Dict]
    current_step: int
    max_steps: int
    state: str
    metadata: Dict = {}
    
    @classmethod
    def from_agent(cls, agent, task_id: Optional[str] = None):
        """Create a snapshot from an agent instance."""
        if task_id is None:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        return cls(
            task_id=task_id,
            timestamp=datetime.now().isoformat(),
            agent_name=agent.name,
            messages=[msg.to_dict() for msg in agent.messages],
            current_step=agent.current_step,
            max_steps=agent.max_steps,
            state=agent.state.value,
            metadata={
                "description": getattr(agent, "description", None),
                "system_prompt": getattr(agent, "system_prompt", None),
                "next_step_prompt": getattr(agent, "next_step_prompt", None),
            }
        )


class TaskPersistenceManager:
    """Manager for saving and loading agent state."""
    
    def __init__(self, storage_dir: Union[str, Path] = "tasks"):
        """Initialize the task persistence manager.
        
        Args:
            storage_dir: Directory to store task snapshots
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        
    def save_task(self, agent, task_id: Optional[str] = None) -> str:
        """Save agent state to disk.
        
        Args:
            agent: The agent instance to save
            task_id: Optional task ID, will be generated if not provided
            
        Returns:
            The task ID
        """
        snapshot = TaskSnapshot.from_agent(agent, task_id)
        task_id = snapshot.task_id
        
        # Save as JSON for human readability
        json_path = self.storage_dir / f"{task_id}.json"
        with open(json_path, "w") as f:
            f.write(snapshot.model_dump_json(indent=2))
            
        # Also save as pickle for more reliable restoration
        pickle_path = self.storage_dir / f"{task_id}.pkl"
        with open(pickle_path, "wb") as f:
            pickle.dump(snapshot, f)
            
        logger.info(f"Task saved: {task_id}")
        return task_id
    
    def load_task(self, task_id: str, agent):
        """Load agent state from disk.
        
        Args:
            task_id: The task ID to load
            agent: The agent instance to restore state to
            
        Returns:
            True if successful, False otherwise
        """
        pickle_path = self.storage_dir / f"{task_id}.pkl"
        if not pickle_path.exists():
            logger.error(f"Task not found: {task_id}")
            return False
            
        try:
            with open(pickle_path, "rb") as f:
                snapshot = pickle.load(f)
                
            # Restore agent state
            agent.current_step = snapshot.current_step
            agent.max_steps = snapshot.max_steps
            agent.state = AgentState(snapshot.state)
            
            # Restore messages
            memory = Memory()
            for msg_dict in snapshot.messages:
                msg = Message(**msg_dict)
                memory.add_message(msg)
            agent.memory = memory
            
            # Restore metadata if applicable
            if snapshot.metadata.get("system_prompt"):
                agent.system_prompt = snapshot.metadata["system_prompt"]
            if snapshot.metadata.get("next_step_prompt"):
                agent.next_step_prompt = snapshot.metadata["next_step_prompt"]
                
            logger.info(f"Task loaded: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading task {task_id}: {str(e)}")
            return False
            
    def list_tasks(self):
        """List all saved tasks.
        
        Returns:
            List of task IDs and timestamps
        """
        tasks = []
        for path in self.storage_dir.glob("*.json"):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    tasks.append({
                        "task_id": data.get("task_id"),
                        "timestamp": data.get("timestamp"),
                        "agent_name": data.get("agent_name"),
                        "messages": len(data.get("messages", [])),
                        "state": data.get("state")
                    })
            except Exception as e:
                logger.error(f"Error reading task file {path}: {str(e)}")
                
        return sorted(tasks, key=lambda x: x.get("timestamp", ""), reverse=True)
        
    def delete_task(self, task_id: str) -> bool:
        """Delete a saved task.
        
        Args:
            task_id: The task ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        json_path = self.storage_dir / f"{task_id}.json"
        pickle_path = self.storage_dir / f"{task_id}.pkl"
        
        success = True
        if json_path.exists():
            try:
                os.remove(json_path)
            except Exception as e:
                logger.error(f"Error deleting task JSON {task_id}: {str(e)}")
                success = False
                
        if pickle_path.exists():
            try:
                os.remove(pickle_path)
            except Exception as e:
                logger.error(f"Error deleting task pickle {task_id}: {str(e)}")
                success = False
                
        return success