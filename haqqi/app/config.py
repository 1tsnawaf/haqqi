"""Central settings. Loads from environment / .env."""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM provider: "openai" | "anthropic" | "mock"
# Auto-fall back to mock if the chosen provider has no API key, so the
# walking skeleton always runs.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    LLM_PROVIDER = "mock"
elif LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
    LLM_PROVIDER = "mock"

# RAG — two corpora under DATA_DIR, each its own subfolder.
DATA_DIR = os.getenv("DATA_DIR", "data")
# labor_law is the PRIMARY corpus (employment); civil_procedure is secondary
# (where/how to file). Retrieval biases toward PRIMARY_CORPUS.
CORPORA = ["labor_law", "civil_procedure"]
PRIMARY_CORPUS = "labor_law"
LAW_DATA_DIR = os.getenv("LAW_DATA_DIR", DATA_DIR)   # kept for back-compat
INDEX_PATH = os.getenv("INDEX_PATH", os.path.join(DATA_DIR, ".index.json"))
TOP_K = int(os.getenv("TOP_K", "8"))
# How strongly to favour the primary corpus (multiplies its similarity score).
PRIMARY_BOOST = float(os.getenv("PRIMARY_BOOST", "1.12"))
# Hybrid retrieval: weight of the lexical (Arabic-stemmed overlap) signal vs the
# semantic (embedding) signal. Recovers matches `-small` embeddings miss.
LEX_WEIGHT = float(os.getenv("LEX_WEIGHT", "0.5"))

# Agent loop safety
MAX_CLARIFYING_QUESTIONS = int(os.getenv("MAX_CLARIFYING_QUESTIONS", "3"))

# Backend URL the UI calls
API_URL = os.getenv("API_URL", "http://localhost:8000")
