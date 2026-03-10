# Transcript Intent Router (GPT-powered)

This app takes a transcript, classifies it into one of:

- `Note`
- `Inquiry`
- `Reminder`
- `Message`

It then sends the transcript to the matching processor prompt and returns a final formatted output.

## Why this implementation

The ChatGPT Custom GPT URLs you shared are browser products and are not directly callable over the public OpenAI API by URL. This app mirrors that workflow programmatically using GPT calls and separate prompts for each stage.

## Quick start (from a fresh terminal)

```bash
git clone <your_repo_url>
cd Prompt-Tests
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY="your_key_here"
python3 app.py --web
```

If you see `requirements.txt` or `app.py` "not found", you are not in the repo folder yet. Run `pwd` and `ls` to confirm you are inside `Prompt-Tests`.

## Web app mode (single command)

```bash
python3 app.py --web
```

This starts a local site (default: `http://127.0.0.1:8000`) with:
- transcript input box
- submit button
- classification result
- full structured JSON output panel

Optional host/port:

```bash
python3 app.py --web --host 0.0.0.0 --port 8080
```

## Optional: install once and run from anywhere

```bash
cd Prompt-Tests
python3 -m pip install --no-build-isolation .
export OPENAI_API_KEY="your_key_here"
transcript-router --web
```

This installs a global CLI command named `transcript-router` so you don't have to run `python3 app.py` from the repo directory.
In locked-down networks, `--no-build-isolation` avoids extra build-dependency downloads.

## Setup

1. Create and activate a Python virtual environment (recommended).
2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Set your API key:

```bash
export OPENAI_API_KEY="your_key_here"
```

## CLI run mode

```bash
python3 app.py --transcript "Message Mark it's going to rain"
```

You can also read from stdin:

```bash
echo "Blue tall doors look good for the exterior" | python3 app.py
```

## Output shape

The app prints JSON like:

```json
{
  "transcript": "Message Mark it's going to rain",
  "classification": "Message",
  "processed_output": {
    "type": "Message",
    "recipient": "Mark",
    "message": "It's going to rain",
    "priority": "normal",
    "follow_up_needed": false
  }
}
```

## Demo mode (single command)

Run a built-in set of example transcripts in one command:

```bash
python3 app.py --demo
```

Or, if installed as a CLI:

```bash
transcript-router --demo
```

This prints a JSON array of processed results for:
- `Message Mark it's going to rain`
- `Blue tall doors look good for the exterior`
- `Remind me tomorrow at 9am to submit the permit`
- `Can you ask the contractor for the updated timeline?`

## Optional model override

Default model is `gpt-4o-mini`.

```bash
python3 app.py --transcript "..." --model gpt-4.1-mini
```

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
