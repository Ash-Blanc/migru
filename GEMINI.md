# GEMINI.md - Migru Project Context

This document provides essential context and instructions for AI agents (like Gemini) working on the **Migru** project.

## 🌟 Project Overview

**Migru** is a warm, AI-powered companion designed to support users through migraines and stress. It prioritizes empathy, research-backed relief strategies, and ultra-fast performance.

- **Primary Mission**: To walk alongside users with a "wise, humble, and deeply curious" persona, helping them discover wellness patterns.
- **Key Technologies**:
    - **Language**: Python 3.12+ (managed with `uv`)
    - **Agent Framework**: [Agno AI](https://agno.com) (formerly Phidata)
    - **AI Models**: Cerebras (llama3.1-8b) for speed, Mistral Small for intelligence, Gemini 2.0 Flash for fallback.
    - **Database/Memory**: Redis (Conversation history, user profiles, and real-time pattern detection).
    - **Streaming Analytics**: [Pathway](https://pathway.com) for low-latency pattern recognition.
    - **UI**: [Rich](https://github.com/Textualize/rich) for a beautiful terminal-based interface.

## 🏗️ Architecture & Core Components

### 1. Agent Logic (`app/agents.py`)
- **Migru Agent**: The primary companion persona. Uses a 3-history-run window for speed.
- **Wisdom Researcher**: Specialized in web search (DuckDuckGo, Firecrawl) and YouTube for evidence-based wellness.
- **Team vs. Direct**: Prefers **Direct Agent Mode** for 2-3x faster responses. Team coordination is available but used sparingly.
- **Fallbacks**: Implements a robust 3-tier fallback system across different AI providers.

### 2. Services (`app/services/`)
- **Context Service (`context.py`)**: Manages dynamic persona adaptation based on user mood and history.
- **Knowledge Service (`knowledge.py`)**: A basic knowledge graph for storing entities and relationships.
- **Real-time Analytics (`realtime_analytics.py`)**: Uses Redis Streams to detect temporal and environmental (e.g., weather pressure) correlations.
- **User Insights (`user_insights.py`)**: Extracts life context (age hints, interests, schedule) from natural conversation.

### 3. State & Memory (`app/db.py`, `app/memory.py`, `app/personalization.py`)
- **Redis**: The backbone for persistence.
- **Personalization Engine**: Adapts the agent's behavior to the user's specific wellness journey and communication style.

## 🚀 Building and Running

### Prerequisites
- Python 3.12+
- `uv` package manager
- Redis server (local or via Docker)

### Key Commands
- **Setup**: `./setup.sh` (installs `uv`, dependencies, and sets up `.env`)
- **Run (CLI)**: `uv run -m app.main`
- **Run (Docker)**: `docker-compose up --build`
- **Test**: `pytest` (Configured in `pyproject.toml`)
- **Lint**: `ruff check .`
- **Type Check**: `mypy app/`

## 🛠️ Development Conventions

### 1. Coding Style
- **Imports**: Standard library -> Third-party -> Local application.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes.
- **Typing**: Strict type hints required (checked by `mypy`).
- **Docstrings**: Required for all public methods; use `dedent()` for multi-line strings.

### 2. Error Handling
- Use the `MigruError` hierarchy in `app/exceptions.py`.
- Suppress verbose third-party logs to maintain a clean CLI experience (`app.logger.suppress_verbose_logging`).

### 3. Performance First
- **Streaming**: Always enable streaming for perceived speed.
- **Context Optimization**: Keep history runs low (default: 3).
- **Direct Agents**: Avoid `Team` coordination unless complex multi-agent reasoning is strictly necessary.

### 4. Personality Guidelines
- **Persona**: Gender-neutral, ageless, curious, and humble.
- **Tone**: Gentle, metaphorical, and supportive.
- **Avoid**: Absolute claims, clinical language, or over-apologizing.

## 📂 Directory Structure
- `app/`: Source code.
- `.letta/`: Configuration/settings for the Letta integration (if used).
- `tests/`: (TODO) Expansion of test suites.
- `AGENTS.md`: Detailed agent development guidelines.
- `PERFORMANCE.md`: Tuning for speed and reliability.

---
*Note: This file is intended for AI consumption to ensure consistent and high-quality assistance.*
