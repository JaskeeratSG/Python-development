"""Main entry point for the intelligent agent system."""

from graph.agent_graph import AgentGraph
from config.settings import settings


def initialize_agent_system():
    """
    Initialize and validate the agent system.
    
    Returns:
        AgentGraph instance if successful, None otherwise
    
    Raises:
        ValueError: If configuration validation fails
    """
    # Validate settings
    settings.validate()
    
    # Create the agent graph
    agent_graph = AgentGraph()
    
    return agent_graph


def process_query(agent_graph: AgentGraph, query: str):
    """
    Process a query through the agent system.
    
    Args:
        agent_graph: Initialized AgentGraph instance
        query: User query string
    
    Returns:
        AgentState with results
    
    Raises:
        Exception: If processing fails
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    return agent_graph.run(query.strip())


if __name__ == "__main__":
    # For CLI usage (if needed)
    try:
        agent_graph = initialize_agent_system()
        print("Agent system initialized successfully")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Initialization error: {e}")

