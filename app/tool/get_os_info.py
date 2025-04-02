import platform
from app.tool.base import BaseTool, ToolResult

class GetOSInfo(BaseTool):
    name: str = "get_os_info"
    description: str = "Returns information about the operating system."

    async def execute(self, **kwargs) -> ToolResult:
        try:
            os_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "platform": platform.platform()
            }
            return ToolResult(output=str(os_info))
        except Exception as e:
            return ToolResult(error=str(e))