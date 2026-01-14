# Migru Refactor Summary

We have streamlined the codebase to be concise, accessible, and therapeutic.

## 🛠️ Key Changes

### 1. Unified CLI (`app/main.py`)
- **One Entry Point**: Replaced multiple main files with a single, robust `AsyncTherapeuticCLI`.
- **Work Mode**: Added `/work` command (or `--work` flag) for a discreet, high-contrast interface suitable for office environments.
- **Privacy Controls**: Integrated `/privacy` commands to switch between Local, Hybrid, and Flexible modes directly from the chat.

### 2. Med-Gemma Impact Challenge Integration
- **Med-Gemma Agent**: Specialized agent for clinical insights using **Gemma 2 (9B)**, adhering to Google's **HAI-DEF** principles.
- **Edge AI**: Runs entirely locally for maximum privacy.
- **New Command**: `/med` for direct access to medical analysis.

### 3. Centralized Core (`app/core.py`)
- **Single Source of Truth**: All agent logic, routing, and persona instructions are now in `MigruCore`.
- **Smart Routing**: Retained the intelligent routing between Companion, Researcher, and Advisor modes.
- **Local-First**: Deep integration with local LLMs for privacy and speed.

### 4. Clean Configuration (`app/config.py`)
- Merged enhanced settings into the main config file.
- Removed redundant `_enhanced.py` files.

### 5. Legacy Compatibility (`app/agents.py`)
- Kept as a lightweight wrapper to ensure existing tests and imports continue to work without changes.

## 🚀 How to Run

**Standard Therapeutic Mode:**
```bash
uv run -m app.main
```

**Discreet Work Mode:**
```bash
uv run -m app.main --work
```

**With Specific User Name:**
```bash
uv run -m app.main --user "Ash"
```

## ⌨️ New Shortcuts
- `Ctrl+M`: Quick Med-Gemma
- `Ctrl+W`: Toggle Work Mode
- `Ctrl+R`: Quick Research
- `Ctrl+P`: View Patterns
- `Ctrl+H`: Help

The project is now cleaner, faster, and ready for development.
