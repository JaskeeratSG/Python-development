<!-- 47671124-4aee-49f2-b037-e73ca6fc0009 aae68033-57e9-4984-9da2-c122a2d803c3 -->
# Multi-Agent System with LangGraph and Streamlit

## Project Overview

A production-ready multi-agent system that uses LangGraph for agent orchestration, integrates MCP-style tools (Google Search via Tavily/Serper), and provides a Streamlit UI showing data freshness and agent workflows.

## Technology Stack

### Core Framework

- **LangGraph**: Multi-agent orchestration and workflow management
- **LangChain**: LLM integration and tool abstractions
- **Streamlit**: Frontend UI with real-time updates

### LLM Options (Free Tier)

1. **Groq** (Recommended - Fast, generous free tier, multiple models)
2. **Ollama** (Local, no API key needed)
3. **HuggingFace Inference API** (Free tier available)
4. **Google Gemini** (Free tier)

### Search Tools

- **Tavily API**: Primary search tool (MCP-compatible)
- **Serper API**: Alternative/backup search tool
- **Google Custom Search**: Optional fallback

## Project Structure

```
intelligent_agent/
├── config/
│   ├── __init__.py
│   ├── settings.py              # Environment config & validation
│   └── llm_config.py            # LLM provider configuration
├── agents/
│   ├── __init__.py
│   ├── base_agent.py            # Base agent class
│   ├── search_agent.py          # Specialized: Web search queries
│   ├── research_agent.py        # Specialized: Deep research & analysis
│   ├── planner_agent.py         # Specialized: Trip/event planning
│   ├── fact_checker_agent.py    # Specialized: Verification & accuracy
│   └── coordinator_agent.py     # Supervisor: Routes & coordinates
├── tools/
│   ├── __init__.py
│   ├── search_tools.py          # Tavily, Serper integrations
│   ├── custom_tools.py          # Custom tool implementations
│   └── mcp_adapter.py           # MCP protocol adapter
├── graph/
│   ├── __init__.py
│   ├── agent_graph.py           # LangGraph workflow definition
│   └── state_schema.py          # State management schemas
├── ui/
│   ├── __init__.py
│   ├── streamlit_app.py         # Main Streamlit interface
│   ├── components/
│   │   ├── agent_status.py      # Agent status widgets
│   │   ├── data_freshness.py    # Data freshness display
│   │   └── conversation_view.py # Chat interface
├── storage/
│   ├── __init__.py
│   ├── conversation_store.py    # Conversation history
│   └── data_cache.py            # Cache with timestamps
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Logging configuration
│   └── helpers.py               # Utility functions
├── main.py                      # Entry point for CLI
├── requirements.txt
├── .env.example
├── setup.sh                     # Installation script
└── README.md                    # Comprehensive documentation
```

## Implementation Plan

### Phase 1: Setup & Configuration

1. **Environment Setup**

   - Create virtual environment
   - Install dependencies (LangGraph, LangChain, Streamlit, Tavily, etc.)
   - Set up `.env` file with API keys
   - Configuration validation

2. **LLM Provider Integration**

   - Implement LLM factory pattern supporting multiple providers
   - Start with Groq (default) - fast and free
   - Abstract provider switching

3. **Base Infrastructure**

   - Settings management with validation
   - Logging setup
   - Error handling framework

### Phase 2: Tool Development

4. **Search Tools Implementation**

   - Tavily API integration with error handling
   - Serper API as backup
   - MCP adapter for tool standardization
   - Response parsing and formatting

5. **Custom Tools**

   - Data freshness tracker
   - Result formatter
   - Cache manager with TTL

### Phase 3: Agent Development

6. **Base Agent Class**

   - Common agent interface
   - Tool binding mechanism
   - State management
   - Error recovery

7. **Specialized Agents**

   - **SearchAgent**: Handles web searches, extracts relevant results
   - **ResearchAgent**: Deep analysis, multiple source synthesis
   - **PlannerAgent**: Trip/event planning with date awareness
   - **FactCheckerAgent**: Cross-reference verification
   - **CoordinatorAgent**: Routes queries, manages workflow

### Phase 4: LangGraph Integration

8. **State Schema**

   - Define agent state structure
   - Include: query, context, results, metadata, timestamps

9. **Graph Workflow**

   - Define agent nodes
   - Conditional routing logic
   - Parallel agent execution where applicable
   - Error handling edges

### Phase 5: Frontend Development

10. **Streamlit UI**

    - Main interface with query input
    - Real-time agent status display
    - Data freshness indicators (e.g., "Data updated till: 2025-01-XX")
    - Conversation history
    - Agent workflow visualization
    - Settings panel for API keys

### Phase 6: Storage & Caching

11. **Data Management**

    - Conversation history storage (SQLite/JSON)
    - Cached search results with timestamps
    - Data freshness tracking per query type

### Phase 7: Testing & Documentation

12. **Testing**

    - Unit tests for agents
    - Integration tests for workflows
    - UI component tests

13. **Documentation**

    - README with setup instructions
    - API key acquisition guide
    - Usage examples
    - Architecture documentation

## Key Features

1. **Multi-Agent Orchestration**: Coordinated workflow with specialized agents
2. **Real-Time Search**: Integration with Tavily/Serper for current data
3. **Data Freshness Tracking**: UI shows when data was last updated
4. **MCP-Compatible Tools**: Standardized tool interface
5. **Free LLM Support**: Multiple free LLM providers
6. **Streamlit UI**: Interactive interface with real-time updates
7. **Error Handling**: Robust error recovery and fallback mechanisms
8. **Extensible**: Easy to add new agents and tools

## Installation Steps

1. Create virtual environment: `python3 -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add API keys
5. Run setup script: `bash setup.sh`
6. Launch Streamlit: `streamlit run ui/streamlit_app.py`

## API Keys Required

1. **Groq API Key** (Free): https://console.groq.com/
2. **Tavily API Key** (Free tier): https://tavily.com/
3. **Serper API Key** (Optional, Free tier): https://serper.dev/

## Sample Queries Supported

- "Plan a trip to Bangkok for March 15-20, 2025"
- "What is the best time to visit Bangkok?"
- "Find flight details from NYC to Bangkok"
- "Who won IPL in 2025?"
- "Latest news about [topic]"

## Next Steps After Plan Approval

1. Create project structure
2. Set up configuration system
3. Implement base agent framework
4. Integrate search tools
5. Build LangGraph workflow
6. Develop Streamlit UI
7. Add testing and documentation

### To-dos

- [ ] Set up virtual environment, dependencies, and configuration system with API key validation
- [ ] Implement LLM factory supporting Groq (default), Ollama, HuggingFace, and Google Gemini
- [ ] Build Tavily and Serper search tool integrations with MCP adapter pattern
- [ ] Create base agent class with tool binding, state management, and error handling
- [ ] Implement SearchAgent, ResearchAgent, PlannerAgent, FactCheckerAgent, and CoordinatorAgent
- [ ] Build LangGraph state schema and workflow with agent nodes, routing logic, and conditional edges
- [ ] Develop Streamlit frontend with query input, agent status, data freshness display, and conversation view
- [ ] Implement conversation storage and cached search results with timestamp tracking
- [ ] Add unit tests, integration tests, and comprehensive documentation with setup guide