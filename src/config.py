import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("aiscraping")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# LiteLLM provider format: "provider/model"
# See https://docs.litellm.ai/docs/providers
PROVIDERS = {
    "OpenAI": {
        "models": [
            ("gpt-4.1-mini", "openai/gpt-4.1-mini"),
            ("gpt-4.1-nano", "openai/gpt-4.1-nano"),
            ("o4-mini", "openai/o4-mini"),
            ("gpt-4o-mini", "openai/gpt-4o-mini"),
        ],
        "env_key": "OPENAI_API_KEY",
    },
    "Anthropic": {
        "models": [
            ("Claude Sonnet 4", "anthropic/claude-sonnet-4-20250514"),
            ("Claude Haiku 3.5", "anthropic/claude-3-5-haiku-20241022"),
        ],
        "env_key": "ANTHROPIC_API_KEY",
    },
}

MAX_RETRIES = 3
