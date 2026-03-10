import io
import json
import unittest
from unittest.mock import patch

import app


class FakePipeline:
    def __init__(self, model: str):
        self.model = model

    def run(self, transcript: str) -> dict:
        return {
            "transcript": transcript,
            "classification": "Note",
            "processed_output": {"type": "Note"},
        }


class AppTests(unittest.TestCase):
    def test_demo_mode_outputs_multiple_items(self):
        stdout = io.StringIO()
        with patch("app.TranscriptPipeline", FakePipeline), patch("sys.argv", ["app.py", "--demo"]), patch("sys.stdout", stdout):
            exit_code = app.main()

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), len(app.DEMO_TRANSCRIPTS))

    def test_transcript_mode_outputs_single_item(self):
        stdout = io.StringIO()
        with patch("app.TranscriptPipeline", FakePipeline), patch(
            "sys.argv", ["app.py", "--transcript", "Message Mark it's going to rain"]
        ), patch("sys.stdout", stdout):
            exit_code = app.main()

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["transcript"], "Message Mark it's going to rain")

    def test_web_mode_dispatches(self):
        with patch("app.run_web_mode", return_value=0) as run_web_mode, patch("sys.argv", ["app.py", "--web", "--port", "8010"]):
            exit_code = app.main()

        self.assertEqual(exit_code, 0)
        run_web_mode.assert_called_once_with("127.0.0.1", 8010, "gpt-4o-mini")

    def test_process_transcript(self):
        with patch("app.TranscriptPipeline", FakePipeline):
            status, payload = app.process_transcript("Blue tall doors", "fake-model")

        self.assertEqual(status, 200)
        self.assertEqual(payload["classification"], "Note")


if __name__ == "__main__":
    unittest.main()
