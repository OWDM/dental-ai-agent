# Dental AI Agent - Task Progress Tracker

**Project Goal:** Build a LangGraph-based AI customer service agent for a dental clinic

**Development Approach:** Phased, testable implementation (no speed running!)

**Last Updated:** 2025-11-18

---

## 📊 Current Status

**Current Phase:** Not Started
**Last Completed Phase:** None
**Next Phase:** Phase 1 - Project Setup & Environment

---

## 📋 Phase Breakdown

### ✅ Phase 0: Planning & Setup (COMPLETED)
- [x] Explored codebase structure
- [x] Verified database schema (UUIDs confirmed ✓)
- [x] Confirmed API integrations are documented
- [x] Created this tracking file

---

### ⬜ Phase 1: Project Setup & Environment
**Status:** NOT STARTED
**Goal:** Get all dependencies installed and verify APIs work

#### Tasks:
- [ ] Update `requirements.txt` with all needed packages:
  - LangGraph & LangChain
  - ChromaDB (vector database)
  - OpenAI SDK (for OpenRouter API)
  - Jina AI embeddings
  - Other utilities (tiktoken, etc.)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Add missing API keys to `.env`:
  - `OPENROUTER_API_KEY=`
  - `JINA_API_KEY=`
- [ ] Create basic `src/` folder structure:
  - `src/llm/` - LLM client
  - `src/rag/` - RAG system
  - `src/tools/` - Agent tools
  - `src/graph/` - LangGraph workflow
  - `src/utils/` - Utilities
- [ ] Test existing APIs:
  - Run `python database/test_connection.py`
  - Run `python gmail/test_gmail.py`
  - Manually verify Google Calendar credentials work

#### Success Criteria:
- ✓ All packages install without errors
- ✓ Database connection works
- ✓ Calendar API responds
- ✓ Gmail can send test email

#### Testing Instructions:
1. Run database test: `python database/test_connection.py`
2. Run gmail test: `python gmail/test_gmail.py`
3. Create a simple test script to verify calendar API access
4. Verify no import errors when importing new packages

#### Notes:
-

---

### ⬜ Phase 2: Mock Documentation & RAG Setup
**Status:** NOT STARTED
**Goal:** Build the knowledge base for FAQ support

#### Tasks:
- [ ] Create `docs/` directory
- [ ] Create `docs/clinic_faq.txt` with mock content:
  - Business hours (example: Sun-Thu 9AM-8PM, Sat 10AM-6PM, Closed Fridays)
  - Examination fees (example: Initial consultation 200 SAR)
  - Services offered (cleaning, extraction, root canal, whitening, etc.)
  - Insurance types accepted (example: Bupa, Tawuniya, Medgulf)
  - Pricing for common procedures
  - Appointment policies (cancellation, rescheduling)
  - Contact information
- [ ] Create `src/rag/embeddings.py` - Jina AI embeddings client
- [ ] Create `src/rag/vector_store.py` - ChromaDB setup
- [ ] Create `src/rag/chunker.py` - Semantic chunking logic
- [ ] Create `src/rag/retriever.py` - Retrieval function
- [ ] Create test script: `tests/test_rag.py`
- [ ] Ingest documentation into ChromaDB
- [ ] Test retrieval with sample queries

#### Success Criteria:
- ✓ Documentation file exists with realistic, comprehensive content
- ✓ ChromaDB collection created successfully
- ✓ Can query "What are your business hours?" and get relevant chunks
- ✓ Can query "How much is teeth cleaning?" and get pricing info
- ✓ Retrieval returns top-k most relevant chunks

#### Testing Instructions:
1. Run `python tests/test_rag.py`
2. Try different queries:
   - "What are your business hours?"
   - "Do you accept insurance?"
   - "How much does a consultation cost?"
3. Verify returned chunks are relevant and accurate

#### Notes:
-

---

### ⬜ Phase 3: LLM Client Setup
**Status:** NOT STARTED
**Goal:** Connect to OpenRouter and test qwen3-14b model

