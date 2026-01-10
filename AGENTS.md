# Migru - Agent Development Guidelines

## Project Overview
Migru is an AI-powered companion application for migraine and stress relief support. Built with Python 3.12+, Agno AI framework, and Redis for persistent memory.

## Development Commands

### Setup & Installation
```bash
# Quick setup (installs uv, dependencies, creates .env)
./setup.sh

# Manual setup
uv sync                    # Install dependencies
cp .env.example .env       # Create environment file
```

### Running the Application
```bash
# Primary execution
uv run -m app.main

# With Docker (includes Redis)
docker-compose up --build
```

### Testing
**Note**: No testing framework is currently configured. When adding tests:
- Use `pytest` for unit testing
- Place tests in `tests/` directory
- Test files should follow pattern `test_*.py`
- Run single test: `pytest tests/test_module.py::test_function`

### Code Quality (Recommended Additions)
```bash
# Linting (add ruff.toml to configure)
uv run ruff check .

# Formatting (add ruff.toml to configure)
uv run ruff format .

# Type checking (add pyproject.toml [tool.mypy] section)
uv run mypy app/
```

## Code Style Guidelines

### Import Organization
```python
# Standard library imports first
import os
import sys
from typing import Optional, Union

# Third-party imports
from agno.agent import Agent
from dotenv import load_dotenv

# Local application imports
from app.config import config
from app.exceptions import MigruError
```

### Naming Conventions
- **Files**: `snake_case.py` (e.g., `knowledge_service.py`)
- **Classes**: `PascalCase` (e.g., `KnowledgeGraphService`)
- **Functions/Variables**: `snake_case` (e.g., `create_research_agent`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MODEL_SMALL`)
- **Private**: Leading underscore (e.g., `_internal_method`)

### Type Hints
Always use type hints for function signatures and class attributes:
```python
from typing import List, Dict, Optional

def add_node(self, node_id: str, label: str, attributes: Dict) -> None:
    """Adds or updates a node (entity)."""
    pass

knowledge_service: KnowledgeGraphService = KnowledgeGraphService()
```

### Error Handling
- Use custom exception hierarchy from `app.exceptions`
- Specific exceptions for different error types
- Always log errors with structured logging

```python
from app.exceptions import ConfigurationError, MigruError
from app.logger import get_logger

logger = get_logger(__name__)

try:
    config.validate()
except ConfigurationError as e:
    logger.error(f"Configuration Error: {e}")
    sys.exit(1)
except MigruError as e:
    logger.exception(f"Application error: {e}")
```

### Logging
Use the centralized logger from `app.logger`:
```python
from app.logger import get_logger

logger = get_logger("module.name")
logger.info("Information message")
logger.error("Error message")
logger.exception("Exception with traceback")
```

### Configuration
- All configuration via environment variables
- Use `app.config.Config` class for access
- Validate configuration on startup
- Provide warnings for optional missing keys

### Documentation
- Use docstrings for all classes and public methods
- Keep docstrings concise but informative
- Use `dedent()` for multi-line string instructions

```python
def create_research_agent(model: Optional[str] = None):
    """Creates a research agent with web search and scraping tools."""
    return Agent(
        instructions=dedent("""
            You are the Relief Researcher.
            CORE RESPONSIBILITIES:
            1. Search & Verify relief techniques.
            2. Check local weather if relevant.
            3. Provide concise summaries.
        """),
    )
```

## Architecture Patterns

### Multi-tier Fallback System
The application uses a 3-tier fallback system:
1. **Primary**: Mistral AI models
2. **Fallback 1**: Cerebras (llama3.1-8b)
3. **Fallback 2**: OpenRouter (gemini-2.0-flash)

Always implement fallback logic in main execution paths.

### Agent-based Architecture
- Create agents using factory functions
- Use teams for coordinated agent workflows
- Enable memory, culture, and context features
- Configure retry logic with exponential backoff

### Memory & Context
- Redis for persistent user data
- Dynamic context adaptation based on user state
- Cultural knowledge integration
- Conversation history management

### Service Layer
Business logic goes in `app/services/`:
- Keep services focused and single-purpose
- Use dependency injection for database connections
- Implement proper error handling and logging

## Development Workflow

### Environment Setup
1. Run `./setup.sh` for automated setup
2. Add API keys to `.env` file
3. Ensure Redis is running (auto-started by app)

### Adding New Features
1. Create service in `app/services/` if needed
2. Add agent factory functions in `app/agents.py`
3. Update configuration if new env vars needed
4. Add proper error handling and logging
5. Test with fallback tiers

### Code Organization
```
app/
├── main.py              # Application entry point
├── config.py            # Configuration management
├── agents.py            # Agent definitions and factories
├── db.py                # Redis database management
├── memory.py            # Memory and culture managers
├── logger.py            # Logging configuration
├── exceptions.py        # Custom exception hierarchy
├── services/            # Business logic services
└── evals.py            # Evaluation utilities
```

## Best Practices

### Security
- Never commit API keys or secrets
- Use environment variables for all sensitive data
- Validate all external inputs

### Performance
- Use Redis for caching and persistence
- Implement proper retry logic
- Consider rate limiting for external APIs

### Reliability
- Always implement fallback mechanisms
- Use structured logging for debugging
- Test failure scenarios

### User Experience
- Provide clear error messages to users
- Use emojis and friendly tone (Migru's personality)
- Graceful degradation when features are unavailable

## Required Dependencies
Key dependencies are managed in `pyproject.toml`:
- `agno>=2.3.24` - AI agent framework
- `redis>=7.1.0` - Memory/database
- `mistralai>=1.10.0` - Primary AI provider
- `python-dotenv>=1.2.1` - Environment management

Always use `uv sync` to install dependencies and maintain `uv.lock` for reproducible builds.