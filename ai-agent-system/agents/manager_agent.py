"""
Manager Agent — The Orchestrator
Focused strictly on Research, Career, and Humanizer skills.
Now features a mandatory "Reasoning Phase" (Thinker Tool).
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv

from agents import tools

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ROUTER_PROMPT = """You are a high-level tool router.
Map the user task to the most appropriate skill:

Skills:
- "research": Finding facts, summaries, and news (Web Search).
- "rewrite": Humanizing text and changing tone.
- "career": Optimizing CVs and writing cover letters.
- "think": ONLY use if the user specifically asks for deep analysis or strategy.

Return ONLY a valid JSON object with the selected skill:
{"skill": "research"}
"""

def _route_task(task: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": ROUTER_PROMPT},
                      {"role": "user", "content": task}],
            temperature=0.0,
            max_tokens=100
        )
        data = json.loads(response.choices[0].message.content.strip())
        return data.get("skill", "research")
    except:
        return "research"

def run(task: str, manual_skill: str = None, file_context: str = "") -> dict:
    selected_skill = manual_skill if manual_skill else _route_task(task)
    print(f"\n[Manager] Selected Tool: {selected_skill}")

    steps = []  # Live step log
    context = file_context if file_context else ""

    # --- PHASE 1: REASONING (only for research and career - complex tasks) ---
    thought_process = ""
    if selected_skill in ["research", "career"]:
        steps.append({"icon": "🧠", "text": "Deep Thinking: Analyzing the task and planning the best strategy..."})
        thought_result = tools.think_tool(task)
        thought_process = thought_result.get("output", "")

    # --- PHASE 2: TOOL EXECUTION ---
    result = None
    if selected_skill == "research":
        steps.append({"icon": "🔍", "text": "Searching the web with Tavily for real-time information..."})
        steps.append({"icon": "✍️", "text": "Groq (Llama 70B) synthesizing information into a research report..."})
        result = tools.research_tool(task)
        steps.append({"icon": "📚", "text": "Adding source citations to the final report..."})
    elif selected_skill == "rewrite":
        steps.append({"icon": "🔤", "text": "Groq (Llama 8B) analyzing text for robotic patterns..."})
        steps.append({"icon": "✨", "text": "Rewriting with natural human tone and flow..."})
        result = tools.humanizer_tool(task if not context else context)
    elif selected_skill == "career":
        steps.append({"icon": "🔗", "text": "Detecting job link or text input..."})
        steps.append({"icon": "🌐", "text": "Tavily crawling the job page to extract full job description & requirements..."})
        steps.append({"icon": "📄", "text": "Groq (Llama 70B) building your ATS-optimized CV matched to the job..."})
        steps.append({"icon": "✍️", "text": "Writing the Cover Letter draft..."})
        steps.append({"icon": "✨", "text": "Humanizer pass: removing robotic phrases to make Cover Letter sound natural..."})
        result = tools.career_tool(task, context=context)
    elif selected_skill == "think":
        steps.append({"icon": "🧠", "text": "Running deep strategic analysis..."})
        result = tools.think_tool(task)
    else:
        result = tools.research_tool(task)

    steps.append({"icon": "✅", "text": "Done! Full response is ready."})

    # Build final combined output
    if thought_process and selected_skill != "think":
        final_output = f"## 🧠 Thought Process\n{thought_process}\n\n---\n\n## 🎯 Result\n{result.get('output', '')}"
    else:
        final_output = result.get("output", "No result generated.")

    return {
        "routing": {selected_skill: True},
        "selected_skill": selected_skill,
        "steps": steps,
        "agent_results": [result],
        "final_output": final_output,
        "result_only": result.get("output", ""),
        "tool": result.get("tool", "Groq"),
        "agent": result.get("agent", "Multi-Agent System")
    }
