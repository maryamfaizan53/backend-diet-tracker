## [1.1.0] - 2025-09-12
- Added OpenAI async client with tools.
- Implemented agents: workout_generator, etc.
- Streaming SSE endpoint /api/ai/stream-agent-response.
- Bug fixes: auth deps, CORS, validation.
- Added tests, rate limiting, subscription gating.
- Modified: ai.py, main.py, added services/agents.py, openai_client.py.