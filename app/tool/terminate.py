from app.tool.base import BaseTool
from app.agent.task_lifecycle import TaskLifecycleManager
from pydantic import Field, model_validator
import importlib.util


# Create a function to get the shared lifecycle instance
def get_shared_lifecycle():
    try:
        # Dynamically import the module to avoid circular imports
        module = importlib.import_module("app.tool")
        return getattr(module, "lifecycle", TaskLifecycleManager())
    except (ImportError, AttributeError):
        # If import fails or attribute doesn't exist, create a new instance
        return TaskLifecycleManager()

_TERMINATE_DESCRIPTION = """Terminate the interaction when the request is met OR if the assistant cannot proceed further with the task.
When you have finished all the tasks, call this tool to end the work."""


class Terminate(BaseTool):
    name: str = "terminate"
    description: str = _TERMINATE_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "The finish status of the interaction.",
                "enum": ["success", "failure"],
            }
        },
        "required": ["status"],
    }

    lifecycle: TaskLifecycleManager = Field(default_factory=get_shared_lifecycle, exclude=True)
    
    @model_validator(mode="after")
    def ensure_lifecycle(self) -> "Terminate":
        """Ensure the lifecycle is set"""
        if not self.lifecycle:
            self.lifecycle = get_shared_lifecycle()
        return self

    async def execute(self, status: str) -> str:
        """Finish the current execution"""
        self.lifecycle.confirm_termination()  # ⬅️ this is what you're using it for, right?
        return f"The interaction has been completed with status: {status}"
