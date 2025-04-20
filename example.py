import ast
from transformers import AutoTokenizer, T5ForConditionalGeneration, BartForConditionalGeneration, AutoModelForSeq2SeqLM
import os
from groq import Groq


def extract_functions(file_path):
    """Extracts individual function definitions from a Python script."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        tree = ast.parse(code)
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno
                function_code = '\n'.join(code.splitlines()[start_line:end_line])
                functions.append({
                    'name': node.name,
                    'code': function_code.strip(),
                    'line_start': node.lineno
                })
        return functions
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return []


def summarize_function(function_code, tokenizer, model):
    """Generates a summary for a given function's code."""
    try:
        inputs = tokenizer(
            function_code,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=50,
            num_beams=4,
            early_stopping=True
        )
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        return f"Error summarizing function: {e}"


def main():
    # Specify the input file path (adjust this to your script's name)
    input_file = "/Users/amitabhdas/Documents/Projects/code_sum/sample.py"
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"File {input_file} not found in Colab directory. Please upload it to /content/.")
        return

    print(f"Processing file: {input_file}")

    # Load model and tokenizer for function summarization
    model_name_summarizer = "Amitabhdas/code-summarizer-python"
    print(f"Loading model {model_name_summarizer}...")
    tokenizer_summarizer = AutoTokenizer.from_pretrained(model_name_summarizer)
    model_summarizer = T5ForConditionalGeneration.from_pretrained(model_name_summarizer)
    model_summarizer.eval()

    # Extract functions
    functions = extract_functions(input_file)
    if not functions:
        print("No functions found or error occurred.")
        return

    # Generate and store function summaries
    extracted_summaries = []  # List to store function summaries
    print("\n=== Function Summaries ===")
    for func in functions:
        summary = summarize_function(func['code'], tokenizer_summarizer, model_summarizer)
        extracted_summaries.append(summary)  # Add summary to the list
        # print(f"\nFunction: {func['name']} (Line {func['line_start']})")
        # print("Code:")
        # print(func['code'])
        # print("Summary:")
        # print(summary)
        # print("-" * 50)
    # print("\n=== Extracted Summaries ===\n", extracted_summaries)
    # Now use extracted_summaries for generate_summary
    generate_overall_summary(extracted_summaries)


