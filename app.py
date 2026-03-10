import argparse
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

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

    raise ValueError("Provide --transcript, --demo, --web, or pipe transcript text via stdin.")


def run_demo(pipeline: TranscriptPipeline) -> list[dict]:
    return [pipeline.run(t) for t in DEMO_TRANSCRIPTS]


def render_index_html(model: str) -> bytes:
    template = Path("templates/index.html").read_text(encoding="utf-8")
    return template.replace("{{MODEL_NAME}}", model).encode("utf-8")


def process_transcript(transcript: str, model: str) -> tuple[int, dict]:
    transcript = transcript.strip()
    if not transcript:
        return 400, {"error": "Please provide a transcript."}

    try:
        pipeline = TranscriptPipeline(model=model)
        return 200, pipeline.run(transcript)
    except Exception as exc:
        return 500, {"error": str(exc)}


def make_handler(model: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                payload = render_index_html(model)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            if self.path == "/styles.css":
                payload = Path("static/styles.css").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/css; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            self.send_error(404)

        def do_POST(self):
            if self.path != "/api/process":
                self.send_error(404)
                return

            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                payload = {}

            status, response = process_transcript(str(payload.get("transcript", "")), model)
            data = json.dumps(response).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            return

    return Handler


def run_web_mode(host: str, port: int, model: str, open_browser: bool = True) -> int:
    server = ThreadingHTTPServer((host, port), make_handler(model))
    if open_browser:
        webbrowser.open(f"http://{host}:{port}")
    print(f"Web UI running at http://{host}:{port}")
    server.serve_forever()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Route and process transcript via GPT.")
    parser.add_argument("--transcript", type=str, help="Input transcript text")
    parser.add_argument("--demo", action="store_true", help="Run built-in demo transcripts")
    parser.add_argument("--web", action="store_true", help="Start a local web UI")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Web host (for --web)")
    parser.add_argument("--port", type=int, default=8000, help="Web port (for --web)")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI model")
    args = parser.parse_args()

    try:
        if args.web:
            return run_web_mode(args.host, args.port, args.model)

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
