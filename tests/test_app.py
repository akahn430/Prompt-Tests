import io
import json
import unittest
from unittest.mock import patch

import app


class FakePipeline:
    def __init__(self, model: str):
        self.model = model

    def run(self, transcript: str) -> dict:
        return {"transcript": transcript, "classification": "Note", "processed_output": {"type": "Note"}}


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


if __name__ == "__main__":
    unittest.main()