#### Tasks:
- [ ] Create `src/llm/client.py` - OpenRouter API wrapper
- [ ] Configure for `qwen/qwen3-14b` model
- [ ] Create `src/llm/prompts.py` - Prompt templates:
  - System prompt for dental clinic agent
  - FAQ answering prompt (with RAG context)
  - Appointment booking prompt
  - Feedback handling prompt
- [ ] Add error handling and retries
- [ ] Create test script: `tests/test_llm.py`
- [ ] Test basic LLM calls

#### Success Criteria:
- ✓ Can send message to qwen3-14b via OpenRouter and get response
- ✓ Prompt templates work correctly with variable substitution
- ✓ Error handling prevents crashes on API failures
- ✓ Response format is usable (clean text)

#### Testing Instructions:
1. Run `python tests/test_llm.py`
2. Test with various prompts:
   - Simple query: "What services do you offer?"
   - With context: Include RAG chunks and verify LLM uses them
   - Error case: Invalid API key (should handle gracefully)
3. Verify responses are coherent and relevant

#### Notes:
-

---

### ⬜ Phase 4: Database & Calendar Tools
**Status:** NOT STARTED
**Goal:** Build the tools the agent will use

#### Tasks:
- [ ] Create `src/tools/database.py`:
  - `list_doctors()` - Get all available doctors
  - `get_doctor_by_id(doctor_id)` - Get specific doctor details
  - `get_doctor_availability(doctor_id)` - Check if doctor is available
  - `list_services()` - Get all available services with pricing
  - `get_patient_info(patient_id)` - Fetch patient details
  - `get_patient_appointments(patient_id)` - Get patient's appointments
- [ ] Create `src/tools/calendar.py`:
  - `get_available_slots(doctor_id, date)` - Find free time slots
  - `book_appointment(doctor_id, patient_id, datetime, service_id)` - Create appointment
  - `cancel_appointment(appointment_id)` - Cancel appointment
  - `reschedule_appointment(appointment_id, new_datetime)` - Reschedule
- [ ] Create `src/tools/email.py`:
  - `send_confirmation_email(patient_email, appointment_details)`
  - `send_cancellation_email(patient_email, appointment_details)`
  - `send_escalation_email(staff_email, ticket_details)`
- [ ] Create `src/tools/feedback.py`:
  - `save_feedback(patient_id, feedback_type, message)`
  - `create_support_ticket(conversation_id, patient_id, conversation_history)`
- [ ] Create test script: `tests/test_tools.py`
- [ ] Test each tool independently

#### Success Criteria:
- ✓ Can list doctors from database and see their details
- ✓ Can list services with correct pricing
- ✓ Can check available time slots for a specific doctor/date
- ✓ Can book a test appointment (appears in Google Calendar)
- ✓ Can send test emails successfully
- ✓ Can save feedback to database

#### Testing Instructions:
1. Run `python tests/test_tools.py`
2. Verify database tools:
   - List all doctors (should show 5 doctors from mock data)
   - Get services (should show prices in SAR)
3. Verify calendar tools:
   - Check available slots for tomorrow
   - Book a test appointment
   - Check Google Calendar to confirm it appears
   - Cancel the test appointment
4. Verify email tool:
   - Send test confirmation email to yourself
5. Verify feedback tool:
   - Save test feedback to database
   - Check Supabase to confirm it's saved

#### Notes:
-

---

### ⬜ Phase 5: LangGraph Workflow Structure
**Status:** NOT STARTED
**Goal:** Set up the agent's state machine and basic flow

#### Tasks:
- [ ] Create `src/graph/state.py` - Define AgentState:
  - `conversation_history` (list of messages)
  - `patient_id` (UUID)
  - `patient_info` (dict)
  - `current_intent` (str: faq/booking/management/feedback)
  - `booking_context` (dict: doctor, service, datetime)
  - `rag_context` (retrieved documents)
  - `requires_escalation` (bool)
  - `session_id` (str)
