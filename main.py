

import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import requests

# Ensure .env is loaded
for env_path in [
    Path.cwd() / ".env",
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent.parent / ".env",
]:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        if os.getenv("GROQ_API_KEY"):
            break
load_dotenv()

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease Detection",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Enhanced modern CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #f7f9fa 100%);
    }
    .result-card {
        background: rgba(255,255,255,0.95);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(44,62,80,0.10);
        padding: 2.5em 2em;
        margin-top: 1.5em;
        margin-bottom: 1.5em;
        transition: box-shadow 0.3s;
    }
    .result-card:hover {
        box-shadow: 0 8px 32px rgba(44,62,80,0.18);
    }
    .disease-title {
        color: #1b5e20;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 0.5em;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px #e0e0e0;
    }
    .section-title {
        color: #1976d2;
        font-size: 1.25em;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .timestamp {
        color: #616161;
        font-size: 0.95em;
        margin-top: 1.2em;
        text-align: right;
    }
    .info-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        border-radius: 8px;
        padding: 0.3em 0.8em;
        font-size: 1em;
        margin-right: 0.5em;
        margin-bottom: 0.3em;
    }
    .symptom-list, .cause-list, .treatment-list {
        margin-left: 1em;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <div style='text-align: center; margin-top: 1em;'>
        <span style='font-size:2.5em;'>🌿</span>
        <h1 style='color: #1565c0; margin-bottom:0;'>Leaf Disease Detection</h1>
        <p style='color: #616161; font-size:1.15em;'>Upload a leaf image to detect diseases and get expert recommendations.</p>
    </div>
""", unsafe_allow_html=True)

api_url = os.getenv("LEAF_DISEASE_API_URL", "http://localhost:8000").rstrip("/")

col1, col2 = st.columns([1, 2])
with col1:
    uploaded_file = st.file_uploader(
        "Upload Leaf Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Preview")

with col2:
    if uploaded_file is not None:
        if st.button("🔍 Detect Disease", use_container_width=True):
            with st.spinner("Analyzing leaf image with AI..."):
                result = None
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }
                    try:
                        response = requests.post(
                            f"{api_url}/disease-detection-file", files=files, timeout=120)
                        if response.status_code == 200:
                            result = response.json()
                        else:
                            st.error(f"API Error: {response.status_code}")
                            try:
                                detail = response.json().get("detail", response.text)
                            except ValueError:
                                detail = response.text
                            st.write(detail)
                    except requests.exceptions.ConnectionError:
                        st.info("FastAPI backend is offline. Running direct AI detection...")
                        from utils import convert_image_to_base64_and_test
                        result = convert_image_to_base64_and_test(uploaded_file.getvalue())

                    if result is not None:
                        # Check if it's an invalid image
                        if result.get("disease_type") == "invalid_image":
                            st.markdown("<div class='result-card'>",
                                        unsafe_allow_html=True)
                            st.markdown(
                                "<div class='disease-title'>⚠️ Invalid Image</div>", unsafe_allow_html=True)
                            st.markdown(
                                "<div style='color: #ff5722; font-size: 1.1em; margin-bottom: 1em;'>Please upload a clear image of a plant leaf for accurate disease detection.</div>", unsafe_allow_html=True)

                            # Show the symptoms (which contain the error message)
                            if result.get("symptoms"):
                                st.markdown(
                                    "<div class='section-title'>Issue</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='symptom-list'>",
                                            unsafe_allow_html=True)
                                for symptom in result.get("symptoms", []):
                                    st.markdown(
                                        f"<li>{symptom}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            # Show treatment recommendations
                            if result.get("treatment"):
                                st.markdown(
                                    "<div class='section-title'>What to do</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='treatment-list'>",
                                            unsafe_allow_html=True)
                                for treat in result.get("treatment", []):
                                    st.markdown(
                                        f"<li>{treat}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            st.markdown("</div>", unsafe_allow_html=True)

                        elif result.get("disease_detected"):
                            st.markdown("<div class='result-card'>",
                                        unsafe_allow_html=True)
                            st.markdown(
                                f"<div class='disease-title'>🦠 {result.get('disease_name', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Type: {result.get('disease_type', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Severity: {result.get('severity', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Symptoms</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='symptom-list'>",
                                        unsafe_allow_html=True)
                            for symptom in result.get("symptoms", []):
                                st.markdown(
                                    f"<li>{symptom}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Possible Causes</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='cause-list'>",
                                        unsafe_allow_html=True)
                            for cause in result.get("possible_causes", []):
                                st.markdown(
                                    f"<li>{cause}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Treatment</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='treatment-list'>",
                                        unsafe_allow_html=True)
                            for treat in result.get("treatment", []):
                                st.markdown(
                                    f"<li>{treat}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                f"<div class='timestamp'>🕒 {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            # Healthy leaf case
                            st.markdown("<div class='result-card'>",
                                        unsafe_allow_html=True)
                            st.markdown(
                                "<div class='disease-title'>✅ Healthy Leaf</div>", unsafe_allow_html=True)
                            st.markdown(
                                "<div style='color: #4caf50; font-size: 1.1em; margin-bottom: 1em;'>No disease detected in this leaf. The plant appears to be healthy!</div>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Status: {result.get('disease_type', 'healthy')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<div class='timestamp'>🕒 {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
