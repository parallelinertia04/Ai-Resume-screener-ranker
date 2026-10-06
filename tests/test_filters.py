import pytest
from src.filters import EligibilityFilter

def test_eligibility_filter_pass():
    text = "Experienced in Python and Django. Built a RAG pipeline using LangChain."
    eligible, reasons, skills = EligibilityFilter.check_eligibility(text)
    assert eligible is True
    assert len(reasons) == 0
    assert "Python" in skills
    assert "Django" in skills

def test_eligibility_filter_fail_no_python():
    text = "Java developer. Built a LangChain AI agent."
    eligible, reasons, skills = EligibilityFilter.check_eligibility(text)
    assert eligible is False
    assert "No evidence of Python stack" in reasons

def test_eligibility_filter_fail_no_ai():
    text = "Python backend engineer using FastAPI and PostgreSQL."
    eligible, reasons, skills = EligibilityFilter.check_eligibility(text)
    assert eligible is False
    assert "No AI/agentic project evidence" in reasons
