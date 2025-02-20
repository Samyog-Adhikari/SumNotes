import streamlit as st
import google.generativeai as genai
from PIL import Image
import pytesseract
import numpy as np
import cv2
import os
import speech_recognition as sr
from gtts import gTTS
from pdf2image import convert_from_path
from io import BytesIO
import base64
import streamlit.components.v1 as components
import pyttsx3
import tempfile

# ----------------- Page & API Configuration -----------------
st.set_page_config(page_title="Doubt Solver - SumNotes", page_icon="🤷‍♂️", layout="wide")

# ----------------- API Configuration -----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "Your API Key")
genai.configure(api_key=GEMINI_API_KEY)

# ----------------- Model Initialization -----------------
generation_config = {
    "temperature": 1.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 65535,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-thinking-exp-01-21",
    generation_config=generation_config,
)

# Set Tesseract Path default (You might need to change this)
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe" 

# ----------------- Custom CSS -----------------
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    .main {
        background-color: #0F1117;
        color: white;
        padding-top: 80px;
        padding-bottom: 80px;
    }

    .navigation {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background-color: white;
        padding: 1rem 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background-color: #0F1117;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem 2rem;
        font-size: 0.9rem;
    }

    .content-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        text-align: center; /* Align items to center */
    }

    .stButton > button {
        background-color: #2D74FF;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
    }

    .stTextArea > div > div > textarea {
        background-color: #1C1F26;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTextInput > div > div > input {
        background-color: #1C1F26;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .feature-card {
        background-color: #1C1F26;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        font-size: 18px;
        margin: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Style for the list items within feature cards */
    .feature-card ul {
        text-align: left; /* Align list items to the left */
        padding: 0; /* Remove default list padding */
        margin-top: 10px; /* Add some spacing above the list */
    }

    .feature-card li {
        list-style-type: disc; /* Use disc for list item markers */
        margin-left: 40px; /* Indent list items */
    }

    /* Styles for improved alignment and spacing */
    .main h1, .main p {
        text-align: center; 
    }

    .input-container {
        margin-top: 20px; 
        text-align: left; /* Reset text alignment for input */
    }

    .notes-output {
        margin-top: 20px; 
        text-align: left; /* Reset text alignment for output*/
        padding: 10px; /* Add some padding */
        border: 1px solid rgba(255, 255, 255, 0.1); /* Optional: Add a border */
    }

    .notes-output h3, 
    .notes-output p {
        margin-bottom: 10px; /* Reduced bottom margin for headings and paragraphs */
    }

    .ocr-preview { 
        border: 2px dashed #4a5568; 
        padding: 10px; 
        margin: 10px 0; 
    }

    .voice-controls { 
        background-color: #2d3446; 
        padding: 15px; 
        border-radius: 8px; 
        margin: 10px 0; 
    }
</style>
""", unsafe_allow_html=True)


# ----------------- Navigation Bar -----------------
st.markdown("""
    <div class="navigation">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center;">
                <span style="background-color: #2D74FF; color: white; padding: 6px 12px; margin-right: 12px; border-radius: 6px;">S</span>
                <span class="logo-text" style="font-size: 24px; color: #0F1117;">SumNotes</span>
            </div>
            <div>
                <a href="home" class="nav-link" style="color: #0F1117; text-decoration: none; margin: 0 15px;">Home</a>
                <a href="ai_notes_generator" class="nav-link" style="color: #0F1117; text-decoration: none; margin: 0 15px;">Notes Generator</a>
                <a href="summarizer" class="nav-link" style="color: #0F1117; text-decoration: none; margin: 0 15px;">Summarizer</a>
                <a href="doubt_solver" class="nav-link" style="color: #0F1117; text-decoration: none; margin: 0 15px;">Doubt Solver</a>
                <a href="ai_question_generator" class="nav-link" style="color: #0F1117; text-decoration: none; margin: 0 15px;">Question Predictor</a>
                <a href="ai_buddy" class="nav-link" style="color: #0F1117; text-decoration: none; margin: 0 15px;">AI Buddy</a>
                <a href="mind_maps" class="nav-link" style="color: #0F1117; text-decoration: none; margin: 0 15px;">Mind Maps</a>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ----------------- OCR Processing -----------------
class OCRProcessor:
    @staticmethod
    def preprocess_image(image):
        np_image = np.array(image)
        gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
        # Apply Otsu's thresholding
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # Dilate to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        gray = cv2.dilate(gray, kernel, iterations=1)
        return gray

    @staticmethod
    def process_image(image_file):
        try:
            image = Image.open(image_file)
            processed_image = OCRProcessor.preprocess_image(image)
            text = pytesseract.image_to_string(processed_image, config='--oem 3 --psm 6')
            return text, processed_image
        except Exception as e:
            st.error(f"Error processing image: {e}")
            return None, None

# ----------------- Voice Processing with gTTS -----------------
class VoiceProcessor:
    @staticmethod
    def text_to_speech_bytes(text, lang='en'):
        """
        Converts text to speech using gTTS and returns the audio bytes.
        """
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            st.error(f"Error converting text to speech (gTTS): {e}")
            return None

    @staticmethod
    def record_audio():
        """
        Records audio from the microphone and converts it to text.
        """
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening... Please speak now.")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                try:
                    text = r.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    st.error("Could not understand the audio.")
                    return None
                except sr.RequestError as e:
                    st.error(f"Error from speech recognition service: {e}")
                    return None
        except Exception as e:
            st.error(f"Microphone error: {e}")
            return None

# ----------------- Pyttsx3 TTS Function -----------------
def text_to_speech_pyttsx3(text, rate_multiplier):
    """
    Uses pyttsx3 to convert text to speech, saves the output as a temporary WAV file,
    then returns the file's audio bytes.
    """
    try:
        engine = pyttsx3.init()
        default_rate = engine.getProperty('rate')  # Typically around 200 wpm
        new_rate = int(default_rate * rate_multiplier)
        engine.setProperty('rate', new_rate)
        temp_file = tempfile.mktemp(suffix=".wav")
        engine.save_to_file(text, temp_file)
        engine.runAndWait()
        with open(temp_file, "rb") as f:
            audio_bytes = f.read()
        os.remove(temp_file)
        return audio_bytes
    except Exception as e:
        st.error(f"Error in pyttsx3 TTS: {e}")
        return None

# ----------------- Function to Play Audio Hidden -----------------
def play_audio_hidden(audio_bytes, playback_rate, mime_type="audio/mp3"):
    """
    Embeds a hidden HTML audio element that autoplays the provided audio bytes.
    The playback_rate is applied via JavaScript (for gTTS/MP3).
    For pyttsx3 (WAV), we keep playbackRate=1 because the audio is pre-rendered.
    """
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f"""
        <audio id="audio-player" autoplay style="display:none">
          <source src="data:{mime_type};base64,{audio_base64}" type="{mime_type}">
        </audio>
        <script>
          var audio = document.getElementById("audio-player");
          audio.playbackRate = {playback_rate};
          audio.play();
        </script>
        """
        components.html(audio_html, height=0)

# ----------------- AI Answer Generation -----------------
def get_answer_from_ai(question, context=""):
    chat_session = model.start_chat(history=[])
    prompt = f"Question: {question}\nContext: {context}\nPlease provide a clear, detailed answer."
    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating answer: {e}")
        return None

# ----------------- Main Application -----------------
def main():
    # Main content
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 style="font-size: 48px; text-align:center;;">🤷‍♂️ AI Doubt Solver</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 20px; margin-bottom: 40px; text-align:center;">Get Instant Answers to your questions</p>', unsafe_allow_html=True)

    # Input and Output sections
    st.markdown('<div class="input-container">', unsafe_allow_html=True) 

    # Create two tabs: Text & Voice, OCR
    tab1, tab2 = st.tabs(["Text & Voice", "OCR"])
    
    # ----- Tab 1: Text & Voice Input -----
    with tab1:
        input_method = st.radio("Choose input method:", ["Text", "Voice"])
        question = ""
        if input_method == "Text":
            question = st.text_area("Type your question here", height=100)
        else:
            st.markdown('<div class="voice-controls"><h4>Voice Input Controls</h4></div>', unsafe_allow_html=True)
            if st.button("🎤 Start Recording"):
                recorded_text = VoiceProcessor.record_audio()
                if recorded_text:
                    st.session_state.recorded_question = recorded_text
                    st.success(f"Recorded: {recorded_text}")
            # Display recorded question for review/editing.
            question = st.text_area("Recorded Question", value=st.session_state.get("recorded_question", ""), height=100)
        
        context = st.text_area("Additional Context (Optional)", height=100)
        
        if st.button("Get Answer", type="primary"):
            if question:
                with st.spinner("Generating answer..."):
                    answer = get_answer_from_ai(question, context)
                    if answer:
                        st.markdown('<div class="notes-output">', unsafe_allow_html=True) 
                        st.markdown("<h3> Answer: </h3>", unsafe_allow_html=True)
                        st.write(answer)
                        # Use pyttsx3 for TTS by default
                        voice_speed = st.session_state.get("voice_speed", 1.0) # Default speed
                        audio_bytes = text_to_speech_pyttsx3(answer, rate_multiplier=voice_speed)
                        play_audio_hidden(audio_bytes, playback_rate=1, mime_type="audio/wav")
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Please provide a question (either type or record one).")
    
    # ----- Tab 2: OCR -----
    with tab2:
        uploaded_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg', 'pdf'])
        if uploaded_file:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h3> Original Image </h3>", unsafe_allow_html=True)
                image = Image.open(uploaded_file)
                st.image(image, use_column_width=True)
            with col2:
                st.markdown("<h3> Processed Text </h3>", unsafe_allow_html=True)
                if st.button("Extract Text"):
                    text, _ = OCRProcessor.process_image(uploaded_file)
                    if text:
                        st.code(text)
                        if st.button("Use as Question"):
                            st.session_state.question = text
                            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True) # Close input-container
    st.markdown('</div>', unsafe_allow_html=True) # Close content-container

# Footer
st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center;">
            <div> SumNotes - Doubt Solver © 2025</div>
        </div>
    </div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
