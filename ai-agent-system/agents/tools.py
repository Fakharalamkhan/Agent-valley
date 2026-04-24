
import os
import re
import json
from datetime import datetime
from pathlib import Path
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# --- CLIENT INITIALIZATION ---
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Paths
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "outputs"
(OUTPUT_ROOT / "career").mkdir(parents=True, exist_ok=True)

# Models
# We use the powerhouse 70B model for deep tasks and 8B for fast tasks
SMART_MODEL = "llama-3.3-70b-versatile"
FAST_MODEL = "llama-3.1-8b-instant"

# --- SHARED CONSTANTS ---
MY_BASE_CV = """
FAKHR E ALAM KHAN
Karlsruhe, Germany | +49 160 7748327 | fakharalamkhhan@gmail.com | github.com/Fakharalamkhan
PROFILE
Master’s student in Natural Language Processing with a strong interest in applied AI systems, especially Large Language Models, retrieval-augmented generation, and agent-based architectures. Seeking volunteer research assistant opportunities or collaborative projects in NLP and AI systems to deepen research experience and contribute to academic or applied research work. Comfortable working on LLM pipelines, backend systems, and AI-driven automation.
EDUCATION
**University of Trier** | *Trier, Germany* | Oct 2025 – Present |
Master of Science in Natural Language Processing nm
• Focus areas: Large Language Models, Neural Machine Translation, Stochastic Modeling, and NLP systems.

**Sir Syed CASE Institute of Technology** | *Islamabad* | Sep 2020 – Jul 2024 |
Bachelor of Science in Computer Science nm
• Strong foundation in software engineering, algorithms, and machine learning.
• Winner: IEEE Speed Coding Competition (2022).
"""

CAREER_SYSTEM_PROMPT = """You are a world-class ATS Specialist and Career Coach.
Generate a perfectly ATS-optimized CV and a professional Cover Letter based on the candidate's base CV and the provided job description.

=== CV RULES (FOLLOW EXACTLY) ===

LAYOUT:
- Single-column layout ONLY. No tables, no multi-column sections.
- Consistent spacing throughout. No decorative elements.

SECTION ORDER (top to bottom, no exceptions):
1. Full Name (bold, largest text)
2. Contact Info (Email | Phone | City | GitHub — single line)
3. Professional Summary (2-3 tight sentences, no fluff)
4. Technical Skills (bullet list, keyword-rich from the JD)
5. Work Experience (reverse chronological)
6. Education
7. Projects (if applicable)

FORMATTING:
- Use ## for section headings (e.g., ## WORK EXPERIENCE)
- Use ** bold for job titles and company names only
- Every bullet point starts with a strong action verb: Developed, Built, Engineered, Automated, Improved, Designed, Delivered, Managed, Reduced, Increased
- Bullet points are impact-focused. Use numbers/metrics wherever possible.
- NO icons, NO emojis, NO profile pictures, NO graphics
- NO colored text, NO highlights — pure black text only
- NO headers or footers
- Blank line between each section

ATS KEYWORD RULES:
- Extract exact skills, tools, and qualifications from the job description
- Embed them naturally into the Summary, Skills section, and experience bullets
- Do NOT keyword-stuff — use them where they genuinely fit

DATA INTEGRITY (SACRED RULES):
- DO NOT change: Full Name, Email, Phone, City/Country, GitHub URL
- NEVER invent jobs, companies, dates, degrees, or skills
- Rephrase and strengthen existing content only

=== COVER LETTER RULES (FOLLOW EXACTLY) ===

FORMAT:
- Standard business letter. Left-aligned. No columns or design.
- Same clean text style as the CV.

STRUCTURE:
1. Candidate Name, Email, Phone (top)
2. Date (today)
3. Hiring Manager (if name known, otherwise "Hiring Team") + Company Name
4. Opening Paragraph: State the exact job title. Show you understand what the company does. 1-2 sentences.
5. Body Paragraph: Highlight 2-3 relevant, quantified achievements. Match job keywords. Keep sentences short and direct.
6. Closing Paragraph: Express clear interest in an interview. Thank them. 2 sentences max.
7. Sign off with: "Best regards," then a blank line and the candidate name.

WRITING RULES (STRICT):
- NO "I am writing to apply..."
- NO "I am the perfect fit" or "I would be a great addition"
- NO emotional language or storytelling
- NO long paragraphs. Max 3 sentences per paragraph.
- Total word count: 150 to 220 words. Not a word more.
- Match job keywords naturally. One per paragraph is enough.
- Short, clear sentences. Confident tone. No fluff.

=== OUTPUT FORMAT ===
Return exactly two sections separated by a horizontal rule:

## TAILORED CV
[CV here]

---

## COVER LETTER
[Cover Letter here]
"""

HUMANIZER_SYSTEM_PROMPT = """You are an expert editor specializing in professional cover letters.
Rewrite the following cover letter to sound natural and human while keeping it ATS-friendly.

RULES:
1. Remove ALL corporate buzzwords: "leverage", "synergy", "passionate", "driven", "results-oriented".
2. Short sentences. Mix short and slightly longer for natural rhythm.
3. Confident and direct. Like one professional writing to another.
4. Keep ALL factual content — achievements, company name, job title, dates.
5. Do NOT add new information or change any facts.
6. Max 220 words. If longer, trim the fluff.
7. Do NOT write commentary or explanations. Return ONLY the rewritten letter.
"""

# --- THE ESSENTIAL TOOLBOX (GROQ ONLY) ---

