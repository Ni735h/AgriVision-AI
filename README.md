# 🌿 AgriVision AI

AI-powered plant disease detection. Upload a leaf image → get plant name, disease, and treatment suggestions.

## ✨ Features
- 📤 Upload leaf image
- 🔬 Detect plant + disease
- 📊 Confidence score
- 💊 Treatment recommendations
- 🎨 Clean, modern UI

## 🛠️ Tech Stack
- **AI/ML**: Google Gemini 3.6 Flash (Multimodal LLM)
- **UI**: Streamlit
- **Image Processing**: Pillow
- **Language**: Python 3.12

## 🚀 Quick Start

1. Clone repo:
   git clone https://github.com/TUMHARA-USERNAME/agrivision-ai.git

2. Install dependencies:
   pip install -r requirements.txt

3. Add your Gemini API key:
   - Get free key from https://aistudio.google.com/app/apikey
   - Create `config/.env` file
   - Add: `GEMINI_API_KEY=your_key_here`

4. Run:
   streamlit run app/app.py

## 📸 Screenshots
![AgriVision AI](screenshot.png)

## 📄 License
MIT