- [ ] Create `src/graph/nodes.py` - Core nodes:
  - `router_node()` - Decides which capability to use
  - `rag_node()` - Handles FAQ queries (retrieves docs)
  - `booking_node()` - Handles appointment booking
  - `management_node()` - Handles appointment changes
  - `feedback_node()` - Handles complaints/feedback
  - `llm_response_node()` - Generates final response using LLM
  - `escalation_node()` - Creates ticket & escalates
- [ ] Create `src/graph/workflow.py` - Define graph:
  - Add all nodes
  - Define edges and conditional routing
  - Set entry and exit points
  - Compile graph
- [ ] Create simple routing logic (pattern matching for testing):
  - Keywords like "hours", "price", "cost" → rag_node
  - Keywords like "book", "appointment", "schedule" → booking_node
  - Keywords like "cancel", "change", "reschedule" → management_node
  - Keywords like "complaint", "problem", "issue" → feedback_node
- [ ] Create test script: `tests/test_graph.py`

#### Success Criteria:
- ✓ Graph compiles without errors
- ✓ Can invoke graph with test input
- ✓ Graph reaches correct nodes based on input patterns
- ✓ State is passed correctly between nodes
- ✓ Can visualize graph structure (optional but helpful)

#### Testing Instructions:
1. Run `python tests/test_graph.py`
2. Test routing with various inputs:
   - "What are your business hours?" → should route to rag_node
   - "I want to book an appointment" → should route to booking_node
   - "I want to cancel my appointment" → should route to management_node
   - "I have a complaint" → should route to feedback_node
3. Print state after each node to verify data flows correctly

#### Notes:
-

---

### ⬜ Phase 6: Core Agent - FAQ & Booking
**Status:** NOT STARTED
**Goal:** Implement the two main conversational flows

#### Tasks:
- [ ] Implement RAG-powered FAQ answering:
  - In `rag_node`: Retrieve relevant documents based on query
  - In `llm_response_node`: Pass RAG context to LLM with prompt
  - Generate natural, helpful response
  - Handle "no relevant docs found" case
- [ ] Implement appointment booking flow:
  - Multi-turn conversation to collect:
    1. Preferred doctor (show list, let user choose)
    2. Preferred date
    3. Available time slots (show options)
    4. Service type (show list with prices)
  - Validate each input
  - Check availability before confirming
  - Book appointment using calendar tool
  - Save appointment reference in state
  - Send confirmation email
- [ ] Add conversation state management:
  - Track partial booking data between turns
  - Handle user changing their mind ("actually, different doctor")
  - Allow "start over" option
- [ ] Improve routing to use LLM instead of keywords
- [ ] Create test script: `tests/test_agent_core.py`

#### Success Criteria:
- ✓ Can ask FAQ questions and get accurate answers from RAG
- ✓ Answers are natural and conversational (not just raw chunks)
- ✓ Can complete full booking through multi-turn conversation
- ✓ Appointment appears in Google Calendar
- ✓ Receives confirmation email with correct details
- ✓ Handles invalid inputs gracefully (e.g., invalid date)

#### Testing Instructions:
1. Test FAQ flow:
   - "What are your business hours?"
   - "Do you accept Bupa insurance?"
   - "How much is teeth whitening?"
   - Verify answers match documentation
2. Test booking flow:
   - Start: "I want to book an appointment"
   - Follow prompts to select doctor, date, time, service
   - Verify appointment created in calendar
   - Check email inbox for confirmation
3. Test edge cases:
   - "I want to book an appointment tomorrow" (should still ask for doctor, etc.)
   - Change selection mid-conversation
   - Invalid date formats

#### Notes:
-

---

### ⬜ Phase 7: Appointment Management
**Status:** NOT STARTED
**Goal:** Handle modifications and cancellations

#### Tasks:
- [ ] Implement appointment lookup:
  - Fetch patient's existing appointments from database/calendar
  - Display appointments with details (date, time, doctor, service)
  - Handle "no appointments found" case
