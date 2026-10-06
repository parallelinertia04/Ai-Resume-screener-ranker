import json
from google import genai
from typing import Optional
from src.config import LLM_PROVIDER, GEMINI_API_KEY, GROQ_API_KEY, GEMINI_MODEL, GROQ_MODEL
from src.models import LLMEvaluation

class LLMAdapter:
    @staticmethod
    def evaluate_candidate(text: str) -> Optional[LLMEvaluation]:
        if LLM_PROVIDER == "groq":
            return LLMAdapter._evaluate_groq(text)
        else:
            return LLMAdapter._evaluate_gemini(text)

    @staticmethod
    def _evaluate_gemini(text: str) -> Optional[LLMEvaluation]:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        
        client = genai.Client(api_key=GEMINI_API_KEY)
        system_prompt = """You are a technical recruiter. Extract structured evaluation in JSON format exactly matching this schema:
{
    "score_breakdown": {
        "ai_project_depth": 0,
        "python_backend": 0,
        "cloud_fullstack": 0,
        "github": 0,
        "engineering_depth": 0
    },
    "matched_skills": ["skill1"],
    "project_summary": "summary",
    "strengths": ["str1"],
    "concerns": ["con1"]
}"""

        prompt = f"""
{system_prompt}

Evaluate the following resume text based on these criteria:
1. AI/Agentic Depth (0-40): Reward real systems, tools, retrieval, orchestration over wrappers. Deduct 5-15 pts if it's just a thin wrapper.
2. Python/Backend (0-30): Reward FastAPI, async, PostgreSQL, Redis.
3. Cloud/Fullstack (0-15): Reward GCP, Docker, React.
4. Engineering Depth (0-5): Reward testing, architecture, queues, etc.

Resume Text:
{text[:4000]}
"""
        
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'temperature': 0.1
                }
            )
            data = json.loads(response.text)
            return LLMEvaluation(**data)
        except Exception as e:
            print(f"Gemini evaluation error: {e}")
            return None

    @staticmethod
    def _evaluate_groq(text: str) -> Optional[LLMEvaluation]:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set.")
        
        from groq import Groq
        import time
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
Evaluate the following resume text.
Resume Text: {text[:3000]}
"""
        
        system_prompt = f"""You are a technical recruiter. Extract structured evaluation in JSON format exactly matching this schema:
{{
    "score_breakdown": {{
        "ai_project_depth": 0,
        "python_backend": 0,
        "cloud_fullstack": 0,
        "github": 0,
        "engineering_depth": 0
    }},
    "matched_skills": ["skill1"],
    "project_summary": "summary",
    "strengths": ["str1"],
    "concerns": ["con1"]
}}"""
        
        max_retries = 3
        delay = 15
        
        for attempt in range(max_retries):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model=GROQ_MODEL,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                result_text = chat_completion.choices[0].message.content
                data = json.loads(result_text)
                return LLMEvaluation(**data)
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
                    import re
                    match = re.search(r"try again in (\d+\.?\d*)s", error_msg) or re.search(r"please try again in (\d+\.?\d*)s", error_msg)
                    if match:
                        wait_seconds = float(match.group(1)) + 2.0
                    else:
                        wait_seconds = delay

                    if attempt < max_retries - 1:
                        print(f"Groq Rate limit hit. Waiting {wait_seconds:.1f}s before retry (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(wait_seconds)
                        delay *= 2
                        continue
                print(f"Groq evaluation error: {e}")
                return None
