from app.tool.base import BaseTool
from app.tool.bash import Bash
from app.tool.create_chat_completion import CreateChatCompletion
from app.tool.planning import PlanningTool
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.tool_collection import ToolCollection
from app.tool.set_wallpaper_from_base64 import SetWallpaperFromBase64
from app.tool.set_wallpaper_from_url import SetWallpaperFromURL
from app.agent.task_lifecycle import TaskLifecycleManager

from app.tool.system_tools import (
    GetSystemStats,
    TakeScreenshot,
    SayText,
    OpenApp,
    LockPC,
    SetWallpaper,
)

from app.tool.get_os_info import GetOSInfo
from app.tool.terminate import Terminate

# Import task persistence tools
from app.tool.task_persistence_tools import (
    SaveTask,
    ListTasks,
    ResumeTask,
    DeleteTask,
)

# Import computer control tools
from app.tool.computer_control_tools import (
    SystemInfo,
    ListRunningProcesses,
    MonitorSystem,
    FileSystemExplorer,
)

__all__ = [
    "BaseTool",
    "Bash",
    "Terminate",
    "StrReplaceEditor",
    "ToolCollection",
    "CreateChatCompletion",
    "PlanningTool",
    "GetSystemStats",
    "TakeScreenshot",
    "SayText",
    "OpenApp",
    "LockPC",
    # Task persistence tools
    "SaveTask",
    "ListTasks",
    "ResumeTask",
    "DeleteTask",
    # Computer control tools
    "SystemInfo",
    "ListRunningProcesses",
    "MonitorSystem",
    "FileSystemExplorer",
]

# ✅ Step 1: Create the shared lifecycle instance
lifecycle = TaskLifecycleManager()

# ✅ Step 2: Create the tools, including Terminate(lifecycle)
tools = ToolCollection(
    # Basic tools
    Bash(),
    CreateChatCompletion(),
    PlanningTool(),
    StrReplaceEditor(),
    
    # System tools
    GetSystemStats(),
    TakeScreenshot(),
    SayText(),
    OpenApp(),
    LockPC(),
    SetWallpaper(),
    GetOSInfo(),
    SetWallpaperFromBase64(),
    SetWallpaperFromURL(),
    
    # Task persistence tools
    SaveTask(),
    ListTasks(),
    ResumeTask(),
    DeleteTask(),
    
    # Computer control tools
    SystemInfo(),
    ListRunningProcesses(),
    MonitorSystem(),
    FileSystemExplorer(),
    
    # Special tools
    Terminate(lifecycle=lifecycle),
)
