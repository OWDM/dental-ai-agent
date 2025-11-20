"""
Human Handoff Node
Handles escalation to a human agent.
"""

from langchain_core.messages import AIMessage
from src.graph.state import AgentState

def human_handoff_node(state: AgentState) -> AgentState:
    """
    Handles the handoff to a human agent.
    
    This node is triggered when:
    1. Sentiment analysis detects hostility
    2. Agents fail repeatedly (loop detection)
    3. Explicit user request
    """
    
    # Create the handoff message
    reason = state.get("escalation_reason", "Unknown reason")
    
    # In a real system, this would call an API (Zendesk, Intercom, etc.)
    # For now, we just return a confirmation message.
    
    handoff_msg = AIMessage(
        content="I've escalated your issue to a human specialist."
    )
    
    return {
        "messages": [handoff_msg],
        "escalated": True,
        "next_agent": "end"  # End the automated flow
    }
