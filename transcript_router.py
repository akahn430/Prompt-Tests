from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime if dependency missing
    OpenAI = None  # type: ignore


VALID_INTENTS = ("reminder", "message", "inquiry", "note")
INTENT_TO_DISPLAY = {
    "message": "Message",
    "reminder": "Reminder",
    "inquiry": "Inquiry",
    "note": "Note",
}


def _load_prompt_file(filename: str) -> str:
    path = Path(__file__).parent / "prompts" / filename
    return path.read_text(encoding="utf-8").strip()


CLASSIFIER_PROMPT = _load_prompt_file("intent_classifier.txt")

PROCESSOR_PROMPTS: Dict[str, str] = {
    "message": _load_prompt_file("message_processor.txt"),
    "reminder": _load_prompt_file("reminder_processor.txt"),
    "inquiry": _load_prompt_file("inquiry_processor.txt"),
    "note": _load_prompt_file("note_processor.txt"),
}


@dataclass
class TranscriptPipeline:
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        if OpenAI is None:
            raise RuntimeError(
                "openai package is not installed. Run: pip install -r requirements.txt"
            )

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to your shell profile and reload (e.g., source ~/.zshrc)."
            )

        self.client = OpenAI(api_key=api_key)

    def run(self, transcript: str) -> dict:
        classification = self.classify(transcript)
        processed_output = self.process(transcript, classification)
        return {
            "transcript": transcript,
            "classification": INTENT_TO_DISPLAY[classification],
            "processed_output": processed_output,
        }

    def classify(self, transcript: str) -> str:
        raw = self._ask_model(CLASSIFIER_PROMPT, transcript)
        normalized = raw.strip().lower()

        if normalized not in VALID_INTENTS:
            normalized = self._fallback_classification(transcript)

        return normalized

    def process(self, transcript: str, classification: str) -> dict:
        prompt = PROCESSOR_PROMPTS[classification]
        raw = self._ask_model(prompt, transcript)
        parsed = try_parse_json(raw)

        if isinstance(parsed, dict):
            return parsed

        return {
            "type": INTENT_TO_DISPLAY[classification],
            "raw": raw.strip(),
        }

    def _ask_model(self, system_prompt: str, transcript: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript},
            ],
            temperature=0,
        )
        return response.output_text

    @staticmethod
    def _fallback_classification(transcript: str) -> str:
        t = transcript.lower().strip()

        message_tokens = (
            "message ",
            "text ",
            "email ",
            "slack ",
            "tell ",
            "send ",
            "write to ",
        )
        reminder_tokens = ("remind me", "set a reminder", "reminder")
        inquiry_tokens = (
            "?",
            "what",
            "who",
            "where",
            "when",
            "why",
            "how",
            "tell me",
            "explain",
            "look up",
            "find out",
        )

        if any(tok in t[:40] for tok in message_tokens) or any(tok in t for tok in message_tokens):
            return "message"
        if any(tok in t for tok in reminder_tokens):
            return "reminder"
        if any(tok in t for tok in inquiry_tokens):
            return "inquiry"
        return "note"


def try_parse_json(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    if "```" in text:
        parts = [p.strip() for p in text.split("```") if p.strip()]
        for chunk in parts:
            chunk = chunk.removeprefix("json").strip()
            try:
                return json.loads(chunk)
            except json.JSONDecodeError:
                continue

    return None


class FakePipeline(TranscriptPipeline):
    """Used for tests/offline mode by injecting custom LLM behavior."""

    def __init__(self, responder: Callable[[str, str], str], model: str = "fake"):
        self.model = model
        self._responder = responder

    def _ask_model(self, system_prompt: str, transcript: str) -> str:
        return self._responder(system_prompt, transcript)
