"""State schema for the multi-agent LangGraph system."""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State structure that flows through the multi-agent system.
    
    This state is passed between agents and contains all necessary
    information for processing user queries.
    """
    
    # User's original query
    query: str
    
    # Messages in the conversation (for LLM context)
    messages: List[BaseMessage]
    
    # Context accumulated from agents
    context: str
    
    # Search results from web searches
    results: List[Dict[str, Any]]
    
    # Metadata about the processing
    metadata: Dict[str, Any]
    
    # Current agent working on the task
    current_agent: Optional[str]
    
    # Agent execution history
    agent_history: List[Dict[str, Any]]
    
    # Final response to user
    response: Optional[str]
    
    # Data freshness information
    data_freshness: Dict[str, Any]
    
    # Timestamps
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    # Error information (if any)
    error: Optional[str]


def create_initial_state(query: str) -> AgentState:
    """
    Create initial state for a new query.
    
    Args:
        query: User's query string
    
    Returns:
        Initialized AgentState
    """
    from datetime import datetime
    
    return AgentState(
        query=query,
        messages=[],
        context="",
        results=[],
        metadata={},
        current_agent=None,
        agent_history=[],
        response=None,
        data_freshness={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        error=None
    )

