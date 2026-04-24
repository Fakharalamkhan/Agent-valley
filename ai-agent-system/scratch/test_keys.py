import os
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
import google.generativeai as genai

load_dotenv()

def test_groq():
    print("\nTesting Groq...")
    key = os.getenv("GROQ_API_KEY")
    print(f"Key: {key[:10]}...{key[-5:] if key else 'None'}")
    try:
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("Groq Success:", response.choices[0].message.content)
    except Exception as e:
        print("Groq Error:", str(e))

def test_tavily():
    print("\nTesting Tavily...")
    key = os.getenv("TAVILY_API_KEY")
    print(f"Key: {key[:10]}...{key[-5:] if key else 'None'}")
    try:
        client = TavilyClient(api_key=key)
        response = client.search(query="test", max_results=1)
        print("Tavily Success:", response.get("results")[0].get("title") if response.get("results") else "No results")
    except Exception as e:
        print("Tavily Error:", str(e))

def test_gemini():
    print("\nTesting Gemini...")
    key = os.getenv("GEMINI_API_KEY")
    print(f"Key: {key[:10]}...{key[-5:] if key else 'None'}")
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Hello")
        print("Gemini Success:", response.text)
    except Exception as e:
        print("Gemini Error:", str(e))

if __name__ == "__main__":
    test_groq()
    test_tavily()
    test_gemini()
