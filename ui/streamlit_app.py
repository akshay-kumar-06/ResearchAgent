"""
Streamlit Frontend - Multi-Agent Research Assistant

Chat-like interface for research queries with real-time status updates
and markdown report display.
"""

import streamlit as st
import requests
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-running {
        color: #FF9800;
        font-weight: bold;
    }
    .status-complete {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-error {
        color: #F44336;
        font-weight: bold;
    }
    .research-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_research(query: str) -> dict:
    """Start a new research task"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/research",
            json={"query": query},
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_research_status(research_id: str) -> dict:
    """Get status of a research task"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/research/{research_id}/status",
            timeout=10
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_research_result(research_id: str) -> dict:
    """Get completed research result"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/research/{research_id}",
            timeout=10
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_research_history(limit: int = 10) -> list:
    """Get research history"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/research",
            params={"limit": limit},
            timeout=10
        )
        return response.json()
    except requests.exceptions.RequestException:
        return []


# Initialize session state
if "research_history" not in st.session_state:
    st.session_state.research_history = []
if "current_research_id" not in st.session_state:
    st.session_state.current_research_id = None
if "current_report" not in st.session_state:
    st.session_state.current_report = None


# Sidebar - Research History
with st.sidebar:
    st.markdown("## 📚 Research History")
    
    # Refresh history button
    if st.button("🔄 Refresh History"):
        st.session_state.research_history = get_research_history(10)
    
    # Load history on first run
    if not st.session_state.research_history:
        st.session_state.research_history = get_research_history(10)
    
    # Display history
    if st.session_state.research_history:
        for item in st.session_state.research_history:
            query_preview = item.get("query", "")[:50] + "..." if len(item.get("query", "")) > 50 else item.get("query", "")
            status = item.get("status", "unknown")
            
            status_icon = "✅" if status == "complete" else "❌" if status == "error" else "⏳"
            
            if st.button(f"{status_icon} {query_preview}", key=item.get("research_id")):
                st.session_state.current_research_id = item.get("research_id")
                if status == "complete":
                    result = get_research_result(item.get("research_id"))
                    if "report" in result:
                        st.session_state.current_report = result["report"]
    else:
        st.info("No research history yet.")
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    # API status indicator
    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Disconnected")
        st.info("Make sure the FastAPI server is running:\n`uvicorn app.main:app --reload`")


# Main content
st.markdown('<div class="main-header">🔬 AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous research powered by multiple AI agents</div>', unsafe_allow_html=True)

# Research input
st.markdown("### 📝 New Research Query")

with st.form("research_form"):
    query = st.text_area(
        "What would you like to research?",
        placeholder="Enter your research question here... (e.g., 'Compare AI regulations in EU vs US')",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_button = st.form_submit_button("🚀 Start Research", use_container_width=True)

# Handle form submission
if submit_button and query:
    if not check_api_health():
        st.error("❌ Cannot connect to the API. Please make sure the server is running.")
    else:
        with st.spinner("🚀 Starting research..."):
            result = start_research(query)
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            elif "research_id" in result:
                research_id = result["research_id"]
                st.session_state.current_research_id = research_id
                st.success(f"✅ Research started! ID: {research_id}")
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                stages = {
                    "started": (10, "📋 Initializing..."),
                    "running": (20, "🔄 Processing..."),
                    "planning": (30, "🧠 Planning research strategy..."),
                    "searching": (50, "🔍 Searching the web..."),
                    "analyzing": (70, "📊 Analyzing results..."),
                    "writing": (90, "✍️ Writing report..."),
                    "complete": (100, "✅ Research complete!"),
                    "error": (100, "❌ Research failed")
                }
                
                # Poll for status
                max_polls = 120  # 10 minutes max
                poll_count = 0
                
                while poll_count < max_polls:
                    status_result = get_research_status(research_id)
                    
                    if "error" in status_result:
                        st.error(f"❌ Error checking status: {status_result['error']}")
                        break
                    
                    current_status = status_result.get("status", "unknown")
                    progress, message = stages.get(current_status, (50, f"Status: {current_status}"))
                    
                    progress_bar.progress(progress)
                    status_text.markdown(f"**{message}**")
                    
                    if current_status == "complete":
                        # Fetch and display the report
                        report_result = get_research_result(research_id)
                        if "report" in report_result:
                            st.session_state.current_report = report_result["report"]
                            
                            # Display metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("⏱️ Time", f"{report_result.get('execution_time', 0):.1f}s")
                            with col2:
                                st.metric("📚 Sources", report_result.get("num_sources", 0))
                            with col3:
                                st.metric("📄 Report Length", f"{len(report_result.get('report', ''))} chars")
                        break
                    
                    elif current_status == "error":
                        st.error(f"❌ Research failed: {status_result.get('error_message', 'Unknown error')}")
                        break
                    
                    time.sleep(5)  # Poll every 5 seconds
                    poll_count += 1
                
                if poll_count >= max_polls:
                    st.warning("⏳ Research is taking longer than expected. Check the history later.")
                
                # Refresh history
                st.session_state.research_history = get_research_history(10)

# Display current report
if st.session_state.current_report:
    st.markdown("---")
    st.markdown("### 📄 Research Report")
    
    # Download button
    st.download_button(
        label="📥 Download Report",
        data=st.session_state.current_report,
        file_name="research_report.md",
        mime="text/markdown"
    )
    
    # Display report in expandable section
    with st.expander("📖 View Full Report", expanded=True):
        st.markdown(st.session_state.current_report)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Multi-Agent Research Assistant | Built with LangGraph, FastAPI, and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
