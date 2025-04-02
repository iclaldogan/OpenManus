from app.tool.base import BaseTool, ToolResult
from typing import Dict, Callable, Any

class ToolFactory:
    def __init__(self):
        self.tools = {}

    def create_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: Callable,
    ) -> BaseTool:
        class DynamicTool(BaseTool):
            name = name
            description = description
            parameters = {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys()),
            }

            async def execute(self, **kwargs) -> ToolResult:
                try:
                    result = function(**kwargs)
                    return ToolResult(output=result)
                except Exception as e:
                    return ToolResult(output=str(e), error=str(e))

        return DynamicTool()

    def get_tool(self, name):
        return self.tools.get(name)
