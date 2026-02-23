"""Coordinator agent that routes queries to appropriate agents."""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from agents.base_agent import BaseAgent
from graph.state_schema import AgentState


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that analyzes queries and routes them to appropriate agents.
    
    This agent decides which specialized agent should handle the query
    based on the query type and content.
    """
    
    def __init__(self):
        """Initialize the coordinator agent."""
        super().__init__(
            name="coordinator_agent",
            description="Routes queries to appropriate specialized agents"
        )
    
    def process(self, state: AgentState) -> AgentState:
        """
        Analyze query and determine routing.
        
        Args:
            state: Current agent state
        
        Returns:
            Updated state with routing decision
        """
        # Add system message for routing - let LLM make intelligent decisions
        routing_prompt = SystemMessage(content="""
        You are a coordinator that routes queries to specialized agents.
        Analyze the query and conversation history to determine which agent should handle it.
        
        Routing options:
        - "planner_agent": For trip planning, flight booking, hotel booking, travel planning, event planning, scheduling
        - "search_agent": For queries needing current web information, news, latest data, recent events, or real-time information (but NOT flight/travel booking)
        - "end": For conversational queries, follow-up questions, or when the user explicitly doesn't want external search
        
        Important: 
        - Pay attention to user instructions like "don't search" or "no external search"
        - Follow-up questions referencing previous conversation should use "end" to access conversation history
        - Use conversation context to understand what the user is asking about
        
        Respond with ONLY the agent name ("planner_agent", "search_agent", or "end"), nothing else.
        """)
        
        # Build message history for context
        messages = [routing_prompt]
        
        # Add conversation history for context
        conversation_messages = state.get("messages", [])
        if len(conversation_messages) > 1:
            # Include recent conversation history (excluding the current query which is last)
            recent_messages = conversation_messages[-6:-1]  # Last 5 messages before current
            messages.extend(recent_messages)
        
        # Add current user query
        user_message = HumanMessage(content=f"Route this query: {state['query']}")
        messages.append(user_message)
        
        # Get routing decision from LLM - trust its judgment
        response = self.llm.invoke(messages)
        
        # Extract and normalize agent name from response
        next_agent = response.content.strip().lower()
        if "planner_agent" in next_agent:
            next_agent = "planner_agent"
        elif "search_agent" in next_agent:
            next_agent = "search_agent"
        else:
            next_agent = "end"
        
        # For queries routed to "end" (not needing search), generate a response
        if next_agent == "end":
            # Generate a conversational response using LLM with conversation history
            conversational_prompt = SystemMessage(content="""
            You are a friendly AI assistant. Respond naturally to conversational queries.
            Keep responses brief, friendly, and helpful.
            Use conversation history to provide context-aware responses.
            If the user is responding to something you said, acknowledge it naturally.
            """)
            # Build messages with conversation history
            conv_messages = [conversational_prompt]
            # Include recent conversation history
            conversation_messages = state.get("messages", [])
            if len(conversation_messages) > 1:
                recent_messages = conversation_messages[-6:-1]  # Last 5 messages before current
                conv_messages.extend(recent_messages)
            # Add current query
            conv_messages.append(HumanMessage(content=state["query"]))
            conv_response = self.llm.invoke(conv_messages)
            state["response"] = conv_response.content
            self.update_context(state, f"Direct response: {conv_response.content}")
            # Add assistant response to message history
            self.add_message(state, conv_response.content, role="assistant")
        
        # Update metadata with routing decision
        state["metadata"]["routing_decision"] = next_agent
        state["metadata"]["routing_reason"] = response.content
        
        # Don't add routing message to context - it's verbose and accumulates
        # The metadata already contains this information
        # Only add meaningful context (like direct responses)
        
        return state
    
    def should_use_search(self, query: str, conversation_context: list = None) -> bool:
        """
        Determine if query needs web search using LLM.
        
        Args:
            query: User query
            conversation_context: Optional conversation history for context
        
        Returns:
            True if search is needed
        """
        # Use LLM to determine if search is needed
        search_prompt = SystemMessage(content="""
        You are a query classifier. Determine if a query needs web search for current/real-time information.
        
        Return ONLY "yes" or "no":
        - "yes": Query needs current information (news, latest data, recent events, real-time info)
        - "no": Query is conversational, general knowledge, or doesn't need current web data
        
        Examples:
        - "Who won IPL in 2025?" → "yes" (needs current info)
        - "Hey how are you?" → "no" (conversational)
        - "What's the weather today?" → "yes" (needs current data)
        - "I am also good" → "no" (conversational response)
        """)
        
        messages = [search_prompt]
        if conversation_context:
            messages.extend(conversation_context[-3:])  # Last 3 messages for context
        messages.append(HumanMessage(content=f"Does this query need web search: {query}"))
        
        response = self.llm.invoke(messages)
        decision = response.content.strip().lower()
        
        return "yes" in decision or "true" in decision
    
    def _is_conversational_query(self, query: str, conversation_context: list = None) -> bool:
        """
        Check if query is conversational using LLM.
        
        Args:
            query: User query
            conversation_context: Optional conversation history for context
        
        Returns:
            True if conversational
        """
        # Use LLM to determine if query is conversational
        conv_prompt = SystemMessage(content="""
        You are a query classifier. Determine if a query is conversational (greeting, casual chat, follow-up response).
        
        Return ONLY "yes" or "no":
        - "yes": Query is conversational (greeting, casual chat, responding to previous message)
        - "no": Query needs information, search, or specific action
        
        Examples:
        - "Hey how are you?" → "yes"
        - "I am also good" → "yes" (follow-up response)
        - "Who won IPL?" → "no" (needs information)
        - "Tell me a joke" → "yes" (conversational)
        """)
        
        messages = [conv_prompt]
        if conversation_context:
            messages.extend(conversation_context[-3:])  # Last 3 messages for context
        messages.append(HumanMessage(content=f"Is this query conversational: {query}"))
        
        response = self.llm.invoke(messages)
        decision = response.content.strip().lower()
        
        return "yes" in decision or "true" in decision

