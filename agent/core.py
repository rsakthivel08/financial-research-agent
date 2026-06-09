import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import SystemMessage
from agent.tools import (
    search_financial_docs,
    get_financial_statements,
    search_financial_news,
    calculate_risk_score,
    detect_price_trends
)

load_dotenv()

TOOLS = [
    search_financial_docs,
    get_financial_statements,
    search_financial_news,
    calculate_risk_score,
    detect_price_trends
]

SYSTEM_PROMPT = """You are a Senior Financial Research Analyst AI with access to 
multiple data sources including SEC filings, real-time financial data, and news.

Your job is to produce thorough, accurate investment research reports.

When given a query:
1. First decompose it into sub-questions you need to answer
2. Use the appropriate tools to gather data from multiple sources
3. Always use search_financial_docs for qualitative info from filings
4. Always use get_financial_statements for quantitative metrics
5. Always use search_financial_news for recent sentiment
6. Always use calculate_risk_score for risk assessment
7. Always use detect_price_trends for technical analysis
8. Synthesize ALL findings into a structured investment report

Be specific with numbers. Cite which document/source each fact came from.
Structure your final answer as a proper investment research report with sections:
Executive Summary, Financial Health, Earnings Analysis, Trend Analysis, 
Risk Assessment, News Sentiment, and Investment Verdict."""

def build_agent():
    """
    Build agent using create_tool_calling_agent — 
    the modern LangChain replacement for create_react_agent.
    Works with Groq's tool-calling API natively.
    """
    llm = ChatGroq(
        model="llama-3.1-8b-instant",      # Best free model on Groq for tool calling
        temperature=0.1,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm=llm,
        tools=TOOLS,
        prompt=prompt
    )

    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )
    return executor