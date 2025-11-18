# Dental Clinic Database Schema

This document describes the Supabase database schema for the AI Customer Service Agent demo.

## Database Overview

The database consists of **5 main tables** that support the AI agent's operations:
- Patient management
- Doctor information
- Service catalog
- Conversation tracking
- Feedback collection

---

## Tables

### 1. **patients**
Stores patient information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `name` | VARCHAR(255) | Patient full name |
| `email` | VARCHAR(255) | Patient email (unique) |
| `phone` | VARCHAR(50) | Patient phone number |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

---

### 2. **doctors**
Stores doctor information and Google Calendar integration.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `name` | VARCHAR(255) | Doctor full name |
| `specialization` | VARCHAR(255) | Dental specialization |
| `email` | VARCHAR(255) | Doctor email (unique) |
| `google_calendar_id` | VARCHAR(255) | Google Calendar ID for appointments |
| `available` | BOOLEAN | Is doctor accepting patients? |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

---

### 3. **services**
Catalog of dental services and pricing.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `name` | VARCHAR(255) | Service name (Arabic/English) |
| `description` | TEXT | Service description |
| `duration_minutes` | INTEGER | Service duration |
| `price` | DECIMAL(10,2) | Price in SAR |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

---

### 4. **support_tickets**
Tracks every AI conversation for dashboard analytics.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `conversation_id` | VARCHAR(255) | Unique conversation session ID |
| `patient_id` | UUID | Foreign key to patients (nullable) |
| `type` | TEXT[] | Array of ticket types (multi-category support) |
| `subject` | VARCHAR(255) | Brief conversation summary |
| `conversation_history` | JSONB | Full conversation messages in JSON format |
| `status` | VARCHAR(50) | `resolved` or `escalated` |
| `created_at` | TIMESTAMP | Conversation start time |
| `updated_at` | TIMESTAMP | Last update timestamp |
| `resolved_at` | TIMESTAMP | Resolution timestamp (nullable) |

**Valid ticket types:**
- `appointment_booking`
- `appointment_modification`
- `appointment_cancellation`
- `complaint`
- `feedback`
- `general_inquiry`

**conversation_history JSON structure:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Message text",
      "timestamp": "2025-11-18T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Response text",
      "timestamp": "2025-11-18T10:00:05Z"
    }
  ]
}
```

---

### 5. **feedback**
Stores patient feedback and complaints.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `patient_id` | UUID | Foreign key to patients (nullable) |
| `feedback_type` | VARCHAR(50) | `complaint`, `positive`, or `suggestion` |
| `category` | VARCHAR(100) | Feedback category |
| `message` | TEXT | Feedback message |
| `status` | VARCHAR(50) | `resolved` or `escalated` |
| `created_at` | TIMESTAMP | Submission timestamp |
| `resolved_at` | TIMESTAMP | Resolution timestamp (nullable) |

**Common categories:**
- `appointment_delay`
- `staff_service`
- `facility`
- `treatment_quality`

---

## Connection Information

### Environment Variables

Create a `.env` file in the project root with:

```env
SUPABASE_URL=https://luwwsynruweasugqlsmi.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres.luwwsynruweasugqlsmi:PASSWORD@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres
```

### Python Connection Example

```python
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

# Example: Fetch all patients
response = supabase.table("patients").select("*").execute()
print(response.data)
```

---

## Testing Connection

Run the test script to verify database connectivity:

```bash
# Using virtual environment
venv/bin/python test_connection.py
```

The test script will verify:
- ✅ Database connection
- ✅ All tables are accessible
- ✅ Mock data is present
- ✅ Conversation history JSON structure

---

## Mock Data

The database is pre-populated with Saudi-specific mock data:
- **8 patients** with Arabic names
- **5 doctors** with specializations
- **10 dental services** (prices in SAR)
- **3 support tickets** with Arabic conversations
- **4 feedback entries**

---

## Indexes

Performance indexes are created on:
- `support_tickets.patient_id`
- `support_tickets.status`
- `support_tickets.conversation_id`
- `support_tickets.type` (GIN index for array search)
- `feedback.patient_id`
- `feedback.status`
- `doctors.available`

---

## Notes

- All tables use UUID primary keys
- Timestamps are auto-managed with triggers
- The `type` column in `support_tickets` is an array allowing multi-category classification
- Conversation history is stored as JSONB for flexible querying
- Status can only be `resolved` or `escalated` for demo simplicity