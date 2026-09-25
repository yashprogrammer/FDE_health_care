import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")
os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")

MODEL = os.getenv("COPILOT_MODEL", "groq:openai/gpt-oss-20b")
PRICE_IN = float(os.getenv("PRICE_INPUT_PER_M", "0.075"))
PRICE_OUT = float(os.getenv("PRICE_OUTPUT_PER_M", "0.30"))
USD_INR = float(os.getenv("USD_INR", "88"))
OFFLINE = os.getenv("COPILOT_OFFLINE", "0") == "1" or not os.getenv("GROQ_API_KEY")
CACHE_DIR = Path(__file__).resolve().parent / "cache"
WRITE_CACHE = False   # only `./run.sh warm` refreshes the committed fallback drafts
