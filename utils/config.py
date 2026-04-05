import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
SEC_API_KEY = os.getenv("SEC_API_KEY")

# Validate required API keys
required_keys = {
    "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
    "APIFY_API_KEY": APIFY_API_KEY,
    "SEC_API_KEY": SEC_API_KEY,
}

missing_keys = [key for key, value in required_keys.items() if not value]
if missing_keys:
    logger.warning(f"Missing API keys: {', '.join(missing_keys)}")

# Configuration constants
SEC_QUERY_RANGE = "NOW-7DAYS"  # Fetch last 7 days of insider trades
TWEET_SEARCH_LIMIT = 100
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SIMILARITY_THRESHOLD = 0.5

# Model configuration
LLM_MODEL = "mistralai/mistral-7b-instruct"
LLM_TIMEOUT = 30
MAX_RETRIES = 3

logger.info("Configuration loaded successfully")