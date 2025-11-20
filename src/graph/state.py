"""
LangGraph State Schema for Dental AI Agent
This defines the shared state that flows through all agent nodes
"""

from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state for the dental clinic AI agent.

    This state is passed between all nodes in the LangGraph workflow.
    Using TypedDict ensures type safety and clear documentation.
    """

    # Conversation context
    messages: Annotated[list, add_messages]  # LangChain messages with automatic deduplication
    current_intent: Optional[str]  # Current classified intent: "faq", "booking", "management", "escalate"

    # Patient data (populated during conversation)
    patient_id: Optional[str]
    patient_name: Optional[str]
    patient_email: Optional[str]
    patient_phone: Optional[str]

    # Booking context (used by booking and management agents)
    selected_doctor_id: Optional[str]
    selected_doctor_name: Optional[str]
    selected_service_id: Optional[str]
    selected_service_name: Optional[str]
    selected_time_slot: Optional[str]  # ISO format datetime string
    appointment_id: Optional[str]  # For modifications/cancellations

    # Error handling
    error_count: int  # Track number of errors for graceful degradation
    last_error: Optional[str]  # Last error message for debugging

    # Support ticket tracking
    conversation_id: str  # Unique ID for this conversation session
    ticket_types: list[str]  # Array of ticket types: ["appointment_booking", "general_inquiry", etc.]
    escalated: bool  # Whether this conversation was escalated to human
    
    # Escalation Logic
    sentiment_score: Optional[str]  # "positive", "neutral", "negative", "hostile"
    escalation_reason: Optional[str]  # Why we are escalating
    should_escalate: bool  # Signal to override normal routing

    # Agent routing
    next_agent: Optional[str]  # Next agent to route to: "faq", "booking", "management", "end"
