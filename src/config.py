import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Configuration settings for the code summarization project"""
    # INPUT_FILE_PATH = os.getenv("INPUT_FILE_PATH", "/Users/amitabhdas/Documents/Projects/code_sum/sample.py")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    FUNCTION_SUMMARIZER_MODEL: str = "Amitabhdas/Code-summarizer-python"
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    @staticmethod
    def validate(api_key: Optional[str], file_path: Optional[str]):
        """Validate the configuration settings"""
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found. Please set it in the .env file.")
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file {file_path} does not exist.")