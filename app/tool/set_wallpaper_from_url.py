import os
import urllib.request
import platform
from app.tool.base import BaseTool, ToolResult


class SetWallpaperFromURL(BaseTool):
    name: str = "set_wallpaper_from_url"
    description: str = "Downloads an image from a URL and sets it as the desktop wallpaper."

    parameters: dict = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Direct URL to the image file",
            },
        },
        "required": ["url"],
    }

    async def execute(self, url: str, **kwargs):
        try:
            filename = "downloaded_wallpaper.jpg"
            urllib.request.urlretrieve(url, filename)
            abs_path = os.path.abspath(filename)

            os_name = platform.system().lower()

            if "windows" in os_name:
                import ctypes
                ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
            elif "darwin" in os_name:  # macOS
                os.system(f'''osascript -e 'tell application "System Events" to set picture of every desktop to "{abs_path}"' ''')
            elif "linux" in os_name:
                os.system(f"gsettings set org.gnome.desktop.background picture-uri 'file://{abs_path}'")
            else:
                return ToolResult(error=f"Unsupported OS: {os_name}")

            return ToolResult(output="Wallpaper changed successfully.")
        except Exception as e:
            return ToolResult(error=str(e))
