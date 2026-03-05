"""
LangGraph Workflow Orchestration

Defines and compiles the StateGraph that coordinates all research agents
"""

import structlog
import time
from langgraph.graph import StateGraph, END
from app.agents.state import ResearchState
from app.agents.planner import planner_node
from app.agents.searcher import search_node
from app.agents.analyzer import analyzer_node
from app.agents.writer import writer_node

logger = structlog.get_logger()


def should_continue(state: ResearchState) -> str:
    """
    Conditional edge function - determines next node based on state
    
    Args:
        state: Current research state
        
    Returns:
        Next node name or END
    """
    status = state.get("status", "")
    
    if status == "error":
        return END
    elif status == "searching":
        return "search"
    elif status == "analyzing":
        return "analyze"
    elif status == "writing":
        return "write"
    elif status == "complete":
        return END
    else:
        return "plan"  # Default start


def create_research_graph() -> StateGraph:
    """
    Create the LangGraph workflow for research assistant
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize graph with state schema
    workflow = StateGraph(ResearchState)
    
    # Add nodes - each node is an async function that transforms state
    workflow.add_node("plan", planner_node)
    workflow.add_node("search", search_node)
    workflow.add_node("analyze", analyzer_node)
    workflow.add_node("write", writer_node)
    
    # Set entry point - workflow always starts with planning
    workflow.set_entry_point("plan")
    
    # Add conditional edges from planner
    workflow.add_conditional_edges(
        "plan",
        should_continue,
        {
            "search": "search",
            END: END
        }
    )
    
    # Add conditional edges from search
    workflow.add_conditional_edges(
        "search",
        should_continue,
        {
            "analyze": "analyze",
            END: END
        }
    )
    
    # Add conditional edges from analyzer
    workflow.add_conditional_edges(
        "analyze",
        should_continue,
        {
            "write": "write",
            END: END
        }
    )
    
    # Writer always ends the workflow
    workflow.add_edge("write", END)
    
    # Compile the workflow
    app = workflow.compile()
    
    logger.info("research_graph_created")
    return app


async def run_research(query: str) -> ResearchState:
    """
    Execute research workflow for a given query
    
    This is the main entry point for running a complete research workflow.
    It initializes the state, creates the graph, and runs to completion.
    
    Args:
        query: User's research question
        
    Returns:
        Final research state containing the report and all intermediate data
    """
    logger.info("research_started", query=query)
    start_time = time.time()
    
    # Initialize state with empty/default values
    initial_state: ResearchState = {
        "original_query": query,
        "research_plan": None,
        "sub_questions": [],
        "search_results": {},
        "total_sources": 0,
        "key_findings": [],
        "citations": [],
        "synthesis": "",
        "final_report": "",
        "status": "planning",
        "error_message": None,
        "execution_time": 0.0,
        "messages": []
    }
    
    # Create and run graph
    app = create_research_graph()
    
    try:
        # Run the workflow asynchronously
        final_state = await app.ainvoke(initial_state)
        
        # Record execution time
        execution_time = time.time() - start_time
        final_state["execution_time"] = execution_time
        
        logger.info(
            "research_completed",
            status=final_state["status"],
            execution_time=execution_time,
            total_sources=final_state.get("total_sources", 0)
        )
        
        return final_state
        
    except Exception as e:
        logger.error("research_failed", error=str(e))
        return {
            **initial_state,
            "status": "error",
            "error_message": str(e),
            "execution_time": time.time() - start_time
        }
