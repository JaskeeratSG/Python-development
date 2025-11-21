"""Base agent class with common functionality."""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage

from graph.state_schema import AgentState
from config.llm_config import get_default_llm


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.
    
    Provides common functionality like LLM access, tool binding,
    and state management.
    """
    
    def __init__(
        self,
        name: str,
        llm: Optional[BaseChatModel] = None,
        tools: Optional[List[BaseTool]] = None,
        description: Optional[str] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name/identifier
            llm: Language model instance (defaults to configured LLM)
            tools: List of tools available to this agent
            description: Description of what this agent does
        """
        self.name = name
        self.llm = llm or get_default_llm()
        self.tools = tools or []
        self.description = description or f"Agent: {name}"
        
        # Bind tools to LLM if available
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm
    
    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """
        Process the state and return updated state.
        
        This method must be implemented by each specialized agent.
        
        Args:
            state: Current agent state
        
        Returns:
            Updated agent state
        """
        pass
    
    def run(self, state: AgentState) -> AgentState:
        """
        Execute the agent with error handling and state updates.
        
        Args:
            state: Current agent state
        
        Returns:
            Updated agent state
        """
        try:
            # Update metadata
            state["current_agent"] = self.name
            state["updated_at"] = datetime.now()
            
            # Add to agent history
            state["agent_history"].append({
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
                "query": state["query"]
            })
            
            # Process the state
            updated_state = self.process(state)
            
            return updated_state
            
        except Exception as e:
            # Handle errors gracefully
            state["error"] = f"{self.name} error: {str(e)}"
            state["updated_at"] = datetime.now()
            return state
    
    def add_message(self, state: AgentState, message: str, role: str = "assistant") -> None:
        """
        Add a message to the state's message history.
        
        Args:
            state: Agent state
            message: Message content
            role: Message role (human or assistant)
        """
        if role == "human":
            state["messages"].append(HumanMessage(content=message))
        else:
            state["messages"].append(AIMessage(content=message))
    
    def update_context(self, state: AgentState, additional_context: str) -> None:
        """
        Update the context in the state.
        
        Args:
            state: Agent state
            additional_context: Context to add
        """
        if state["context"]:
            state["context"] += f"\n\n{additional_context}"
        else:
            state["context"] = additional_context
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

