"""
Report Writer Agent - Generates comprehensive markdown reports

Uses Gemini LLM to create publication-ready research reports with proper formatting
"""

import structlog
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import get_settings
from app.agents.state import ResearchState

logger = structlog.get_logger()

WRITER_SYSTEM_PROMPT = """You are an expert research report writer. Create comprehensive, well-structured markdown reports.

RULES:
1. Use proper markdown formatting
2. Include all citations as numbered references
3. Structure: Title → Summary → Key Findings → Detailed Analysis → Sources
4. Be professional and objective
5. Use headers, lists, and emphasis appropriately
6. Make it publication-ready

OUTPUT FORMAT:
# [Title Based on Query]

**Research Date:** [Date]
**Total Sources Analyzed:** [Number]

## Executive Summary
[Brief summary of the research findings]

## Key Findings
[List of key discoveries]

## Detailed Analysis
[In-depth analysis of the topic]

## Sources
[Numbered list of sources with URLs]

"""


def create_writer_agent():
    """Create and configure the Gemini LLM for report writing"""
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=0.4,  # Slightly higher for better writing
        google_api_key=settings.google_api_key,
        max_output_tokens=4000,
    )


async def writer_node(state: ResearchState) -> ResearchState:
    """
    Writer agent node - generates final markdown report

    Args:
        state: Current research state with analysis complete

    Returns:
        Updated state with final_report
    """
    logger.info("writer_agent_started")

    try:
        llm = create_writer_agent()

        # Prepare content for report
        findings_text = "\n".join(
            [f"{i + 1}. {f}" for i, f in enumerate(state["key_findings"])]
        )
        citations_text = "\n".join(
            [
                f"[{i + 1}] {c.source_title} - Full URL: {c.source_url} - Quote: {c.quote[:100]}..."
                for i, c in enumerate(state["citations"])
            ]
        )

        messages = [
            HumanMessage(
                content=f"""{WRITER_SYSTEM_PROMPT}

Original Query: {state["original_query"]}

Research Plan: {state["research_plan"]}

Key Findings:
{findings_text}

Synthesis:
{state["synthesis"]}

Citations:
{citations_text}

Total Sources: {state["total_sources"]}

Generate a comprehensive research report in markdown format."""
            )
        ]

        response = await llm.ainvoke(messages)
        final_report = response.content

        # Ensure final_report is a string
        if not isinstance(final_report, str):
            final_report = str(final_report)

        # Add metadata footer
        final_report += f"\n\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        final_report += f"*Powered by Multi-Agent Research Assistant*"

        logger.info("writer_agent_completed", report_length=len(final_report))

        # Return updated state matching ResearchState structure
        return ResearchState(
            original_query=state["original_query"],
            research_plan=state["research_plan"],
            sub_questions=state["sub_questions"],
            search_results=state["search_results"],
            total_sources=state["total_sources"],
            key_findings=state["key_findings"],
            citations=state["citations"],
            synthesis=state["synthesis"],
            final_report=final_report,
            status="complete",
            error_message=state["error_message"],
            execution_time=state["execution_time"],
            messages=state.get("messages", []) + [response],
        )

    except Exception as e:
        logger.error("writer_agent_failed", error=str(e))
        # Safely get messages field
        messages_field = state.get("messages", [])
        if messages_field is None:
            messages_field = []
        return ResearchState(
            original_query=state["original_query"],
            research_plan=state["research_plan"],
            sub_questions=state["sub_questions"],
            search_results=state["search_results"],
            total_sources=state["total_sources"],
            key_findings=state["key_findings"],
            citations=state["citations"],
            synthesis=state["synthesis"],
            final_report=str(state["final_report"]),
            status="error",
            error_message=f"Report writing failed: {str(e)}",
            execution_time=state["execution_time"],
            messages=messages_field,
        )
