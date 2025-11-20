# 🦷 Dental AI Customer Service Agent

AI-powered customer service agent for dental clinics using **LangGraph** and **open-source models**.

---

## ✅ Phase 1, 2 & 3: COMPLETED

### What's Built

**Router + FAQ + Booking + Management Agents**
- ✅ **Router** - LLM-based intent classification with conversation memory
- ✅ **FAQ Agent** - RAG-powered Q&A (ChromaDB + Jina embeddings)
- ✅ **Booking Agent** - Google Calendar integration with conflict detection + email notifications
  - Check patient appointments
  - Show available doctors & services from database
  - Create bookings with duplicate prevention
  - Detects both doctor and patient time conflicts
  - Sends confirmation emails automatically
- ✅ **Management Agent** - Appointment management with natural language + email notifications
  - View all upcoming appointments
  - Cancel appointments (by doctor name, service, or date)
  - Reschedule appointments with conflict detection
  - No IDs needed - uses natural references like "my appointment with Dr. Saad"
  - Sends cancellation/reschedule confirmation emails automatically
- ✅ **Escalation Agent** - Human handoff for emergencies and hostility
  - Parallel execution with intent classification (Zero Latency)
  - Detects hostility, threats, and medical emergencies
  - Handles "Talk to human" requests
- ✅ Patient selection at startup (knows who you are throughout conversation)

### Components

```
src/
├── config/settings.py          # Environment configuration
├── graph/
│   ├── state.py               # AgentState schema
│   ├── workflow.py            # LangGraph workflow
│   └── nodes/
│       ├── sentiment.py       # Sentiment guardrail
│       ├── intent.py          # Intent classification
│       ├── decision.py        # Routing logic
│       ├── faq_agent.py       # FAQ with RAG
│       ├── booking_agent.py   # Booking with Calendar
│       ├── management_agent.py # Appointment management
│       └── human_handoff.py   # Escalation handler
├── llm/client.py              # OpenRouter (Qwen)
├── rag/retriever.py           # ChromaDB + Jina
├── tools/
│   ├── rag_tool.py            # Knowledge base query
│   ├── booking_tools.py       # Booking operations + email
│   └── management_tools.py    # Appointment management + email
└── services/
    ├── database.py            # Supabase client
    ├── calendar.py            # Google Calendar API
    └── gmail.py               # Email notifications

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

## 🧪 Test Examples

**FAQ Agent:**
```
💬 You: Hey, do you know who I am?
🤖 Assistant: Yes! You are أحمد محمد العتيبي, email: ahmed.alotaibi@gmail.com

💬 You: What are your business hours?
🤖 Assistant: Open Sunday-Thursday 9AM-8PM, Saturday 10AM-6PM. Closed Fridays.
```

**Booking Agent:**
```
💬 You: I want to book an appointment
🤖 Assistant: [Shows 10 services and 5 doctors with names and prices]

💬 You: Teeth cleaning with Dr. Saad on Wednesday at 3:30pm
🤖 Assistant: ✅ Booked! Service: تنظيف الأسنان, Dr. Saad, Wed Nov 19 at 3:30 PM

💬 You: Book another at 3:30pm with Dr. Layla
🤖 Assistant: ❌ You already have an appointment at this time
```

**Management Agent:**
```
💬 You: What are my appointments?
🤖 Assistant: You have 2 upcoming appointments:
1. Teeth Cleaning
   Doctor: Dr. Saad Al-Mutairi
   Time: Wednesday, November 20, 2024 at 3:30 PM
2. Dental Examination
   Doctor: Dr. Sarah Ahmed
   Time: Friday, November 22, 2024 at 10:00 AM

💬 You: Cancel my teeth cleaning appointment
🤖 Assistant: ✅ Appointment cancelled successfully! ...

💬 You: Reschedule my appointment with Dr. Sarah to next Monday at 2pm
🤖 Assistant: ✅ Appointment rescheduled successfully! ...
```

---

## 📊 Architecture

### Hierarchical Multi-Agent System

```
User Input
    ↓
[Parallel Execution]
 ├─> Sentiment Guardrail (Safety)
 └─> Intent Classification (Logic)
    ↓
[Decision Node]
    │
    ├─> Human Handoff (Escalation) ✅
    ├─> FAQ Agent (RAG) ✅
    ├─> Booking Agent (Calendar) ✅
    └─> Management Agent (Calendar) ✅
```

### Design Principles
- **1-5 tools per agent** (avoid tool overload)
- **Natural language interface** (no IDs shown to users)
- **Patient selected at startup** (agent always knows who you are)
- **Auto email notifications** (booking confirmations, cancellations, reschedules)
- **Appointments in Google Calendar only** (not in database)

---

## 📝 Future Phases

- **Phase 4:** Feedback & complaints agent
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
