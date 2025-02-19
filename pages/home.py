import streamlit as st

# Page config
st.set_page_config(page_title="Home - SumNotes", page_icon="📔", layout="wide")

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
        
        .feature-card {
            background-color: #1C1F26;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            font-size: 18px;
            height: 140px;
            margin: 10px;
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
st.markdown('<h1 style="text-align: center; font-size: 48px; margin-top: 40px;">🎊 Welcome to SumNotes 🎊</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 20px; margin-bottom: 40px;">Transform your learning experience with AI-powered tools</p>', unsafe_allow_html=True)

# Feature cards
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    st.markdown('<div class="feature-card"><b>AI Notes Generator</b><br>Create structured notes effortlessly</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card"><b>AI Summarizer</b><br>Get quick summaries of your content</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card"><b>Doubt Solver</b><br>Get instant answers to your questions</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card"><b>Exam Question Predictor</b><br>Predict the question from PYQs.</div>', unsafe_allow_html=True)
with col5:
    st.markdown('<div class="feature-card"><b>Mind Maps</b><br>Visualize concepts and connections</div>', unsafe_allow_html=True)
with col6:
    st.markdown('<div class="feature-card"><b>AI Buddy</b><br>Your personal AI study companion</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center;">
            <div> SumNotes - Home © 2025</div>
        </div>
    </div>
""", unsafe_allow_html=True)
