from app.tool.base import BaseTool
from typing import Dict, Callable, Any
from app.tool.base import ToolResult 

class DynamicTool(BaseTool):
    def __init__(self, name: str, description: str, parameters: dict, function: Callable[[dict], Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
        self._function = function

    async def execute(self, **kwargs) -> ToolResult:
        try:
            result = await self._function(kwargs)
            return ToolResult(output=result)
        except Exception as e:
            return ToolResult(output=str(e), error=str(e))