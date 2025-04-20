# import streamlit as st
# import os
# from src.config import Config
# from src.code_parser import extract_functions
# from src.summarizer import Summarizer
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# def main():
#     """Main function to run the Streamlit app for codebase summarization."""
#     st.title("Codebase Summarizer")
#     st.markdown(
#         """
#         Upload a Python file to generate summaries for each function and an overall codebase summary.
#         Select a perspective (Product Manager, Developer, or Manager) for the overall summary.
#         """
#     )

#     # Validate configuration
#     try:
#         Config.validate()
#     except ValueError as e:
#         st.error(f"Configuration error: {e}")
#         logger.error(f"Configuration error: {e}")
#         return
#     except FileNotFoundError as e:
#         st.error(f"File error: {e}")
#         logger.error(f"File error: {e}")
#         return
#     except Exception as e:
#         st.error(f"Unexpected error: {e}")
#         logger.error(f"Unexpected error: {e}")
#         return

#     # Initialize summarizer
#     try:
#         summarizer = Summarizer(
#             function_model_name=Config.FUNCTION_SUMMARIZER_MODEL,
#             groq_api_key=Config.GROQ_API_KEY,
#             groq_model=Config.GROQ_MODEL
#         )
#     except Exception as e:
#         st.error(f"Failed to initialize summarizer: {e}")
#         logger.error(f"Failed to initialize summarizer: {e}")
#         return

#     # File uploader
#     uploaded_file = st.file_uploader("Choose a Python file", type=["py"], help="Upload a .py file containing Python functions.")

#     if uploaded_file:
#         # Save uploaded file temporarily
#         temp_file_path = "temp.py"
#         try:
#             with open(temp_file_path, "wb") as f:
#                 f.write(uploaded_file.read())
#             logger.info(f"Saved uploaded file to {temp_file_path}")
#         except Exception as e:
#             st.error(f"Error saving uploaded file: {e}")
#             logger.error(f"Error saving uploaded file: {e}")
#             return

#         # Extract functions
#         functions = extract_functions(temp_file_path)
#         if not functions:
#             st.warning("No functions found in the uploaded file.")
#             logger.warning(f"No functions found in {temp_file_path}")
#             if os.path.exists(temp_file_path):
#                 os.remove(temp_file_path)
#             return

#         # Generate function summaries
#         st.header("Function Summaries")
#         extracted_summaries = []
#         for func in functions:
#             summary = summarizer.summarize_function(func['code'])
#             extracted_summaries.append(summary)
#             st.subheader(f"Function: {func['name']} (Line {func['line_start']})")
#             st.code(func['code'], language="python")
#             st.write("**Summary:**")
#             st.write(summary)
#             st.markdown("---")
#             logger.info(f"Generated summary for function {func['name']}: {summary}")

#         # Generate overall summary
#         st.header("Overall Codebase Summary")
#         user_type = st.selectbox(
#             "Select perspective",
#             ["product_manager", "developer", "manager"],
#             index=0,
#             help="Choose the perspective for the overall summary."
#         )
#         if st.button("Generate Overall Summary"):
#             with st.spinner("Generating overall summary..."):
#                 try:
#                     placeholder = st.empty()
#                     summary = summarizer.summarize_codebase(extracted_summaries, user_type)
#                     placeholder.markdown("**Summary:**")
#                     placeholder.write(summary)
#                     logger.info(f"Generated overall summary for {user_type}: {summary}")
#                 except Exception as e:
#                     st.error(f"Error generating overall summary: {e}")
#                     logger.error(f"Error generating overall summary: {e}")

#         # Clean up temporary file
#         if os.path.exists(temp_file_path):
#             try:
#                 os.remove(temp_file_path)
#                 logger.info(f"Removed temporary file {temp_file_path}")
#             except Exception as e:
#                 logger.error(f"Error removing temporary file {temp_file_path}: {e}")

# if __name__ == "__main__":
#     main()

import streamlit as st
import os
import nest_asyncio
from streamlit.watcher import local_sources_watcher
from src.config import Config
from src.code_parser import extract_functions
from src.summarizer import Summarizer
import logging
from datetime import datetime

# ✅ This must come first before ANY Streamlit commands
st.set_page_config(page_title="Codebase Summarizer", layout="wide", initial_sidebar_state="expanded")

# Apply nest_asyncio to patch asyncio
nest_asyncio.apply()

# Patch get_module_paths to skip torch.classes
original_get_module_paths = local_sources_watcher.get_module_paths
def patched_get_module_paths(module):
    if module.__name__ == "torch.classes":
        return []
    return original_get_module_paths(module)
