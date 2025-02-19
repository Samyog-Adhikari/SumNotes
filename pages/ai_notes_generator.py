import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import PyPDF2
import io
import docx  # Import the python-docx library

# Page configuration
st.set_page_config(page_title="Notes Generator - SumNotes", page_icon="✍️", layout="wide")

# Custom CSS
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

# Main content 
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# Title and Description
st.markdown('<h1 style="font-size: 48px; text-align:center;">✍️ AI Notes Generator</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 20px; margin-bottom: 40px; text-align:center;">Transform your textbooks and documents into comprehensive study notes</p>', unsafe_allow_html=True)

# Feature cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <b>How it works:</b>
        <ul>
            <li>Upload your syllabus or study materials (PDF, DOC, DOCX).</li>
            <li>Enter your prompt or instructions for note generation.</li>
            <li>Get structured notes with main points and summaries.</li>
            <li>Review and organize your study materials effectively.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <b>Key Features:</b>
        <ul>
            <li>Smart content extraction and organization.</li>
            <li>Automatic summary generation.</li>
            <li>Key points identification.</li>
            <li>Easy-to-read formatted output.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Input and Output sections
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Initialize session state and Gemini API
if 'chapter_text' not in st.session_state:
    st.session_state.chapter_text = ""
if 'notes_history' not in st.session_state:
    st.session_state.notes_history = []

# ----------------- API Configuration -----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB-4ynxUsnEsnES-qINI6skuZL5_05o1AA")
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

def extract_text_from_pdf(pdf_file, page_range):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(page_range[0]-1, page_range[1]):
            text += pdf_reader.pages[page_num].extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_docx(docx_file):
    try:
        doc = docx.Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"

def generate_notes(text, custom_prompt=""):
    default_prompt = """
    Please analyze this book chapter and create comprehensive notes. Include:
    1. Main themes and key concepts
    2. Important points and arguments
    3. Notable quotes or passages
    4. Summary of the chapter
    5. Key takeaways
    """
    prompt = custom_prompt if custom_prompt else default_prompt
    prompt += f"\n\nChapter content: {text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating notes: {str(e)}"

def save_notes(notes, filename):
    notes_dir = Path("generated_notes")
    notes_dir.mkdir(exist_ok=True)
    file_path = notes_dir / f"{filename}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(notes)
    return file_path

def main():
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "PDF Upload", "DOCX Upload"]
    )
    
    if input_method == "Text Input":
        st.session_state.chapter_text = st.text_area(
            "Paste your chapter text here",
            value=st.session_state.chapter_text,
            height=300,
            placeholder="Enter the chapter content here..."
        )
    elif input_method == "PDF Upload":
        uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
        if uploaded_file is not None:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            num_pages = len(pdf_reader.pages)
            
            st.write(f"PDF has {num_pages} pages")
            page_range = st.slider(
                "Select page range",
                1, num_pages, (1, min(5, num_pages)),
                help="Select the range of pages to analyze"
            )
            
            if st.button("Extract Text from PDF"):
                with st.spinner("Extracting text from PDF..."):
                    st.session_state.chapter_text = extract_text_from_pdf(uploaded_file, page_range)
                    if st.session_state.chapter_text.startswith("Error"):
                        st.error(st.session_state.chapter_text)
                    else:
                        st.success("Text extracted successfully!")
                        with st.expander("Show extracted text"):
                            st.text(st.session_state.chapter_text[:1000] + "...")
    elif input_method == "DOCX Upload":
        uploaded_file = st.file_uploader("Upload DOCX file", type="docx")
        if uploaded_file is not None:
            if st.button("Extract Text from DOCX"):
                with st.spinner("Extracting text from DOCX..."):
                    st.session_state.chapter_text = extract_text_from_docx(uploaded_file)
                    if st.session_state.chapter_text.startswith("Error"):
                        st.error(st.session_state.chapter_text)
                    else:
                        st.success("Text extracted successfully!")
                        with st.expander("Show extracted text"):
                            st.text(st.session_state.chapter_text[:1000] + "...")
    
    chapter_name = st.text_input(
        "Chapter name/number",
        placeholder="e.g., Chapter 1 - Introduction"
    )
    
    custom_prompt = st.text_area(
        "Custom Prompt (Optional)",
        placeholder="Enter your custom instructions for note generation here...",
        help="Leave blank to use the default prompt"
    )
    
    if st.session_state.chapter_text:
        with st.expander("Current Text for Processing"):
            st.text(st.session_state.chapter_text[:500] + "...")
    
    if st.button("Generate Notes", type="primary"):
        if not st.session_state.chapter_text:
            st.error("Please enter text or upload a PDF or DOCX file.")
            return
            
        with st.spinner("Generating notes... This may take a moment."):
            notes = generate_notes(st.session_state.chapter_text, custom_prompt)
            
            if notes.startswith("Error"):
                st.error(notes)
            else:
                st.success("Notes generated successfully!")
                
                if chapter_name:
                    st.session_state.notes_history.append((chapter_name, notes))
                
                st.markdown("### Generated Notes")
                st.markdown(notes)
                
                if chapter_name:
                    file_path = save_notes(notes, chapter_name)
                    st.download_button(
                        label="Download Notes",
                        data=notes,
                        file_name=f"{chapter_name}_notes.txt",
                        mime="text/plain"
                    )
                    st.info(f"Notes saved to: {file_path}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center;">
            <div> SumNotes - Notes Generator © 2025</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()