- [ ] Implement cancellation flow:
  - Show patient's appointments
  - Let user select which to cancel
  - Confirm cancellation intent
  - Cancel in calendar
  - Send cancellation email
  - Update appointment status
- [ ] Implement rescheduling flow:
  - Show patient's appointments
  - Let user select which to reschedule
  - Show available new time slots
  - Update calendar
  - Send rescheduling confirmation email
- [ ] Create test script: `tests/test_management.py`

#### Success Criteria:
- ✓ Can list patient's existing appointments
- ✓ Can cancel appointment (disappears from calendar)
- ✓ Receives cancellation confirmation email
- ✓ Can reschedule appointment (updates in calendar)
- ✓ Receives rescheduling confirmation email
- ✓ Handles edge cases (no appointments, invalid selection)

#### Testing Instructions:
1. First, book 2-3 test appointments using Phase 6 functionality
2. Test listing: "Show my appointments"
3. Test cancellation:
   - "I want to cancel my appointment"
   - Select one from the list
   - Verify it's removed from calendar
4. Test rescheduling:
   - "I want to reschedule my appointment"
   - Select appointment and new time
   - Verify calendar is updated
5. Check emails for all notifications

#### Notes:
-

---

### ⬜ Phase 8: Feedback & Smart Escalation
**Status:** NOT STARTED
**Goal:** Handle complaints with intelligent escalation

#### Tasks:
- [ ] Implement feedback collection:
  - Ask for feedback type (complaint/positive/suggestion)
  - Collect detailed message
  - Determine category (appointment_delay/staff_behavior/facility/other)
  - Save to feedback table in database
- [ ] Add LLM-based escalation detection:
  - After collecting feedback, pass to LLM with special prompt
  - LLM analyzes:
    - Severity (minor/moderate/severe)
    - Sentiment (angry/disappointed/neutral)
    - Resolvability (can agent resolve or needs human?)
  - LLM returns: `{"escalate": true/false, "reason": "..."}`
  - Set `requires_escalation` in state
- [ ] Implement automatic ticket creation:
  - At end of conversation (or when escalating)
  - Collect full conversation history
  - Pass to LLM to generate summary
  - Create support_ticket in database with:
    - conversation_id (session_id)
    - patient_id
    - type (array: faq/booking/complaint/etc.)
    - subject (generated by LLM)
    - conversation_history (full JSON)
    - status ('resolved' or 'escalated')
  - If escalated: send email to clinic staff
- [ ] Update `escalation_node` in graph
- [ ] Create test script: `tests/test_feedback.py`

#### Success Criteria:
- ✓ Can submit feedback/complaint
- ✓ LLM correctly identifies minor issues as non-escalated
- ✓ LLM correctly identifies serious issues requiring escalation
- ✓ Ticket created in database with full context
- ✓ Ticket summary is accurate and helpful
- ✓ Escalation email sent only for serious issues
- ✓ Email includes ticket details and conversation summary

#### Testing Instructions:
1. Test minor complaint (should NOT escalate):
   - "I had to wait 10 minutes past my appointment time"
   - Verify: feedback saved, ticket created with status='resolved'
   - Verify: NO escalation email sent
2. Test serious complaint (should escalate):
   - "The dentist was very rude and didn't listen to my concerns at all. I'm extremely upset and want a refund."
   - Verify: feedback saved, ticket created with status='escalated'
   - Verify: Escalation email sent to staff
3. Check database to see tickets and verify accuracy

#### Notes:
-

---

### ⬜ Phase 9: CLI Interface & Session Management
**Status:** NOT STARTED
**Goal:** Create the user-facing interface

#### Tasks:
- [ ] Create `main.py` - Main entry point
- [ ] Implement patient selection:
  - Connect to database
  - Fetch all patients (or filter active patients)
  - Display numbered list with name, email
  - Let user type number to select
  - Handle invalid selections
  - Load patient info into session
- [ ] Implement conversation loop:
  - Display welcome message
  - Show patient info (name, upcoming appointments if any)
  - Accept user input (text)
  - Call LangGraph agent with input
  - Display agent response
  - Continue loop until user types 'exit' or 'quit'
