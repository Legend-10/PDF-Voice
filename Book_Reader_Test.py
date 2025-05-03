import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import requests
import io
import base64
from pydub import AudioSegment
from pydub.playback import play

# ElevenLabs API setup (Replace 'YOUR_API_KEY' with your actual API key)
ELEVENLABS_API_KEY = "sk_e3bbbd9c1f1fdb9205d36bfa08ccbfce77caf0d80e729ab8"
ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Change to preferred voice ID

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def generate_audio(text):
    """Converts text to speech using ElevenLabs API."""
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + ELEVENLABS_VOICE_ID
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error("Failed to generate audio. Check API key and voice ID.")
        return None

def save_audio(audio_data):
    """Saves the generated audio as an MP3 file."""
    audio_file = "output.mp3"
    with open(audio_file, "wb") as f:
        f.write(audio_data)
    return audio_file

def get_audio_download_link(audio_file):
    """Generates a download link for the generated audio file."""
    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="book_audio.mp3">Download Audio</a>'
    return href

# Streamlit UI
st.title("📖 Book-to-Audio Converter")
st.write("Upload a book PDF and listen to its narration in a natural voice.")

pdf_file = st.file_uploader("Upload your book (PDF)", type=["pdf"])
if pdf_file is not None:
    st.success("PDF uploaded successfully!")
    text = extract_text_from_pdf(pdf_file)
    
    if st.button("Convert to Audio"):
        with st.spinner("Generating audio..."):
            audio_data = generate_audio(text[:5000])  # Limiting to 5000 chars per request
            if audio_data:
                audio_file = save_audio(audio_data)
                st.audio(audio_file, format='audio/mp3')
                st.markdown(get_audio_download_link(audio_file), unsafe_allow_html=True)
