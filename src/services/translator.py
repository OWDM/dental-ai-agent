"""
Translation service for TRT (Translate-Reason-Translate) architecture.
Handles language detection and bidirectional Arabic-English translation.
"""

import re
import time
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.debug import debug


# =============================================================================
# DENTAL GLOSSARY - Consistent terminology mappings
# =============================================================================
DENTAL_GLOSSARY = {
    # Procedures (English -> Arabic)
    "Tooth Extraction": "خلع الأسنان",
    "Emergency Visit": "زيارة طوارئ",
    "Crown Installation": "تركيب التاج",
    "Root Canal Treatment": "علاج قناة الجذر",
    "Teeth Cleaning": "تنظيف الأسنان",
    "Initial Examination": "الفحص الأولي",
    "Orthodontic Consultation": "استشارة تقويم الأسنان",
    "Teeth Whitening": "تبييض الأسنان",
    "Tooth Filling": "حشو الأسنان",
    "Deep Cleaning": "تنظيف عميق",
    # Specializations
    "Oral Surgery": "جراحة الفم",
    "Orthodontics": "تقويم الأسنان",
    "General Dentistry": "طب الأسنان العام",
    "Pediatric Dentistry": "طب أسنان الأطفال",
    "Periodontics": "أمراض اللثة",
}

# =============================================================================
# NAME MAPPINGS - Bidirectional Arabic ↔ English
# =============================================================================
PATIENT_NAMES = {
    # Arabic -> English
    "محمد علي القحطاني": "Mohammed Ali Al-Qahtani",
    "فاطمة عبدالله السعيد": "Fatimah Abdullah Al-Saeed",
    "سارة حسن الشهري": "Sara Hassan Al-Shehri",
    "عبدالرحمن فهد الدوسري": "Abdulrahman Fahad Al-Dossary",
    "ريم ماجد الحربي": "Reem Majed Al-Harbi",
    "أحمد محمد العتيبي": "Ahmed Mohammed Al-Otaibi",
    "نورة إبراهيم الغامدي": "Noura Ibrahim Al-Ghamdi",
    "خالد سعود المطيري": "Khalid Saud Al-Mutairi",
}

DOCTOR_NAMES = {
    # Arabic -> English
    "د. هند محمد السديري": "Dr. Hind Mohammed Al-Sudairy",
    "دكتورة هند محمد السديري": "Dr. Hind Mohammed Al-Sudairy",
    "د. ليلى أحمد الفيصل": "Dr. Laila Ahmed Al-Faisal",
    "دكتورة ليلى أحمد الفيصل": "Dr. Laila Ahmed Al-Faisal",
    "د. سعد بن عبدالعزيز الخالد": "Dr. Saad bin Abdulaziz Al-Khaled",
    "دكتور سعد بن عبدالعزيز الخالد": "Dr. Saad bin Abdulaziz Al-Khaled",
    "د. يوسف سليمان العجلان": "Dr. Yousef Sulaiman Al-Ajlan",
    "دكتور يوسف سليمان العجلان": "Dr. Yousef Sulaiman Al-Ajlan",
    "د. عمر فهد الراشد": "Dr. Omar Fahad Al-Rashed",
    "دكتور عمر فهد الراشد": "Dr. Omar Fahad Al-Rashed",
}

# Reverse mappings for EN -> AR translation
PATIENT_NAMES_REVERSE = {v: k for k, v in PATIENT_NAMES.items()}
DOCTOR_NAMES_REVERSE = {v: k for k, v in list(DOCTOR_NAMES.items())[::2]}  # Take first Arabic variant


def _build_glossary_prompt() -> str:
    """Build the glossary section for translation prompts."""
    lines = ["GLOSSARY (use these exact translations):"]
    for en, ar in DENTAL_GLOSSARY.items():
        lines.append(f'- "{en}" ↔ "{ar}"')
    return "\n".join(lines)


def _build_names_prompt_ar_to_en() -> str:
    """Build name mappings for Arabic to English translation."""
    lines = ["NAME MAPPINGS (Arabic → English):"]

    lines.append("\nPatients:")
    for ar, en in PATIENT_NAMES.items():
        lines.append(f'- "{ar}" → "{en}"')

    lines.append("\nDoctors:")
    for ar, en in DOCTOR_NAMES.items():
        lines.append(f'- "{ar}" → "{en}"')

    return "\n".join(lines)


def _build_names_prompt_en_to_ar() -> str:
    """Build name mappings for English to Arabic translation."""
    lines = ["NAME MAPPINGS (English → Arabic):"]

    lines.append("\nPatients:")
    for en, ar in PATIENT_NAMES_REVERSE.items():
        lines.append(f'- "{en}" → "{ar}"')

    lines.append("\nDoctors:")
    for en, ar in DOCTOR_NAMES_REVERSE.items():
        lines.append(f'- "{en}" → "{ar}"')

    return "\n".join(lines)


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

        # Build dynamic prompts
        glossary = _build_glossary_prompt()
        names = _build_names_prompt_ar_to_en()

        system_prompt = f"""You are a deterministic translation engine. You are NOT an AI assistant.
You do not converse, explain, summarize, or add commentary.
Output ONLY the English translation - nothing else.

RULES:
1. Translate Arabic to English accurately
2. Preserve all formatting, numbers, dates, times, and punctuation
3. Use glossary terms exactly as specified
4. Convert Arabic names to their English equivalents using the name mappings

{glossary}

{names}

Examples:
Arabic: أريد حجز موعد لتنظيف الأسنان
English: I want to book an appointment for Teeth Cleaning

Arabic: موعدي مع د. سعد بن عبدالعزيز الخالد
English: My appointment with Dr. Saad bin Abdulaziz Al-Khaled

Arabic: أحتاج علاج قناة الجذر مع دكتور عمر فهد الراشد
English: I need Root Canal Treatment with Dr. Omar Fahad Al-Rashed

Arabic: أنا محمد علي القحطاني
English: I am Mohammed Ali Al-Qahtani"""

        messages = [
            SystemMessage(content=system_prompt),
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

        # Build dynamic prompts
        glossary = _build_glossary_prompt()
        names = _build_names_prompt_en_to_ar()

        system_prompt = f"""You are a deterministic translation engine. You are NOT an AI assistant.
You do not converse, explain, summarize, or add commentary.
Output ONLY the Arabic translation - nothing else.

RULES:
1. Translate English to Arabic accurately
2. Preserve all formatting, numbers, dates, times, emails, and punctuation
3. Use glossary terms exactly as specified (use the Arabic equivalents)
4. Convert English names to their Arabic equivalents using the name mappings

{glossary}

{names}

Examples:
English: I've booked your Teeth Cleaning appointment with Dr. Saad bin Abdulaziz Al-Khaled
Arabic: لقد حجزت موعد تنظيف الأسنان مع د. سعد بن عبدالعزيز الخالد

English: Your Root Canal Treatment is scheduled for November 25 at 3:30 PM
Arabic: موعد علاج قناة الجذر الخاص بك في 25 نوفمبر الساعة 3:30 مساءً

English: Dr. Omar Fahad Al-Rashed specializes in Periodontics
Arabic: د. عمر فهد الراشد متخصص في أمراض اللثة

English: Mohammed Ali Al-Qahtani, your appointment is confirmed
Arabic: محمد علي القحطاني، تم تأكيد موعدك"""

        messages = [
            SystemMessage(content=system_prompt),
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
