# Transcript Intent Router (GPT-powered)

This app classifies a transcript into one of:

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
# CLI
python3 app.py --transcript "Message Mark it's going to rain"

# Demo
python3 app.py --demo

# Web UI
python3 -m streamlit run web_app.py
```

## One-command web launch

```bash
./run_web.sh
```

This installs dependencies and launches the Streamlit web interface.

## Notes

- Default model is `gpt-4o-mini`.
- You can override with CLI: `python3 app.py --transcript "..." --model gpt-4.1-mini`.

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```


## Web Interface

The Streamlit UI includes:
- realtime execution logs in the sidebar (classification, API call, processor step, completion),
- persistent latest classified intent,
- persistent processed message output and full JSON payload.

## Public website deployment

To make it publicly accessible, run on a cloud VM/container and bind Streamlit to `0.0.0.0`:

```bash
./run_public.sh
```

Optional custom port:

```bash
PORT=8080 ./run_public.sh
```

Then expose that port in your cloud firewall/security group and point a domain/reverse-proxy to it.

Direct command equivalent:

```bash
python3 -m streamlit run web_app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
```
