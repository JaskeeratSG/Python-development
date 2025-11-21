"""Search tools using Tavily and Serper APIs."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool
from tavily import TavilyClient

from config.settings import settings


class TavilySearchTool:
    """Tavily search tool for web searches."""
    
    def __init__(self):
        """Initialize Tavily client."""
        api_key = settings.get_api_key("tavily")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        self.client = TavilyClient(api_key=api_key)
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic"
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search using Tavily.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            search_depth: Search depth ("basic" or "advanced")
        
        Returns:
            List of search results with title, url, content, and score
        """
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date"),
                    "source": "tavily",
                    "timestamp": datetime.now().isoformat()
                })
            
            return results
            
        except Exception as e:
            print(f"Tavily search error: {str(e)}")
            return []


# Create a LangChain tool wrapper for Tavily
def create_tavily_search_tool() -> Any:
    """Create a LangChain tool for Tavily search."""
    tavily_client = TavilySearchTool()
    
    @tool
    def tavily_search(query: str, max_results: int = 5) -> str:
        """
        Search the web for current information using Tavily.
        
        Use this tool when you need to find:
        - Current events or news
        - Latest information about a topic
        - Real-time data that LLMs might not have
        
        Args:
            query: The search query
            max_results: Maximum number of results (default: 5)
        
        Returns:
            Formatted string with search results
        """
        results = tavily_client.search(query, max_results=max_results)
        
        if not results:
            return "No results found."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. {result['title']}\n"
                f"   URL: {result['url']}\n"
                f"   Content: {result['content'][:200]}...\n"
            )
        
        return "\n".join(formatted_results)
    
    return tavily_search

