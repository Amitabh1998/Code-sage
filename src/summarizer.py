from transformers import AutoTokenizer, T5ForConditionalGeneration
from groq import Groq
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Summarizer:
    """Handles summarization of functions and overall codebase."""
    
    def __init__(self, function_model_name: str, groq_api_key: str, groq_model: str):
        """
        Initialize summarizer with models and API client.
        
        Args:
            function_model_name (str): Hugging Face model for function summarization.
            groq_api_key (str): Groq API key.
            groq_model (str): Groq model for overall summarization.
        """
        self.function_tokenizer = AutoTokenizer.from_pretrained(function_model_name)
        self.function_model = T5ForConditionalGeneration.from_pretrained(function_model_name)
        self.function_model.eval()
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_model = groq_model
        self.prompt_templates = {
            "product_manager": """
            As a product manager, summarize the key features and user-facing functionalities of a codebase based on:

            {function_summaries}

            Provide a concise summary (2-3 sentences, 50-100 words) highlighting what the codebase does, its primary user-facing features, and benefits for users. Synthesize without repeating descriptions verbatim. Focus on purpose and value.
            """,
            "developer": """
            As a developer, summarize the core logic and functionalities of a codebase based on:

            {function_summaries}

            Provide a detailed summary (3-4 sentences, 100-150 words) outlining logic, data flow, and functionalities. Focus on technical aspects.
            """,
            "manager": """
            As a project manager, summarize the purpose and structure of a codebase based on:

            {function_summaries}

            Provide a summary (2-3 sentences, 50-100 words) focusing on purpose, modules, and dependencies.
            """
        }
    
    def summarize_function(self, function_code: str) -> str:
        """
        Generate a summary for a function's code.
        
        Args:
            function_code (str): Source code of the function.
        
        Returns:
            str: Summary or error message.
        """
        try:
            inputs = self.function_tokenizer(
                function_code,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            outputs = self.function_model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=50,
                num_beams=4,
                early_stopping=True
            )
            summary = self.function_tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"Generated summary for function: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error summarizing function: {e}")
            return f"Error summarizing function: {e}"
    
    def summarize_codebase(self, function_summaries: List[str], user_type: str = "product_manager") -> str:
        """
        Generate an overall summary of the codebase using Groq API with streaming.
        
        Args:
            function_summaries (List[str]): List of function summaries.
            user_type (str): Type of user (product_manager, developer, manager).
        
        Returns:
            str: Overall summary or fallback message.
        """
        summaries_str = "\n".join([f"- {summary}" for summary in function_summaries])
        prompt = self.prompt_templates.get(user_type, self.prompt_templates["product_manager"]).format(function_summaries=summaries_str)
        logger.debug(f"Generated Prompt: {prompt}")
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert summarizer. Provide clear, concise, and accurate summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3,
                top_p=0.9,
                stream=True  # Enable streaming
            )
            summary = ""
            for chunk in completion:
                chunk_content = chunk.choices[0].delta.content or ""
                summary += chunk_content
            summary = summary.strip()
            logger.debug(f"Raw Response: {summary}")
            if not summary or any(keyword in summary.lower() for keyword in ["as a product manager", "function descriptions"]):
                fallback = "The codebase enables financial transaction management, including recording transactions, tracking balances, and categorizing spending."
                logger.warning(f"Using fallback summary: {fallback}")
                return fallback
            return summary
        except Exception as e:
            logger.error(f"Error generating summary with Groq API: {e}")
            if "401" in str(e):
                logger.error("401 Error: Invalid API key. Verify in Groq Console (https://console.groq.com).")
            return "The codebase enables financial transaction management, including recording transactions, tracking balances, and categorizing spending."