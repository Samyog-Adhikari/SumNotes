import streamlit as st
import os
import google.generativeai as genai
from docx import Document
import PyPDF2

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

chat_session = model.start_chat(history=[])

def predict_questions(subject, topics, num_questions, question_type, custom_prompt=None):
    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = f"""
        You are an AI exam predictor. Generate {num_questions} {question_type} exam questions for the subject: {subject}.
        Focus on the following topics: {topics}.
        """
    
    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Error generating questions: {str(e)}"

def extract_text_from_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return ' '.join(full_text)

def extract_text_from_pdf(file, page_range=None):
    pdf_reader = PyPDF2.PdfReader(file)
    full_text = []
    pages = pdf_reader.pages
    if page_range:
        pages = pages[page_range[0]-1:page_range[1]]
    for page in pages:
        full_text.append(page.extract_text())
    return ' '.join(full_text)

# ----------------- Page Configuration -----------------
st.set_page_config(page_title="Question Predictor - SumNotes", page_icon="❓", layout="wide")


# ----------------- Custom CSS for Styling -----------------
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
        
        .content-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .stButton > button {
            background-color: #2D74FF;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
        }

        .stTextInput > div > div > input {
            background-color: #1C1F26;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stNumberInput > div > div > input {
            background-color: #1C1F26;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .prediction-output {
            margin-top: 20px;
            padding: 15px;
            background-color: #1C1F26;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            font-family: 'Courier New', Courier, monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-wrap: break-word;
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

# ----------------- Main Content -----------------
st.markdown('<div class="content-container">', unsafe_allow_html=True)
st.markdown('<h1 style="font-size: 48px; text-align: center;">❓ AI Exam Questions Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 20px; margin-bottom: 40px; text-align: center;">Predict possible exam questions based on topics you select or by uploading a document.</p>', unsafe_allow_html=True)

# Radio button for selecting input mode
input_mode = st.radio("Select Input Mode", ("Text Mode", "Upload Mode"))

if input_mode == "Text Mode":
    subject = st.text_input("Subject", placeholder="Enter the subject (e.g., Physics, Chemistry)")
    topics = st.text_input("Topics", placeholder="Enter topics separated by commas")
else:
    uploaded_file = st.file_uploader("Upload a .docx or .pdf file", type=["docx", "pdf"])
    if uploaded_file:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            topics = extract_text_from_docx(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            num_pages = len(PyPDF2.PdfReader(uploaded_file).pages)
            st.write(f"PDF has {num_pages} pages")
            page_range = st.slider(
                "Select page range",
                1, num_pages, (1, min(5, num_pages)),
                help="Select the range of pages to analyze"
            )
            topics = extract_text_from_pdf(uploaded_file, page_range)
        subject = "From Uploaded Document"

# Custom prompt input
custom_prompt = st.text_area("Custom Prompt (Optional)", placeholder="Enter a custom prompt for generating questions")

# Select box for question type
question_type = st.selectbox("Select Question Type", ("Multiple Choice", "Short Answer", "Long Answer"))

num_questions = st.number_input("Number of Questions", min_value=1, max_value=100, value=10)

# Button to generate questions
if st.button("Generate Questions"):
    with st.spinner("Generating questions... This may take a moment."):
        if custom_prompt:
            questions = predict_questions(subject, topics, num_questions, question_type, custom_prompt)
        elif subject and topics:
            questions = predict_questions(subject, topics, num_questions, question_type)
        else:
            st.warning("Please provide subject and topics or a custom prompt.")
            questions = None

    if questions:
        st.markdown('<div class="prediction-output">', unsafe_allow_html=True)
        st.markdown("### Generated Questions", unsafe_allow_html=True)
        st.code(questions, language='text')
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Footer -----------------
st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center;">
            <div> SumNotes - Question Predictor © 2025</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Closing the content container
st.markdown('</div>', unsafe_allow_html=True)
