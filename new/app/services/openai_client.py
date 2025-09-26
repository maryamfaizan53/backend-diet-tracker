# # py
# import asyncio
# import openai
# from typing import AsyncIterator, List, Dict
# from app.core.config import get_settings
# from loguru import logger

# settings = get_settings()
# openai.api_key = settings.OPENAI_API_KEY

# async def async_generate(messages: List[Dict], model: str = "gpt-4o-mini", max_tokens: int = 512) -> Dict:
#     backoff = 1
#     for attempt in range(3):
#         try:
#             resp = await openai.ChatCompletion.acreate(model=model, messages=messages, max_tokens=max_tokens)
#             return resp.to_dict()
#         except Exception as e:
#             logger.warning("OpenAI generate failed attempt=%s: %s", attempt, str(e))
#             await asyncio.sleep(backoff)
#             backoff *= 2
#     raise RuntimeError("OpenAI request failed after retries")

# async def async_stream_chat(messages: List[Dict], model: str = "gpt-4o-mini") -> AsyncIterator[str]:
#     # stream=True returns an async iterator
#     try:
#         stream = await openai.ChatCompletion.acreate(model=model, messages=messages, stream=True)
#         async for chunk in stream:
#             # chunk is dict-like, extract delta content
#             for choice in chunk.get("choices", []):
#                 delta = choice.get("delta", {})
#                 text = delta.get("content") or delta.get("text")
#                 if text:
#                     yield text
#     except Exception as e:
#         logger.exception("OpenAI streaming error")
#         raise


import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, List
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel
import os
from loguru import logger

class Tool(BaseModel):
    type: str = "function"
    function: Dict[str, Any]

class AgentResponse(BaseModel):
    content: str
    tool_calls: List[Dict] = []

class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_with_tools(
        self,
        messages: List[Dict],
        tools: List[Dict],
        stream: bool = False
    ) -> AsyncGenerator[Dict, None] | Dict:
        start_time = asyncio.get_event_loop().time()
        try:
            if stream:
                stream_iter = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    stream=True
                )
                async for chunk in stream_iter:
                    if chunk.choices[0].delta.tool_calls:
                        yield {"type": "tool_call", "data": chunk.choices[0].delta}
                    elif chunk.choices[0].delta.content:
                        yield {"type": "content", "data": chunk.choices[0].delta.content}
                    await asyncio.sleep(0.01)  # Heartbeat
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
                tokens = response.usage.total_tokens if response.usage else 0
                latency = asyncio.get_event_loop().time() - start_time
                logger.info("OpenAI call", model=self.model, tokens=tokens, latency=latency)
                # Execute tools here if needed (deterministic helpers)
                return response.model_dump()
        except Exception as e:
            logger.error("OpenAI error", error=str(e))
            raise

# Tools definitions (JSON schemas)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "estimate_calories",
            "description": "Estimate daily calorie needs",
            "parameters": {
                "type": "object",
                "properties": {"calories_in": {"type": "number"}, "activity_level": {"type": "string", "enum": ["low", "medium", "high"]}},
                "required": ["calories_in", "activity_level"]
            }
        }
    },
    # Add other tools: fetch_user_history, select_exercises, save_plan, get_subscription_tier, log_tokens
    # ... (similar structure)
]

openai_client = OpenAIClient()
