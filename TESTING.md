# Phase 1 Testing Guide - Router + FAQ Agent

## What's Implemented

✅ **Router Agent** - Classifies user intent (faq, booking, management, feedback, escalate)
✅ **FAQ Agent** - Answers questions using RAG (ChromaDB knowledge base)
✅ **LangGraph Workflow** - Hierarchical routing architecture
✅ **CLI Interface** - Interactive chat for testing

## Prerequisites

1. **Python Environment**
   ```bash
   # Activate your virtual environment
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure .env File**

   Add these variables to your `.env` file:
   ```bash
   # Required: Choose ONE LLM provider
   LLM_PROVIDER=openai  # or "anthropic"

   # For OpenAI:
   OPENAI_API_KEY=sk-your-openai-api-key-here
   LLM_MODEL=gpt-4o  # or gpt-4o-mini for cheaper testing

   # For Anthropic:
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
   LLM_MODEL=claude-3-5-sonnet-20241022

   # Other configs (already in your .env)
   SUPABASE_URL=...
   SUPABASE_SERVICE_ROLE_KEY=...
   ```

## How to Test

### 1. Start the CLI

```bash
python main.py
```

You should see:
```
============================================================
🦷 RIYADH DENTAL CARE CLINIC - AI ASSISTANT
============================================================
LLM Provider: OPENAI
Model: gpt-4o
============================================================

Type your message and press Enter to chat.
Type 'quit', 'exit', or 'q' to end the conversation.
Type 'reset' to start a new conversation.

Initializing AI agent... ✅ Ready!
```

### 2. Test FAQ Queries (Should work)

Try these questions:

**English:**
```
💬 You: What are your business hours?
💬 You: How much does teeth cleaning cost?
💬 You: Do you accept insurance?
💬 You: Where is the clinic located?
💬 You: What services do you offer?
```

**Arabic:**
```
💬 You: ما هي ساعات العمل؟
💬 You: كم سعر تنظيف الأسنان؟
💬 You: هل تقبلون التأمين؟
```

**Expected behavior:**
- Router classifies intent as `faq`
- FAQ agent uses `query_knowledge_base` tool
- Returns accurate answer from the knowledge base
- Shows `[Intent: faq]` at the bottom

### 3. Test Other Intents (Placeholder responses)

These will route to the placeholder node (not implemented yet):

```
💬 You: I want to book an appointment
[Intent: booking]
🤖 Assistant: I understand you'd like to book an appointment. This feature is coming soon!...

💬 You: Cancel my appointment
[Intent: management]
🤖 Assistant: I understand you'd like to manage your existing appointment...

💬 You: The receptionist was rude
[Intent: feedback]
🤖 Assistant: Thank you for wanting to share your feedback...
```

### 4. Test Multi-turn Conversations

```
💬 You: What are your business hours?
🤖 Assistant: [Answers from knowledge base]

💬 You: And what about parking?
🤖 Assistant: [Answers about parking]

💬 You: How much is a dental examination?
🤖 Assistant: [Answers about pricing]
```

### 5. CLI Commands

- `quit`, `exit`, or `q` - End conversation and show summary
- `reset` - Start a new conversation
- `Ctrl+C` during processing - Interrupt (can continue chatting)

## Expected Output Structure

```
💬 You: What are your business hours?

⏳ Processing...

🤖 Assistant: Our clinic is open Sunday to Thursday from 9:00 AM to 8:00 PM,
and Saturday from 10:00 AM to 6:00 PM. We are closed on Fridays. Emergency
dental services are available 24/7 for existing patients.

[Intent: faq]
```

## Troubleshooting

### Error: "OPENAI_API_KEY is not set"
- Check your `.env` file has the correct API key
- Make sure `.env` is in the project root directory
- Run `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"` to verify

### Error: "Collection dental_clinic_faq not found"
- Your ChromaDB might not be initialized
- Check that `chroma_db/` directory exists
- Verify the collection name in `chroma_db/`

### Error: "No module named 'src'"
- Make sure you're running from the project root directory
- Check that all `__init__.py` files exist in src/ subdirectories

### Agent gives wrong answers
- The RAG retrieval might need tuning (we'll improve this in Phase 6)
- Check if the mock data in `rag-doc/mock-data.txt` has the information

### Router misclassifies intent
- This is expected occasionally with deterministic classification
- We can improve prompts if you see consistent issues

## What to Check

✅ **Router works** - Correctly identifies FAQ vs booking vs feedback intents
✅ **FAQ agent uses RAG** - Retrieves relevant chunks from ChromaDB
✅ **Multilingual support** - Works in both English and Arabic
✅ **Error handling** - Gracefully handles errors without crashing
✅ **Placeholders work** - Non-implemented intents show friendly messages
✅ **Conversation flow** - Multi-turn conversations maintain context

## Next Steps

Once Phase 1 testing is successful:
- **Phase 2**: Implement Appointment Booking Agent (database + calendar integration)
- **Phase 3**: Implement Appointment Management Agent
- **Phase 4**: Implement Feedback & Complaint Agent
- **Phase 5**: Add support ticket auto-creation
- **Phase 6**: Enhance RAG with hybrid retrieval and query expansion

## Debug Mode

To see more detailed logs, you can modify `src/graph/nodes/faq_agent.py`:

Change:
```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=rag_tools,
    verbose=False,  # ← Change to True
```

This will show the agent's reasoning steps.
