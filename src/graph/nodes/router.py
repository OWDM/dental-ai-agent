"""
Router Agent Node
Classifies user intent and routes to appropriate specialized agent
"""

from langchain_core.messages import HumanMessage, SystemMessage
from src.graph.state import AgentState
from src.llm.client import llm_router


# System prompt for intent classification
ROUTER_SYSTEM_PROMPT = """You are an intent classification expert for a dental clinic AI customer service system.

Your ONLY job is to analyze the user's message and classify their intent into ONE of these categories:

1. **faq** - General questions about the clinic (DEFAULT for greetings and unclear queries):
   - Greetings: "hi", "hello", "hey"
   - Simple thanks: "thank you", "thanks", "great", "ok"
   - Business hours, location, contact information
   - Services offered and pricing
   - Insurance coverage and payment policies
   - Dental procedures information
   - Parking and facility questions
   - Any general conversation or unclear intent

2. **booking** - Appointment booking requests (ONLY when explicitly requesting to book):
   - "I want to book an appointment"
   - "Schedule a visit"
   - "I need to see a dentist"
   - Asking about available time slots

3. **management** - Modify or cancel existing appointments (ONLY for existing appointments):
   - "Change my appointment"
   - "Cancel my booking"
   - "Reschedule my visit"
   - "What are my upcoming appointments?"

4. **feedback** - Feedback, complaints, or compliments (ONLY when providing detailed feedback):
   - Service quality issues
   - Staff interaction concerns
   - Facility problems
   - Detailed positive feedback about specific experiences
   - Complaints about delays or treatment
   - NOTE: Simple "thank you" should be classified as "faq", not "feedback"

5. **escalate** - ONLY for urgent medical emergencies:
   - "I have severe pain right now"
   - "Dental emergency"
   - "My tooth is bleeding badly"
   - DO NOT use for general questions or greetings

IMPORTANT: When in doubt, classify as "faq". Only use "escalate" for true emergencies.

Respond with ONLY the category name: faq, booking, management, feedback, or escalate

Examples:
User: "hey"
Response: faq

User: "hello"
Response: faq

User: "thank you"
Response: faq

User: "wow great! thank you!"
Response: faq

User: "What are your business hours?"
Response: faq

User: "I want to book a teeth cleaning appointment"
Response: booking

User: "i wanna book"
Response: booking

User: "I need to see a dentist"
Response: booking

User: "I need to cancel my appointment tomorrow"
Response: management

User: "The service was excellent, Dr. Ahmed was very professional"
Response: feedback

User: "The receptionist was rude to me"
Response: feedback

User: "I have severe tooth pain right now!"
Response: escalate
"""


def router_node(state: AgentState) -> AgentState:
    """
    Router agent that classifies user intent and determines next agent.

    Uses LLM for all intent classification to ensure accurate routing.

    Args:
        state: Current agent state with conversation messages

    Returns:
        Updated state with current_intent and next_agent set
    """

    # Get the last user message
    messages = state["messages"]
    if not messages:
        state["current_intent"] = "faq"
        state["next_agent"] = "faq"
        return state

    last_message = messages[-1].content.lower().strip()

    # ============================================
    # Context-aware routing: Check if we're continuing a conversation
    # ============================================
    # If there are previous messages, check if we're in the middle of a booking/management flow
    previous_intent = state.get("current_intent")

    # Check if the last assistant message suggests we're waiting for user input in booking/management
    if len(messages) >= 2:
        last_assistant_msg = None
        for msg in reversed(messages[:-1]):  # Look at messages before the current user message
            if hasattr(msg, 'type') and msg.type == 'ai':
                last_assistant_msg = msg.content.lower()
                break

        # If booking agent just asked for details (doctor, service, time), stay in booking
        if previous_intent == "booking" and last_assistant_msg:
            booking_keywords = ["which doctor", "service you need", "preferred time", "date and time",
                              "available doctors", "available services", "select the service"]
            if any(keyword in last_assistant_msg for keyword in booking_keywords):
                # User is responding to booking questions - stay in booking
                state["current_intent"] = "booking"
                state["next_agent"] = "booking"
                return state

    # ============================================
    # Use LLM for intent classification with conversation context
    # ============================================
    # Build context from recent messages (last 4 messages for context)
    recent_messages = messages[-4:] if len(messages) > 4 else messages
    context = "\n".join([
        f"{'User' if hasattr(msg, 'type') and msg.type == 'human' else 'Assistant'}: {msg.content}"
        for msg in recent_messages[:-1]  # Exclude the current message
    ])

    prompt = f"""Previous conversation:
{context}

Current user message: {last_message}

Based on the conversation context and the current message, classify the intent."""

    response = llm_router.invoke([
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])

    intent = response.content.strip().lower()

    # Validate intent
    valid_intents = ["faq", "booking", "management", "feedback", "escalate"]
    if intent not in valid_intents:
        intent = "faq"  # Default to FAQ if classification fails

    # Update state
    state["current_intent"] = intent
    state["next_agent"] = intent

    # Update ticket types if not already present
    if intent not in state.get("ticket_types", []):
        if "ticket_types" not in state:
            state["ticket_types"] = []
        state["ticket_types"].append(intent)

    return state
