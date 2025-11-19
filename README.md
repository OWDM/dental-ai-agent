# 🦷 Dental AI Customer Service Agent

AI-powered customer service agent for dental clinics using **LangGraph** and **open-source models**.

---

## ✅ Phase 1: COMPLETED

### What's Built

**1. Router + FAQ Agent Architecture**
- ✅ Router agent - classifies user intent (hybrid: pattern matching + LLM)
- ✅ FAQ agent - answers questions using RAG (ChromaDB + Jina embeddings)
- ✅ LangGraph workflow - hierarchical routing
- ✅ Patient selection at startup (select from 8 existing patients)

### Components

```
src/
├── config/settings.py          # Environment configuration
├── graph/
│   ├── state.py               # AgentState schema
│   ├── workflow.py            # LangGraph workflow
│   └── nodes/
│       ├── router.py          # Intent classification
│       ├── faq_agent.py       # FAQ with RAG
│       └── placeholder.py     # Future agents
├── llm/client.py              # OpenRouter (Qwen)
├── rag/retriever.py           # ChromaDB + Jina
├── tools/rag_tool.py          # Knowledge base query
└── services/database.py       # Supabase client

main.py                        # CLI with patient selection
init_chromadb.py              # Vector DB initialization
```

### Database Schema (Supabase)

**Existing Data:**
- 8 patients (already in database - NO creation needed)
- 5 doctors
- 10 services
- Appointments stored in Google Calendar only

**Tables:**
- `patients` - id, name, email, phone
- `doctors` - id, name, specialization, google_calendar_id, available
- `services` - id, name, description, duration_minutes, price
- `support_tickets` - conversation tracking
- `feedback` - patient feedback

---

## 🚧 Phase 2: NEXT - Simple Booking Agent

### Goal
Agent that can:
1. Check booking status (read from Google Calendar)
2. Create new booking (write to Google Calendar) but make sure no duplications in booking for same doctor!

### What to Build

**1. Calendar Service** `src/services/calendar.py`
```python
- get_patient_appointments(patient_email)  # Read from Google Calendar
- create_appointment(patient, doctor, service, time)  # Write to Google Calendar
```

**2. Booking Tools** `src/tools/booking_tools.py`
```python
- check_my_bookings()  # Show patient their appointments
- create_new_booking(doctor_id, service_id, datetime)  # Book appointment
```

**3. Booking Agent** `src/graph/nodes/booking_agent.py`
- Multi-turn conversation
- Uses patient info from state (already selected at startup)
- Shows available doctors and times
- Creates Google Calendar event

### Workflow

```
User: "Do I have any appointments?"
→ check_my_bookings() → reads Google Calendar
→ Agent: "You have 1 appointment: Nov 25, 2PM with Dr. Saad"

User: "I want to book a cleaning"
→ Agent: "Available doctors: 1) Dr. Saad, 2) Dr. Ahmed..."
→ User: "Dr. Saad"
→ Agent: "Available times: ..."
→ User: "Tomorrow 2PM"
→ create_new_booking() → writes to Google Calendar
→ Agent: "✅ Booked!"
```

---

## 🏃 Quick Start

### 1. Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure .env
```bash
# OpenRouter (Qwen LLM)
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_MODEL=qwen/qwen3-14b

# Jina AI (Embeddings)
JINA_API_KEY=jina_your-key

# Supabase (Database - 8 patients already exist)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-key

# Google Calendar (for appointments)
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=your-calendar-id

# Gmail (for confirmation emails)
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

### 3. Initialize ChromaDB
```bash
python init_chromadb.py
```

### 4. Run Agent
```bash
python main.py
```

**On startup:**
1. Select patient (1-8)
2. Agent knows who you are
3. Start chatting!

---

## 🧪 Test FAQ Agent (Phase 1)

```bash
python main.py

# Select patient
Enter number (1-8): 1

# Ask FAQ questions
💬 You: What are your business hours?
🤖 Assistant: Our clinic is open Sunday to Thursday from 9:00 AM to 8:00 PM...

💬 You: How much is teeth cleaning?
🤖 Assistant: Teeth cleaning costs 200 SAR...
```

---

## 📊 Architecture

### Hierarchical Multi-Agent System

```
User Input
    ↓
[Router Agent]
    │
    ├─> FAQ Agent (RAG) ✅ DONE
    ├─> Booking Agent (Calendar) 🚧 NEXT
    ├─> Management Agent ⏳ Future
    └─> Feedback Agent ⏳ Future
```

### Design Principles
- **1-3 tools per agent** (avoid tool overload)
- **Patient selected at startup** (agent always knows who you are)
- **8 existing patients in database** (no patient creation)
- **Appointments in Google Calendar only** (not in database)

---

## 📝 Future Phases

- **Phase 3:** Appointment management (modify/cancel)
- **Phase 4:** Feedback & complaints
- **Phase 5:** Auto-create support tickets
- **Phase 6:** Advanced RAG (hybrid retrieval)

---

## 🔧 Tech Stack

- **LangGraph** - Agent workflow
- **Qwen 3 14B** - LLM (via OpenRouter)
- **Jina AI v3** - Embeddings
- **ChromaDB** - Vector database
- **Supabase** - PostgreSQL
- **Google Calendar** - Appointments
- **Gmail** - Notifications
