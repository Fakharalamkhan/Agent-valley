# AI Multi-Agent System

## Overview
This is an AI-powered multi-agent system built with Python and FastAPI. It provides a web-based interface for interacting with various AI agents that can perform tasks such as research, text rewriting, career optimization, and deep analysis. The system supports file uploads (PDF and CSV) and can execute generated Python code.

## Technologies Used
- **Backend Framework**: FastAPI (for building the REST API)
- **Server**: Uvicorn (ASGI server for running the FastAPI app)
- **AI Models**:
  - Groq (for LLM-based routing and text generation)
  - Google Generative AI (for additional AI capabilities)
  - Sambanova (for advanced AI processing)
- **Web Search**: Tavily (for research and information retrieval)
- **File Processing**:
  - PyPDF2 (for PDF text extraction)
  - Pandas (for CSV data handling)
- **Image Processing**: Pillow (for image manipulation and saving)
- **Environment Management**: python-dotenv (for loading environment variables)
- **HTTP Client**: httpx (for making HTTP requests)
- **File Upload Handling**: python-multipart (for multipart form data)

## Key Services and Functions

### 1. Web Interface
- Serves a chat-like UI for user interaction
- Accessible via the root endpoint `/`
- Static file serving for UI assets and outputs

### 2. Agent Routing and Execution
- **Manager Agent**: Orchestrates task routing based on user input
- **Skills Available**:
  - **Research**: Performs web searches and summarizes information using Tavily
  - **Rewrite**: Humanizes text and changes tone
  - **Career**: Optimizes CVs and generates cover letters based on job descriptions
  - **Think**: Provides deep analysis and strategic thinking
- Automatic skill selection or manual override

### 3. File Upload and Processing
- Supports PDF and CSV file uploads
- Extracts text from PDFs using PyPDF2
- Parses CSV files with Pandas (limited to 100 rows for context safety)
- Integrates file content into agent tasks

### 4. Code Execution
- Executes generated Python code in a sandboxed environment
- Supports timeout limits (15 seconds) for safety
- Returns stdout and stderr output

### 5. Output Management
- Saves generated code, images, and other outputs to the `outputs/` directory
- Organized subdirectories: `code/`, `images/`, `career/`
- Static file serving for accessing saved outputs

### 6. API Endpoints
- `GET /`: Serves the main UI
- `POST /run`: Runs the multi-agent pipeline with task and optional file
- `POST /execute`: Executes provided code
- `POST /save`: Saves content to outputs folder

## Project Structure
```
ai-agent-system/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── system_check.py         # System health checks
├── test_all_agents.py      # Agent testing script
├── agents/
│   ├── __init__.py
│   ├── manager_agent.py    # Agent orchestration logic
│   └── tools.py            # Agent tools and utilities
├── ui/
│   └── index.html          # Web interface
├── outputs/
│   ├── career/             # Career-related outputs
│   ├── code/               # Generated code files
│   └── images/             # Generated images
└── scratch/
    └── test_keys.py        # API key testing
```

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in a `.env` file:
   - `GROQ_API_KEY`: Your Groq API key
   - `TAVILY_API_KEY`: Your Tavily API key
   - Other API keys as needed
4. Run the application: `uvicorn main:app --reload`

## Usage
1. Start the server
2. Open a web browser and navigate to `http://localhost:8000`
3. Enter a task in the UI
4. Optionally upload a PDF or CSV file
5. The system will route the task to the appropriate agent and return results
6. Generated code can be executed, and outputs can be saved

## Contributing
Contributions are welcome. Please ensure to follow the existing code structure and add tests for new features.

## License
[Specify your license here]