def generate_overall_summary(function_summaries):
    prompt_templates = {
        "product_manager": """
        As a product manager, your task is to summarize the key features and user-facing functionalities of a codebase based on the following function descriptions:

        {function_summaries}

        Provide a concise summary (2-3 sentences, 50-100 words) highlighting what the codebase does, its primary user-facing features, and benefits for users. Synthesize the information into a cohesive description without repeating the function descriptions verbatim. Focus on the overall purpose and value for end-users.
        """,
        "developer": """
        As a software developer, your task is to summarize the core logic and functionalities of a codebase based on the following function descriptions:

        {function_summaries}

        Provide a detailed summary (3-4 sentences, 100-150 words) outlining the main logic, data flow, and key functionalities implemented. Focus on technical aspects and how the functions work together.
        """,
        "manager": """
        As a project manager, your task is to summarize the overall purpose and structure of a codebase based on the following function descriptions:

        {function_summaries}

        Provide a summary (2-3 sentences, 50-100 words) focusing on the codebase's purpose, its main modules, and any notable dependencies or components.
        """
    }
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Please set GROQ_API_KEY environment variable.")
    client = Groq(api_key="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")

    def generate_summary(function_summaries, user_type, model ="llama-3.1-8b-instant"):
        summaries_str = "\n".join([f"-{summary}" for summary in function_summaries])
        prompt = prompt_templates[user_type].format(function_summaries=summaries_str)

        try:
            response = client.chat.completions.create(
                model=model,  # Use Llama 3.1 8B for speed and cost-efficiency
                messages=[
                    {"role": "system", "content": "You are an expert summarizer. Provide clear, concise, and accurate summaries based on the given instructions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,  # Limit output for conciseness
                temperature=0.3,  # Low temperature for deterministic output
                top_p=0.9,       # Control diversity
                stream=False
            )
            summary = response.choices[0].message.content.strip()
            
            # Fallback if summary is empty or repeats prompt
            if not summary or prompt.lower() in summary.lower():
                return "Failed to generate a meaningful summary. The codebase supports recording and analyzing financial transactions."
            
            return summary
        except Exception as e:
            print(f"Error generating summary with Groq API: {e}")
            return "Failed to generate summary due to API error."
    
    # Generate summary for product manager
    product_summary = generate_summary(function_summaries, "product_manager")
    print("Product Manager Summary:", product_summary)

    
# def generate_overall_summary(function_summaries):
#     prompt_templates = {
#         "product_manager": """
#         You are a product manager.
#         Given the following function summaries for a codebase:
#         {function_summaries}
#         Provide a concise summary highlighting the key features and user-facing functionalities of the codebase.
#         """,
#         "developer": """
#         You are a software developer.
#         Given the following function summaries for a codebase:
#         {function_summaries}
#         Provide a detailed summary outlining the core logic, data flow, and functionalities implemented in the codebase.
#         """,
#         "manager": """
#         You are a project manager.
#         Given the following function summaries for a codebase:
#         {function_summaries}
#         Provide a summary focusing on the overall purpose, modules, and dependencies of the codebase.
#         """
#     }

#     model_name_overall = "t5-small"  # Lightweight model
#     tokenizer_overall = AutoTokenizer.from_pretrained(model_name_overall)
#     model_overall = AutoModelForSeq2SeqLM.from_pretrained(model_name_overall)

#     def generate_summary(function_summaries, user_type):
#         summaries_str = "\n".join([f"- {summary}" for summary in function_summaries])
#         prompt = prompt_templates[user_type].format(function_summaries=summaries_str)
#         print("\n=== Prompt for Overall Summary (Product Manager) ===\n", prompt)  # Debugging
#         inputs = tokenizer_overall(prompt, return_tensors="pt", max_length=512, truncation=True)
#         outputs = model_overall.generate(
#             input_ids=inputs["input_ids"],
#             attention_mask=inputs["attention_mask"],
#             max_length=300,
#             num_beams=4,
#             early_stopping=True,
#             no_repeat_ngram_size=2
#         )
#         summary = tokenizer_overall.decode(outputs[0], skip_special_tokens=True)
#         if not summary.strip():
#             return "Failed to generate a meaningful summary."
#         return summary

#     product_summary = generate_summary(function_summaries, "product_manager")
#     print("Product Manager Summary:", product_summary)
# def generate_overall_summary(function_summaries):
#     # print("\n=== Overall Codebase Summary ===\n", function_summaries)
#     prompt_templates = {
#         "product_manager": """
#         You are a product manager.
#         Given the following function summaries for a codebase:
#         {function_summaries}
#         Provide a concise summary highlighting the key features and user-facing functionalities of the codebase.
#         """,
#         "developer": """
#         You are a software developer.
#         Given the following function summaries for a codebase:
#         {function_summaries}
#         Provide a detailed summary outlining the core logic, data flow, and functionalities implemented in the codebase.
#         """,
#         "manager": """
#         You are a project manager.
#         Given the following function summaries for a codebase:
#         {function_summaries}
#         Provide a summary focusing on the overall purpose, modules, and dependencies of the codebase.
#         """
#     }
    
#     model_name_overall = "google/flan-t5-base"  # or any other suitable LLM
#     tokenizer_overall = AutoTokenizer.from_pretrained(model_name_overall)
#     model_overall = AutoModelForSeq2SeqLM.from_pretrained(model_name_overall)
    
#     def generate_summary(function_summaries, user_type):
#         prompt = prompt_templates[user_type].format(function_summaries=function_summaries)
#         # print("Prompt:", prompt)
#         inputs = tokenizer_overall(prompt, return_tensors="pt", max_length=512, truncation=True)
#         # print("Inputs:", inputs)
#         outputs = model_overall.generate(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"], max_length=200)
#         print("Outputs:", outputs)
#         summary = tokenizer_overall.decode(outputs[0], skip_special_tokens=True)
#         print("Summary:", summary)
#         return summary

#     # Example usage:
#     product_summary = generate_summary(function_summaries, "product_manager")
#     # developer_summary = generate_summary(function_summaries, "developer")
#     # manager_summary = generate_summary(function_summaries, "manager")

#     print("Product Manager Summary:", product_summary)
#     # print("Developer Summary:", developer_summary)
#     # print("Manager Summary:", manager_summary)

if __name__ == "__main__":
    main()