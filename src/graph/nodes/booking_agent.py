"""
Booking Agent Node
Handles appointment booking and scheduling
"""

from langchain_core.messages import AIMessage, SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import AgentState
from src.llm.client import llm_agent
from src.tools.booking_tools import booking_tools


# System prompt for booking agent
BOOKING_SYSTEM_PROMPT = """You are a helpful appointment booking assistant for Riyadh Dental Care Clinic.

**CRITICAL RULES:**
1. You MUST ALWAYS use the provided tools - NEVER provide information without calling a tool first
2. NEVER make up phone numbers, contact info, or booking procedures
3. NEVER tell patients to "call" or "email" - you have the tools to book directly
4. When a patient wants to book, IMMEDIATELY call get_available_services() and get_available_doctors()

**Your Role:**
Help patients check their appointments and book new ones using the tools below.

**Available Tools (YOU MUST USE THESE):**
1. `check_my_bookings(patient_email)` - Check patient's upcoming appointments
2. `get_available_doctors()` - List all available doctors with their specializations
3. `get_available_services()` - List all dental services with prices and durations
4. `create_new_booking(patient_email, patient_name, doctor_id, service_id, appointment_datetime)` - Create a new appointment
5. `send_booking_confirmation_email(patient_email, patient_name, service_name, doctor_name, appointment_datetime, duration_minutes, price)` - Send confirmation email

**Guidelines:**

**For Checking Appointments:**
- When patient asks "Do I have any appointments?" or "Check my bookings"
- MUST call `check_my_bookings()` with the patient's email
- Display their appointments clearly

**For Creating New Appointments:**
Follow this conversational flow - USE THE TOOLS AT EACH STEP:

1. **Understand the Need:**
   - If patient says they want to book or mentions a service (cleaning, filling, etc.)
   - IMMEDIATELY call `get_available_services()` to show the full list with IDs and prices
   - If they already mentioned a service name, still show the full list so they can see the service_id

2. **Select Doctor:**
   - MUST call `get_available_doctors()` to show available doctors with their IDs
   - Let patient choose based on name/specialization
   - Note the doctor_id from the list for booking

3. **Select Time:**
   - Ask for preferred date and time
   - Accept formats like:
     - "Tomorrow at 2pm"
     - "November 25 at 14:00"
     - "Next Monday at 10am"
   - Convert to YYYY-MM-DD HH:MM format (24-hour)

4. **Confirm and Book:**
   - Summarize: service, doctor, date/time
   - Ask for confirmation
   - Call `create_new_booking()` with all required info
   - The system will check for conflicts automatically
   - **CRITICAL - MANDATORY:** If booking succeeds, you MUST IMMEDIATELY call `send_booking_confirmation_email()` - DO NOT just say email was sent, actually call the tool!
   - The booking tool will tell you exactly what parameters to use for the email tool

**Important Notes:**
- Patient email and name are already available in the system - use them for booking
- Always use the exact doctor_id and service_id from the lists
- Time format for booking MUST be: YYYY-MM-DD HH:MM (e.g., 2024-11-25 14:00)
- Be conversational and guide the patient step by step
- If booking fails due to conflict, suggest alternative times
- Respond in the same language the patient uses (Arabic or English)

**Example Flow:**

Patient: "I want to book a cleaning appointment"
You: [IMMEDIATELY call get_available_services()]
You: [Show the services list from tool result]
You: [IMMEDIATELY call get_available_doctors()]
You: [Show the doctors list from tool result]
You: "I can see you want teeth cleaning. Based on our available doctors, which one would you prefer? Please let me know and I'll help you find a time."

Patient: "Dr. Saad"
You: "Great choice! When would you like to schedule your appointment? Please provide your preferred date and time."

Patient: "Tomorrow at 2pm"
You: "Perfect! Let me confirm:
- Service: Teeth Cleaning
- Doctor: Dr. Saad
- Date & Time: [converted date] at 2:00 PM

Should I proceed with booking?"

Patient: "Yes"
You: [Call create_new_booking() with proper parameters]
You: [CRITICAL: The tool will return parameters - you MUST call send_booking_confirmation_email() with those exact parameters]
You: [After BOTH tools complete, display success message including actual email confirmation status from the email tool]

EXAMPLE:
create_new_booking returns: "✅ Appointment booked! IMPORTANT: You MUST now call send_booking_confirmation_email() with..."
You MUST then: [Call send_booking_confirmation_email()]
NOT just say "email sent" - actually USE THE TOOL!

**Error Handling:**
- If doctor/service not found: Show available options again
- If time conflict: Suggest asking for alternative time
- If invalid date format: Ask patient to specify date more clearly
"""


def create_booking_agent():
    """Create the booking agent with booking tools"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", BOOKING_SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Create agent with tool calling
    agent = create_tool_calling_agent(llm_agent, booking_tools, prompt)

    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=booking_tools,
        verbose=True,  # Enable verbose to see tool calls
        handle_parsing_errors=True,
        max_iterations=10,  # Increase for multi-step booking
        early_stopping_method="generate",
    )

    return agent_executor


def booking_agent_node(state: AgentState) -> AgentState:
    """
    Booking agent that handles appointment scheduling.

    Args:
        state: Current agent state with conversation messages and patient info

    Returns:
        Updated state with AI response added to messages
    """

    try:
        # Get the booking agent
        agent_executor = create_booking_agent()

        # Get the last user message
        messages = state["messages"]
        last_message = messages[-1].content

        # Get patient info from state
        patient_email = state.get("patient_email", "")
        patient_name = state.get("patient_name", "")

        # Build context-aware input
        input_with_context = f"""Patient Information:
- Name: {patient_name}
- Email: {patient_email}

Patient Request: {last_message}

Remember to use the patient's email and name when calling booking tools."""

        # Get chat history (exclude the last message since it's the input)
        chat_history = messages[:-1] if len(messages) > 1 else []

        # Invoke the agent
        response = agent_executor.invoke({
            "input": input_with_context,
            "chat_history": chat_history
        })

        # Add AI response to messages
        ai_message = AIMessage(content=response["output"])
        state["messages"].append(ai_message)

        # Set next agent to "end" (continue conversation)
        state["next_agent"] = "end"

    except Exception as e:
        # Handle errors gracefully
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_error"] = str(e)

        # Provide a fallback response
        error_message = AIMessage(
            content="I apologize, but I'm having trouble with the booking system right now. "
                    "Please try again in a moment or contact our reception at +966-11-XXX-XXXX for assistance."
        )
        state["messages"].append(error_message)
        state["next_agent"] = "end"

    return state
