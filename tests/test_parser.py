import pytest
from src.parser import ResumeParser

def test_extract_github_url():
    text1 = "My portfolio is at https://github.com/johndoe/ and it has projects."
    text2 = "Check out github.com/janedoe"
    
    assert ResumeParser.extract_github_url(text1) == "https://github.com/johndoe/"
    assert ResumeParser.extract_github_url(text2) == "github.com/janedoe"

def test_extract_github_url_none():
    text = "I have no github profile listed here."
    assert ResumeParser.extract_github_url(text) is None
