"""
Planner Agent - Breaks down research topics into focused sub-questions

Uses Gemini LLM to analyze the research query and generate 3-5 searchable sub-questions
"""

import structlog
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import get_settings
from app.agents.state import ResearchState

logger = structlog.get_logger()

PLANNER_SYSTEM_PROMPT = """You are an expert research planner. Your job is to break down complex research topics into focused, searchable sub-questions.

RULES:
1. Generate exactly 3-5 sub-questions
2. Each sub-question should be specific and searchable
3. Sub-questions should cover different aspects of the topic
4. Questions should be answerable through web search
5. Avoid yes/no questions - ask for information
6. Order questions from foundational to advanced

OUTPUT FORMAT (strictly follow):
RESEARCH PLAN: [One sentence describing the overall research strategy]

SUB-QUESTIONS:
1. [First focused question]
2. [Second focused question]
3. [Third focused question]
4. [Fourth focused question (if needed)]
5. [Fifth focused question (if needed)]

EXAMPLE:
Query: "AI regulations in EU vs US"

RESEARCH PLAN: Compare regulatory frameworks, enforcement mechanisms, and business impacts of AI regulations in the European Union and United States.

SUB-QUESTIONS:
1. What are the key AI regulations currently in effect in the European Union?
2. What are the key AI regulations currently in effect in the United States?
3. How do EU and US AI regulations differ in their approach to data privacy and algorithmic transparency?
4. What are the compliance requirements and penalties for businesses under EU vs US AI regulations?
5. What are the practical impacts of these regulations on AI companies operating in both regions?
"""


def create_planner_agent() -> ChatGoogleGenerativeAI:
    """
    Create the planner LLM instance
    
    Returns:
        ChatGoogleGenerativeAI: Configured Gemini LLM
    """
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        google_api_key=settings.google_api_key,
    )


async def planner_node(state: ResearchState) -> ResearchState:
    """
    Planner agent node - breaks down research query into sub-questions
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with research_plan and sub_questions
    """
    logger.info("planner_agent_started", query=state["original_query"])
    
    try:
        llm = create_planner_agent()
        
        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"Research Query: {state['original_query']}")
        ]
        
        response = await llm.ainvoke(messages)
        response_text = response.content
        
        # Parse response
        research_plan, sub_questions = parse_planner_output(response_text)
        
        logger.info(
            "planner_agent_completed",
            num_sub_questions=len(sub_questions),
            plan=research_plan
        )
        
        return {
            **state,
            "research_plan": research_plan,
            "sub_questions": sub_questions,
            "status": "searching",
            "messages": state.get("messages", []) + [response]
        }
        
    except Exception as e:
        logger.error("planner_agent_failed", error=str(e))
        return {
            **state,
            "status": "error",
            "error_message": f"Planning failed: {str(e)}"
        }


def parse_planner_output(response: str) -> tuple[str, List[str]]:
    """
    Parse planner LLM output to extract research plan and sub-questions
    
    Args:
        response: Raw LLM response
        
    Returns:
        Tuple of (research_plan, sub_questions_list)
    """
    lines = response.strip().split("\n")
    
    research_plan = ""
    sub_questions = []
    
    in_questions_section = False
    
    for line in lines:
        line = line.strip()
        
        # Extract research plan
        if line.startswith("RESEARCH PLAN:"):
            research_plan = line.replace("RESEARCH PLAN:", "").strip()
        
        # Detect sub-questions section
        if line.startswith("SUB-QUESTIONS:"):
            in_questions_section = True
            continue
        
        # Extract sub-questions (numbered lines)
        if in_questions_section and line:
            # Remove numbering (1., 2., etc.)
            if line[0].isdigit():
                question = line.split(".", 1)[1].strip() if "." in line else line
                sub_questions.append(question)
    
    # Validation
    if not research_plan:
        research_plan = "Comprehensive research on the given topic"
    
    if len(sub_questions) < 3:
        raise ValueError(f"Planner generated insufficient sub-questions: {len(sub_questions)}")
    
    return research_plan, sub_questions[:5]  # Max 5 questions
