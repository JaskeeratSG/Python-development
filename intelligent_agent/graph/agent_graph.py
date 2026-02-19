"""LangGraph workflow definition for multi-agent system."""

from typing import Literal, Optional, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage

from graph.state_schema import AgentState, create_initial_state
from agents.coordinator_agent import CoordinatorAgent
from agents.search_agent import SearchAgent
from agents.planner_agent import PlannerAgent
from config.database import create_checkpointer


class AgentGraph:
    """
    LangGraph workflow for the multi-agent system.
    
    This graph orchestrates the flow between different agents
    to process user queries.
    """
    
    def __init__(self, checkpointer: Optional[Union[MemorySaver, PostgresSaver]] = None):
        """
        Initialize the agent graph.
        
        Args:
            checkpointer: Optional checkpointer for state persistence.
                         If None, creates a database checkpointer (PostgresSaver) if DATABASE_URL
                         is configured, otherwise falls back to MemorySaver for in-memory persistence.
        """
        self.coordinator = CoordinatorAgent()
        self.search_agent = SearchAgent()
        self.planner_agent = PlannerAgent()
        
        # Create checkpointer if not provided - use database if configured
        self.checkpointer = checkpointer or create_checkpointer()
        
        # Create the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("coordinator", self.coordinator.run)
        workflow.add_node("search_agent", self.search_agent.run)
        workflow.add_node("planner_agent", self.planner_agent.run)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        # Add edges - coordinator routes to appropriate agent
        workflow.add_conditional_edges(
            "coordinator",
            self._route_after_coordinator,
            {
                "planner_agent": "planner_agent",
                "search_agent": "search_agent",
                "end": END
            }
        )
        
        # After agents complete, go to response generation
        workflow.add_edge("search_agent", END)
        workflow.add_edge("planner_agent", END)
        
        # Compile the graph with checkpointer for state persistence
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _route_after_coordinator(self, state: AgentState) -> Literal["planner_agent", "search_agent", "end"]:
        """
        Route after coordinator decides.
        
        Args:
            state: Current state
        
        Returns:
            Next node name
        """
        routing_decision = state.get("metadata", {}).get("routing_decision", "")
        
        # If coordinator explicitly says "end" (for conversational queries), respect it
        if routing_decision.lower() == "end":
            return "end"
        
        # If coordinator suggests planner_agent, route there
        if "planner_agent" in routing_decision.lower():
            return "planner_agent"
        
        # If coordinator suggests search_agent, route there
        if "search_agent" in routing_decision.lower():
            return "search_agent"
        
        # Fallback: check if query needs search using LLM (but only if not already decided as "end")
        conversation_messages = state.get("messages", [])
        if self.coordinator.should_use_search(state["query"], conversation_messages):
            return "search_agent"
        
        # Default: end the workflow
        return "end"
    
    def run(
        self,
        query: str,
        thread_id: Optional[str] = None,
        config: Optional[dict] = None
    ) -> AgentState:
        """
        Execute the graph with a user query.
        
        Args:
            query: User's query string
            thread_id: Optional thread ID for conversation continuity.
                      If None, generates a new thread.
            config: Optional configuration dict with thread_id.
        
        Returns:
            Final agent state with response
        """
        # Use provided config or create new one with thread_id
        if config is None:
            config = {"configurable": {"thread_id": thread_id or "default"}}
        
        # Create initial state with the new query
        initial_state = create_initial_state(query)
        initial_state["messages"] = [HumanMessage(content=query)]
        
        # Load previous conversation messages from checkpointer for this thread_id
        # This preserves conversation history across queries with the same thread_id
        try:
            existing_checkpoint = self.graph.get_state(config)
            if existing_checkpoint and existing_checkpoint.values:
                # Get previous messages from the saved checkpoint
                previous_messages = existing_checkpoint.values.get("messages", [])
                if previous_messages:
                    # Prepend previous conversation history to maintain context
                    # The new query is already added above
                    initial_state["messages"] = previous_messages + [HumanMessage(content=query)]
        except Exception:
            # If checkpoint doesn't exist or loading fails, start fresh
            # This is normal for new conversations
            pass
        
        # Run the graph with config for state persistence
        final_state = self.graph.invoke(initial_state, config=config)
        
        return final_state
    
    def stream(
        self,
        query: str,
        thread_id: Optional[str] = None,
        config: Optional[dict] = None
    ):
        """
        Stream the graph execution for real-time updates.
        
        Args:
            query: User's query string
            thread_id: Optional thread ID for conversation continuity
            config: Optional configuration dict with thread_id
        
        Yields:
            State updates as they occur
        """
        # Use provided config or create new one with thread_id
        if config is None:
            config = {"configurable": {"thread_id": thread_id or "default"}}
        
        # Try to get existing state for conversation continuity
        try:
            existing_state = self.graph.get_state(config)
            if existing_state and existing_state.values:
                current_state = existing_state.values
                current_state["query"] = query
                current_state["messages"].append(HumanMessage(content=query))
                current_state["response"] = None
                current_state["error"] = None
                current_state["context"] = ""  # Clear context for new query
                current_state["results"] = []  # Clear previous results
                current_state["data_freshness"] = {}  # Clear freshness info
                initial_state = current_state
            else:
                initial_state = create_initial_state(query)
                initial_state["messages"].append(HumanMessage(content=query))
        except Exception:
            initial_state = create_initial_state(query)
            initial_state["messages"].append(HumanMessage(content=query))
        
        for state in self.graph.stream(initial_state, config=config):
            yield state
    
    def get_state(self, thread_id: str):
        """
        Get the current state for a thread (resume conversation).
        
        Args:
            thread_id: Thread ID to retrieve state for
        
        Returns:
            Current state for the thread
        """
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.get_state(config)
    
    def update_state(self, thread_id: str, values: dict):
        """
        Update state for a thread.
        
        Args:
            thread_id: Thread ID
            values: Dictionary of state values to update
        """
        config = {"configurable": {"thread_id": thread_id}}
        self.graph.update_state(config, values)

