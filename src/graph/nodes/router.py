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
   - Greetings: "hi", "hello", "hey", "السلام عليكم"
   - Simple thanks: "thank you", "thanks", "شكرا", "great", "ok"
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

    Uses a hybrid approach:
    1. Fast pattern matching for obvious cases (greetings, thanks, etc.)
    2. LLM classification for complex queries

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
    # FAST PATH: Pattern matching for obvious cases
    # ============================================

    # Greetings and simple interactions (FAQ)
    greetings = ["hi", "hello", "hey", "مرحبا", "السلام عليكم", "السلام", "هلا", "اهلا"]
    thanks = ["thank", "thanks", "شكرا", "شكراً", "تسلم", "great", "good", "ok", "okay"]

    # Check for greetings
    if any(greeting in last_message.split() for greeting in greetings):
        intent = "faq"

    # Check for thanks
    elif any(thank in last_message for thank in thanks):
        intent = "faq"

    # Booking keywords (very explicit)
    elif any(keyword in last_message for keyword in ["book", "حجز", "موعد", "schedule", "appointment"]):
        # Check if it's asking about how to book vs actually booking
        if any(word in last_message for word in ["want", "need", "i'd like", "أريد", "ابغى", "ودي"]):
            intent = "booking"
        else:
            intent = "faq"  # Just asking about booking process

    # Cancel/modify keywords
    elif any(keyword in last_message for keyword in ["cancel", "إلغاء", "modify", "change", "reschedule", "تغيير", "تعديل"]):
        intent = "management"

    # Emergency keywords
    elif any(keyword in last_message for keyword in ["emergency", "urgent", "pain", "bleeding", "طوارئ", "ألم", "نزيف"]):
        if any(word in last_message for word in ["severe", "bad", "شديد", "قوي", "now", "الآن"]):
            intent = "escalate"
        else:
            intent = "faq"  # General question about pain

    # Complaint keywords (detailed feedback)
    elif any(keyword in last_message for keyword in ["rude", "bad service", "complaint", "شكوى", "سيء", "terrible"]):
        intent = "feedback"

    else:
        # ============================================
        # SLOW PATH: Use LLM for complex queries
        # ============================================
        response = llm_router.invoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=f"Classify this message: {last_message}")
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
