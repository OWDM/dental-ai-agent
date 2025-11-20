"""
Intent Classification Node
Classifies user intent into functional categories.
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

4. **escalate** - Urgent issues or requests for human agent:
   - "I have severe pain right now"
   - "Dental emergency"
   - "My tooth is bleeding badly"
   - "I want to talk to a human"
   - "Connect me to an agent"
   - "I want to speak to a manager"

IMPORTANT: When in doubt, classify as "faq".

Respond with ONLY the category name: faq, booking, management, or escalate
"""

async def intent_node(state: AgentState) -> AgentState:
    """
    Classifies the user's intent.
    """
    messages = state["messages"]
    if not messages:
        return {"current_intent": "faq"}

    last_message = messages[-1].content.lower().strip()

    # Context-aware check (Synchronous part, fast)
    previous_intent = state.get("current_intent")
    if len(messages) >= 2:
        last_assistant_msg = None
        for msg in reversed(messages[:-1]):
            if hasattr(msg, 'type') and msg.type == 'ai':
                last_assistant_msg = msg.content.lower()
                break
        
        if previous_intent == "booking" and last_assistant_msg:
            booking_keywords = ["which doctor", "service you need", "preferred time", "date and time", 
                              "available doctors", "available services", "select the service"]
            if any(keyword in last_assistant_msg for keyword in booking_keywords):
                return {"current_intent": "booking"}

    # LLM Classification
    recent_messages = messages[-4:] if len(messages) > 4 else messages
    context = "\n".join([
        f"{'User' if hasattr(msg, 'type') and msg.type == 'human' else 'Assistant'}: {msg.content}"
        for msg in recent_messages[:-1]
    ])
    
    prompt = f"""Previous conversation:
{context}

Current user message: {last_message}

Based on the conversation context and the current message, classify the intent."""

    response = await llm_router.ainvoke([
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])
    
    intent = response.content.strip().lower()
    valid_intents = ["faq", "booking", "management", "escalate"]
    final_intent = intent if intent in valid_intents else "faq"
    
    # Update ticket types
    ticket_types = state.get("ticket_types", [])
    if final_intent not in ticket_types:
        ticket_types.append(final_intent)

    return {
        "current_intent": final_intent,
        "ticket_types": ticket_types
    }
