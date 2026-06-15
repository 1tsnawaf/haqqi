"""Central settings. Loads from environment / .env."""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM provider: "anthropic" | "openai" | "gemini" | "mock"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_MODEL = os.getenv("LLM_MODEL", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# RAG
LAW_DATA_DIR = os.getenv("LAW_DATA_DIR", "data/labor_law")
TOP_K = int(os.getenv("TOP_K", "4"))

# Agent loop safety
MAX_CLARIFYING_QUESTIONS = int(os.getenv("MAX_CLARIFYING_QUESTIONS", "3"))

# Backend URL the UI calls
API_URL = os.getenv("API_URL", "http://localhost:8000")
