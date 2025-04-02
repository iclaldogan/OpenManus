import threading
import sys
from io import StringIO
from typing import Dict

from app.tool.base import BaseTool

# 🧠 Shared global memory for all executions
PERSISTENT_GLOBALS: Dict = {"__builtins__": __builtins__}

class PythonExecute(BaseTool):
    name: str = "python_execute"
    description: str = "Executes Python code with persistent memory and timeout."
    parameters: dict = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute.",
            },
        },
        "required": ["code"],
    }

    async def execute(self, code: str, timeout: int = 5) -> Dict:
        result = {"observation": ""}

        def run_code():
            try:
                output_buffer = StringIO()
                sys.stdout = output_buffer

                exec(code, PERSISTENT_GLOBALS)

                sys.stdout = sys.__stdout__
                result["observation"] = output_buffer.getvalue()
                result["success"] = True
            except Exception as e:
                result["observation"] = str(e)
                result["success"] = False

        thread = threading.Thread(target=run_code)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            return {"observation": f"Execution timeout after {timeout} seconds", "success": False}
        return result
