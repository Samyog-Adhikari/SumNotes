# SumNotes

**SumNotes** is an AI-powered study companion built with [Streamlit](https://streamlit.io/) and [Google Gemini](https://ai.google.dev/). It brings together note summarization, note generation, doubt solving, exam question prediction, mind mapping, and a conversational study buddy into one multi-page web app — designed to help students learn faster and retain more.

## ✨ Features

| Page | Description |
|---|---|
| 🏠 **Home** | Landing page with navigation to every tool. |
| ↕️ **Summarizer** | Paste text or upload a PDF (with a custom page range) and get a concise AI-generated summary. |
| 📝 **AI Notes Generator** | Turn raw text, PDFs, or DOCX files into structured, well-formatted study notes, with support for custom prompts. |
| 🤷‍♂️ **Doubt Solver** | Ask a question by typing, speaking (voice-to-text), or uploading an image/PDF (OCR text extraction), and get a clear explanation — read aloud via text-to-speech. |
| ❓ **AI Question Generator** | Generate likely exam questions from your notes or previous-year questions (PYQs), with optional custom prompts. |
| 🤖 **AI Buddy** | A conversational AI study companion with voice input/output for a more natural, tutor-like experience. |
| 🧠 **Mind Maps** | Convert text, PDFs, or DOCX files into visual mind maps/flowcharts using Graphviz. |

## 🛠️ Tech Stack

- **Framework:** [Streamlit](https://streamlit.io/) (multi-page app)
- **AI Model:** [Google Gemini](https://ai.google.dev/) via `google-generativeai`
- **Document Parsing:** `PyPDF2`, `python-docx`, `pdf2image`
- **OCR:** `pytesseract`, `opencv-python`, `Pillow`
- **Voice:** `SpeechRecognition`, `gTTS`, `pyttsx3`
- **Visualization:** `graphviz`

## 📂 Project Structure

```
SumNotes/
├── app.py                       # Entry point — redirects to the Home page
├── pages/
│   ├── home.py                  # Landing page & navigation
│   ├── summarizer.py            # AI Summarizer
│   ├── ai_notes_generator.py    # AI Notes Generator
│   ├── ai_question_generator.py # Exam Question Predictor
│   ├── doubt_solver.py          # AI Doubt Solver (text/voice/OCR)
│   ├── ai_buddy.py              # AI Buddy (voice chat companion)
│   └── mind_maps.py             # Mind Map generator
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on your `PATH` (required for the Doubt Solver's image-to-text feature)
- [Poppler](https://poppler.freedesktop.org/) installed (required by `pdf2image` for PDF-to-image conversion)
- (Linux only) `espeak`/`espeak-ng` installed for `pyttsx3` text-to-speech

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Samyog-Adhikari/SumNotes.git
   cd SumNotes
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit google-generativeai PyPDF2 python-docx pdf2image pytesseract opencv-python Pillow SpeechRecognition gTTS pyttsx3 graphviz numpy
   ```

   > A `requirements.txt` isn't included yet — the command above installs everything the app imports. Consider adding one with `pip freeze > requirements.txt` once your environment is set up.

4. **Set your Gemini API key**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"   # On Windows: set GEMINI_API_KEY=your-api-key-here
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`.

## 🔑 Configuration

SumNotes reads your Gemini API key from the `GEMINI_API_KEY` environment variable. If it isn't set, the app falls back to a placeholder and AI features will not work until a valid key is provided.

## 🗺️ Roadmap

- [ ] Add a `requirements.txt` for one-command setup
- [ ] Improve speech recognition accuracy
- [ ] Export generated notes as formatted PDF/PowerPoint
- [ ] Persist user notes/history (currently session-based)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Samyog-Adhikari/SumNotes/issues) or open a pull request.

## 📄 License

No license has been specified yet. Consider adding one (e.g. MIT) so others know how they can use this project.

## 👤 Author

**Samyog Adhikari**
[GitHub](https://github.com/Samyog-Adhikari)
