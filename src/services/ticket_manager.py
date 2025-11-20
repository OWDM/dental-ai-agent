"""
Ticket Manager Service
Handles post-conversation processing: summarization, categorization, and database archiving.
"""

import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from src.llm.client import llm_router
from src.services.database import get_database
from src.graph.state import AgentState

# System prompt for the ticket analyzer
TICKET_ANALYZER_PROMPT = """You are a Support Ticket Analyst for Riyadh Dental Care Clinic.

Your job is to analyze a completed customer service conversation and extract structured data for our CRM.

Input: A conversation history between a Patient and an AI Assistant.

Output: A JSON object with the following fields:
1. "subject": A concise, professional summary of the conversation (max 10 words).
   - Bad: "User asked about booking"
   - Good: "Appointment Booking - Dr. Saad - Teeth Cleaning"
2. "ticket_types": A list of categories that apply to this conversation.
   - Valid options ONLY: ["appointment_booking", "appointment_modification", "appointment_cancellation", "complaint", "general_inquiry"]
   - IMPORTANT: You MUST only use these exact values. Do NOT use "emergency" or any other values.
   - If the user was hostile or requested escalation, use "complaint"
3. "status": The final status of the interaction.
   - "resolved": If the user's request was handled (booked, answered, cancelled).
   - "escalated": If the user asked for a human, was hostile, or the AI couldn't help.

Analyze the conversation carefully. If multiple topics were discussed, include all relevant ticket types.
CRITICAL: Only use the 5 valid ticket types listed above.
"""

class TicketManager:
    """
    Manages the lifecycle of support tickets.
    Analyzes completed conversations and saves them to Supabase.
    """
    
    def __init__(self):
        self.db = get_database()
        self.llm = llm_router  # Use the router model (Qwen) for analysis as it's smart enough

    async def process_conversation(self, state: AgentState):
        """
        Process a completed conversation: analyze it and save to database.
        
        Args:
            state: The final AgentState containing messages and metadata
        """
        messages = state.get("messages", [])
        
        # 1. Skip empty conversations
        if not messages or len(messages) < 2:
            print("Skipping empty conversation.")
            return

        # 2. Prepare conversation text for LLM analysis
        conversation_text = ""
        formatted_history = {"messages": []}
        
        for msg in messages:
            role = "user" if hasattr(msg, 'type') and msg.type == 'human' else "assistant"
            content = msg.content
            
            # Add to text for LLM
            conversation_text += f"{role.upper()}: {content}\n"
            
            # Add to JSON structure for DB
            formatted_history["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat() # Approximate timestamp
            })

        # 3. Analyze conversation using LLM
        print("\n📊 Analyzing conversation for support ticket...")
        try:
            analysis = await self._analyze_conversation(conversation_text)
            
            # Override status if explicitly escalated in state
            if state.get("escalated", False):
                analysis["status"] = "escalated"
                # Ensure complaint is in the ticket types for escalations
                if "complaint" not in analysis["ticket_types"]:
                    analysis["ticket_types"].append("complaint")

            # 4. Save to Supabase
            self._save_ticket(state, analysis, formatted_history)
            
        except Exception as e:
            print(f"❌ Error processing ticket: {e}")

    async def _analyze_conversation(self, conversation_text: str) -> dict:
        """Run LLM analysis on the conversation text with self-correction"""
        
        valid_types = ["appointment_booking", "appointment_modification", "appointment_cancellation", "complaint", "general_inquiry"]
        max_retries = 2
        invalid_types = []  # Initialize outside loop
        
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    # First attempt - normal prompt
                    response = await self.llm.ainvoke([
                        SystemMessage(content=TICKET_ANALYZER_PROMPT),
                        HumanMessage(content=f"Analyze this conversation:\n\n{conversation_text}")
                    ])
                else:
                    # Retry with error feedback
                    error_message = f"""Your previous response contained invalid ticket types: {invalid_types}

CRITICAL ERROR: You MUST only use these exact ticket types:
- appointment_booking
- appointment_modification
- appointment_cancellation
- complaint
- general_inquiry

DO NOT use: "emergency", "escalation", or any other values.

Please analyze the conversation again and provide a corrected JSON response with ONLY the valid ticket types listed above."""
                    
                    response = await self.llm.ainvoke([
                        SystemMessage(content=TICKET_ANALYZER_PROMPT),
                        HumanMessage(content=f"Analyze this conversation:\n\n{conversation_text}"),
                        HumanMessage(content=error_message)
                    ])
                
                # Clean up code blocks if present
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                    
                analysis = json.loads(content)
                
                # Validate ticket types
                ticket_types = analysis.get("ticket_types", [])
                invalid_types = [t for t in ticket_types if t not in valid_types]
                
                if invalid_types:
                    print(f"⚠️ LLM returned invalid ticket types: {invalid_types}. Retrying... (Attempt {attempt + 1}/{max_retries})")
                    continue  # Retry
                
                # Success - all types are valid
                print(f"✅ Ticket analysis successful with types: {ticket_types}")
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    break
                continue
            except Exception as e:
                print(f"⚠️ LLM Analysis failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    break
                continue
        
        # All retries failed - return safe defaults
        print(f"❌ All retry attempts failed. Using default values.")
        return {
            "subject": "General Inquiry (Auto-generated)",
            "ticket_types": ["general_inquiry"],
            "status": "resolved"
        }

    def _save_ticket(self, state: AgentState, analysis: dict, history: dict):
        """Insert the ticket into Supabase"""
        
        ticket_data = {
            "conversation_id": state.get("conversation_id"),
            "patient_id": state.get("patient_id"), # Can be None if patient not identified
            "type": analysis["ticket_types"],
            "subject": analysis["subject"],
            "conversation_history": history,
            "status": analysis["status"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if analysis["status"] == "resolved":
            ticket_data["resolved_at"] = datetime.now().isoformat()

        print(f"💾 Saving ticket: {analysis['subject']} ({analysis['status']})")
        
        try:
            self.db.client.table("support_tickets").insert(ticket_data).execute()
            print("✅ Ticket saved successfully!")
        except Exception as e:
            print(f"❌ Database insert failed: {e}")

# Singleton instance
ticket_manager = TicketManager()
