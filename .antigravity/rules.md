# Polymarket God Mode - Antigravity Agent Rules

## Project Overview
This is a prediction market trading platform with multi-agent AI decision-making. 
Built with Python 3.9+, Streamlit, async/await patterns, and Pydantic models.

## Architecture
```
core/           - Data models, state management, API clients, LLM integration
agents/         - Council of Agents (swarm intelligence)
strategies/     - Trading strategies (whale watcher, etc.)
dashboard/      - Streamlit War Room UI
config/         - Pydantic Settings configuration
```

## Key Patterns

### State Management
- Use `state_manager` singleton for all state operations
- Thread-safe via `RLock` - safe for concurrent access
- Never access `_private` attributes directly

### Agent Development
- All agents inherit from `BaseAgent` in `agents/swarm.py`
- Implement `async def analyze(market, context) -> AgentAnalysis`
- Use `llm_manager` for AI analysis, fall back to rule-based
- Return `AgentAnalysis` via `self._create_analysis()` helper

### Adding New Agents
```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.MY_TYPE, "Agent Name")
        self.system_prompt = "..."
    
    async def analyze(self, market, context):
        # Your analysis logic
        pass
```
Then add to `CouncilOfAgents.agents` list.

### API Calls
- Use `polymarket_client` for market data and trading
- Use `llm_manager.analyze()` for JSON responses
- Use `llm_manager.generate()` for text responses
- All API calls are async - use `await`

## Code Standards

### Imports
- Standard library first, then third-party, then local
- Use absolute imports from project root

### Type Hints
- All function parameters and returns must be typed
- Use `Optional[T]` for nullable values
- Use `List`, `Dict`, `Any` from typing module

### Error Handling
- Wrap external calls in try/except
- Log errors with `logger.error()`
- Return graceful fallbacks (ABSTAIN votes, empty lists)
- Call `state_manager.increment_errors()` on failures

### Async Patterns
- All I/O operations must be async
- Use `asyncio.gather()` for concurrent operations
- Use `asyncio.sleep()` not `time.sleep()` in async code

## Testing
- Tests in `tests/` directory
- Use pytest with pytest-asyncio
- Mock external APIs in tests
- Run: `pytest -v`

## Common Tasks

### Add a new market data source
1. Create client in `core/` 
2. Add to `__init__.py` exports
3. Integrate into relevant agent's context

### Modify dashboard
1. Edit `dashboard/app.py`
2. Follow existing CSS patterns in `CYBERPUNK_CSS`
3. Use `state_manager` for data, never direct API calls

### Add configuration
1. Add field to `Settings` class in `config/settings.py`
2. Add corresponding env var to `.env.example`
3. Access via `settings.field_name`

## Do Not
- Modify `_private` attributes directly
- Use synchronous I/O in async functions
- Hardcode API keys or secrets
- Skip error handling on external calls
- Break the singleton patterns
