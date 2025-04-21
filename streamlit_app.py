import streamlit as st
import os
import nest_asyncio
from streamlit.watcher import local_sources_watcher
from src.config import Config
from src.code_parser import extract_functions
from src.summarizer import Summarizer
import logging
from datetime import datetime

# Page config
st.set_page_config(page_title="Codebase Summarizer", layout="wide")

# Patch for asyncio and torch
nest_asyncio.apply()
original_get_module_paths = local_sources_watcher.get_module_paths
def patched_get_module_paths(module):
    if module.__name__ == "torch.classes":
        return []
    return original_get_module_paths(module)
local_sources_watcher.get_module_paths = patched_get_module_paths

# Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Light-themed custom CSS
st.markdown(
    """
    <style>
    body, .main {
        background-color: #ffffff;
        color: #333333;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        font-weight: 600;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #105a8b;
        transform: scale(1.03);
    }
    .section-title {
        font-size: 26px;
        font-weight: 700;
        margin-top: 20px;
        color: white;
    }
    .card {
        background: #f9f9f9;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .summary-text {
        font-size: 16px;
        line-height: 1.6;
        color: white;
    }
    .error-box {
        background-color: #ffdddd;
        border-left: 5px solid #e60000;
        padding: 10px;
        margin: 10px 0;
    }
    .success-box {
        display: inline-block;
        padding: 6px 12px;
        background-color: #e0f7e9;
        color: #2e7d32;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 500;
        margin: 5px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    with st.sidebar:
        st.image("machine-learning-4-robot-developer-working-programming-coding-ai-machine-learning-script-1024.webp", caption="Codebase Summarizer", use_container_width=True)
        st.markdown("## 👋 Welcome")
        st.write("Upload a Python `.py` file to generate function-level and codebase summaries.")
        st.write("Choose a perspective (Product Manager, Developer, or Manager).")

    st.markdown('<div class="section-title">📄 Upload Python File</div>', unsafe_allow_html=True)

    try:
        Config.validate()
    except Exception as e:
        st.markdown(f'<div class="error-box">⚠️ {e}</div>', unsafe_allow_html=True)
        return

    try:
        summarizer = Summarizer(
            function_model_name=Config.FUNCTION_SUMMARIZER_MODEL,
            groq_api_key=Config.GROQ_API_KEY,
            groq_model=Config.GROQ_MODEL
        )
    except Exception as e:
        st.markdown(f'<div class="error-box">⚠️ {e}</div>', unsafe_allow_html=True)
        return

    uploaded_file = st.file_uploader("",type=["py"])
    if uploaded_file:
        temp_path = "temp.py"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.markdown('<div class="success-box">✅ File uploaded successfully!</div>', unsafe_allow_html=True)

        functions = extract_functions(temp_path)
        if not functions:
            st.markdown('<div class="error-box">⚠️ No functions found in the file.</div>', unsafe_allow_html=True)
            return

        extracted_summaries = []

        st.markdown('<div class="section-title">🧠 Function Summaries</div>', unsafe_allow_html=True)
        for func in functions:
            with st.expander(f"{func['name']} (Line {func['line_start']})"):
                summary = summarizer.summarize_function(func['code'])
                extracted_summaries.append(summary)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.code(func['code'], language='python')
                st.markdown("**Summary:**")
                st.markdown(f'<div class="summary-text">{summary}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if extracted_summaries:
            summary_text = "\n\n".join(
                f"Function: {func['name']} (Line {func['line_start']})\nSummary: {summary}"
                for func, summary in zip(functions, extracted_summaries)
            )
            st.download_button(
                "⬇️ Download Function Summaries",
                summary_text,
                file_name=f"function_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

        st.markdown('<div class="section-title">🧾 Overall Codebase Summary</div>', unsafe_allow_html=True)

        # Two columns: dropdown on left, button on right
        col1, col2 = st.columns([3, 1])

        with col1:
            user_type = st.selectbox(
                "Select a role",
                ["product_manager", "developer", "manager"],
                key="perspective_select",
            )

        with col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)  # vertical align trick
            generate = st.button("Generate Summary", key="generate_summary")

        # Trigger summary generation
        if generate:
            with st.spinner("Generating summary..."):
                try:
                    summary = summarizer.summarize_codebase(extracted_summaries, user_type)

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("**Overall Summary:**")
                    st.markdown(f'<div class="summary-text">{summary}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Download button
                    st.download_button(
                        label="⬇️ Download Overall Summary",
                        data=summary,
                        file_name=f"overall_summary_{user_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        help="Download the overall summary as a .txt file"
                    )

                except Exception as e:
                    st.markdown(f'<div class="error-box">⚠️ {e}</div>', unsafe_allow_html=True)

        # Final cleanup
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"Removed temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()
