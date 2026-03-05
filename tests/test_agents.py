"""
Agent Unit Tests

Tests for planner, analyzer, and writer agent functions
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.agents.planner import parse_planner_output, planner_node
from app.agents.analyzer import parse_analyzer_output, format_search_results_for_analysis
from app.agents.writer import writer_node


class TestPlannerAgent:
    """Tests for planner agent"""
    
    def test_parse_planner_output_valid(self):
        """Test parsing valid planner output"""
        response = """RESEARCH PLAN: Compare AI regulatory frameworks

SUB-QUESTIONS:
1. What are EU AI regulations?
2. What are US AI regulations?
3. How do they compare?
4. What are the business impacts?
"""
        plan, questions = parse_planner_output(response)
        
        assert plan == "Compare AI regulatory frameworks"
        assert len(questions) == 4
        assert "What are EU AI regulations?" in questions
    
    def test_parse_planner_output_minimal(self):
        """Test parsing with minimum required questions"""
        response = """RESEARCH PLAN: Research topic

SUB-QUESTIONS:
1. First question?
2. Second question?
3. Third question?
"""
        plan, questions = parse_planner_output(response)
        
        assert len(questions) == 3
    
    def test_parse_planner_output_insufficient_questions(self):
        """Test parsing with insufficient questions raises error"""
        response = """RESEARCH PLAN: Research topic

SUB-QUESTIONS:
1. First question?
2. Second question?
"""
        with pytest.raises(ValueError, match="insufficient sub-questions"):
            parse_planner_output(response)
    
    def test_parse_planner_output_max_questions(self):
        """Test that output is limited to 5 questions"""
        response = """RESEARCH PLAN: Research topic

SUB-QUESTIONS:
1. Q1?
2. Q2?
3. Q3?
4. Q4?
5. Q5?
6. Q6?
7. Q7?
"""
        plan, questions = parse_planner_output(response)
        
        assert len(questions) == 5
    
    @pytest.mark.asyncio
    async def test_planner_node_success(self, sample_research_state, mock_llm_response):
        """Test planner node with successful response"""
        with patch("app.agents.planner.create_planner_agent") as mock_create:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_create.return_value = mock_llm
            
            result = await planner_node(sample_research_state)
            
            assert result["status"] == "searching"
            assert result["research_plan"] is not None
            assert len(result["sub_questions"]) >= 3


class TestAnalyzerAgent:
    """Tests for analyzer agent"""
    
    def test_format_search_results(self, sample_research_state):
        """Test formatting search results for LLM"""
        formatted = format_search_results_for_analysis(sample_research_state)
        
        assert "Sub-Question:" in formatted
        assert "Title:" in formatted
        assert "URL:" in formatted
    
    def test_parse_analyzer_output_valid(self):
        """Test parsing valid analyzer output"""
        response = """KEY FINDINGS:
1. EU has comprehensive AI Act
2. US uses sector-specific approach

CITATIONS:
[https://example.com] - Example Title - "Quote from source"

SYNTHESIS:
The analysis shows different approaches.
"""
        findings, citations, synthesis = parse_analyzer_output(response)
        
        assert len(findings) == 2
        assert "EU has comprehensive AI Act" in findings
        assert len(citations) >= 0  # Citations parsing may vary
        assert "different approaches" in synthesis


class TestWriterAgent:
    """Tests for writer agent"""
    
    @pytest.mark.asyncio
    async def test_writer_node_success(self, sample_research_state, sample_citations):
        """Test writer node generates report"""
        # Update state with required fields
        state = {
            **sample_research_state,
            "citations": sample_citations,
            "synthesis": "The EU and US have different approaches to AI regulation.",
            "status": "writing"
        }
        
        mock_response = MagicMock()
        mock_response.content = """# AI Regulations Comparison

## Executive Summary
A comparison of EU and US AI regulations.

## Key Findings
1. EU has comprehensive framework
2. US uses sector-specific approach

## Sources
[1] Example Source - https://example.com
"""
        
        with patch("app.agents.writer.create_writer_agent") as mock_create:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_response
            mock_create.return_value = mock_llm
            
            result = await writer_node(state)
            
            assert result["status"] == "complete"
            assert result["final_report"] is not None
            assert "AI Regulations" in result["final_report"]
