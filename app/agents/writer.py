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
[2-3 sentence overview of findings]

## Key Findings
1. [Finding 1]
2. [Finding 2]
...

## Detailed Analysis

### [Section 1 Title]
[Analysis with citations [1], [2]]

### [Section 2 Title]
[Analysis with citations]

## Conclusion
[Summary and implications]

## Sources
IMPORTANT: Each source MUST be on its own separate line with a blank line between entries.
You MUST use the EXACT full URLs provided in the Citations data below. Do NOT replace URLs with placeholders like "URL1" or "URL2".

[1] Author. (Date). *Title*. Retrieved from https://exact-url-from-citations.com/page

[2] Author. (Date). *Title*. Retrieved from https://exact-url-from-citations.com/other

...
"""


def create_writer_agent() -> ChatGoogleGenerativeAI:
    """
    Create the writer LLM instance
    
    Returns:
        ChatGoogleGenerativeAI: Configured Gemini LLM for writing
    """
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=0.4,  # Slightly higher for better writing
        google_api_key=settings.google_api_key,
        max_output_tokens=4000
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
        findings_text = "\n".join([f"{i+1}. {f}" for i, f in enumerate(state["key_findings"])])
        citations_text = "\n".join([
            f"[{i+1}] {c.source_title} - Full URL: {c.source_url} - Quote: {c.quote[:100]}..."
            for i, c in enumerate(state["citations"])
        ])
        
        messages = [
            HumanMessage(content=f"""{WRITER_SYSTEM_PROMPT}

Original Query: {state['original_query']}

Research Plan: {state['research_plan']}

Key Findings:
{findings_text}

Synthesis:
{state['synthesis']}

Citations:
{citations_text}

Total Sources: {state['total_sources']}

Generate a comprehensive research report in markdown format.""")
        ]
        
        response = await llm.ainvoke(messages)
        final_report = response.content
        
        # Add metadata footer
        final_report += f"\n\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        final_report += f"*Powered by Multi-Agent Research Assistant*"
        
        logger.info("writer_agent_completed", report_length=len(final_report))
        
        return {
            **state,
            "final_report": final_report,
            "status": "complete",
            "messages": state.get("messages", []) + [response]
        }
        
    except Exception as e:
        logger.error("writer_agent_failed", error=str(e))
        return {
            **state,
            "status": "error",
            "error_message": f"Report writing failed: {str(e)}"
        }
