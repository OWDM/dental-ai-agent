"""
Debug utilities for TRT architecture
Provides colored output for debugging translation and agent flows
"""

import time
from typing import Optional
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class DebugLogger:
    """Colored debug logger for TRT architecture"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.start_time = None

    def enable(self):
        """Enable debug logging"""
        self.enabled = True

    def disable(self):
        """Disable debug logging"""
        self.enabled = False

    def start_timer(self):
        """Start timing an operation"""
        self.start_time = time.time()

    def get_elapsed(self) -> float:
        """Get elapsed time since start_timer was called"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def print_separator(self, char="=", length=80, color=Fore.WHITE):
        """Print a colored separator line"""
        if not self.enabled:
            return
        print(f"{color}{char * length}{Style.RESET_ALL}")

    def print_header(self, text: str, color=Fore.CYAN):
        """Print a colored header"""
        if not self.enabled:
            return
        self.print_separator("=", length=80, color=color)
        print(f"{color}{Style.BRIGHT}{text}{Style.RESET_ALL}")
        self.print_separator("=", length=80, color=color)

    def print_section(self, text: str, color=Fore.YELLOW):
        """Print a section header"""
        if not self.enabled:
            return
        print(f"\n{color}{Style.BRIGHT}{'─' * 80}")
        print(f"{text}")
        print(f"{'─' * 80}{Style.RESET_ALL}")

    def print_input(self, text: str, label: str = "INPUT", color=Fore.GREEN):
        """Print input text with label"""
        if not self.enabled:
            return
        print(f"\n{color}{Style.BRIGHT}📥 {label}:{Style.RESET_ALL}")
        print(f"{color}{text}{Style.RESET_ALL}")

    def print_output(self, text: str, label: str = "OUTPUT", color=Fore.BLUE):
        """Print output text with label"""
        if not self.enabled:
            return
        print(f"\n{color}{Style.BRIGHT}📤 {label}:{Style.RESET_ALL}")
        print(f"{color}{text}{Style.RESET_ALL}")

    def print_translation(self, original: str, translated: str, direction: str):
        """Print translation with before/after"""
        if not self.enabled:
            return

        if direction == "ar->en":
            self.print_section(f"🔄 TRANSLATION: Arabic → English", Fore.MAGENTA)
            self.print_input(original, "ARABIC INPUT", Fore.YELLOW)
            self.print_output(translated, "ENGLISH OUTPUT", Fore.GREEN)
        else:  # en->ar
            self.print_section(f"🔄 TRANSLATION: English → Arabic", Fore.MAGENTA)
            self.print_input(original, "ENGLISH INPUT", Fore.GREEN)
            self.print_output(translated, "ARABIC OUTPUT", Fore.YELLOW)

    def print_metrics(self, elapsed_time: float, tokens: Optional[dict] = None):
        """Print timing and token metrics"""
        if not self.enabled:
            return

        print(f"\n{Fore.CYAN}{Style.BRIGHT}⏱️  METRICS:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}├─ Time: {elapsed_time:.2f}s{Style.RESET_ALL}")

        if tokens:
            print(f"{Fore.CYAN}├─ Input Tokens: {tokens.get('input_tokens', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}├─ Output Tokens: {tokens.get('output_tokens', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└─ Total Tokens: {tokens.get('total_tokens', 'N/A')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}└─ Tokens: N/A{Style.RESET_ALL}")

    def print_agent_flow(self, intent: str, agent_name: str):
        """Print agent routing information"""
        if not self.enabled:
            return
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}🤖 AGENT ROUTING:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}├─ Intent: {intent}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}└─ Agent: {agent_name}{Style.RESET_ALL}")

    def print_state_info(self, language: str, message_count: int):
        """Print state information"""
        if not self.enabled:
            return
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 STATE INFO:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}├─ Language: {language}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└─ Messages in history: {message_count}{Style.RESET_ALL}")

    def print_error(self, error: str):
        """Print error message"""
        if not self.enabled:
            return
        print(f"\n{Fore.RED}{Style.BRIGHT}❌ ERROR:{Style.RESET_ALL}")
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")

    def print_llm_call(self, model: str, input_text: str, output_text: str,
                       elapsed: float, tokens: Optional[dict] = None):
        """Print complete LLM call information"""
        if not self.enabled:
            return

        # Color based on model type
        if "cohere" in model.lower() or "translation" in model.lower():
            color = Fore.MAGENTA
            icon = "🌐"
        else:
            color = Fore.BLUE
            icon = "🧠"

        self.print_section(f"{icon} LLM CALL: {model}", color)
        self.print_input(input_text, "INPUT", color)
        self.print_output(output_text, "OUTPUT", color)
        self.print_metrics(elapsed, tokens)


# Global debug logger instance
debug = DebugLogger(enabled=True)
