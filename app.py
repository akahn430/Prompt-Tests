import argparse
import json
import sys

from transcript_router import TranscriptPipeline


def get_transcript(arg_value: str | None) -> str:
    if arg_value:
        return arg_value.strip()

    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            return piped

    raise ValueError("Provide --transcript or pipe transcript text via stdin.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Route and process transcript via GPT.")
    parser.add_argument("--transcript", type=str, help="Input transcript text")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI model")
    args = parser.parse_args()

    try:
        transcript = get_transcript(args.transcript)
        pipeline = TranscriptPipeline(model=args.model)
        result = pipeline.run(transcript)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
