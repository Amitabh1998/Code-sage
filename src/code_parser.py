import ast
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_functions(file_path: str) -> List[Dict]:
    """
    Extracts individual function definitions from a Python script.
    
    Args:
        file_path (str): Path to the Python file.
    
    Returns:
        List[Dict]: List of dictionaries containing function name, code, and line number.
        Each dictionary has keys: 'name' (str), 'code' (str), 'line_start' (int).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        tree = ast.parse(code)
        functions = []
        code_lines = code.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno
                # Extract function code, handling edge cases
                function_code = '\n'.join(code_lines[start_line:end_line]) if start_line < len(code_lines) else ""
                functions.append({
                    'name': node.name,
                    'code': function_code.strip(),
                    'line_start': node.lineno
                })
        logger.info(f"Extracted {len(functions)} functions from {file_path}")
        return functions
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error parsing file {file_path}: {e}")
        return []