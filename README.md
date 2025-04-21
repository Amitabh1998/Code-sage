# Codebase Summarizer

A powerful tool that analyzes Python code to generate function-level and overall codebase summaries using AI models. This application helps developers, product managers, and project managers quickly understand code functionality without reading through every line.

![Codebase Summarizer](https://via.placeholder.com/800x400?text=Codebase+Summarizer)

## 🌟 Features

- **Function-Level Summaries**: Extract and summarize individual functions from Python files
- **Overall Codebase Summary**: Generate a comprehensive summary of the entire codebase
- **Multiple Perspectives**: Choose between Product Manager, Developer, or Manager views
- **Interactive UI**: User-friendly Streamlit interface with expandable sections
- **Export Functionality**: Download summaries as text files
- **Syntax Highlighting**: View code with proper syntax highlighting
- **Error Handling**: Robust error handling and user feedback

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/code_sum.git
   cd code_sum
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will be available at http://localhost:8501 in your web browser.

## 🔧 Usage

1. **Upload a Python File**: Use the file uploader to select a `.py` file
2. **View Function Summaries**: Expand function sections to see code and summaries
3. **Select a Perspective**: Choose between Product Manager, Developer, or Manager views
4. **Generate Overall Summary**: Click the "Generate Summary" button
5. **Download Results**: Use the download buttons to save summaries

## 🧩 Project Structure

```
code_sum/
├── .streamlit/            # Streamlit configuration
├── src/                   # Source code
│   ├── __init__.py        # Package initialization
│   ├── code_parser.py     # Function extraction logic
│   ├── config.py          # Configuration settings
│   └── summarizer.py      # AI summarization logic
├── app.py                 # Main Streamlit application
├── streamlit_app.py       # Alternative Streamlit interface
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## 🔍 How It Works

1. **Code Parsing**: The application uses Python's AST (Abstract Syntax Tree) to extract functions from the uploaded file.
2. **Function Summarization**: Each function is summarized using a fine-tuned T5 model specialized for code summarization.
3. **Codebase Summarization**: Function summaries are aggregated and processed by Groq's LLM to generate an overall summary.
4. **Perspective Adaptation**: The overall summary is tailored to the selected user perspective (Product Manager, Developer, or Manager).

## � Data Privacy & Security

The Codebase Summarizer is designed with data privacy as a priority, especially for organizations working with sensitive or proprietary code:

- **Local Function Summarization**: The T5 model for function-level summarization runs entirely on your local machine, ensuring your actual code never leaves your environment.
- **Abstracted Summaries**: Only the generated function summaries (not the original code) are sent to external APIs for overall summarization.
- **Minimal Data Exposure**: The function summaries are designed to capture functionality without exposing implementation details, variable names, or other sensitive information.
- **No Code Storage**: The application doesn't store your code or the generated summaries on any external servers.
- **Temporary File Handling**: Uploaded files are stored temporarily during processing and automatically deleted after summarization.
- **API Key Security**: Your Groq API key is stored locally in the .env file and never shared.

This architecture ensures that your internal, proprietary code remains protected while still benefiting from AI-powered summarization capabilities.

## �🛠️ Technologies Used

- **Streamlit**: For the interactive web interface
- **Hugging Face Transformers**: For function-level code summarization
- **Groq API**: For generating overall codebase summaries
- **Python AST**: For parsing and extracting functions from code
- **nest_asyncio**: For handling asyncio event loop in Streamlit

## ⚙️ Configuration

The application can be configured through the `src/config.py` file or environment variables:

- `GROQ_API_KEY`: Your Groq API key (required)
- `FUNCTION_SUMMARIZER_MODEL`: Hugging Face model for function summarization
- `GROQ_MODEL`: Groq model for overall summarization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Hugging Face](https://huggingface.co/) for providing pre-trained models
- [Groq](https://groq.com/) for their powerful LLM API
- [Streamlit](https://streamlit.io/) for the interactive web app framework

## 📧 Contact

For questions or feedback, please reach out to [amitabh.das1998@gmail.com](mailto:amitabh.das1998@gmail.com)
