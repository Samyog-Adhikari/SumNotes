import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import os
import base64
import streamlit.components.v1 as components
import pyttsx3
import tempfile

# ----------------- Page & API Configuration -----------------
st.set_page_config(page_title="AI Buddy - SumNotes", page_icon="🤖", layout="wide")

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

# ----------------- Shared CSS -----------------
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
            text-align: center;
        }

        .stButton > button {
            background-color: #2D74FF;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
        }

        .stTextArea > div > div > textarea,
        .stTextInput > div > div > input {
            background-color: #1C1F26;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px;
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

        .feature-card ul {
            text-align: left;
            padding: 0;
            margin-top: 10px;
        }

        .feature-card li {
            list-style-type: disc;
            margin-left: 40px;
        }

        .main h1, .main p {
            text-align: center; 
        }

        .input-container, .notes-output {
            margin-top: 20px; 
            text-align: left;
        }

        .stop-icon {
            margin-left: 5px;
            vertical-align: middle;
        }

        .chat-log {
            background-color: #1C1F26;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            max-height: 400px;
            overflow-y: auto;
        }

        .chat-log p {
            margin: 5px 0;
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

# ----------------- Voice Processing with gTTS -----------------
class VoiceProcessor:
    @staticmethod
    def text_to_speech_bytes(text, lang='en'):
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
    try:
        engine = pyttsx3.init()
        default_rate = engine.getProperty('rate')
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
def get_answer_from_ai(question, ai_name):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = f"You are {ai_name}, a helpful AI assistant. The user asks: {question}\nPlease provide a clear, detailed answer."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating answer: {e}")
        return None

# ----------------- Main Application -----------------
def main():

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "ai_name" not in st.session_state:
        st.session_state.ai_name = "Buddy"
    if "recording" not in st.session_state:
        st.session_state.recording = False
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "stop_response" not in st.session_state:
        st.session_state.stop_response = False

    # --- Main content layout ---
    # ----------------- Main Content -----------------
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h1 style="font-size: 48px; text-align: center;">🤖 AI Buddy</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 20px; margin-bottom: 40px; text-align: center;">Chat with your virtual friend.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <b>How it works:</b>
            <ul>
                <li>Start a conversation with your AI study buddy.</li>
                <li>Ask questions about any subject or concept.</li>
                <li>Get detailed explanations and examples.</li>
                <li>Engage in interactive learning discussions.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <b>Key Features:</b>
            <ul>
                <li>Personalized learning companion</li>
                <li>Interactive Q&A sessions</li>
                <li>Brainstorming and summarizing capabilities</li>
                <li>Support for various topics and concepts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="settings-box">', unsafe_allow_html=True)
        st.markdown('<div class="settings-box-title">Voice Settings</div>', unsafe_allow_html=True)
        tts_engine = st.selectbox("TTS Engine", ["pyttsx3", "gTTS"])
        st.session_state["tts_engine"] = tts_engine
        if tts_engine == "pyttsx3":
            voice_speed = st.slider("Rate Multiplier (pyttsx3)", min_value=1.0, max_value=2.0, value=1.0, step=0.1)
            st.session_state["voice_speed"] = voice_speed
        else:
            voice_speed = st.slider("Playback Speed (gTTS)", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
            st.session_state["voice_speed"] = voice_speed
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader(f"AI Buddy")

        with st.container():
            st.markdown('<div class="name-setting-container">', unsafe_allow_html=True)
            ai_name_input = st.text_input("Enter AI Buddy's name", value=st.session_state.ai_name, label_visibility="collapsed")
            if st.button("Set Name", key="set_name_button"):
                st.session_state.ai_name = ai_name_input
                st.success(f"AI Buddy's name set to {ai_name_input}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Chat Log")

        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-log">', unsafe_allow_html=True)
            for message in st.session_state.chat_history:
                role = "User" if message["role"] == "user" else "AI"
                st.markdown(f"<p><b>{role}:</b> {message['content']}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        input_method = st.radio("Input method:", ["Text", "Voice"], horizontal=True)

        if input_method == "Text":
            with st.container():
                col_input, col_button = st.columns([4, 1])
                with col_input:
                    st.session_state.user_input = st.text_input("Type your message...", key="text_input_area", label_visibility="collapsed")
                with col_button:
                    if st.button("Send", key="send_button", type="primary", disabled=not st.session_state.user_input):
                        user_input = st.session_state.user_input
                        st.session_state.user_input = ""
                        if user_input:
                            st.session_state.chat_history.append({"role": "user", "content": user_input})
                            with st.spinner(f"{st.session_state.ai_name} is thinking..."):
                                ai_response = get_answer_from_ai(user_input, st.session_state.ai_name)
                                if ai_response:
                                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                                    if ai_response:
                                        tts_engine = st.session_state.get("tts_engine", "gTTS")
                                        voice_speed = st.session_state.get("voice_speed", 1.5)
                                        if tts_engine == "gTTS":
                                            audio_bytes = VoiceProcessor.text_to_speech_bytes(ai_response)
                                            play_audio_hidden(audio_bytes, playback_rate=voice_speed, mime_type="audio/mp3")
                                        else:
                                            audio_bytes = text_to_speech_pyttsx3(ai_response, rate_multiplier=voice_speed)
                                            play_audio_hidden(audio_bytes, playback_rate=1, mime_type="audio/wav")

        else:
            if st.session_state.recording:
                if st.button("Stop Recording 🎤"):
                    st.session_state.recording = False
                    recorded_text = VoiceProcessor.record_audio()
                    if recorded_text:
                        user_input = recorded_text
                        if user_input:
                            st.session_state.chat_history.append({"role": "user", "content": user_input})
                            with st.spinner(f"{st.session_state.ai_name} is thinking..."):
                                ai_response = get_answer_from_ai(user_input, st.session_state.ai_name)
                                if ai_response:
                                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                                    if ai_response:
                                        tts_engine = st.session_state.get("tts_engine", "gTTS")
                                        voice_speed = st.session_state.get("voice_speed", 1.5)
                                        if tts_engine == "gTTS":
                                            audio_bytes = VoiceProcessor.text_to_speech_bytes(ai_response)
                                            play_audio_hidden(audio_bytes, playback_rate=voice_speed, mime_type="audio/mp3")
                                        else:
                                            audio_bytes = text_to_speech_pyttsx3(ai_response, rate_multiplier=voice_speed)
                                            play_audio_hidden(audio_bytes, playback_rate=1, mime_type="audio/wav")
            else:
                if st.button("Start Recording 🎤"):
                    st.session_state.recording = True
                    user_input = ""

    # Button to stop AI response with an icon
    if st.button("Stop AI Response", key="stop_response_button"):
        st.session_state.stop_response = True
        st.warning("AI response stopped.")
        st.markdown('<img src="https://img.icons8.com/ios-filled/50/000000/stop.png" class="stop-icon"/>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
# Footer
st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center;">
            <div> SumNotes - Buddy © 2025</div>
        </div>
    </div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
