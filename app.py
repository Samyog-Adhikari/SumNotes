import streamlit as st

# Page config
st.set_page_config(
    page_title="SumNotes",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit elements and sidebar
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
    </style>
""", unsafe_allow_html=True)

# Redirect to home page
st.switch_page("pages/home.py")