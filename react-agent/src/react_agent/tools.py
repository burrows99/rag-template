"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast
import sys
import os
import asyncio

from langchain_tavily import TavilySearch
from langgraph.runtime import get_runtime

# MCP Integration - Source: https://langchain-ai.github.io/langgraph/agents/mcp/
from langchain_mcp_adapters.client import MultiServerMCPClient

from react_agent.context import Context


async def search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    runtime = get_runtime(Context)
    wrapped = TavilySearch(max_results=runtime.context.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


# Initialize MCP client for Cognee server
# Source: https://langchain-ai.github.io/langgraph/agents/mcp/#use-mcp-tools
async def get_mcp_tools():
    """Load tools from Cognee MCP server.
    
    The MCP client connects to the Cognee MCP server running locally,
    which provides cognify, search, and other knowledge graph tools.
    """
    # SSE transport uses /sse endpoint, not /mcp
    mcp_url = os.getenv("COGNEE_MCP_URL", "http://localhost:8000/sse")
    
    client = MultiServerMCPClient(
        {
            "cognee": {
                "url": mcp_url,
                "transport": "sse",
            }
        }
    )
    
    # Get tools from MCP server
    # These will include: cognify, search, prune, etc.
    return await client.get_tools()


# Load MCP tools synchronously at module initialization
# Note: In production, consider lazy loading or caching
try:
    mcp_tools = asyncio.run(get_mcp_tools())
    TOOLS: List[Callable[..., Any]] = [search] + mcp_tools
except Exception as e:
    print(f"Warning: Could not load MCP tools: {e}", file=sys.stderr)
    print("Falling back to basic tools only", file=sys.stderr)
    TOOLS: List[Callable[..., Any]] = [search]
