"""FastAPI endpoint for the intelligent agent system."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.agent_graph import AgentGraph
from config.settings import settings


# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Agent API",
    description="Multi-agent system API with LangGraph and web search capabilities",
    version="1.0.0"
)

# Add CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent graph (singleton)
agent_graph: Optional[AgentGraph] = None


# Request/Response Models
class QueryRequest(BaseModel):
    """
    Request model for query endpoint.
    
    Attributes:
        text: The user's query text (required)
        thread_id: Optional thread ID for conversation continuity.
                  Use the same thread_id to continue a conversation.
                  If not provided, a new conversation thread is created.
        max_results: Maximum number of search results to return (default: 5)
    
    Example:
        {
            "text": "Who won IPL in 2025?",
            "thread_id": "user-123",
            "max_results": 5
        }
    """
    text: str
    thread_id: Optional[str] = None
    max_results: Optional[int] = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Who won IPL in 2025?",
                "thread_id": "user-123",
                "max_results": 5
            }
        }


class SearchResult(BaseModel):
    """
    Model for a single search result.
    
    Attributes:
        title: Title of the search result
        url: URL of the source
        content: Content snippet from the source
        score: Relevance score (0.0 to 1.0)
        timestamp: When the result was retrieved
    """
    title: str
    url: str
    content: str
    score: Optional[float] = None
    timestamp: Optional[str] = None


class DataFreshness(BaseModel):
    """Model for data freshness information."""
    last_updated: Optional[str] = None
    source: Optional[str] = None
    result_count: Optional[int] = None


class QueryResponse(BaseModel):
    """
    Response model for query endpoint.
    
    Attributes:
        success: Whether the query was processed successfully
        query: The original query text
        results: List of search results
        context: Accumulated context from agent processing
        data_freshness: Information about when data was last updated
        metadata: Additional metadata including thread_id
        error: Error message if processing failed
        timestamp: When the response was generated
    """
    success: bool
    query: str
    results: List[SearchResult]
    context: str
    data_freshness: Optional[DataFreshness] = None
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize agent graph on startup."""
    global agent_graph
    
    # Validate settings
    try:
        settings.validate()
        print("✅ Configuration validated successfully!")
    except ValueError as e:
        print(f"⚠️  Configuration warning: {e}")
        print("⚠️  API will start but may not work properly without API keys")
    
    # Initialize agent graph
    try:
        agent_graph = AgentGraph()
        print("✅ Agent graph initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent graph: {e}")
        agent_graph = None


@app.get(
    "/",
    summary="API Information",
    description="Get information about the API and available endpoints",
    tags=["Info"]
)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Intelligent Agent API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "swagger_ui": "http://localhost:8001/docs",
        "redoc": "http://localhost:8001/redoc"
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check if the API and agent system are running properly",
    tags=["Info"]
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_graph_initialized": agent_graph is not None,
        "api_keys_configured": {
            "groq": bool(settings.GROQ_API_KEY),
            "tavily": bool(settings.TAVILY_API_KEY)
        }
    }


@app.post(
    "/api/query",
    response_model=QueryResponse,
    summary="Process a query through the multi-agent system",
    description="""
    Process a text query through the intelligent agent system.
    
    The system uses multiple specialized agents:
    - **Coordinator Agent**: Routes queries to appropriate agents
    - **Search Agent**: Performs web searches using Tavily
    
    **Memory/Thread Support:**
    - Use `thread_id` to maintain conversation context
    - Same `thread_id` = same conversation thread
    - State is persisted using LangGraph checkpointer
    
    **Example Flow:**
    1. First query: `{"text": "Who won IPL?", "thread_id": "user-123"}`
    2. Follow-up: `{"text": "Tell me more", "thread_id": "user-123"}`
       - Agent remembers previous conversation
    """,
    response_description="Query response with search results and context",
    tags=["Queries"]
)
async def process_query(request: QueryRequest):
    """
    Process a text query through the agent system.
    
    Args:
        request: QueryRequest containing the text query
    
    Returns:
        QueryResponse with results, context, and metadata
    """
    if not agent_graph:
        raise HTTPException(
            status_code=503,
            detail="Agent graph not initialized. Please check configuration."
        )
    
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Query text cannot be empty"
        )
    
    try:
        # Process query through agent graph with thread_id for memory
        result = agent_graph.run(
            query=request.text.strip(),
            thread_id=request.thread_id
        )
        
        # Format search results
        formatted_results = []
        for res in result.get("results", [])[:request.max_results]:
            formatted_results.append(SearchResult(
                title=res.get("title", ""),
                url=res.get("url", ""),
                content=res.get("content", ""),
                score=res.get("score"),
                timestamp=res.get("timestamp")
            ))
        
        # Format data freshness
        data_freshness = None
        if result.get("data_freshness"):
            freshness_data = result["data_freshness"]
            data_freshness = DataFreshness(
                last_updated=freshness_data.get("last_updated"),
                source=freshness_data.get("source"),
                result_count=freshness_data.get("result_count")
            )
        
        # Build response
        response = QueryResponse(
            success=True,
            query=request.text,
            results=formatted_results,
            context=result.get("context", ""),
            data_freshness=data_freshness,
            metadata={
                **result.get("metadata", {}),
                "thread_id": request.thread_id  # Include thread_id in response
            },
            error=result.get("error"),
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/api/query/stream")
async def process_query_stream(request: QueryRequest):
    """
    Process a query with streaming responses.
    
    Args:
        request: QueryRequest containing the text query
    
    Yields:
        Streaming updates as the agent processes the query
    """
    if not agent_graph:
        raise HTTPException(
            status_code=503,
            detail="Agent graph not initialized"
        )
    
    from fastapi.responses import StreamingResponse
    import json
    
    def generate():
        try:
            for state_update in agent_graph.stream(request.text.strip()):
                # Format each state update
                update_data = {
                    "query": request.text,
                    "current_agent": state_update.get("current_agent"),
                    "context": state_update.get("context", ""),
                    "results_count": len(state_update.get("results", [])),
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(update_data)}\n\n"
        except Exception as e:
            error_data = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

