import streamlit as st
from PIL import Image
import io
import os
import sys
import requests

# Add parent directory to path so we can import api_helper
sys.path.append(os.path.dirname(__file__))
from api_helper import analyze_plant

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="AgriVision AI",
    page_icon="🪴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# HELPER: Crop Sample Images to Equal Size
# ============================================
@st.cache_data
def load_cropped_image(url, target_size=(400, 300)):
    response = requests.get(url, timeout=10)
    img = Image.open(io.BytesIO(response.content)).convert("RGB")
    target_w, target_h = target_size
    target_ratio = target_w / target_h
    img_ratio = img.width / img.height
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
    img = img.resize(target_size, Image.LANCZOS)
    return img

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}

    .stApp { background: linear-gradient(180deg, #f1f8e9 0%, #ffffff 100%); }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100% !important;
    }

    h1, h2, h3, h4, h5, h6 { color: #1b5e20 !important; font-weight: 700 !important; }
    p, span, div, label { color: #212121; }

    .main-header {
        display: flex; align-items: center; gap: 18px;
        padding: 22px 30px;
        background: linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%);
        border-radius: 16px; border-bottom: 3px solid #4CAF50;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.15);
        margin-bottom: 35px;
    }
    .logo-circle {
        width: 60px; height: 60px;
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 30px; box-shadow: 0 6px 15px rgba(76, 175, 80, 0.4);
    }
    .title-text { font-size: 30px; font-weight: 800; color: #1b5e20; margin: 0; }
    .subtitle-text { font-size: 14px; color: #555555; margin: 4px 0 0 0; }

    .section-title {
        color: #1b5e20 !important; font-weight: 700; font-size: 22px;
        margin-top: 25px; margin-bottom: 15px;
    }

    [data-testid="stImage"] img {
        border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        width: 100% !important; height: auto !important; display: block;
    }
    [data-testid="stImage"] figcaption {
        color: #1b5e20 !important; font-weight: 600;
        text-align: center; margin-top: 8px;
    }

    .uploaded-img [data-testid="stImage"] img {
        border-radius: 14px; box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        border: 3px solid #4CAF50;
    }

    [data-testid="stFileUploader"] {
        background: #ffffff; border: 2px dashed #4CAF50;
        border-radius: 16px; padding: 25px;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #2E7D32; background: #f9fdf7;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white !important; border: none; border-radius: 10px;
        padding: 12px 24px; font-weight: 600; font-size: 16px;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(76, 175, 80, 0.5);
        color: white !important;
    }

    .result-row {
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
        border-left: 5px solid #4CAF50;
        padding: 14px 18px; border-radius: 10px;
        margin-bottom: 14px;
    }
    .result-label {
        font-size: 12px; color: #666; text-transform: uppercase;
        letter-spacing: 1px; margin-bottom: 4px;
    }
    .result-value { font-size: 18px; font-weight: 700; color: #1b5e20; }

    .confidence-header {
        display: flex; justify-content: space-between; align-items: center;
        margin: 16px 0 8px 0;
    }
    .confidence-title { font-size: 15px; font-weight: 700; color: #1b5e20; }
    .confidence-badge {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white; padding: 5px 14px; border-radius: 20px;
        font-weight: 700; font-size: 13px;
        box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
    }

    /* Custom single progress bar */
    .custom-progress {
        background: #e8f5e9;
        border-radius: 10px;
        height: 14px;
        width: 100%;
        overflow: hidden;
        margin-top: 8px;
    }
    .custom-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    .treatment-box {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 6px solid #ff9800;
        padding: 18px 22px; border-radius: 14px; margin-top: 16px;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.15);
    }
    .treatment-title {
        font-size: 16px; font-weight: 700; color: #e65100; margin-bottom: 10px;
    }
    .treatment-text { font-size: 14px; line-height: 1.7; color: #4e342e; }
    </style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("""
    <div class="main-header">
        <div class="logo-circle">🪴</div>
        <div>
            <p class="title-text">AgriVision AI</p>
            <p class="subtitle-text">AI-powered plant disease detection, instantly</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================
# SAMPLE IMAGES
# ============================================
st.markdown('<p class="section-title">🔬 See It In Action</p>', unsafe_allow_html=True)

SAMPLE_URLS = [
    ("https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400", "🍅 Tomato — Early Blight"),
    ("https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400", "🥔 Potato — Healthy"),
    ("https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400", "🌶️ Pepper — Late Blight"),
]

col1, col2, col3 = st.columns(3)
for col, (url, caption) in zip([col1, col2, col3], SAMPLE_URLS):
    with col:
        try:
            img = load_cropped_image(url, target_size=(400, 300))
            st.image(img, caption=caption, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load image: {e}")

# ============================================
# UPLOAD SECTION
# ============================================
st.markdown('<p class="section-title">📤 Start Your Diagnosis</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drag & drop your leaf image, or browse",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed"
)

# ============================================
# PREVIEW + ANALYZER
# ============================================
if uploaded_file is not None:
    image_bytes = uploaded_file.read()

    st.markdown("")
    left, right = st.columns(2)

    # ---- LEFT: Uploaded Image ----
    with left:
        st.markdown('<p class="section-title">🖼️ Uploaded Image</p>', unsafe_allow_html=True)
        st.markdown('<div class="uploaded-img">', unsafe_allow_html=True)
        st.image(image_bytes, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- RIGHT: AI Analyzer ----
    with right:
        st.markdown('<p class="section-title">🔍 AI Analyzer</p>', unsafe_allow_html=True)

        if st.button("🌿 Run Diagnosis"):
            with st.spinner("Analyzing your plant with AI..."):
                result = analyze_plant(image_bytes)
            st.session_state["result"] = result

        if "result" in st.session_state:
            result = st.session_state["result"]

            st.markdown(f"""
                <div class="result-row">
                    <div class="result-label">🌱 Plant Identified</div>
                    <div class="result-value">{result['crop']}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="result-row">
                    <div class="result-label">🦠 Condition Detected</div>
                    <div class="result-value">{result['disease']}</div>
                </div>
            """, unsafe_allow_html=True)

            confidence = result.get("confidence", 0)
            st.markdown(f"""
                <div class="confidence-header">
                    <span class="confidence-title">📈 AI Confidence Level</span>
                    <span class="confidence-badge">{confidence}%</span>
                </div>
                <div class="custom-progress">
                    <div class="custom-progress-fill" style="width: {confidence}%;"></div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="treatment-box">
                    <div class="treatment-title">💊 Recommended Treatment</div>
                    <div class="treatment-text">{result['treatment']}</div>
                </div>
            """, unsafe_allow_html=True)

    if "result" in st.session_state:
        st.markdown("")
        center_col1, center_col2, center_col3 = st.columns([1, 1, 1])
        with center_col2:
            if st.button("🔄 New Diagnosis", use_container_width=True):
                del st.session_state["result"]
                st.rerun()

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #757575; font-size: 13px;'>"
    "Powered by Google Gemini AI • Built with Streamlit"
    "</p>",
    unsafe_allow_html=True
)