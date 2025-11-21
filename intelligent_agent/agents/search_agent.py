"""Search agent for handling web search queries."""

from typing import List
from langchain_core.messages import HumanMessage, AIMessage

from agents.base_agent import BaseAgent
from graph.state_schema import AgentState
from tools.search_tools import TavilySearchTool, create_tavily_search_tool


class SearchAgent(BaseAgent):
    """
    Agent specialized in performing web searches.
    
    This agent uses Tavily to search the web for current information
    and updates the state with search results.
    """
    
    def __init__(self):
        """Initialize the search agent."""
        search_tool = create_tavily_search_tool()
        super().__init__(
            name="search_agent",
            tools=[search_tool],
            description="Searches the web for current information using Tavily"
        )
        self.tavily_client = TavilySearchTool()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process search query and update state with results.
        
        Args:
            state: Current agent state
        
        Returns:
            Updated state with search results
        """
        query = state["query"]
        
        # Perform search
        search_results = self.tavily_client.search(query, max_results=5)
        
        # Update state with results
        state["results"] = search_results
        
        # Update context with search results summary
        if search_results:
            summary = f"Found {len(search_results)} search results for: {query}\n"
            summary += "\n".join([
                f"- {r['title']} ({r['url']})" 
                for r in search_results[:3]
            ])
            self.update_context(state, summary)
            
            # Update data freshness
            state["data_freshness"] = {
                "last_updated": search_results[0].get("timestamp", ""),
                "source": "tavily",
                "result_count": len(search_results)
            }
        else:
            self.update_context(state, f"No search results found for: {query}")
        
        # Add message to conversation
        self.add_message(
            state,
            f"Search completed. Found {len(search_results)} results.",
            role="assistant"
        )
        
        return state

