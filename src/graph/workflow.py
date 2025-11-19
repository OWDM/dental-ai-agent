"""
LangGraph Workflow for Dental AI Agent
Defines the state graph and routing logic
"""

import uuid
from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes.router import router_node
from src.graph.nodes.faq_agent import faq_agent_node
from src.graph.nodes.booking_agent import booking_agent_node
from src.graph.nodes.placeholder import placeholder_node


def route_to_agent(state: AgentState) -> str:
    """
    Routing function that determines which agent to execute next.

    This is called by LangGraph's conditional_edges to route based on
    the router's classification.

    Args:
        state: Current agent state with next_agent set by router

    Returns:
        Name of the next node to execute
    """
    next_agent = state.get("next_agent", "end")

    # Map intents to node names
    routing_map = {
        "faq": "faq_agent",
        "booking": "booking_agent",
        "management": "placeholder",
        "feedback": "placeholder",
        "escalate": "placeholder",
        "end": END,
    }

    return routing_map.get(next_agent, END)


def create_workflow():
    """
    Create the LangGraph workflow for the dental AI agent.

    Workflow structure (Phase 1):
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         v
    ┌─────────┐
    │ Router  │  (Classify intent)
    └────┬────┘
         │
    ┌────┴─────────┬──────────┬───────────┐
    │              │          │           │
    v              v          v           v
┌─────────┐  ┌──────────┐  ┌─────────┐  ...
│FAQ Agent│  │Placeholder│ │Placeholder│
└────┬────┘  └────┬─────┘  └────┬────┘
     │            │             │
     └────────────┴─────────────┘
                  │
                  v
               ┌─────┐
               │ END │
               └─────┘

    Returns:
        Compiled LangGraph application
    """

    # Initialize the state graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("faq_agent", faq_agent_node)
    workflow.add_node("booking_agent", booking_agent_node)
    workflow.add_node("placeholder", placeholder_node)

    # Set entry point
    workflow.set_entry_point("router")

    # Add conditional routing from router to specialized agents
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "faq_agent": "faq_agent",
            "booking_agent": "booking_agent",
            "placeholder": "placeholder",
            END: END,
        }
    )

    # All agents flow to END
    workflow.add_edge("faq_agent", END)
    workflow.add_edge("booking_agent", END)
    workflow.add_edge("placeholder", END)

    # Compile the graph
    app = workflow.compile()

    return app


def initialize_state(conversation_id: str = None) -> AgentState:
    """
    Initialize a new conversation state.

    Args:
        conversation_id: Optional conversation ID (generates UUID if not provided)

    Returns:
        Initialized AgentState dictionary
    """
    return {
        "messages": [],
        "current_intent": None,
        "patient_id": None,
        "patient_name": None,
        "patient_email": None,
        "patient_phone": None,
        "selected_doctor_id": None,
        "selected_doctor_name": None,
        "selected_service_id": None,
        "selected_service_name": None,
        "selected_time_slot": None,
        "appointment_id": None,
        "error_count": 0,
        "last_error": None,
        "conversation_id": conversation_id or str(uuid.uuid4()),
        "ticket_types": [],
        "escalated": False,
        "next_agent": None,
    }