- [ ] Add session tracking:
  - Generate unique session_id at start
  - Pass to agent state
  - Track conversation start/end time
- [ ] Implement automatic ticket creation:
  - When conversation ends (user exits)
  - Call ticket creation function with full conversation
  - Display ticket ID to user
  - Save ticket to database
- [ ] Add nice CLI formatting:
  - Colors for different message types (optional)
  - Clear prompts ("You: ", "Agent: ")
  - Help text ("Type 'exit' to end conversation")
- [ ] Error handling:
  - API failures (show friendly message, don't crash)
  - Network issues
  - Invalid inputs

#### Success Criteria:
- ✓ Can run `python main.py` from project root
- ✓ Shows list of patients to choose from
- ✓ Can select patient by number
- ✓ Can have multi-turn conversation
- ✓ Agent responds appropriately to all query types
- ✓ Can type 'exit' to end conversation gracefully
- ✓ Ticket automatically created at end
- ✓ No crashes on errors

#### Testing Instructions:
1. Run: `python main.py`
2. Select a patient from the list
3. Test complete user journey:
   - Ask FAQ: "What are your business hours?"
   - Book appointment: "I want to book an appointment"
     - Complete full booking flow
   - Ask about appointment: "What appointments do I have?"
   - Cancel/reschedule one
   - Submit feedback: "I want to give feedback"
   - Exit conversation
4. Verify ticket created in database
5. Check that all emails were sent correctly
6. Start new session and verify state is clean

#### Notes:
-

---

## 🎯 Context Restoration Template

**Use this when starting a new session:**

> Hi! I'm continuing work on the Dental AI Agent project. We're working through phases systematically.
>
> Current status: [Check TASK_PROGRESS.md]
> Last completed: Phase X
> Next phase: Phase Y
>
> Please help me implement Phase Y according to the task list in TASK_PROGRESS.md.

---

## 📝 Session Notes

### Session 1 (2025-11-18)
- Created TASK_PROGRESS.md
- Confirmed project requirements:
  - LangGraph agent
  - RAG with Jina AI + ChromaDB
  - OpenRouter API with qwen/qwen3-14b
  - CLI interface
  - Patient selection from database
  - Smart escalation (LLM-based, not keyword)
  - Ticket creation at end with full context
- Database schema already has UUIDs (no concerns)
- Starting fresh (old src/ deleted)

---

## 🔗 Important Links & References

**APIs:**
- OpenRouter: https://openrouter.ai/
- Jina AI Embeddings: https://jina.ai/embeddings
- ChromaDB Docs: https://docs.trychroma.com/
- LangGraph Docs: https://langchain-ai.github.io/langgraph/

**Database Schema:**
- Located in: `database/README.md`
- Tables: patients, doctors, services, support_tickets, feedback
- All use UUID primary keys

**Existing Integrations:**
- Database: `database/test_connection.py`
- Gmail: `gmail/test_gmail.py`
- Calendar: Documented in `calendar/README.md`

---

## ✅ Quality Checklist

Before marking any phase as complete, verify:

- [ ] All code has proper error handling
- [ ] All functions have docstrings
- [ ] Test script created and passes
- [ ] Manual testing completed successfully
- [ ] No hardcoded values (use environment variables)
- [ ] Code is clean and readable
- [ ] No obvious security issues
- [ ] README or documentation updated if needed

---

## 🚫 Common Pitfalls to Avoid

1. **Don't hardcode API keys** - Always use .env
2. **Don't skip testing** - Each phase must be tested before moving on
3. **Don't speed run** - One phase at a time, get approval before continuing
4. **Don't use keyword-based logic** - Use LLM for intelligence (especially routing and escalation)
5. **Don't forget error handling** - APIs fail, handle gracefully
6. **Don't ignore the database schema** - Use UUIDs correctly
7. **Don't forget to update this file** - Keep progress tracked!

---

**Remember:** The goal is a working, reliable agent. Take time to test each phase properly!
