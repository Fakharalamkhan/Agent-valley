
import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path to allow importing from agents
sys.path.append(os.getcwd())

load_dotenv()

def test_agent(name, func, *args, **kwargs):
    print(f"\n--- Testing Agent: {name} ---", flush=True)
    try:
        result = func(*args, **kwargs)
        if result.get("status") == "success":
            print(f"[OK] {name} returned success.", flush=True)
        else:
            print(f"[X] {name} returned error: {result.get('output')}", flush=True)
    except Exception as e:
        print(f"[X] {name} raised an exception: {e}", flush=True)

def run_all_tests():
    print("=== Starting Multi-Agent System Functional Test ===\n", flush=True)

    # 1. Test Core Skills (Research)
    try:
        from agents import core_skills
        test_agent("Research Agent", core_skills.research_agent, "What is the capital of France?")
    except ImportError:
        print("[X] Could not import core_skills", flush=True)

    # 2. Test Core Skills (Rewrite)
    try:
        from agents import core_skills
        test_agent("Rewrite Agent", core_skills.rewrite_agent, "This is a simple test.", context="Hello world")
    except ImportError:
        print("[X] Could not import core_skills", flush=True)

    # 3. Test Core Skills (Student Rewrite)
    try:
        from agents import core_skills
        test_agent("Student Rewrite Agent", core_skills.student_rewrite_agent, "Artificial intelligence is changing the world.")
    except ImportError:
        print("[X] Could not import core_skills", flush=True)

    # 4. Test Career Agent
    try:
        from agents import career_agent
        test_agent("Career Agent", career_agent.run, "Software Engineer job at Google")
    except ImportError as e:
        print(f"[X] Could not import career_agent: {e}", flush=True)

    # 5. Test Humanizer Agent
    try:
        from agents import humanizer_agent
        test_agent("Humanizer Agent", humanizer_agent.run, "Test context", "AI content to humanize")
    except ImportError:
        print("[X] Could not import humanizer_agent", flush=True)

    # 6. Test Tavily Agent (Standalone)
    try:
        from agents import tavily_agent
        test_agent("Tavily Agent", tavily_agent.run, "Current weather in Paris")
    except ImportError:
        print("[X] Could not import tavily_agent", flush=True)

    # 7. Test Gemini Agent (Text-only fallback)
    try:
        from agents import gemini_agent
        test_agent("Gemini Agent", gemini_agent.run, "Analyze this layout description: A header, sidebar, and main content area.")
    except ImportError:
        print("[X] Could not import gemini_agent", flush=True)

    # 8. Test Groq Agent
    try:
        from agents import groq_agent
        test_agent("Groq Agent", groq_agent.run, "Write a hello world in Python")
    except ImportError:
        print("[X] Could not import groq_agent", flush=True)

    # 9. Test Image Agent
    try:
        from agents import image_agent
        test_agent("Image Agent", image_agent.run, "A futuristic city with flying cars")
    except ImportError:
        print("[X] Could not import image_agent", flush=True)

    # 10. Test Paper Agent
    try:
        from agents import paper_agent
        test_agent("Paper Agent", paper_agent.run, "Create a quiz about Python basics")
    except ImportError:
        print("[X] Could not import paper_agent", flush=True)

    # 11. Test Reviewer Agent
    try:
        from agents import reviewer_agent
        test_agent("Reviewer Agent", reviewer_agent.run, "Fix the CSS", "Use blue theme", "<html><body>Hello</body></html>")
    except ImportError:
        print("[X] Could not import reviewer_agent", flush=True)

    # 12. Test Design Agent
    try:
        from agents import design_agent
        test_agent("Design Agent", design_agent.run, "Design a modern landing page for a SaaS")
    except ImportError:
        print("[X] Could not import design_agent", flush=True)

    # 13. Test SambaNova Agent (Reasoning)
    try:
        from agents import sambanova_agent
        test_agent("SambaNova (Reasoning)", sambanova_agent.run, "Explain quantum physics to a 5-year old", model_type="reasoning")
    except ImportError:
        print("[X] Could not import sambanova_agent", flush=True)

    # 14. Test SambaNova Agent (General)
    try:
        from agents import sambanova_agent
        test_agent("SambaNova (General)", sambanova_agent.run, "Write a short poem about AI", model_type="general")
    except ImportError:
        print("[X] Could not import sambanova_agent", flush=True)

    # 15. Test Manager Agent (Orchestration)
    print("\n--- Testing Manager Agent (Orchestration) ---", flush=True)
    try:
        from agents import manager_agent
        result = manager_agent.run("What are the latest news about AI?")
        print(f"[OK] Manager Agent returned: {result.get('selected_skill')}", flush=True)
    except Exception as e:
        print(f"[X] Manager Agent failed: {e}", flush=True)

if __name__ == "__main__":
    run_all_tests()
