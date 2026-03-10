# Transcript Intent Router (GPT-powered)

This app takes a transcript, classifies it into one of:

- `Note`
- `Inquiry`
- `Reminder`
- `Message`

It then sends the transcript to the matching processor prompt and returns a final formatted output.

## Why this implementation

The ChatGPT Custom GPT URLs you shared are browser products and are not directly callable over the public OpenAI API by URL. This app mirrors that workflow programmatically using GPT calls and separate prompts for each stage.

## Setup

1. Create and activate a Python virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your API key:

```bash
export OPENAI_API_KEY="your_key_here"
```

## Run

```bash
python app.py --transcript "Message Mark it's going to rain"
```

You can also read from stdin:

```bash
echo "Blue tall doors look good for the exterior" | python app.py
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
python app.py --demo
```

This prints a JSON array of processed results for:
- `Message Mark it's going to rain`
- `Blue tall doors look good for the exterior`
- `Remind me tomorrow at 9am to submit the permit`
- `Can you ask the contractor for the updated timeline?`

## Optional model override

Default model is `gpt-4o-mini`.

```bash
python app.py --transcript "..." --model gpt-4.1-mini
```

## Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```
