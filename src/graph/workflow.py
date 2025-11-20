"""
LangGraph Workflow for Dental AI Agent
Defines the state graph and routing logic
"""

import uuid
from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes.sentiment import sentiment_node
from src.graph.nodes.intent import intent_node
from src.graph.nodes.decision import decision_node
from src.graph.nodes.faq_agent import faq_agent_node
from src.graph.nodes.booking_agent import booking_agent_node
from src.graph.nodes.management_agent import management_agent_node
from src.graph.nodes.placeholder import placeholder_node
from src.graph.nodes.human_handoff import human_handoff_node


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
        "management": "management_agent",
        "escalate": "human_handoff",
        "human_handoff": "human_handoff",
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
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("faq_agent", faq_agent_node)
    workflow.add_node("booking_agent", booking_agent_node)
    workflow.add_node("management_agent", management_agent_node)
    workflow.add_node("placeholder", placeholder_node)
    workflow.add_node("human_handoff", human_handoff_node)

    # Set entry point - Start goes to BOTH sentiment and intent in parallel
    workflow.set_entry_point("sentiment")
    workflow.set_entry_point("intent")
    
    # Both parallel nodes feed into decision
    workflow.add_edge("sentiment", "decision")
    workflow.add_edge("intent", "decision")

    # Add conditional routing from decision to specialized agents
    workflow.add_conditional_edges(
        "decision",
        route_to_agent,
        {
            "faq_agent": "faq_agent",
            "booking_agent": "booking_agent",
            "management_agent": "management_agent",
            "placeholder": "placeholder",
            "human_handoff": "human_handoff",
            END: END,
        }
    )

    # All agents flow to END
    workflow.add_edge("faq_agent", END)
    workflow.add_edge("booking_agent", END)
    workflow.add_edge("management_agent", END)
    workflow.add_edge("placeholder", END)
    workflow.add_edge("human_handoff", END)

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
