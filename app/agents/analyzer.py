"""
Analyzer Agent - Synthesizes search results into structured insights

Uses Gemini LLM to analyze search results, extract key findings, and track citations
"""

import structlog
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import get_settings
from app.agents.state import ResearchState, Citation

logger = structlog.get_logger()

ANALYZER_SYSTEM_PROMPT = """You are an expert research analyst. Your job is to synthesize search results into coherent insights with proper citations.

RULES:
1. Extract 5-10 key findings from the search results
2. Synthesize information across multiple sources
3. Track citations for each claim
4. Identify patterns, agreements, and contradictions
5. Prioritize recent and authoritative sources
6. Be objective and balanced

OUTPUT FORMAT (strictly follow):
KEY FINDINGS:
1. [Finding with context]
2. [Finding with context]
...

CITATIONS:
[URL1] - [Title1] - "[Relevant quote or paraphrase]"
[URL2] - [Title2] - "[Relevant quote or paraphrase]"
...

SYNTHESIS:
[2-3 paragraphs synthesizing the key insights, patterns, and conclusions]
"""


def create_analyzer_agent() -> ChatGoogleGenerativeAI:
    """
    Create the analyzer LLM instance
    
    Returns:
        ChatGoogleGenerativeAI: Configured Gemini LLM with lower temperature for factual analysis
    """
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=0.2,  # Lower temperature for factual analysis
        google_api_key=settings.google_api_key,
    )


async def analyzer_node(state: ResearchState) -> ResearchState:
    """
    Analyzer agent node - synthesizes search results into insights
    
    Args:
        state: Current research state with search_results
        
    Returns:
        Updated state with key_findings, citations, synthesis
    """
    logger.info("analyzer_agent_started", total_sources=state["total_sources"])
    
    try:
        llm = create_analyzer_agent()
        
        # Format search results for the LLM
        formatted_results = format_search_results_for_analysis(state)
        
        messages = [
            SystemMessage(content=ANALYZER_SYSTEM_PROMPT),
            HumanMessage(content=f"""Original Query: {state['original_query']}

Research Plan: {state['research_plan']}

Search Results:
{formatted_results}

Analyze these results and provide key findings with citations.""")
        ]
        
        response = await llm.ainvoke(messages)
        response_text = response.content
        
        # Parse response for findings and synthesis only
        key_findings, _, synthesis = parse_analyzer_output(response_text)
        
        # Build citations directly from the original search results
        # to guarantee real, working URLs (LLM tends to corrupt URLs)
        citations = []
        seen_urls = set()
        for question, results in state["search_results"].items():
            for result in results:
                if result.url and result.url not in seen_urls:
                    seen_urls.add(result.url)
                    citations.append(Citation(
                        source_url=result.url,
                        source_title=result.title,
                        quote=result.content[:150] if result.content else "",
                        relevance="high"
                    ))
        
        logger.info(
            "analyzer_agent_completed",
            num_findings=len(key_findings),
            num_citations=len(citations)
        )
        
        return {
            **state,
            "key_findings": key_findings,
            "citations": citations,
            "synthesis": synthesis,
            "status": "writing",
            "messages": state.get("messages", []) + [response]
        }
        
    except Exception as e:
        logger.error("analyzer_agent_failed", error=str(e))
        return {
            **state,
            "status": "error",
            "error_message": f"Analysis failed: {str(e)}"
        }


def format_search_results_for_analysis(state: ResearchState) -> str:
    """
    Format search results into readable text for LLM analysis
    
    Args:
        state: Research state containing search results
        
    Returns:
        Formatted string of search results
    """
    formatted = []
    
    for question, results in state["search_results"].items():
        formatted.append(f"\n### Sub-Question: {question}\n")
        
        for idx, result in enumerate(results, 1):
            content_preview = result.content[:500] if len(result.content) > 500 else result.content
            formatted.append(f"""
**Source {idx}:**
- Title: {result.title}
- URL: {result.url}
- Content: {content_preview}...
- Relevance: {result.relevance_score:.2f}
""")
    
    return "\n".join(formatted)


def parse_analyzer_output(response: str) -> tuple[List[str], List[Citation], str]:
    """
    Parse analyzer LLM output to extract findings, citations, and synthesis
    
    Args:
        response: Raw LLM response
        
    Returns:
        Tuple of (key_findings, citations, synthesis)
    """
    lines = response.strip().split("\n")
    
    key_findings = []
    citations = []
    synthesis = ""
    
    current_section = None
    synthesis_lines = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("KEY FINDINGS:"):
            current_section = "findings"
            continue
        elif line.startswith("CITATIONS:"):
            current_section = "citations"
            continue
        elif line.startswith("SYNTHESIS:"):
            current_section = "synthesis"
            continue
        
        if current_section == "findings" and line and line[0].isdigit():
            finding = line.split(".", 1)[1].strip() if "." in line else line
            key_findings.append(finding)
        
        elif current_section == "citations" and line and line.startswith("["):
            # Parse: [URL] - [Title] - "[Quote]"
            try:
                parts = line.split(" - ", 2)
                if len(parts) >= 3:
                    url = parts[0].strip("[]")
                    title = parts[1].strip()
                    quote = parts[2].strip('"')
                    
                    citation = Citation(
                        source_url=url,
                        source_title=title,
                        quote=quote,
                        relevance="high"
                    )
                    citations.append(citation)
            except Exception:
                # Skip malformed citations
                continue
        
        elif current_section == "synthesis" and line:
            synthesis_lines.append(line)
    
    synthesis = "\n\n".join(synthesis_lines)
    
    return key_findings, citations, synthesis