def research_tool(query: str) -> dict:
    """Uses Tavily to search the web and Groq to synthesize a report."""
    print(f"[*] Tool: Researching '{query}'...")
    try:
        search_response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        results = search_response.get("results", [])
        context_data = "\n\n".join([f"SOURCE: {r['title']}\nURL: {r['url']}\nCONTENT: {r['content']}" for r in results])
        
        prompt = f"Based on these results, write a detailed research report:\n\n{context_data}\n\nTask: {query}"
        response = groq_client.chat.completions.create(
            model=SMART_MODEL,
            messages=[{"role": "system", "content": "You are a research expert. Provide structured reports."},
                      {"role": "user", "content": prompt}],
            temperature=0.3
        )
        return {"status": "success", "output": response.choices[0].message.content, "agent": "Research Tool", "tool": "Tavily + Groq 70B"}
    except Exception as e:
        return {"status": "error", "output": str(e)}

def career_tool(task: str, context: str = "") -> dict:
    """Extracts job details from a link or text, then writes a tailored CV and humanized Cover Letter."""
    base_cv = context.strip() if context else MY_BASE_CV.strip()
    job_input = task.strip()
    job_source = "Text"

    # --- STEP 1: Extract job details from URL if provided ---
    url_match = re.search(r"https?://\S+", job_input)
    if url_match:
        url = url_match.group(0)
        print(f"[*] Career Tool: Extracting job details from: {url}")
        try:
            search = tavily_client.search(
                query=f"job description requirements skills {url}",
                search_depth="advanced",
                max_results=3,
                include_answer=True
            )
            parts = []
            if search.get("answer"):
                parts.append(search["answer"])
            for r in search.get("results", []):
                parts.append(r.get("content", ""))
            job_data = "\n\n".join([p for p in parts if p])
            job_source = f"Link: {url}"
            print(f"[*] Career Tool: Extracted {len(job_data)} chars from job page.")
        except Exception as e:
            print(f"[!] Tavily extraction failed: {e}. Using raw text.")
            job_data = job_input
    else:
        job_data = job_input
        job_source = "Text Input"

    # --- STEP 2: Generate the tailored CV + Cover Letter draft ---
    prompt_payload = f"""CANDIDATE'S BASE CV:
{base_cv}

JOB DESCRIPTION (Source: {job_source}):
{job_data}

Now produce the tailored CV and cover letter following the system rules exactly."""

    try:
        print(f"[*] Career Tool: Generating tailored documents with Groq 70B...")
        gen_response = groq_client.chat.completions.create(
            model=SMART_MODEL,
            messages=[
                {"role": "system", "content": CAREER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_payload}
            ],
            temperature=0.2
        )
        full_output = gen_response.choices[0].message.content

        # --- STEP 3: Split out CV and Cover Letter ---
        if "## COVER LETTER" in full_output:
            cv_part = full_output.split("## COVER LETTER")[0].strip()
            cover_part_raw = "## COVER LETTER\n" + full_output.split("## COVER LETTER")[1].strip()
        else:
            cv_part = full_output
            cover_part_raw = ""

        # --- STEP 4: Run the Cover Letter through the Humanizer ---
        cover_part_final = cover_part_raw
        if cover_part_raw:
            print(f"[*] Career Tool: Humanizing the Cover Letter...")
            try:
                human_response = groq_client.chat.completions.create(
                    model=FAST_MODEL,
                    messages=[
                        {"role": "system", "content": HUMANIZER_SYSTEM_PROMPT},
                        {"role": "user", "content": cover_part_raw}
                    ],
                    temperature=0.8
                )
                cover_part_final = "## COVER LETTER\n" + human_response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[!] Humanizer pass failed, using original: {e}")

        final_output = f"{cv_part}\n\n---\n\n{cover_part_final}"

        return {
            "status": "success",
            "output": final_output,
            "cv_text": cv_part,
            "cover_letter_text": cover_part_final,
            "agent": "Career Assistant",
            "tool": "Groq Llama 70B + Humanizer"
        }
    except Exception as e:
        return {"status": "error", "output": str(e)}

def humanizer_tool(content: str) -> dict:
    """Removes AI robotic patterns from text via Groq."""
    try:
        response = groq_client.chat.completions.create(
            model=FAST_MODEL,
            messages=[{"role": "system", "content": "Make this text sound completely human and natural. Remove all robotic patterns."},
                      {"role": "user", "content": content}],
            temperature=0.7
        )
        return {"status": "success", "output": response.choices[0].message.content, "agent": "Humanizer Tool", "tool": "Groq Llama 8B"}
    except Exception as e:
        return {"status": "error", "output": str(e)}

def think_tool(task: str) -> dict:
    """Uses Groq 70B for deep reasoning and strategy planning."""
    print(f"[*] Tool: Groq thinking about '{task}'...")
    try:
        prompt = f"Think deeply and strategically about the following task. Break it down and plan the execution: {task}"
        response = groq_client.chat.completions.create(
            model=SMART_MODEL,
            messages=[{"role": "system", "content": "You are a Reasoning Engine. Provide a detailed thought process and plan of action for the user's task."},
                      {"role": "user", "content": prompt}],
            temperature=0.1
        )
        return {"status": "success", "output": response.choices[0].message.content, "agent": "Reasoning Tool", "tool": "Groq Llama 70B"}
    except Exception as e:
        return {"status": "error", "output": "Reasoning phase was skipped."}
