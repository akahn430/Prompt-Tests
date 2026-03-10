from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Callable, Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime if dependency missing
    OpenAI = None  # type: ignore


VALID_INTENTS = ("Note", "Inquiry", "Reminder", "Message")


CLASSIFIER_PROMPT = """You are an intent classifier.
Classify the transcript into exactly one of these labels:
- Note
- Inquiry
- Reminder
- Message

Return ONLY the label text and nothing else.
"""


PROCESSOR_PROMPTS: Dict[str, str] = {
    "Note": """You are a Note Processor.
Convert the transcript into a concise, clean note format.
Return JSON with keys:
- type (always \"Note\")
- title
- note
- tags (array of short tags)
""",
    "Inquiry": """You are an Inquiry Processor.
Convert the transcript into a clear question/request format.
Return JSON with keys:
- type (always \"Inquiry\")
- question
- context
- requested_action
""",
    "Reminder": """You are a Reminder Processor.
Convert the transcript into a reminder format.
Return JSON with keys:
- type (always \"Reminder\")
- reminder
- due_time
- priority (low|normal|high)
""",
    "Message": """You are a Message Processor.
Convert the transcript into a sendable message format.
Return JSON with keys:
- type (always \"Message\")
- recipient
- message
- priority (low|normal|high)
- follow_up_needed (boolean)
""",
}


@dataclass
class TranscriptPipeline:
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        if OpenAI is None:
            raise RuntimeError(
                "openai package is not installed. Run: pip install -r requirements.txt"
            )
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, transcript: str) -> dict:
        classification = self.classify(transcript)
        processed_output = self.process(transcript, classification)
        return {
            "transcript": transcript,
            "classification": classification,
            "processed_output": processed_output,
        }

    def classify(self, transcript: str) -> str:
        raw = self._ask_model(CLASSIFIER_PROMPT, transcript)
        normalized = raw.strip().title()

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
            "type": classification,
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
        if t.startswith("message"):
            return "Message"
        if t.startswith("remind") or "reminder" in t:
            return "Reminder"
        if "?" in t or t.startswith("ask"):
            return "Inquiry"
        return "Note"


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
