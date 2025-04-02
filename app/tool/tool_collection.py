"""Collection classes for managing multiple tools."""
from typing import Any, Dict, List

from app.exceptions import ToolError
from app.tool.base import BaseTool, ToolFailure, ToolResult
from app.tool.tool_factory import ToolFactory
from app.tool.terminate import Terminate
from app.agent.task_lifecycle import TaskLifecycleManager


class ToolCollection:
    """A collection of defined and dynamic tools."""

    def __init__(self, *tools: BaseTool):
        self.dynamic_factory = ToolFactory()
        self.lifecycle = TaskLifecycleManager()
        terminate_tool = Terminate(lifecycle=self.lifecycle)
        self.tools = list(tools) + [terminate_tool]
        self.tool_map = {tool.name: tool for tool in self.tools}


    def __iter__(self):
        return iter(self.tools)

    def to_params(self) -> List[Dict[str, Any]]:
        return [tool.to_param() for tool in self.tools]

    async def execute(self, *, name: str, tool_input: Dict[str, Any] = None) -> ToolResult:
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")
        try:
            result = await tool(**tool_input)
            return result
        except ToolError as e:
            return ToolFailure(error=e.message)

    async def execute_all(self) -> List[ToolResult]:
        results = []
        for tool in self.tools:
            try:
                result = await tool()
                results.append(result)
            except ToolError as e:
                results.append(ToolFailure(error=e.message))
        return results

    def get_tool(self, name: str) -> BaseTool:
        return self.tool_map.get(name)

    def add_tool(self, tool: BaseTool):
        self.tools.append(tool)
        self.tool_map[tool.name] = tool
        return self

    def add_tools(self, *tools: BaseTool):
        for tool in tools:
            self.add_tool(tool)
        return self

    def add_dynamic_tool(self, name, description, parameters, function):
        tool = self.dynamic_factory.create_tool(name, description, parameters, function)
        self.add_tool(tool)
        return tool
