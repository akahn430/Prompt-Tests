import unittest

from transcript_router import CLASSIFIER_PROMPT, FakePipeline, try_parse_json


class TranscriptRouterTests(unittest.TestCase):
    def test_classification_and_processing_path(self):
        def responder(system_prompt: str, transcript: str) -> str:
            if system_prompt == CLASSIFIER_PROMPT:
                return "Message"
            return "{\"type\":\"Message\",\"recipient\":\"Mark\",\"message\":\"It is going to rain\",\"priority\":\"normal\",\"follow_up_needed\":false}"

        pipeline = FakePipeline(responder)
        output = pipeline.run("Message Mark it's going to rain")

        self.assertEqual(output["classification"], "Message")
        self.assertEqual(output["processed_output"]["recipient"], "Mark")

    def test_fallback_classification(self):
        def responder(system_prompt: str, transcript: str) -> str:
            if system_prompt == CLASSIFIER_PROMPT:
                return "unknown"
            return "{\"type\":\"Note\",\"title\":\"Design\",\"note\":\"Blue tall doors look good for the exterior\",\"tags\":[\"design\"]}"

        pipeline = FakePipeline(responder)
        output = pipeline.run("Blue tall doors look good for the exterior")

        self.assertEqual(output["classification"], "Note")

    def test_markdown_json_parsing(self):
        payload = """```json
        {"a": 1}
        ```"""
        parsed = try_parse_json(payload)
        self.assertEqual(parsed, {"a": 1})


if __name__ == "__main__":
    unittest.main()
