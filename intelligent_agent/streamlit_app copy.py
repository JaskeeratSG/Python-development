"""
Streamlit UI for Intelligent Agent System
Multi-agent system with LangGraph, web search, and real-time updates
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from graph.agent_graph import AgentGraph
from config.settings import settings


# Page configuration
st.set_page_config(
    page_title="Intelligent Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-status {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-active {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .status-completed {
        background-color: #cce5ff;
        border-left: 4px solid #007bff;
    }
    .result-card {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        background-color: #f8f9fa;
    }
    .freshness-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
    .freshness-recent {
        background-color: #28a745;
        color: white;
    }
    .freshness-old {
        background-color: #ffc107;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if "agent_graph" not in st.session_state:
    try:
        settings.validate()
        st.session_state.agent_graph = AgentGraph()
        st.session_state.agent_initialized = True
    except Exception as e:
        st.session_state.agent_graph = None
        st.session_state.agent_initialized = False
        st.session_state.init_error = str(e)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_{int(time.time())}"

if "current_query" not in st.session_state:
    st.session_state.current_query = ""


def display_agent_status(agent_name: str, status: str):
    """Display agent status with styling."""
    status_class = "status-active" if status == "active" else "status-completed"
    st.markdown(f"""
        <div class="agent-status {status_class}">
            <strong>🤖 {agent_name}</strong> - {status.title()}
        </div>
    """, unsafe_allow_html=True)


def display_search_result(result: dict, index: int):
    """Display a single search result card."""
    st.markdown(f"""
        <div class="result-card">
            <h4>🔍 {result.get('title', 'No title')}</h4>
            <p><strong>URL:</strong> <a href="{result.get('url', '#')}" target="_blank">{result.get('url', 'N/A')}</a></p>
            <p><strong>Content:</strong> {result.get('content', '')[:200]}...</p>
            <p><small>Score: {result.get('score', 0):.2f} | Timestamp: {result.get('timestamp', 'N/A')}</small></p>
        </div>
    """, unsafe_allow_html=True)


def display_data_freshness(freshness: dict):
    """Display data freshness information."""
    if not freshness:
        return
    
    last_updated = freshness.get("last_updated", "")
    source = freshness.get("source", "unknown")
    result_count = freshness.get("result_count", 0)
    
    # Determine freshness badge
    if last_updated:
        try:
            update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            time_diff = (datetime.now() - update_time.replace(tzinfo=None)).total_seconds()
            is_recent = time_diff < 3600  # Less than 1 hour
            badge_class = "freshness-recent" if is_recent else "freshness-old"
            badge_text = "🟢 Recent" if is_recent else "🟡 Older"
        except:
            badge_class = "freshness-old"
            badge_text = "🟡 Unknown"
    else:
        badge_class = "freshness-old"
        badge_text = "🟡 No timestamp"
    
    st.markdown(f"""
        <div style="padding: 1rem; background-color: #e7f3ff; border-radius: 0.5rem; margin: 1rem 0;">
            <h4>📅 Data Freshness</h4>
            <p><span class="freshness-badge {badge_class}">{badge_text}</span></p>
            <p><strong>Source:</strong> {source}</p>
            <p><strong>Last Updated:</strong> {last_updated or 'N/A'}</p>
            <p><strong>Results Found:</strong> {result_count}</p>
        </div>
    """, unsafe_allow_html=True)


def process_query(query: str, thread_id: Optional[str] = None):
    """Process a query through the agent system."""
    if not st.session_state.agent_graph:
        return None
    
    try:
        # Show processing status
        with st.spinner("🤖 Processing query through multi-agent system..."):
            # Process query
            result = st.session_state.agent_graph.run(
                query=query,
                thread_id=thread_id or st.session_state.thread_id
            )
            return result
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None


# Main UI
def main():
    # Header
    st.markdown('<div class="main-header">🤖 Intelligent Agent System</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Agent status
        if st.session_state.agent_initialized:
            st.success("✅ Agent System Initialized")
        else:
            st.error(f"❌ Initialization Failed: {st.session_state.get('init_error', 'Unknown error')}")
        
        st.divider()
        
        # Thread ID management
        st.subheader("💬 Conversation")
        thread_id = st.text_input(
            "Thread ID",
            value=st.session_state.thread_id,
            help="Use the same Thread ID to continue a conversation"
        )
        st.session_state.thread_id = thread_id
        
        if st.button("🔄 New Conversation"):
            st.session_state.thread_id = f"user_{int(time.time())}"
            st.session_state.conversation_history = []
            st.rerun()
        
        st.divider()
        
        # API Keys status
        st.subheader("🔑 API Keys")
        groq_status = "✅" if settings.GROQ_API_KEY else "❌"
        tavily_status = "✅" if settings.TAVILY_API_KEY else "❌"
        st.write(f"Groq: {groq_status}")
        st.write(f"Tavily: {tavily_status}")
        
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        max_results = st.slider("Max Results", 1, 10, 5)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Agent Status", "📚 Conversation History"])
    
    with tab1:
        # Query input
        st.subheader("Ask a Question")
        query = st.text_input(
            "Enter your query:",
            value=st.session_state.current_query,
            placeholder="e.g., Who won IPL in 2025?",
            key="query_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.button("🚀 Submit", type="primary", use_container_width=True)
        
        # Process query
        result = None
        if submit_button and query:
            st.session_state.current_query = query
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process query
            result = process_query(query, st.session_state.thread_id)
        
        if result:
            # Display results
            st.divider()
            st.subheader("📋 Results")
            
            # Display context
            if result.get("context"):
                with st.expander("📝 Context", expanded=True):
                    st.write(result["context"])
            
            # Display search results
            search_results = result.get("results", [])
            if search_results:
                st.subheader(f"🔍 Search Results ({len(search_results)} found)")
                for idx, res in enumerate(search_results[:max_results], 1):
                    with st.expander(f"Result {idx}: {res.get('title', 'No title')[:50]}..."):
                        st.write(f"**URL:** {res.get('url', 'N/A')}")
                        st.write(f"**Content:** {res.get('content', '')}")
                        st.write(f"**Score:** {res.get('score', 0):.2f}")
                        st.write(f"**Timestamp:** {res.get('timestamp', 'N/A')}")
            
            # Display data freshness
            data_freshness = result.get("data_freshness")
            if data_freshness:
                display_data_freshness(data_freshness)
            
            # Display metadata
            metadata = result.get("metadata", {})
            if metadata:
                with st.expander("🔧 Metadata"):
                    st.json(metadata)
            
            # Add response to conversation history
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": result.get("context", "No response generated"),
                "results": search_results,
                "timestamp": datetime.now().isoformat()
            })
            
            # Display error if any
            if result.get("error"):
                st.error(f"⚠️ Error: {result['error']}")
    
    with tab2:
        st.subheader("🤖 Agent Status")
        
        if st.session_state.agent_initialized:
            # Display agent information
            st.info("Agent system is ready and waiting for queries.")
            
            # Show available agents
            st.markdown("### Available Agents")
            st.markdown("""
            - **Coordinator Agent**: Routes queries to appropriate agents
            - **Search Agent**: Performs web searches using Tavily
            """)
            
            # Show last query metadata if available
            if st.session_state.conversation_history:
                last_query = st.session_state.conversation_history[-1]
                if last_query.get("role") == "user":
                    st.markdown("### Last Query Processing")
                    st.write(f"**Query:** {last_query['content']}")
                    st.write(f"**Timestamp:** {last_query['timestamp']}")
        else:
            st.error("Agent system not initialized. Please check configuration.")
    
    with tab3:
        st.subheader("💬 Conversation History")
        
        if st.session_state.conversation_history:
            for idx, msg in enumerate(st.session_state.conversation_history):
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                        st.caption(f"Time: {msg.get('timestamp', 'N/A')}")
                else:
                    with st.chat_message("assistant"):
                        st.write(msg["content"])
                        if msg.get("results"):
                            st.write(f"**Found {len(msg['results'])} search results**")
                        st.caption(f"Time: {msg.get('timestamp', 'N/A')}")
        else:
            st.info("No conversation history yet. Start by asking a question!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Intelligent Agent System | Powered by LangGraph, LangChain, and Tavily</p>
        <p>Thread ID: <code>{}</code></p>
    </div>
    """.format(st.session_state.thread_id), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

