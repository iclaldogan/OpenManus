import os
import platform
import base64
from app.tool.base import BaseTool, ToolResult

class SetWallpaperFromBase64(BaseTool):
    name: str = "set_wallpaper_from_base64"
    description: str = "Decodes a base64 image, saves it as wallpaper, and sets it as desktop background."

    parameters: dict = {
        "type": "object",
        "properties": {
            "image_base64": {"type": "string", "description": "Base64-encoded image content"},
            "filename": {"type": "string", "description": "The filename to save the image as", "default": "wallpaper.png"}
        },
        "required": ["image_base64"]
    }

    async def execute(self, image_base64: str, filename: str = "wallpaper.png", **kwargs):
        try:
            # Decode and save image
            img_data = base64.b64decode(image_base64 + '===')
            with open(filename, 'wb') as f:
                f.write(img_data)

            # Set wallpaper based on OS
            system = platform.system().lower()

            if system == "windows":
                import ctypes
                abs_path = os.path.abspath(filename)
                ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
                return ToolResult(output=f"Wallpaper set on Windows using {abs_path}")
            
            elif system == "darwin":  # macOS
                os.system(f'''osascript -e 'tell application "Finder" to set desktop picture to POSIX file "{os.path.abspath(filename)}"' ''')
                return ToolResult(output=f"Wallpaper set on macOS using {filename}")

            elif system == "linux":
                os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{os.path.abspath(filename)}")
                return ToolResult(output=f"Wallpaper set on Linux using {filename}")

            return ToolResult(output=f"Image saved as {filename}, but could not auto-set wallpaper for this OS: {system}")

        except Exception as e:
            return ToolResult(error=f"Failed to set wallpaper: {str(e)}")
