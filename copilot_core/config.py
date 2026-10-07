import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")
os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")

# Same model (gpt-oss-20b) everywhere; only the endpoint differs:
#   groq    - local runs (GROQ_API_KEY)
#   foundry - Azure deployments: Azure AI Foundry deployment, OpenAI-compatible v1 endpoint
PROVIDER = os.getenv("COPILOT_PROVIDER", "groq")
FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT", "")          # e.g. https://<resource>.openai.azure.com/openai/v1/
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY", "")
FOUNDRY_DEPLOYMENT = os.getenv("FOUNDRY_DEPLOYMENT", "gpt-oss-20b")
if PROVIDER == "foundry":
    MODEL = f"foundry:{FOUNDRY_DEPLOYMENT}"
    _has_key = bool(FOUNDRY_ENDPOINT and FOUNDRY_API_KEY)
else:
    MODEL = os.getenv("COPILOT_MODEL", "groq:openai/gpt-oss-20b")
    _has_key = bool(os.getenv("GROQ_API_KEY"))
PRICE_IN = float(os.getenv("PRICE_INPUT_PER_M", "0.075"))
PRICE_OUT = float(os.getenv("PRICE_OUTPUT_PER_M", "0.30"))
USD_INR = float(os.getenv("USD_INR", "88"))
OFFLINE = os.getenv("COPILOT_OFFLINE", "0") == "1" or not _has_key
CACHE_DIR = Path(__file__).resolve().parent / "cache"
WRITE_CACHE = False   # only `./run.sh warm` refreshes the committed fallback drafts
