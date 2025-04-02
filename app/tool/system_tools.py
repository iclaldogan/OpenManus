import os
import psutil
import pyautogui
import pyttsx3
import subprocess
from datetime import datetime

from app.tool.base import BaseTool, ToolResult

import ctypes
import requests


class GetSystemStats(BaseTool):
    name : str = "get_system_stats"
    description : str = "Returns CPU and RAM usage stats."

    async def execute(self, **kwargs):
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            return ToolResult(output=f"CPU Usage: {cpu}% | RAM Usage: {ram}%")
        except Exception as e:
            return ToolResult(error=str(e))


class TakeScreenshot(BaseTool):
    name : str = "take_screenshot"
    description : str = "Takes a screenshot and saves it to the local directory."

    async def execute(self, **kwargs):
        try:
            path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(path)
            return ToolResult(output=f"Screenshot saved as {path}")
        except Exception as e:
            return ToolResult(error=str(e))


class SayText(BaseTool):
    name: str = "say_text"
    description: str = "Uses text-to-speech to say the given text."
    parameters: dict = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to speak aloud"},
        },
        "required": ["text"],
    }


    async def execute(self, text: str, **kwargs):
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return ToolResult(output=f"Said: {text}")
        except Exception as e:
            return ToolResult(error=str(e))


class OpenApp(BaseTool):
    name: str = "open_app"
    description: str = "Opens a desktop app. Example: notepad, calc, chrome"
    parameters: dict = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "The app to open"
            },
        },
        "required": ["app_name"],
    }

    async def execute(self, app_name: str, **kwargs):
        try:
            subprocess.Popen(app_name)
            return ToolResult(output=f"Opened {app_name}")
        except Exception as e:
            return ToolResult(error=str(e))



class LockPC(BaseTool):
    name : str = "lock_pc"
    description : str = "Locks the computer screen."

    async def execute(self, **kwargs):
        try:
            ctypes = __import__('ctypes')
            ctypes.windll.user32.LockWorkStation()
            return ToolResult(output="PC locked.")
        except Exception as e:
            return ToolResult(error=str(e))



class SetWallpaper(BaseTool):
    name: str = "set_wallpaper"
    description: str = "Downloads an image from a given URL and sets it as the desktop wallpaper."
    parameters: dict = {
        "type": "object",
        "properties": {
            "image_url": {
                "type": "string",
                "description": "Direct URL to the image you want as wallpaper"
            },
        },
        "required": ["image_url"],
    }

    async def execute(self, image_url: str, **kwargs):
        try:
            img_path = os.path.join(os.getcwd(), "wallpaper.jpg")
            response = requests.get(image_url)
            with open(img_path, "wb") as f:
                f.write(response.content)

            # Set wallpaper
            ctypes.windll.user32.SystemParametersInfoW(20, 0, img_path, 3)

            return ToolResult(output=f"Wallpaper set from {image_url}")
        except Exception as e:
            return ToolResult(error=str(e))
