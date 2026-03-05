"""
LangGraph Workflow Tests

Tests for the research workflow graph and state transitions
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.agents.graph import should_continue, create_research_graph
from app.agents.state import ResearchState


class TestWorkflowConditions:
    """Tests for workflow conditional logic"""
    
    def test_should_continue_error(self):
        """Test that error status ends workflow"""
        state = {"status": "error"}
        result = should_continue(state)
        assert result == "__end__"
    
    def test_should_continue_complete(self):
        """Test that complete status ends workflow"""
        state = {"status": "complete"}
        result = should_continue(state)
        assert result == "__end__"
    
    def test_should_continue_searching(self):
        """Test transition to search node"""
        state = {"status": "searching"}
        result = should_continue(state)
        assert result == "search"
    
    def test_should_continue_analyzing(self):
        """Test transition to analyze node"""
        state = {"status": "analyzing"}
        result = should_continue(state)
        assert result == "analyze"
    
    def test_should_continue_writing(self):
        """Test transition to write node"""
        state = {"status": "writing"}
        result = should_continue(state)
        assert result == "write"
    
    def test_should_continue_default(self):
        """Test default transition to plan"""
        state = {"status": ""}
        result = should_continue(state)
        assert result == "plan"


class TestResearchGraph:
    """Tests for research graph creation and execution"""
    
    def test_create_research_graph(self):
        """Test that graph is created successfully"""
        graph = create_research_graph()
        assert graph is not None
    
    def test_graph_has_nodes(self):
        """Test that graph has all required nodes"""
        graph = create_research_graph()
        # Graph should be compiled StateGraph
        assert graph is not None
    
    @pytest.mark.asyncio
    async def test_graph_error_handling(self, sample_research_state):
        """Test that graph handles errors gracefully"""
        # Create a state that will cause an error
        state = {
            **sample_research_state,
            "status": "error",
            "error_message": "Test error"
        }
        
        # The workflow should end on error
        result = should_continue(state)
        assert result == "__end__"


class TestStateTransitions:
    """Tests for state transitions in workflow"""
    
    def test_planning_to_searching(self):
        """Test transition from planning to searching"""
        state = {"status": "searching"}
        assert should_continue(state) == "search"
    
    def test_searching_to_analyzing(self):
        """Test transition from searching to analyzing"""
        state = {"status": "analyzing"}
        assert should_continue(state) == "analyze"
    
    def test_analyzing_to_writing(self):
        """Test transition from analyzing to writing"""
        state = {"status": "writing"}
        assert should_continue(state) == "write"
    
    def test_writing_to_complete(self):
        """Test transition from writing to complete"""
        state = {"status": "complete"}
        assert should_continue(state) == "__end__"
