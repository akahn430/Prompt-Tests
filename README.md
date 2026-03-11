# Transcript Intent Router (GPT-powered)

This app classifies a transcript into one of:

- `Note`
- `Inquiry`
- `Reminder`
- `Message`

Then it routes the transcript to the matching processor and prints structured JSON.

## Setup

```bash
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY="your_key_here"
```

If you saved your key in `~/.zshrc`, reload with:

```bash
source ~/.zshrc
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
