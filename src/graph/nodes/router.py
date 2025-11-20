"""
Router Agent Node with Parallel Sentiment Analysis
Classifies user intent and routes to appropriate specialized agent,
while simultaneously checking for escalation triggers.
"""

import asyncio
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

# System prompt for sentiment analysis
SENTIMENT_SYSTEM_PROMPT = """You are a sentiment analysis guardrail.
Analyze the user's message for hostility, extreme frustration, or legal threats.

Return a JSON object with:
- sentiment: "positive", "neutral", "negative", or "hostile"
- should_escalate: boolean (true ONLY if hostile, threatening, or mentioning suicide/emergency)
- reason: short explanation

Keywords for escalation: lawsuit, sue, police, lawyer, suicide, kill myself, emergency, bleeding heavily.
"""

async def router_node(state: AgentState) -> AgentState:
    """
    Router agent that classifies user intent and checks sentiment in parallel.
    
    Uses asyncio.gather to run both LLM calls simultaneously to minimize latency.
    """
    
    messages = state["messages"]
    if not messages:
        state["current_intent"] = "faq"
        state["next_agent"] = "faq"
        return state

    last_message = messages[-1].content.lower().strip()
    
    # ============================================
    # 1. Define Async Tasks
    # ============================================
    
    async def check_sentiment():
        """Task A: Analyze Sentiment"""
        try:
            response = await llm_router.ainvoke([
                SystemMessage(content=SENTIMENT_SYSTEM_PROMPT),
                HumanMessage(content=f"User message: {last_message}")
            ])
            # Parse the response (assuming LLM returns text, we might need to be robust)
            # For simplicity, we'll do basic string parsing if not JSON
            content = response.content.lower()
            
            should_escalate = "true" in content and ("hostile" in content or "emergency" in content)
            sentiment = "neutral"
            if "hostile" in content: sentiment = "hostile"
            elif "negative" in content: sentiment = "negative"
            elif "positive" in content: sentiment = "positive"
            
            return {
                "sentiment": sentiment,
                "should_escalate": should_escalate,
                "reason": "Detected hostility" if should_escalate else None
            }
        except Exception as e:
            print(f"Sentiment check failed: {e}")
            return {"sentiment": "neutral", "should_escalate": False, "reason": None}

    async def classify_intent():
        """Task B: Classify Intent (Existing Logic)"""
        
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
                    return "booking"

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
        return intent if intent in valid_intents else "faq"

    # ============================================
    # 2. Execute in Parallel
    # ============================================
    
    sentiment_result, intent_result = await asyncio.gather(check_sentiment(), classify_intent())
    
    # ============================================
    # 3. Merge & Decide
    # ============================================
    
    # Update state with sentiment info
    state["sentiment_score"] = sentiment_result["sentiment"]
    state["should_escalate"] = sentiment_result["should_escalate"]
    state["escalation_reason"] = sentiment_result["reason"]
    
    # Decision Logic: Escalation trumps everything
    if sentiment_result["should_escalate"]:
        state["current_intent"] = "escalate"
        state["next_agent"] = "human_handoff"  # Route to our new node
        state["escalated"] = True
    else:
        state["current_intent"] = intent_result
        state["next_agent"] = intent_result
        
        # Update ticket types
        if intent_result not in state.get("ticket_types", []):
            if "ticket_types" not in state:
                state["ticket_types"] = []
            state["ticket_types"].append(intent_result)

    return state
