
import os
import sys
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

def check_dependencies():
    print("--- Checking Dependencies ---")
    required = [
        "fastapi", "uvicorn", "python-dotenv", "groq", 
        "tavily", "google.generativeai", "httpx", "PIL"
    ]
    missing = []
    for pkg in required:
        try:
            if "." in pkg:
                importlib.import_module(pkg)
            else:
                importlib.import_module(pkg)
        except ImportError:
            # Special case for Pillow
            if pkg == "PIL":
                try:
                    importlib.import_module("PIL")
                    continue
                except ImportError:
                    pass
            missing.append(pkg)
    
    if missing:
        print(f"[X] Missing packages: {', '.join(missing)}")
    else:
        print("[OK] All core packages found.")
    return len(missing) == 0

def check_env():
    print("\n--- Checking .env File ---")
    if not os.path.exists(".env"):
        print("[X] .env file not found!")
        return False
    
    load_dotenv()
    keys = ["GROQ_API_KEY", "GEMINI_API_KEY", "TAVILY_API_KEY"]
    all_set = True
    for key in keys:
        val = os.getenv(key)
        if not val or "your_key" in val.lower() or len(val) < 10:
            print(f"[X] {key} is missing or looks like a placeholder.")
            all_set = False
        else:
            print(f"[OK] {key} is set.")
    return all_set

def check_syntax():
    print("\n--- Checking Syntax ---")
    files = ["main.py"] + list(Path("agents").glob("*.py"))
    all_ok = True
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                compile(file.read(), str(f), "exec")
            print(f"[OK] {f} syntax is OK.")
        except Exception as e:
            print(f"[X] {f} syntax error: {e}")
            all_ok = False
    return all_ok

def run_checks():
    print("=== AI Agent System Check ===\n")
    d_ok = check_dependencies()
    e_ok = check_env()
    s_ok = check_syntax()
    
    print("\n=== Summary ===")
    if d_ok and e_ok and s_ok:
        print("System looks healthy and ready to run!")
    else:
        print("System has some issues that need addressing.")

if __name__ == "__main__":
    run_checks()
