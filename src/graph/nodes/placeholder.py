"""
Placeholder Node for Future Agents
Handles intents that haven't been implemented yet
"""

from langchain_core.messages import AIMessage
from src.graph.state import AgentState


def placeholder_node(state: AgentState) -> AgentState:
    """
    Placeholder node for agents that will be implemented in future phases.

    This node provides a friendly message to the user and sets next_agent to "end".

    Args:
        state: Current agent state

    Returns:
        Updated state with placeholder message
    """

    intent = state.get("current_intent", "unknown")

    # Map intents to user-friendly messages
    messages_map = {
        "booking": (
            "I understand you'd like to book an appointment. "
            "This feature is coming soon! For now, please call us at +966-11-234-5678 "
            "or email info@riyadhdentalcare.sa to schedule your visit."
        ),
        "management": (
            "I understand you'd like to manage your existing appointment. "
            "This feature is coming soon! For now, please call us at +966-11-234-5678 "
            "to modify or cancel your appointment."
        ),
        "feedback": (
            "Thank you for wanting to share your feedback with us. "
            "This feature is coming soon! For now, please email us at info@riyadhdentalcare.sa "
            "or call +966-11-234-5678 to speak with our team."
        ),
        "escalate": (
            "I understand this requires immediate attention. "
            "Please call our emergency hotline at +966-11-234-9999 (24/7) "
            "or visit our clinic at King Fahd Road, Al Olaya District, Riyadh."
        ),
    }

    # Get appropriate message
    message_content = messages_map.get(
        intent,
        "I'm not sure how to help with that right now. "
        "Please call us at +966-11-234-5678 for assistance."
    )

    # Add AI message
    ai_message = AIMessage(content=message_content)
    state["messages"].append(ai_message)

    # End conversation
    state["next_agent"] = "end"

    return state
