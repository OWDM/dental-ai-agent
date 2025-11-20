"""
Sentiment Analysis Node
Guardrail that checks for hostility and emergencies.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from src.graph.state import AgentState
from src.llm.client import llm_router

# System prompt for sentiment analysis
SENTIMENT_SYSTEM_PROMPT = """You are a sentiment analysis guardrail.
Analyze the user's message for hostility, extreme frustration, or legal threats.

Return a JSON object with:
- sentiment: "positive", "neutral", "negative", or "hostile"
- should_escalate: boolean (true ONLY if hostile, threatening, or mentioning suicide/emergency)
- reason: short explanation

Keywords for escalation: lawsuit, sue, police, lawyer, suicide, kill myself, emergency, bleeding heavily.
"""

async def sentiment_node(state: AgentState) -> AgentState:
    """
    Analyzes sentiment and checks for escalation triggers.
    """
    messages = state["messages"]
    if not messages:
        return {"sentiment_score": "neutral", "should_escalate": False}

    last_message = messages[-1].content.lower().strip()
    
    try:
        response = await llm_router.ainvoke([
            SystemMessage(content=SENTIMENT_SYSTEM_PROMPT),
            HumanMessage(content=f"User message: {last_message}")
        ])
        
        content = response.content.lower()
        should_escalate = "true" in content and ("hostile" in content or "emergency" in content)
        sentiment = "neutral"
        if "hostile" in content: sentiment = "hostile"
        elif "negative" in content: sentiment = "negative"
        elif "positive" in content: sentiment = "positive"
        
        return {
            "sentiment_score": sentiment,
            "should_escalate": should_escalate,
            "escalation_reason": "Detected hostility" if should_escalate else None
        }
    except Exception as e:
        print(f"Sentiment check failed: {e}")
        return {"sentiment_score": "neutral", "should_escalate": False}
