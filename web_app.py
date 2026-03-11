import json
from datetime import datetime

import streamlit as st

from transcript_router import (
    CLASSIFIER_PROMPT,
    PROCESSOR_PROMPTS,
    VALID_INTENTS,
    TranscriptPipeline,
    try_parse_json,
)

st.set_page_config(page_title="Transcript Intent Router", page_icon="🧭", layout="wide")

st.markdown(
    """
<style>
.block-container {max-width: 1100px; padding-top: 2rem;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(120,120,120,.25);}
.muted {opacity: .7; font-size: .95rem;}
</style>
""",
    unsafe_allow_html=True,
)

if "logs" not in st.session_state:
    st.session_state.logs = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None


def append_log(message: str, sidebar_placeholder) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {message}")
    sidebar_placeholder.code("\n".join(st.session_state.logs[-200:]), language="text")


def run_pipeline_with_logs(transcript: str, model: str, sidebar_placeholder) -> dict:
    append_log("Initializing pipeline", sidebar_placeholder)
    pipeline = TranscriptPipeline(model=model)

    append_log("Classifying intent", sidebar_placeholder)
    raw_label = pipeline._ask_model(CLASSIFIER_PROMPT, transcript)
    classification = raw_label.strip().lower()

    if classification not in VALID_INTENTS:
        append_log(f"Classifier returned '{raw_label.strip()}'; applying fallback", sidebar_placeholder)
        classification = pipeline._fallback_classification(transcript)

    append_log(f"Detected intent: {classification}", sidebar_placeholder)

    append_log("Calling OAI API for processor", sidebar_placeholder)
    raw_processed = pipeline._ask_model(PROCESSOR_PROMPTS[classification], transcript)
    parsed = try_parse_json(raw_processed)

    if isinstance(parsed, dict):
        processed_output = parsed
    else:
        processed_output = {"type": classification.title(), "raw": raw_processed.strip()}

    append_log(f"Processing {classification} complete", sidebar_placeholder)

    return {
        "transcript": transcript,
        "classification": classification.title(),
        "processed_output": processed_output,
    }


st.title("Transcript Intent Router")
st.markdown('<p class="muted">Minimal UI with real-time execution logs.</p>', unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Realtime Logs")
    logs_placeholder = st.empty()
    logs_placeholder.code("\n".join(st.session_state.logs[-200:]) or "No logs yet.", language="text")
    if st.button("Clear Logs"):
        st.session_state.logs = []
        logs_placeholder.code("No logs yet.", language="text")

left, right = st.columns([1.1, 1], gap="large")

with left:
    model = st.text_input("Model", value="gpt-4o-mini")
    transcript = st.text_area(
        "Transcript",
        placeholder="Message Mark it's going to rain",
        height=180,
    )

    if st.button("Process Transcript", type="primary", use_container_width=True):
        if not transcript.strip():
            st.error("Please enter a transcript.")
        else:
            try:
                result = run_pipeline_with_logs(transcript.strip(), model.strip() or "gpt-4o-mini", logs_placeholder)
                st.session_state.last_result = result
                append_log("Result persisted in session", logs_placeholder)
            except Exception as exc:
                append_log(f"Error: {exc}", logs_placeholder)
                st.error(str(exc))

with right:
    st.subheader("Latest Result")
    if st.session_state.last_result:
        result = st.session_state.last_result
        st.metric("Classified Intent", result["classification"])
        st.markdown("**Processed Message**")
        st.json(result["processed_output"])
        with st.expander("Full payload", expanded=False):
            st.code(json.dumps(result, indent=2), language="json")
    else:
        st.info("Run a transcript to persist and display the latest classified intent and processed message.")
