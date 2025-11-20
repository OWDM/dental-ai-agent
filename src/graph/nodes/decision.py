"""
Decision Node
Merges results from Sentiment and Intent nodes and decides routing.
"""

from src.graph.state import AgentState
from langgraph.graph import END

def decision_node(state: AgentState) -> AgentState:
    """
    Decides the next agent based on sentiment and intent results.
    This node doesn't call an LLM, it just applies logic.
    """
    
    should_escalate = state.get("should_escalate", False)
    current_intent = state.get("current_intent", "faq")
    
    # Logic: Escalation trumps everything
    if should_escalate:
        next_agent = "human_handoff"
        state["current_intent"] = "escalate"
        state["escalated"] = True
    elif current_intent == "escalate":
        next_agent = "human_handoff"
        state["escalated"] = True
    else:
        next_agent = current_intent
        
    return {"next_agent": next_agent}
