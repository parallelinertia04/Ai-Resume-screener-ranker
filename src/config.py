import os
from dotenv import load_dotenv

load_dotenv()

# Scoring Weights
WEIGHT_AI = 40
WEIGHT_PYTHON = 30
WEIGHT_CLOUD = 15
WEIGHT_GITHUB = 10
WEIGHT_ENG_DEPTH = 5

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "groq"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# GitHub Enrichment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Pipeline Configuration
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "5"))