local_sources_watcher.get_module_paths = patched_get_module_paths

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Custom CSS for professional styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSelectbox {
        background-color: #ffffff;
        border-radius: 5px;
    }
    .stFileUploader {
        background-color: #ffffff;
        border: 2px dashed #d3d3d3;
        border-radius: 5px;
        padding: 10px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .summary-text {
        font-size: 16px;
        line-height: 1.5;
        color: #333333;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 15px;
    }
    .error-box {
        background-color: #ffe6e6;
        border: 1px solid #ff4d4d;
        border-radius: 5px;
        padding: 10px;
        color: #333333;
    }
    .success-box {
        background-color: #e6f3e6;
        border: 1px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
        color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    """Main function to run the Streamlit app for codebase summarization."""
    # st.set_page_config(page_title="Codebase Summarizer", layout="wide", initial_sidebar_state="expanded")

    # Sidebar for navigation and settings
    with st.sidebar:
        st.image("machine-learning-4-robot-developer-working-programming-coding-ai-machine-learning-script-1024.webp", caption="Codebase Summarizer")
        st.markdown("### About")
        st.markdown(
            "Analyze Python code to generate function-level and overall codebase summaries. "
            "Upload a `.py` file and choose a perspective for the summary."
        )

    # Main content
    with st.container():
        st.markdown('<div class="main">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Codebase Summarizer</div>', unsafe_allow_html=True)
        st.markdown(
            "Upload a Python file to view detailed function summaries and generate a comprehensive "
            "codebase summary tailored to your perspective (Product Manager, Developer, or Manager)."
        )

        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            st.markdown(f'<div class="error-box">Configuration Error: {e}</div>', unsafe_allow_html=True)
            logger.error(f"Configuration error: {e}")
            return
        except FileNotFoundError as e:
            st.markdown(f'<div class="error-box">File Error: {e}</div>', unsafe_allow_html=True)
            logger.error(f"File error: {e}")
            return
        except Exception as e:
            st.markdown(f'<div class="error-box">Unexpected Error: {e}</div>', unsafe_allow_html=True)
            logger.error(f"Unexpected error: {e}")
            return

        # Initialize summarizer
        try:
            summarizer = Summarizer(
                function_model_name=Config.FUNCTION_SUMMARIZER_MODEL,
                groq_api_key=Config.GROQ_API_KEY,
                groq_model=Config.GROQ_MODEL
            )
        except Exception as e:
            st.markdown(f'<div class="error-box">Failed to initialize summarizer: {e}</div>', unsafe_allow_html=True)
            logger.error(f"Failed to initialize summarizer: {e}")
            return

        # File uploader
        st.markdown('<div class="section-title">Upload Python File</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose a Python file",
            type=["py"],
            help="Upload a .py file containing Python functions to analyze.",
            key="file_uploader"
        )

        if uploaded_file:
            # Save uploaded file temporarily
            temp_file_path = "temp.py"
            try:
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.read())
                st.markdown(
                    '<div class="success-box">File uploaded successfully!</div>',
                    unsafe_allow_html=True
                )
                logger.info(f"Saved uploaded file to {temp_file_path}")
            except Exception as e:
                st.markdown(f'<div class="error-box">Error saving uploaded file: {e}</div>', unsafe_allow_html=True)
                logger.error(f"Error saving uploaded file: {e}")
                return

            # Extract functions
            functions = extract_functions(temp_file_path)
            if not functions:
                st.markdown(
                    '<div class="error-box">No functions found in the uploaded file.</div>',
                    unsafe_allow_html=True
                )
                logger.warning(f"No functions found in {temp_file_path}")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return

            # Function summaries
            st.markdown('<div class="section-title">Function Summaries</div>', unsafe_allow_html=True)
            extracted_summaries = []
            for func in functions:
                with st.expander(f"Function: {func['name']} (Line {func['line_start']})", expanded=False):
                    summary = summarizer.summarize_function(func['code'])
                    extracted_summaries.append(summary)
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.code(func['code'], language="python")
                    st.markdown("**Summary:**")
                    st.markdown(f'<div class="summary-text">{summary}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    logger.info(f"Generated summary for function {func['name']}: {summary}")

            # Download function summaries
            if extracted_summaries:
                summary_text = "\n\n".join(
                    f"Function: {func['name']} (Line {func['line_start']})\nSummary: {summary}"
                    for func, summary in zip(functions, extracted_summaries)
                )
                st.download_button(
                    label="Download Function Summaries",
                    data=summary_text,
                    file_name=f"function_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download a text file containing all function summaries."
                )

            # Overall summary
            st.markdown('<div class="section-title">Overall Codebase Summary</div>', unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            with col1:
                user_type = st.selectbox(
                    "Select perspective",
                    ["product_manager", "developer", "manager"],
                    index=0,
                    help="Choose the perspective for the overall summary.",
                    key="perspective_select"
                )
            with col2:
                generate_button = st.button("Generate Summary", key="generate_summary")

            if generate_button:
                with st.spinner("Generating overall summary..."):
                    try:
                        placeholder = st.empty()
                        summary = summarizer.summarize_codebase(extracted_summaries, user_type)
                        with placeholder.container():
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.markdown("**Overall Summary:**")
                            st.markdown(f'<div class="summary-text">{summary}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            # Download overall summary
                            st.download_button(
                                label="Download Overall Summary",
                                data=summary,
                                file_name=f"overall_summary_{user_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                help="Download the overall summary as a text file."
                            )
                        logger.info(f"Generated overall summary for {user_type}: {summary}")
                    except Exception as e:
                        st.markdown(
                            f'<div class="error-box">Error generating overall summary: {e}</div>',
                            unsafe_allow_html=True
                        )
                        logger.error(f"Error generating overall summary: {e}")

            # Clean up temporary file
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Removed temporary file {temp_file_path}")
                except Exception as e:
                    logger.error(f"Error removing temporary file {temp_file_path}: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()