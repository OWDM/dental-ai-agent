"""
Dental AI Agent - CLI Interface
Interactive command-line interface for testing the agent
"""

import sys
import time
from colorama import Fore
from langchain_core.messages import HumanMessage
from src.graph.workflow import create_workflow, initialize_state
from src.config.settings import settings
from src.services.database import get_database
from src.llm.client import llm_translator
from src.services.translator import get_translator
from src.utils.debug import debug


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🦷 RIYADH DENTAL CARE CLINIC - AI ASSISTANT")
    print("=" * 60)
    print(f"LLM: {settings.openrouter_model} (OpenRouter)")
    print(f"Translation: {settings.translation_model}")
    print(f"Embeddings: {settings.jina_embedding_model}")
    print(f"Debug Mode: {'ON' if settings.debug_mode else 'OFF'}")
    print("=" * 60)
    print("\nType your message and press Enter to chat.")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("Type 'reset' to start a new conversation.\n")


def select_patient():
    """Let user select which patient they are (1-8)"""
    print("=" * 60)
    print("👤 PATIENT SELECTION")
    print("=" * 60)

    # Fetch all patients from database
    db = get_database()
    patients = db.get_all_patients()

    if not patients:
        print("❌ Error: No patients found in database")
        return None

    # Display patients
    print("\nPlease select which patient you are:\n")
    for i, patient in enumerate(patients, 1):
        print(f"  {i}. {patient['name']}")
        print(f"     Email: {patient['email']}")
        print(f"     Phone: {patient['phone']}")
        print()

    # Get user selection
    while True:
        try:
            choice = input(f"Enter number (1-{len(patients)}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(patients):
                selected_patient = patients[choice_num - 1]
                print(f"\n✅ Selected: {selected_patient['name']}")
                print("=" * 60)
                print()
                return selected_patient
            else:
                print(f"❌ Please enter a number between 1 and {len(patients)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)


def print_message(role: str, content: str):
    """Print a formatted message"""
    if role == "user":
        print(f"\n👤 You: {content}")
    elif role == "assistant":
        print(f"\n🤖 Assistant: {content}")
    elif role == "system":
        print(f"\n⚙️  System: {content}")


def main():
    """Main CLI loop"""

    try:
        # Select patient
        selected_patient = select_patient()
        if not selected_patient:
            print("❌ Cannot proceed without patient selection")
            sys.exit(1)

        # Print banner
        print_banner()

        # Create workflow
        print("Initializing AI agent...", end="", flush=True)
        app = create_workflow()

        # Initialize translator for TRT architecture
        translator = get_translator(llm_translator)

        # Set debug mode based on settings
        if settings.debug_mode:
            debug.enable()
            print(" ✅ Ready! (Debug Mode: ON)\n")
        else:
            debug.disable()
            print(" ✅ Ready!\n")

        # Initialize state with patient data
        state = initialize_state()
        state["patient_id"] = selected_patient["id"]
        state["patient_name"] = selected_patient["name"]
        state["patient_email"] = selected_patient["email"]
        state["patient_phone"] = selected_patient["phone"]

        while True:
            # Get user input
            try:
                user_input = input("💬 You: ").strip()
            except EOFError:
                print("\n\nGoodbye! 👋")
                break

            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n🏁 Thank you for using our AI assistant!")
                print(f"📊 Conversation ID: {state['conversation_id']}")
                
                # Trigger Ticket Manager
                from src.services.ticket_manager import ticket_manager
                import asyncio
                
                try:
                    # Always try to get the running loop first
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(ticket_manager.process_conversation(state))
                    except RuntimeError:
                        # No running loop, create a new one
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(ticket_manager.process_conversation(state))
                        loop.close()
                except Exception as e:
                    print(f"❌ Error saving ticket: {e}")
                
                print("\nGoodbye! 👋\n")
                break

            if user_input.lower() == "reset":
                state = initialize_state()
                print_message("system", "Conversation reset. Starting fresh!")
                continue

            if not user_input:
                continue

            # TRT Pre-processing: Detect language and translate if Arabic
            detected_language = translator.detect_language(user_input)
            state["original_language"] = detected_language

            debug.print_header("🔍 TRT PRE-PROCESSING", color=Fore.MAGENTA)
            debug.print_state_info(detected_language, len(state["messages"]))

            if detected_language == "arabic":
                # Store original Arabic input for logging
                state["original_input"] = user_input

                # Translate Arabic to English before adding to state
                try:
                    import asyncio
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    translated_input = loop.run_until_complete(translator.translate_to_english(user_input))
                    state["messages"].append(HumanMessage(content=translated_input))

                    # Show what the agent will see
                    debug.print_input(translated_input, "AGENT WILL SEE (English)", color=Fore.LIGHTGREEN_EX)

                except Exception as e:
                    print_message("system", f"Translation error: {str(e)}")
                    debug.print_error(str(e))
                    continue
            else:
                # English input - add directly to state
                state["original_input"] = None
                state["messages"].append(HumanMessage(content=user_input))

                # Show what the agent will see
                debug.print_input(user_input, "AGENT WILL SEE (English)", color=Fore.LIGHTGREEN_EX)

            # Run the agent
            try:
                print("\n⏳ Processing...", end="", flush=True)
                import asyncio

                # Time the agent execution
                agent_start_time = time.time()

                # Use robust loop handling for the agent execution
                try:
                    loop = asyncio.get_running_loop()
                    # If we are in a loop (unlikely in sync main), create a task
                    # But main() is sync, so this branch shouldn't hit unless nested
                    result = loop.run_until_complete(app.ainvoke(state))
                except RuntimeError:
                    # Standard case for sync main()
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(app.ainvoke(state))
                    # Keep loop open for next iteration

                agent_elapsed = time.time() - agent_start_time

                print("\r" + " " * 20 + "\r", end="")  # Clear the "Processing..." message

                # Update state with result
                state = result

                # Debug: Show agent output
                debug.print_header("🧠 AGENT PROCESSING (Qwen)", color=Fore.LIGHTBLUE_EX)

                # TRT Post-processing: Translate response back to Arabic if needed
                if state["messages"]:
                    last_message = state["messages"][-1]
                    if hasattr(last_message, "content"):
                        response_content = last_message.content

                        # Show agent output and timing
                        if state.get("current_intent"):
                            debug.print_agent_flow(state["current_intent"], state.get("next_agent", "unknown"))

                        debug.print_output(response_content, "AGENT PRODUCED (English)", color=Fore.LIGHTBLUE_EX)
                        debug.print_metrics(agent_elapsed, tokens=None)

                        # If original input was Arabic, translate response to Arabic
                        if state.get("original_language") == "arabic":
                            debug.print_header("🔄 TRT POST-PROCESSING", color=Fore.MAGENTA)
                            try:
                                translated_response = loop.run_until_complete(
                                    translator.translate_to_arabic(response_content)
                                )
                                debug.print_separator("=", length=80, color=Fore.GREEN)
                                print_message("assistant", translated_response)
                            except Exception as e:
                                print_message("system", f"Translation error: {str(e)}")
                                debug.print_error(str(e))
                                print_message("assistant", response_content)  # Fallback to English
                        else:
                            # Original input was English, print response as-is
                            debug.print_separator("=", length=80, color=Fore.GREEN)
                            print_message("assistant", response_content)

                # Debug info (optional - can be removed in production)
                if state.get("current_intent"):
                    print(f"\n[Intent: {state['current_intent']}]", end="")

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Type 'quit' to exit or continue chatting.\n")
                continue

            except Exception as e:
                print_message("system", f"Error: {str(e)}")
                print("\n💡 Please try again or contact support if the issue persists.")

                # Log error to state
                state["error_count"] = state.get("error_count", 0) + 1
                state["last_error"] = str(e)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted. Saving conversation...")
        
        # Trigger Ticket Manager on Ctrl+C
        try:
            from src.services.ticket_manager import ticket_manager
            import asyncio
            
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ticket_manager.process_conversation(state))
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(ticket_manager.process_conversation(state))
                loop.close()
        except Exception as e:
            print(f"❌ Failed to save ticket on exit: {e}")

        print("\nGoodbye! 👋\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Check that your .env file is configured correctly")
        print("2. Verify your API keys are valid")
        print("3. Ensure ChromaDB is initialized with data")
        sys.exit(1)


if __name__ == "__main__":
    main()
