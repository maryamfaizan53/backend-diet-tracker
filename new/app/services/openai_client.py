# py
import asyncio
import openai
from typing import AsyncIterator, List, Dict
from app.core.config import get_settings
from loguru import logger

settings = get_settings()
openai.api_key = settings.OPENAI_API_KEY

async def async_generate(messages: List[Dict], model: str = "gpt-4o-mini", max_tokens: int = 512) -> Dict:
    backoff = 1
    for attempt in range(3):
        try:
            resp = await openai.ChatCompletion.acreate(model=model, messages=messages, max_tokens=max_tokens)
            return resp.to_dict()
        except Exception as e:
            logger.warning("OpenAI generate failed attempt=%s: %s", attempt, str(e))
            await asyncio.sleep(backoff)
            backoff *= 2
    raise RuntimeError("OpenAI request failed after retries")

async def async_stream_chat(messages: List[Dict], model: str = "gpt-4o-mini") -> AsyncIterator[str]:
    # stream=True returns an async iterator
    try:
        stream = await openai.ChatCompletion.acreate(model=model, messages=messages, stream=True)
        async for chunk in stream:
            # chunk is dict-like, extract delta content
            for choice in chunk.get("choices", []):
                delta = choice.get("delta", {})
                text = delta.get("content") or delta.get("text")
                if text:
                    yield text
    except Exception as e:
        logger.exception("OpenAI streaming error")
        raise
