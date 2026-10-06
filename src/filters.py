import re
from typing import Tuple, List

class EligibilityFilter:
    PYTHON_KEYWORDS = [r"\bpython\b", r"\bdjango\b", r"\bfastapi\b", r"\bflask\b"]
    AI_KEYWORDS = [
        r"\bai\b", r"\bllm\b", r"\brag\b", r"\blangchain\b", r"\blanggraph\b", 
        r"\bllamaindex\b", r"\bagentic\b", r"\bembeddings\b", r"\bvector search\b"
    ]

    @staticmethod
    def check_eligibility(text: str) -> Tuple[bool, List[str], List[str]]:
        text_lower = text.lower()
        
        has_python = any(re.search(kw, text_lower) for kw in EligibilityFilter.PYTHON_KEYWORDS)
        has_ai = any(re.search(kw, text_lower) for kw in EligibilityFilter.AI_KEYWORDS)
        
        reasons = []
        if not has_python:
            reasons.append("No evidence of Python stack")
        if not has_ai:
            reasons.append("No AI/agentic project evidence")
            
        matched_skills = []
        # Basic scanning for skills mapping
        all_skills = ["Python", "FastAPI", "Django", "Flask", "LangChain", "LangGraph", 
                      "Docker", "GCP", "PostgreSQL", "Redis", "Java", "React", "Next.js"]
        for skill in all_skills:
            if skill.lower() in text_lower:
                matched_skills.append(skill)
                
        return has_python and has_ai, reasons, matched_skills
