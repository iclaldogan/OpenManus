import asyncio
from typing import List

from googlesearch import search

from app.tool.base import BaseTool
import asyncio
from typing import List

from googlesearch import search

from app.tool.base import BaseTool
from app.tool.base import ToolResult



class GoogleSearch(BaseTool):
    name: str = "google_search"
    description: str = """Perform a Google search and return a list of relevant links.
Use this tool when you need to find information on the web, get up-to-date data, or research specific topics.
The tool returns a list of URLs that match the search query.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) The search query to submit to Google.",
            },
            "num_results": {
                "type": "integer",
                "description": "(optional) The number of search results to return. Default is 10.",
                "default": 10,
            },
        },
        "required": ["query"],
    }

    async def execute(self, **kwargs) -> ToolResult:
        if not kwargs:
            return ToolResult(output="Error: No parameters received", error="Missing params")

        query = kwargs.get("query")
        num_results = kwargs.get("num_results", 10)

        if not query:
            return ToolResult(output="Missing 'query' parameter", error="Missing query")

        loop = asyncio.get_event_loop()
        links = await loop.run_in_executor(None, lambda: list(search(query, num_results=num_results)))

        return ToolResult(output="\n".join(links))
