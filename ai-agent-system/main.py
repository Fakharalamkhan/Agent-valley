import os
import json
import uvicorn
import subprocess
import tempfile
import sys
import sys
# from PyPDF2 import PdfReader # Moved to extract_file_content
# import pandas as pd        # Moved to extract_file_content

from fastapi import FastAPI, Form, File, UploadFile, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

from agents import manager_agent

# Load environment variables at the entry point
load_dotenv()

app = FastAPI(title="AI Multi-Agent System", version="1.0.0")

# Serve the UI folder as static files
ui_path = Path(__file__).parent / "ui"
app.mount("/ui", StaticFiles(directory=str(ui_path)), name="ui")

# Serve the outputs folder as static files
outputs_path = Path(__file__).parent / "outputs"
outputs_path.mkdir(parents=True, exist_ok=True)
(outputs_path / "code").mkdir(exist_ok=True)
(outputs_path / "images").mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(outputs_path)), name="outputs")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the chat UI."""
    index_file = ui_path / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))


async def extract_file_content(file: UploadFile) -> str:
    """Extract text from PDF or CSV files."""
    filename = file.filename.lower()
    content = await file.read()
    
    try:
        if filename.endswith(".pdf"):
            import io
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
            
        elif filename.endswith(".csv"):
            import io
            import pandas as pd
            df = pd.read_csv(io.BytesIO(content))

            # Limit to 100 rows for LLM context safety
            return df.head(100).to_string()
            
        return ""
    except Exception as e:
        return f"[Error extracting file: {str(e)}]"


@app.post("/run")
async def run_agents(
    task: str = Form(...),
    manual_skill: str = Form(default=None),
    data_file: UploadFile = File(default=None)
):
    """
    Accept a task, run the multi-agent pipeline with optional skill override.
    """
    context = ""
    if data_file and data_file.filename:
        context = await extract_file_content(data_file)
    try:
        result = manager_agent.run(task=task, manual_skill=manual_skill, file_context=context)
        
        # Safely extract first result or fallback
        agent_info = result["agent_results"][0] if result.get("agent_results") else {"tool": "N/A", "agent": "Manager"}
        
        response_content = {
            "status": "success",
            "selected_skill": result.get("selected_skill", "unknown"),
            "tool": result.get("tool", "Groq"),
            "agent": result.get("agent", "N/A"),
            "steps": result.get("steps", []),
            "final_output": result.get("final_output", "No response generated.")
        }
        # Pass career sub-documents if available
        agent_results = result.get("agent_results", [{}])
        career_result = agent_results[0] if agent_results else {}
        if career_result.get("cv_text"):
            response_content["cv_text"] = career_result["cv_text"]
        if career_result.get("cover_letter_text"):
            response_content["cover_letter_text"] = career_result["cover_letter_text"]
        return JSONResponse(content=response_content)
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Log it for debugging
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )

@app.post("/execute")
async def execute_code(data: dict = Body(...)):
    """
    Execute generated Python code and return the output.
    """
    code = data.get("code")
    language = data.get("language", "python").lower()

    if not code:
        return JSONResponse(status_code=400, content={"message": "Missing code"})

    if language in ["python", "py"]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = subprocess.run([sys.executable, temp_path], capture_output=True, text=True, timeout=15)
            output = result.stdout
            if result.stderr:
                output += ("\n--- Errors ---\n" + result.stderr) if output else result.stderr
            return JSONResponse(content={"status": "success", "output": output})
        except subprocess.TimeoutExpired:
            return JSONResponse(content={"status": "error", "message": "Execution timed out (15s limit)."})
        except Exception as e:
            return JSONResponse(content={"status": "error", "message": str(e)})
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        return JSONResponse(content={"status": "error", "message": f"Execution for language '{language}' is not supported via this endpoint."})


@app.post("/save")
async def save_output(data: dict = Body(...)):
    """
    Save generated code or image to the outputs folder.
    Expected keys: 'content', 'filename', 'type' (code/image)
    """
    content = data.get("content")
    filename = data.get("filename")
    file_type = data.get("type", "code")

    if not content or not filename:
        return JSONResponse(status_code=400, content={"message": "Missing content or filename"})

    target_dir = outputs_path / ("code" if file_type == "code" else "images")
    file_path = target_dir / filename

    try:
        if file_type == "code":
            file_path.write_text(content, encoding="utf-8")
        else:
            # Assume content is base64 for images
            import base64
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(content))

        return JSONResponse(content={
            "status": "success",
            "url": f"/outputs/{file_type}/{filename}",
            "path": str(file_path)
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


if __name__ == "__main__":
    print("Starting AI Multi-Agent System...")
    print("   Open http://localhost:8000 in your browser\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
