import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import PyPDF2
import io

def extract_text_from_pdf(pdf_file, page_range):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(page_range[0]-1, page_range[1]):
            text += pdf_reader.pages[page_num].extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

# Page configuration
st.set_page_config(page_title="Notes Summarizer - SumNotes", page_icon="↕️", layout="wide")


# Custom CSS for dark theme and styling
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
        }

        /* Style the output section with reduced gaps */
        .notes-output {
            margin-top: 20px;
            padding: 10px; /* Add some padding */
            border: 1px solid rgba(255, 255, 255, 0.1); /* Optional: Add a border */
        }
        .notes-output h3, 
        .notes-output p {
            margin-bottom: 10px; /* Reduced bottom margin for headings and paragraphs */
        }
    </style>
""", unsafe_allow_html=True)

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



# Modify the generate_notes function for summarization
def generate_summary(text, summary_length, custom_prompt=""): 
    default_prompt = f"""
    Please summarize the following text, focusing on the main points and key takeaways. 
    The summary should be approximately {summary_length}% of the original text.
    """
    
    prompt = custom_prompt if custom_prompt else default_prompt
    
    prompt += f"\n\nText to summarize: {text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def save_summary(summary, filename):
    summary_dir = Path("generated_summaries") # New directory for summaries
    summary_dir.mkdir(exist_ok=True)
    
    file_path = summary_dir / f"{filename}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(summary)
    return file_path


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

st.markdown('<h1 style="font-size: 48px; text-align: center;">✍️ Notes Summarizer</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 20px; margin-bottom: 40px; text-align: center;">Get concise and insightful summaries of your documents or text.</p>', unsafe_allow_html=True)

# Feature cards
col1, col2 = st.columns(2)  # Create two columns

with col1:
    st.markdown("""
    <div class="feature-card">
        <b>How it works:</b>
        <ul>
            <li>Upload your document or paste text content.</li>
            <li>Our AI analyzes the content structure.</li>
            <li>Get a concise, well-organized summary.</li>
            <li>Export or share your summaries easily.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <b>Key Features:</b>
        <ul>
            <li>Smart content analysis.</li>
            <li>Multiple file format support.</li>
            <li>Customizable summary length.</li>
            <li>Key points extraction.</li> 
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

def main():
    
    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "PDF Upload"]  # Removed DOCX option
    )

    # Summarization length selection
    summary_length = st.selectbox(
        "Choose summarization length:",
        ["Short (20%)", "Medium (30%)", "Long (45%)"]
    )
    
    if input_method == "Text Input":
        # Text input section
        st.session_state.chapter_text = st.text_area(
            "Paste your syllabus/notes text here",
            value=st.session_state.chapter_text,
            height=300,
            placeholder="Enter the text here..."
        )
    elif input_method == "PDF Upload": 
        # PDF upload section
        uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
        if uploaded_file is not None:
            # Add PDF page selection
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
                    # Extract text and store in session state
                    st.session_state.chapter_text = extract_text_from_pdf(uploaded_file, page_range)
                    
                    if st.session_state.chapter_text.startswith("Error"):
                        st.error(st.session_state.chapter_text)
                    else:
                        st.success("Text extracted successfully!")
                        # Show preview of extracted text
                        with st.expander("Show extracted text"):
                            st.text(st.session_state.chapter_text[:1000] + "...")

    # Chapter/Document name input
    document_name = st.text_input( 
        "Document Name (for saving the summary)",
        placeholder="e.g., Introduction to AI"
    )
    
    # Display current text being processed
    if st.session_state.chapter_text:
        with st.expander("Current Text for Processing"):
            st.text(st.session_state.chapter_text[:500] + "...")
    
    # Custom prompt input
    custom_prompt = st.text_area(
        "Custom Prompt (Optional)",
        placeholder="Enter your custom instructions for summarization here...",
        help="Leave blank to use the default prompt"
    )

    # Generate button
    if st.button("Generate Summary", type="primary"):
        if not st.session_state.chapter_text:
            st.error("Please enter text or upload a file.")
            return
        
        # Get the selected summarization length
        if summary_length == "Short (20%)":
            length_percentage = 20
        elif summary_length == "Medium (30%)":
            length_percentage = 30
        else:
            length_percentage = 45
            
        with st.spinner("Generating summary... This may take a moment."):
            summary = generate_summary(st.session_state.chapter_text, length_percentage, custom_prompt)
            
            if summary.startswith("Error"):
                st.error(summary)
            else:
                st.success("Summary generated successfully!")
                
                # Add to history
                if document_name:
                    st.session_state.notes_history.append((document_name, summary))
                
                # Display summary in the output section with adjusted spacing
                st.markdown('<div class="notes-output">', unsafe_allow_html=True) 
                st.header("Generated Summary")
                st.markdown(summary)
                
                # Save summary
                if document_name:
                    file_path = save_summary(summary, document_name)
                    st.download_button(
                        label="Download Summary",
                        data=summary,
                        file_name=f"{document_name}_summary.txt",
                        mime="text/plain"
                    )
                    st.info(f"Summary saved to: {file_path}")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
# Footer
st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center;">
            <div> SumNotes - Notes Summarizer © 2025</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
