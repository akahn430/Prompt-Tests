import streamlit as st

from transcript_router import TranscriptPipeline

st.set_page_config(page_title="Transcript Intent Router", page_icon="🧭", layout="centered")

st.title("🧭 Transcript Intent Router")
st.caption("Classify transcript intent and return processor-formatted JSON output.")

model = st.text_input("Model", value="gpt-4o-mini")
transcript = st.text_area(
    "Transcript",
    placeholder="Message Mark it's going to rain",
    height=140,
)

if st.button("Process Transcript", type="primary"):
    if not transcript.strip():
        st.error("Please enter a transcript.")
    else:
        try:
            pipeline = TranscriptPipeline(model=model.strip() or "gpt-4o-mini")
            result = pipeline.run(transcript.strip())
            st.subheader("Result")
            st.json(result)
        except Exception as exc:
            st.error(str(exc))
