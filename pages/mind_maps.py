import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import os
import graphviz

# ----------------- Function Definitions -----------------

def extract_text_from_pdf(file, start_page, end_page):
    reader = PdfReader(file)
    text = ""
    for page_number in range(start_page - 1, end_page):
        page = reader.pages[page_number]
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def generate_mind_map(topic, description, study_plan, timeframe):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB-4ynxUsnEsnES-qINI6skuZL5_05o1AA")
    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {
        "temperature": 1.6,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-pro-exp-02-05",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])

    prompt = f"""
    Generate a mind map for the following topic:
    Topic: {topic}
    Description: {description}
    Study Plan: {study_plan}
    Timeframe: {timeframe}
    Structure the mind map with the following hierarchy:
    - The main topic should be the central node.
    - Under the main topic, list each day as a sub-heading.
    - Under each day, provide branches with key points or tasks.
    Use "->" to indicate connections between nodes for flowchart visualization.
    """

    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating mind map: {e}")
        return None

def parse_mind_map(mind_map_text):
    lines = mind_map_text.split("\n")
    nodes = set()
    edges = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "->" in line:
            try:
                parent, child = line.split("->")
                parent = parent.strip()
                child = child.strip()
                nodes.add(parent)
                nodes.add(child)
                edges.append((parent, child))
            except ValueError as e:
                print(f"Error parsing line: {line}. Error: {e}")
        else:
            nodes.add(line)

    print(f"Nodes: {nodes}")
    print(f"Edges: {edges}")

    return nodes, edges

def visualize_mind_map(mind_map_text):
    nodes, edges = parse_mind_map(mind_map_text)

    dot = graphviz.Digraph(comment='Mind Map')
    dot.attr(size='50,50!', dpi='500')  # Adjust the size as needed
    for node in nodes:
        dot.node(node)
    for parent, child in edges:
        dot.edge(parent, child)

    st.graphviz_chart(dot.source)

def main():
    st.set_page_config(page_title="Mind Maps Generator", page_icon="🧠", layout="wide")

    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h1 style="font-size: 48px; text-align: center;"> 🧠 AI MindMaps Generator </h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 20px; margin-bottom: 40px; text-align: center;">Generate the mindmaps which helps user is studies.</p>', unsafe_allow_html=True)

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

    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <b>How it works:</b>
            <ul>
                <li>Choose to upload a file or write your topic directly.</li>
                <li>Provide a brief description for better context.</li>
                <li>Select a study plan type and specify your desired study timeframe.</li>
                <li>Our AI will generate a visual mind map and provide a text clarification.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <b>Key Features:</b>
            <ul>
                <li>Upload documents or write topics for mind map generation.</li>
                <li>Interactive mind maps for visual learning.</li>
                <li>Text clarifications for comprehensive understanding.</li>
                <li>Customizable study plans based on your needs.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <div class="footer">
            <div style="display: flex; justify-content: center; align-items: center;">
                <div> SumNotes - Mind Maps © 2025</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.subheader("Input Details")
        
        input_mode = st.radio("Select Input Mode", ("Text Mode", "Upload Mode"))

        if input_mode == "Text Mode":
            topic = st.text_input("Topic", placeholder="Enter the main topic...")
            description = st.text_area("Description", placeholder="Describe the topic...")
            study_plan = st.text_area("Study Plan", placeholder="Outline your study plan...")
            timeframe = st.text_input("Timeframe", placeholder="Enter the timeframe...")
        else:
            uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
            start_page = st.number_input("Start Page (for PDF)", min_value=1, step=1, value=1)
            end_page = st.number_input("End Page (for PDF)", min_value=1, step=1, value=1)
            if uploaded_file is not None:
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file, start_page, end_page)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text = extract_text_from_docx(uploaded_file)
                else:
                    st.error("Unsupported file type.")
                    return

                st.text_area("Extracted Text", text, height=200)
                topic = st.text_input("Topic", placeholder="Enter the main topic...")
                description = st.text_area("Description", placeholder="Describe the topic...")
                study_plan = st.text_area("Study Plan", placeholder="Outline your study plan...")
                timeframe = st.text_input("Timeframe", placeholder="Enter the timeframe...")

        submit_button = st.button(label="Generate Mind Map")

    if submit_button:
        st.info("Generating Mind Map...")
        mind_map_text = generate_mind_map(topic, description, study_plan, timeframe)
        
        if mind_map_text:
            st.success("Mind Map Generated!")
            with st.container():
                st.subheader("Text Form")
                st.code(mind_map_text)

            st.subheader("Flowchart Form")
            visualize_mind_map(mind_map_text)

if __name__ == "__main__":
    main()