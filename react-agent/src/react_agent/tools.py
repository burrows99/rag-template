"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast
import sys
import os

from langchain_tavily import TavilySearch
from langgraph.runtime import get_runtime

from react_agent.context import Context

# # Add the cognee tools directory to the path
# cognee_tools_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../cognee_tools'))
# if cognee_tools_path not in sys.path:
#     sys.path.insert(0, cognee_tools_path)

# # Import cognee tools from the copied cognee_tools directory
# from tools import add_tool, search_tool


async def search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    runtime = get_runtime(Context)
    wrapped = TavilySearch(max_results=runtime.context.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


TOOLS: List[Callable[..., Any]] = [search]  # , add_tool, search_tool]
