import argparse
import json
import sys

from transcript_router import TranscriptPipeline

DEMO_TRANSCRIPTS = [
    "Message Mark it's going to rain",
    "Blue tall doors look good for the exterior",
    "Remind me tomorrow at 9am to submit the permit",
    "Can you ask the contractor for the updated timeline?",
]


def get_transcript(arg_value: str | None) -> str:
    if arg_value:
        return arg_value.strip()

    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            return piped

    raise ValueError("Provide --transcript, --demo, or pipe transcript text via stdin.")


def run_demo(pipeline: TranscriptPipeline) -> list[dict]:
    return [pipeline.run(t) for t in DEMO_TRANSCRIPTS]


def main() -> int:
    parser = argparse.ArgumentParser(description="Route and process transcript via GPT.")
    parser.add_argument("--transcript", type=str, help="Input transcript text")
    parser.add_argument("--demo", action="store_true", help="Run built-in demo transcripts")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI model")
    args = parser.parse_args()

    try:
        pipeline = TranscriptPipeline(model=args.model)

        if args.demo:
            result = run_demo(pipeline)
        else:
            transcript = get_transcript(args.transcript)
            result = pipeline.run(transcript)

        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
