import os
import requests
from dotenv import load_dotenv
import time
import logging

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

logger = logging.getLogger(__name__)

def summarize_with_groq(prompt, max_retries=3):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    # Truncate prompt to avoid 413 error (limit to ~8k tokens, assuming 1 token ~4 chars)
    max_prompt_length = 32000  # Conservative estimate
    if len(prompt) > max_prompt_length:
        prompt = prompt[:max_prompt_length - 100] + "... [truncated]"
        logger.warning("Prompt truncated to fit API limits")

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 500  # Reduced to ensure response fits
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                # Fallback summary
                return f"[Summary failed due to API error: {str(e)}]"