# py
import asyncio
from typing import Dict, List
from app.services.openai_client import async_generate, async_stream_chat
from loguru import logger

AGENT_SPECS = {
    "nutrition": "You are a nutrition expert. Provide dietary recommendations based on user context.",
    "fitness": "You are a certified fitness coach. Provide workout suggestions and activity targets.",
    "mental_health": "You are a mental health support specialist. Provide coping strategies and resources.",
    "risk_assessment": "You are a clinical risk assessor. Highlight potential health risks and red flags."
}

async def run_agent(name: str, user_context: Dict, prompt: str) -> Dict:
    system_prompt = AGENT_SPECS[name]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
        {"role": "user", "content": f"User context: {user_context}"}
    ]
    # TODO: Integrate external tools here (e.g., lookup nutrition DB). Implement tool call in future.
    resp = await async_generate(messages, model="gpt-4o-mini", max_tokens=400)
    text = ""
    try:
        text = resp["choices"][0]["message"]["content"]
    except Exception:
        logger.exception("Malformed OpenAI response")
    # Simple confidence heuristic: presence of assertive words -> higher confidence (deterministic rule)
    confidence = 0.9 if "should" in text or "recommend" in text else 0.7
    return {"name": name, "output": text, "confidence": confidence}

async def nutrition_agent(user_context: Dict, prompt: str) -> Dict:
    return await run_agent("nutrition", user_context, prompt)

async def fitness_agent(user_context: Dict, prompt: str) -> Dict:
    return await run_agent("fitness", user_context, prompt)

async def mental_health_agent(user_context: Dict, prompt: str) -> Dict:
    return await run_agent("mental_health", user_context, prompt)

async def risk_assessment_agent(user_context: Dict, prompt: str) -> Dict:
    return await run_agent("risk_assessment", user_context, prompt)

async def run_agents_concurrently(user_context: Dict, prompt: str) -> Dict:
    tasks = [
        nutrition_agent(user_context, prompt),
        fitness_agent(user_context, prompt),
        mental_health_agent(user_context, prompt),
        risk_assessment_agent(user_context, prompt)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    # Aggregate outputs
    aggregated_text = "\n\n".join([f"{r['name'].upper()}:\n{r['output']}" for r in results])
    # Weighted confidence average
    total_conf = sum([r["confidence"] for r in results])
    avg_conf = total_conf / len(results)
    return {"agents": results, "aggregated_output": aggregated_text, "confidence": float(avg_conf)}

async def stream_orchestrator(user_context: Dict, prompt: str):
    # Streams orchestrated responses by sequentially streaming each agent
    for name in ["nutrition", "fitness", "mental_health", "risk_assessment"]:
        system_prompt = AGENT_SPECS[name]
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
            {"role": "user", "content": f"User context: {user_context}"}
        ]
        async for chunk in async_stream_chat(messages, model="gpt-4o-mini"):
            yield {"agent": name, "chunk": chunk}
