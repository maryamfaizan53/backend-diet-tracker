# # py
# import asyncio
# from typing import Dict, List
# from app.services.openai_client import async_generate, async_stream_chat
# from loguru import logger

# AGENT_SPECS = {
#     "nutrition": "You are a nutrition expert. Provide dietary recommendations based on user context.",
#     "fitness": "You are a certified fitness coach. Provide workout suggestions and activity targets.",
#     "mental_health": "You are a mental health support specialist. Provide coping strategies and resources.",
#     "risk_assessment": "You are a clinical risk assessor. Highlight potential health risks and red flags."
# }

# async def run_agent(name: str, user_context: Dict, prompt: str) -> Dict:
#     system_prompt = AGENT_SPECS[name]
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": prompt},
#         {"role": "user", "content": f"User context: {user_context}"}
#     ]
#     # TODO: Integrate external tools here (e.g., lookup nutrition DB). Implement tool call in future.
#     resp = await async_generate(messages, model="gpt-4o-mini", max_tokens=400)
#     text = ""
#     try:
#         text = resp["choices"][0]["message"]["content"]
#     except Exception:
#         logger.exception("Malformed OpenAI response")
#     # Simple confidence heuristic: presence of assertive words -> higher confidence (deterministic rule)
#     confidence = 0.9 if "should" in text or "recommend" in text else 0.7
#     return {"name": name, "output": text, "confidence": confidence}

# async def nutrition_agent(user_context: Dict, prompt: str) -> Dict:
#     return await run_agent("nutrition", user_context, prompt)

# async def fitness_agent(user_context: Dict, prompt: str) -> Dict:
#     return await run_agent("fitness", user_context, prompt)

# async def mental_health_agent(user_context: Dict, prompt: str) -> Dict:
#     return await run_agent("mental_health", user_context, prompt)

# async def risk_assessment_agent(user_context: Dict, prompt: str) -> Dict:
#     return await run_agent("risk_assessment", user_context, prompt)

# async def run_agents_concurrently(user_context: Dict, prompt: str) -> Dict:
#     tasks = [
#         nutrition_agent(user_context, prompt),
#         fitness_agent(user_context, prompt),
#         mental_health_agent(user_context, prompt),
#         risk_assessment_agent(user_context, prompt)
#     ]
#     results = await asyncio.gather(*tasks, return_exceptions=False)
#     # Aggregate outputs
#     aggregated_text = "\n\n".join([f"{r['name'].upper()}:\n{r['output']}" for r in results])
#     # Weighted confidence average
#     total_conf = sum([r["confidence"] for r in results])
#     avg_conf = total_conf / len(results)
#     return {"agents": results, "aggregated_output": aggregated_text, "confidence": float(avg_conf)}

# async def stream_orchestrator(user_context: Dict, prompt: str):
#     # Streams orchestrated responses by sequentially streaming each agent
#     for name in ["nutrition", "fitness", "mental_health", "risk_assessment"]:
#         system_prompt = AGENT_SPECS[name]
#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": prompt},
#             {"role": "user", "content": f"User context: {user_context}"}
#         ]
#         async for chunk in async_stream_chat(messages, model="gpt-4o-mini"):
#             yield {"agent": name, "chunk": chunk}
import asyncio
from typing import Dict, Any, AsyncGenerator
from pydantic import BaseModel, Field
from app.services.openai_client import openai_client, TOOLS
from app.services.supabase_client import get_user_history, save_plan_to_db  # Assume async wrappers
from app.core.security import get_current_user
from app.core.config import settings
import hashlib
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
import structlog

logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)

class WorkoutPlan(BaseModel):
    title: str
    duration_minutes: int
    difficulty: str = Field(..., regex="^(beginner|intermediate|advanced)$")
    exercises: List[Dict[str, Any]] = Field(..., min_items=1)  # e.g., {"name": str, "sets": int, "reps": str}
    tips: List[str] = []
    progression: Dict[str, str] = {}

class NutritionPlan(BaseModel):  # Similar for other agents
    meals: List[Dict]
    # ...

class AgentOrchestrator:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cache = {}  # In-memory; replace with Redis

    async def run_agent(self, agent_name: str, prompt: str, context: Dict) -> Dict:
        cache_key = hashlib.md5((prompt + str(context) + self.user_id).encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Gate subscription
        tier = await get_subscription_tier(self.user_id)
        if tier == "free" and await is_rate_limited(self.user_id):
            raise ValueError("Quota exceeded")

        messages = [{"role": "system", "content": f"You are {agent_name}. Use tools for accuracy."},
                    {"role": "user", "content": prompt}]
        messages[-1]["content"] += f"\nContext: {context}"

        response = await openai_client.call_with_tools(messages, TOOLS, stream=False)
        
        # Parse tool calls and execute deterministic tools
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                if func_name == "fetch_user_history":
                    args["result"] = await get_user_history(self.user_id)
                elif func_name == "save_plan":
                    args["result"] = await save_plan_to_db(self.user_id, args["plan"])
                # ... handle other tools

        # Validate with Pydantic
        if agent_name == "workout_generator":
            result = WorkoutPlan.model_validate_json(response.choices[0].message.content)
        # ... other agents

        self.cache[cache_key] = result.model_dump()
        return result.model_dump()

    async def run_concurrently(self, agents: List[str], prompt: str, context: Dict) -> AsyncGenerator[Dict, None]:
        tasks = [self.run_agent(agent, prompt, context) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, res in enumerate(results):
            if not isinstance(res, Exception):
                yield {"stage": "done", "agent": agents[i], "result": res}
            else:
                yield {"stage": "error", "agent": agents[i], "error": str(res)}
        # Aggregate
        aggregated = {"action_plan": [f"From {agents[i]}: {r}" for i, r in enumerate(results) if isinstance(r, dict)]}
        yield {"stage": "complete", "aggregated": aggregated}

    async def stream_orchestrator(self, prompt: str, stats: Dict, options: Dict) -> AsyncGenerator[str, None]:
        user_id = get_current_user().id  # From dep
        context = {"stats": stats}
        agents = options.get("agents", ["workout_generator"])

        # Limiter check
        @limiter.limit("10/minute")
        async def check_limit():
            pass
        await check_limit()

        yield '{"stage": "starting", "agent": "' + agents[0] + '"}' + '\n\n'  # SSE format

        async for chunk in self.run_concurrently(agents, prompt, context):
            if request.is_disconnected():  # FastAPI check
                break
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.1)  # Throttle

# Usage in router