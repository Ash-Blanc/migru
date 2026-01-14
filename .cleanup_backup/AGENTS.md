# Migru - Agent Development Guidelines

## Project Overview
Migru is an AI-powered companion application for migraine and stress relief support. Built with Python 3.12+, Agno AI framework, Redis for persistent memory, and Pathway for real-time analytics.

## Development Commands

### Setup & Installation
```bash
# Install dependencies with uv
uv sync

# Create environment file
cp .env.example .env

# Install with development dependencies
uv sync --dev
```

### Running the Application
```bash
# Primary execution
uv run -m app.main

# With custom user
uv run -m app.main --user YourName

# Verbose mode (performance metrics)
uv run -m app.main --verbose
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/ -m unit          # Unit tests only
pytest tests/ -m integration   # Integration tests
pytest tests/ -m performance   # Performance tests
pytest tests/ -m cli           # CLI interface tests

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing

# Run single test
pytest tests/unit/test_agents.py::test_dynamic_agent_routing
```

### Code Quality
```bash
# Linting (ruff configured in pyproject.toml)
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking (strict mode)
uv run mypy app/

# Fix linting issues automatically
uv run ruff check --fix .
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

### Dynamic Agent System
The application uses an intelligent agent routing system in `app/agents.py`:

#### MigruCore Class
- **Companion Agent** (Cerebras): Ultra-low latency for empathetic support
- **Researcher Agent** (Mistral): High intelligence for web search and factual queries
- **Advisor Agent** (Mistral): Practical guidance and micro-actions
- **Intelligent Routing**: Automatically selects the appropriate agent based on query analysis

#### Multi-tier Fallback System
1. **Primary**: Mistral Creative (`mistral:labs-mistral-small-creative`)
2. **Fallback 1**: Cerebras (`cerebras:llama3.1-8b`) 
3. **Fallback 2**: OpenRouter (`openrouter:arcee-ai/trinity-mini:free`)

### Service Layer
Business logic goes in `app/services/`:
- **context.py**: Mood detection and dynamic persona management
- **realtime_analytics.py**: Pattern detection and insight generation via Pathway
- **user_insights.py**: Life context extraction from conversations
- **wellness_nudges.py**: Proactive wellness suggestions

### CLI Architecture
Enhanced CLI interface in `app/cli/`:
- **command_palette.py**: Intelligent command completion and fuzzy search
- **session.py**: Command handlers, onboarding, and user experience features

## Best Practices

### Performance
- **Streaming**: Use `stream=True` for better perceived speed
- **Context Optimization**: Keep history runs low (default: 3)
- **Direct Agents**: Avoid `Team` coordination unless complex multi-agent reasoning is needed
- **Model Selection**: Fast Agent for simple queries, Smart Agent for complex ones

### Reliability
- **Always implement fallback mechanisms**: MigruCore handles automatic model switching
- **Structured logging**: Use `get_logger(__name__)` for consistent logging
- **Graceful degradation**: Continue working even if some services fail

### Security
- Never commit API keys or secrets
- Use environment variables for all sensitive data
- Validate all external inputs

## Required Dependencies

### Core Dependencies
- `agno>=2.3.24` - AI agent framework with memory and culture support
- `redis>=5.0.0` - Memory/database and real-time event streams
- `mistralai>=1.10.0` - Primary AI provider with tiered models
- `cerebras-cloud-sdk>=1.64.1` - Ultra-fast backup AI provider
- `pathway>=0.28.0` - Real-time streaming analytics
- `python-dotenv>=1.0.0` - Environment configuration management

### UI and Experience
- `rich>=13.0.0` - Beautiful CLI with themes and animations
- `prompt_toolkit>=3.0.0` - Enhanced terminal interface with completions
- `psutil>=7.2.1` - Performance monitoring and memory tracking

### Development Dependencies
- `pytest>=7.4.0` with coverage, async, and mocking support
- `ruff>=0.1.0` - Fast linting and formatting (E, W, F, I, B, C4, UP, S)
- `mypy>=1.5.0` - Strict type checking with comprehensive error reporting

## Code Quality Standards
- **Type Hints**: Use strict typing with `mypy` configuration
- **Documentation**: Comprehensive docstrings for all public methods
- **Error Handling**: Specific exceptions with proper logging
- **Performance**: Monitor with decorators and optimize hot paths
- **Testing**: Aim for 80%+ coverage with comprehensive integration tests