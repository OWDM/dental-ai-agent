"""
Translation service for TRT (Translate-Reason-Translate) architecture.
Handles language detection and bidirectional Arabic-English translation.
"""

import re
import time
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.debug import debug


class TranslationService:
    """Service for detecting language and translating between Arabic and English."""

    def __init__(self, translation_llm):
        """
        Initialize the translation service.

        Args:
            translation_llm: LangChain LLM instance for translation (Cohere model)
        """
        self.translation_llm = translation_llm

    def detect_language(self, text: str) -> Literal["arabic", "english"]:
        """
        Detect if the input text is primarily Arabic or English.

        Args:
            text: Input text to analyze

        Returns:
            "arabic" if text contains Arabic characters, "english" otherwise
        """
        # Check for Arabic Unicode range (U+0600 to U+06FF)
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')

        # If we find any Arabic characters, consider it Arabic
        if arabic_pattern.search(text):
            return "arabic"

        return "english"

    async def translate_to_english(self, text: str) -> str:
        """
        Translate Arabic text to English.

        Args:
            text: Arabic text to translate

        Returns:
            English translation
        """
        start_time = time.time()

        messages = [
            SystemMessage(content=(
                "Translate Arabic to English word-for-word. Keep all formatting.\n\n"
                "Examples:\n"
                "Arabic: مرحباً\n"
                "English: Hello\n\n"
                "Arabic: السلام عليكم\n"
                "English: Peace be upon you\n\n"
                "Arabic: أريد حجز موعد\n"
                "English: I want to book an appointment\n\n"
                "Arabic: متى ساعات الدوام؟\n"
                "English: When are the working hours?"
            )),
            HumanMessage(content=f"Arabic: {text}\nEnglish:")
        ]

        response = await self.translation_llm.ainvoke(messages)
        translated = response.content.strip()

        # Debug logging
        elapsed = time.time() - start_time
        tokens = None
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            usage = response.response_metadata['token_usage']
            tokens = {
                'input_tokens': usage.get('prompt_tokens', 'N/A'),
                'output_tokens': usage.get('completion_tokens', 'N/A'),
                'total_tokens': usage.get('total_tokens', 'N/A')
            }

        debug.print_llm_call(
            model="Translation (Cohere)",
            input_text=text,
            output_text=translated,
            elapsed=elapsed,
            tokens=tokens
        )
        debug.print_translation(text, translated, "ar->en")

        return translated

    async def translate_to_arabic(self, text: str) -> str:
        """
        Translate English text to Arabic.

        Args:
            text: English text to translate

        Returns:
            Arabic translation
        """
        start_time = time.time()

        messages = [
            SystemMessage(content=(
                "Translate English to Arabic word-for-word. Keep all formatting and numbers.\n\n"
                "Examples:\n"
                "English: Hello\n"
                "Arabic: مرحباً\n\n"
                "English: I want to book an appointment\n"
                "Arabic: أريد حجز موعد\n\n"
                "English: When are the working hours?\n"
                "Arabic: متى ساعات الدوام؟\n\n"
                "English: Dr. Ahmed - 500 SAR\n"
                "Arabic: د. أحمد - 500 ريال"
            )),
            HumanMessage(content=f"English: {text}\nArabic:")
        ]

        response = await self.translation_llm.ainvoke(messages)
        translated = response.content.strip()

        # Debug logging
        elapsed = time.time() - start_time
        tokens = None
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            usage = response.response_metadata['token_usage']
            tokens = {
                'input_tokens': usage.get('prompt_tokens', 'N/A'),
                'output_tokens': usage.get('completion_tokens', 'N/A'),
                'total_tokens': usage.get('total_tokens', 'N/A')
            }

        debug.print_llm_call(
            model="Translation (Cohere)",
            input_text=text,
            output_text=translated,
            elapsed=elapsed,
            tokens=tokens
        )
        debug.print_translation(text, translated, "en->ar")

        return translated


# Singleton instance (initialized in main.py after LLM client is created)
_translator_instance = None


def get_translator(translation_llm=None):
    """
    Get or create the singleton translator instance.

    Args:
        translation_llm: LLM instance for translation (required on first call)

    Returns:
        TranslationService instance
    """
    global _translator_instance

    if _translator_instance is None:
        if translation_llm is None:
            raise ValueError("translation_llm must be provided on first call")
        _translator_instance = TranslationService(translation_llm)

    return _translator_instance
