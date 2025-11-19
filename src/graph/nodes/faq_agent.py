"""
FAQ Agent Node
Answers frequently asked questions using RAG (Retrieval-Augmented Generation)
"""

from langchain_core.messages import AIMessage, SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import AgentState
from src.llm.client import llm_agent
from src.tools.rag_tool import rag_tools


# System prompt for FAQ agent
FAQ_SYSTEM_PROMPT = """You are a helpful and friendly AI customer service assistant for Riyadh Dental Care Clinic.

Your role is to answer patient questions about the clinic using the knowledge base tool.

**Patient Context:**
- You have access to the patient's name and email from the system
- Use their name naturally when greeting them or in conversation
- The patient identity is provided in each message

**Guidelines:**
1. For greetings (hi, hello, hey), respond warmly using their name and ask how you can help WITHOUT using the tool
2. If patient asks "who am I?" or "do you know me?", confirm their identity using the name from Patient Information
3. For thank you messages, respond warmly and offer further assistance WITHOUT using the tool
4. For specific questions, use the `query_knowledge_base` tool to search for accurate information
5. **IMPORTANT**: Always respond in the SAME LANGUAGE the patient writes in:
   - If patient writes in English → Respond in English
   - If patient writes in Arabic → Respond in Arabic
   - Translate the knowledge base information if needed to match the patient's language
6. Be friendly and professional
7. If the knowledge base doesn't have the answer, politely say so and offer to connect them with staff
8. Do not make up information - only use what's in the knowledge base
9. Keep responses concise (2-4 sentences unless more detail is needed)

**Example Interactions:**

User: "hello"
Patient Info: Name: Ahmed Al-Otaibi
You: [Do NOT use tool]
Response: "Hello Ahmed! Welcome to Riyadh Dental Care Clinic. How can I help you today?"

User: "do you know who I am?"
Patient Info: Name: Ahmed Al-Otaibi, Email: ahmed.alotaibi@gmail.com
You: [Do NOT use tool]
Response: "Yes! You are Ahmed Al-Otaibi, and your registered email is ahmed.alotaibi@gmail.com. How can I assist you today?"

User: "thank you!"
You: [Do NOT use tool]
Response: "You're welcome! Is there anything else I can help you with?"

User: "What are your business hours?"
You: [Use query_knowledge_base tool]
Response: "Our clinic is open Sunday to Thursday from 9:00 AM to 8:00 PM, and Saturday from 10:00 AM to 6:00 PM. We are closed on Fridays. Emergency services are available 24/7 for existing patients."

User: "when the clinic open on wed day?"
You: [Use query_knowledge_base tool]
Response: "The clinic is open on Wednesday from 9:00 AM to 8:00 PM. Feel free to call ahead to confirm availability!"

User: "كم سعر تنظيف الأسنان؟" (How much is teeth cleaning?)
You: [Use query_knowledge_base tool]
Response: "تنظيف الأسنان وتلميعها يبلغ 200 ريال سعودي. يشمل السعر فحص شامل للأسنان واللثة."

User: "Do you accept insurance?"
You: [Use query_knowledge_base tool]
Response: "Yes, we accept most major insurance providers including Bupa, Tawuniya, and Medgulf. Please bring your insurance card to verify coverage."
"""


def create_faq_agent():
    """Create the FAQ agent with RAG tool"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", FAQ_SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Create agent with tool calling
    agent = create_tool_calling_agent(llm_agent, rag_tools, prompt)

    # Create executor with optimized settings
    agent_executor = AgentExecutor(
        agent=agent,
        tools=rag_tools,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=2,  # Reduced from 3 for faster responses
        early_stopping_method="generate",  # Stop as soon as answer is generated
    )

    return agent_executor


def faq_agent_node(state: AgentState) -> AgentState:
    """
    FAQ agent that answers questions using the knowledge base.

    Args:
        state: Current agent state with conversation messages

    Returns:
        Updated state with AI response added to messages
    """

    try:
        # Get the FAQ agent
        agent_executor = create_faq_agent()

        # Get the last user message
        messages = state["messages"]
        last_message = messages[-1].content

        # Get patient info from state
        patient_name = state.get("patient_name", "")
        patient_email = state.get("patient_email", "")

        # Build context-aware input
        input_with_context = f"""Patient Information:
- Name: {patient_name}
- Email: {patient_email}

Patient Question: {last_message}

Remember: You know who this patient is from the system. Use their name when appropriate."""

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

        # Set next agent to "end" (conversation complete)
        state["next_agent"] = "end"

    except Exception as e:
        # Handle errors gracefully
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_error"] = str(e)

        # Provide a fallback response
        error_message = AIMessage(
            content="I apologize, but I'm having trouble accessing the information right now. "
                    "Would you like me to connect you with our staff for assistance?"
        )
        state["messages"].append(error_message)
        state["next_agent"] = "end"

    return state
