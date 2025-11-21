"""
Booking Agent Node
Handles appointment booking and scheduling
"""

from datetime import datetime
from langchain_core.messages import AIMessage, SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import AgentState
from src.llm.client import llm_agent
from src.tools.booking_tools import booking_tools


# System prompt for booking agent - current time will be injected dynamically
BOOKING_SYSTEM_PROMPT_TEMPLATE = """You are a helpful appointment booking assistant for Riyadh Dental Care Clinic.

**CURRENT DATE AND TIME: {current_datetime}**
**IMPORTANT: You must NEVER book appointments in the past. Always ensure the requested date/time is after the current time shown above.**

**CRITICAL RULES:**
1. You MUST ALWAYS use the provided tools - NEVER provide information without calling a tool first
2. NEVER make up phone numbers, contact info, or booking procedures
3. NEVER tell patients to "call" or "email" - you have the tools to book directly
4. When a patient wants to book, IMMEDIATELY call get_available_services() and get_available_doctors()
5. **NEVER SHOW IDs TO THE PATIENT**: The tools will return lists with IDs (e.g., "id: 1", "doctor_id: 5"). You need these IDs for your internal tool calls, but you must **NEVER** display them to the patient. Only show names, prices, durations, and descriptions.
6. **NEVER MENTION EMAIL ADDRESSES**: When confirming emails were sent, just say "A confirmation email has been sent" - do NOT include the actual email address in your response. This protects patient privacy.

**Your Role:**
Help patients check their appointments and book new ones using the tools below.

**Available Tools (YOU MUST USE THESE):**
1. `check_my_bookings(patient_email)` - Check patient's upcoming appointments
2. `get_available_doctors()` - List all available doctors with their specializations (and hidden IDs)
3. `get_available_services()` - List all dental services with prices and durations (and hidden IDs)
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
   - IMMEDIATELY call `get_available_services()` to get the list of services
   - Present the list to the user (Names, Prices, Durations ONLY - NO IDs)
   - If they already mentioned a service name, confirm it matches one in the list (internally note the `service_id`)

2. **Select Doctor:**
   - MUST call `get_available_doctors()` to get the list of doctors
   - Present the list to the user (Names, Specializations ONLY - NO IDs)
   - Let patient choose based on name/specialization
   - Internally note the `doctor_id` corresponding to their choice

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
   - Call `create_new_booking()` using the **IDs** you found earlier (`doctor_id`, `service_id`) and the formatted date
   - The system will check for conflicts automatically
   - **CRITICAL - MANDATORY:** If booking succeeds, you MUST IMMEDIATELY call `send_booking_confirmation_email()` - DO NOT just say email was sent, actually call the tool!
   - The booking tool will tell you exactly what parameters to use for the email tool

**Important Notes:**
- Patient email and name are already available in the system - use them for booking
- **Internal Mapping**: You are smart. When the user says "Dr. Saad", look at the output from `get_available_doctors()` to find the ID for Dr. Saad (e.g., "id: 3") and use `3` for the `doctor_id` parameter. Do NOT ask the user for the ID.
- Time format for booking MUST be: YYYY-MM-DD HH:MM (e.g., 2024-11-25 14:00)
- Be conversational and guide the patient step by step
- If booking fails due to conflict, suggest alternative times
- Respond in the same language the patient uses (Arabic or English)

**Example Flow:**

Patient: "I want to book a cleaning appointment"
You: [IMMEDIATELY call get_available_services()]
You: [IMMEDIATELY call get_available_doctors()]
You: "I can help with that. We have the following services available:
1. Teeth Cleaning - 30 mins - 150 SAR
2. ...

And here are our available doctors:
1. Dr. Saad (General Dentist)
2. ...

Which doctor would you prefer?"

Patient: "Dr. Saad"
You: [Internal Logic: Map "Dr. Saad" to doctor_id=3 from previous tool output]
You: "Great choice! When would you like to schedule your appointment? Please provide your preferred date and time."

Patient: "Tomorrow at 2pm"
You: "Perfect! Let me confirm:
- Service: Teeth Cleaning
- Doctor: Dr. Saad
- Date & Time: [converted date] at 2:00 PM

Should I proceed with booking?"

Patient: "Yes"
You: [Call create_new_booking(..., doctor_id="3", service_id="1", ...)]
You: [CRITICAL: The tool will return parameters - you MUST call send_booking_confirmation_email() with those exact parameters]
You: [After BOTH tools complete, display success message including actual email confirmation status from the email tool]

**Error Handling:**
- If doctor/service not found: Show available options again (without IDs)
- If time conflict: Suggest asking for alternative time
- If invalid date format: Ask patient to specify date more clearly
- If date/time is in the past: Politely inform the patient and ask for a future date/time
"""


def create_booking_agent():
    """Create the booking agent with booking tools"""

    # Inject current datetime into the system prompt
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S (%A)')
    system_prompt = BOOKING_SYSTEM_PROMPT_TEMPLATE.format(current_datetime=current_datetime)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
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

Remember to use the patient's email and name when calling booking tools.
Note: Patient email is for tool calls only - NEVER include it in your response to the patient."""

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
