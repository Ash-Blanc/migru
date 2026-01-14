# Migru

Migru is a **local-first**, personal, and private AI-powered companion designed to support you through migraines and stress with empathy and research-backed relief strategies. It combines ultra-fast responses with deep, personalized wisdom, while keeping your data under your control.

## ✨ Showcase

<div align="center">

### Beautiful CLI Experience
*Clean, calming interface designed for wellness and relief*

<table>
<tr>
<td width="50%">
<img src="app/ss0.webp" alt="Welcome Screen" width="100%"/>
<p align="center"><em>🌸 Warm welcome with elegant design</em></p>
</td>
<td width="50%">
<img src="app/ss1.webp" alt="Conversation" width="100%"/>
<p align="center"><em>💬 Natural, empathetic conversations</em></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="app/ss2.webp" alt="Research Capabilities" width="100%"/>
<p align="center"><em>🔍 Intelligent research with fallbacks</em></p>
</td>
<td width="50%">
<img src="app/ss3.webp" alt="Smart Responses" width="100%"/>
<p align="center"><em>🧠 Thoughtful, context-aware responses</em></p>
</td>
</tr>
<tr>
<td colspan="2">
<img src="app/ss4.webp" alt="Full Experience" width="100%"/>
<p align="center"><em>⚡ Ultra-fast responses (1-3 seconds) with Cerebras AI</em></p>
</td>
</tr>
</table>

</div>

---

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Redis (local or Docker)
- `uv` package manager

## 📁 Project Structure

The project has been refactored for better organization and maintainability:

```
app/
├── cli/                  # CLI components (new!)
│   ├── command_palette.py # Command palette and UI components
│   ├── session.py         # CLI session management
│   └── README.md          # CLI documentation
├── services/             # Business logic services
├── agents.py             # Agent definitions and factories
├── config.py             # Configuration management
├── main.py               # Application entry point
└── ...                   # Other core modules
```

### Key Improvements

1. **Modular CLI Architecture**: Separated CLI components into dedicated modules
2. **Enhanced Error Handling**: Comprehensive error handling with user-friendly messages
3. **Performance Optimization**: Lazy loading and service caching
4. **Improved Testing**: Comprehensive unit tests for CLI components
5. **Better Documentation**: Detailed documentation for all modules

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Run all tests
pytest tests/

# Run specific test modules
pytest tests/unit/test_cli.py       # CLI component tests
pytest tests/unit/test_agents.py    # Agent tests
pytest tests/unit/test_config.py    # Configuration tests
```

### Test Coverage

- **CLI Components**: Command palette, session handlers, error handling
- **Agents**: Agent creation, routing, error handling
- **Configuration**: Validation, environment variables
- **Services**: Pattern detection, user insights, context management

## 🔧 Development

### Code Quality

The codebase follows best practices:

- **Type Hints**: Comprehensive type annotations
- **Error Handling**: Graceful degradation and user-friendly messages
- **Logging**: Structured logging for debugging
- **Modularity**: Clear separation of concerns
- **Documentation**: Comprehensive docstrings and READMEs

### Performance

- **Lazy Loading**: Heavy dependencies loaded only when needed
- **Service Caching**: Frequently accessed services are cached
- **Optimized Imports**: Organized imports to avoid circular dependencies
- **Memory Monitoring**: Memory usage tracking and optimization

## 📚 Documentation

Each module includes comprehensive documentation:

- `app/cli/README.md` - CLI module documentation
- `app/services/` - Service layer documentation
- `app/agents.py` - Agent architecture documentation
- `app/config.py` - Configuration documentation

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Redis (local)
- `uv` package manager

### 1. Install Globally (Recommended)
You can install Migru as a global command line tool directly:

```bash
# If running from the source directory (Development)
# Use editable mode and pin Python 3.12 for binary compatibility
uv tool install -e . --python 3.12

# Or install globally without cloning (once published)
uv tool install migru --python 3.12
```

Then simply run:
```bash
migru
```

### 2. Configure Environment
Create a `.env` file in your working directory with your API keys:
```env
MISTRAL_API_KEY=...     # Primary Intelligence
FIRECRAWL_API_KEY=...   # Deep Research
OPENWEATHER_API_KEY=... # Environmental Context
CEREBRAS_API_KEY=...    # Ultra-Fast Responses (Recommended)
```

---

## 💻 Usage & Commands

Migru is primarily a CLI application.

### Basic Start
If installed globally:
```bash
migru
```

Or run from source:
```bash
uv run -m app.main
```

### Custom User Profile
Start with a specific user context (loads your personal history/patterns):
```bash
migru --user "Alex"
```

### Accessibility Mode
Launch with high-contrast UI and reduced motion/animations:
```bash
migru --accessible
```

### CLI Flags
| Flag | Short | Description |
|------|-------|-------------|
| `--user <name>` | `-u` | Sets the active user profile name (Default: "Friend") |
| `--accessible` | `-a` | Enables high-contrast, reduced-motion UI |
| `--quiet` | `-q` | Suppresses startup banner and welcome messages |
| `--verbose` | `-v` | Shows detailed performance logs and debug info |

### In-App Commands
Once inside the chat, use these slash commands to interact with the system:

| Command | Description | Example Output |
|---------|-------------|----------------|
| `/profile` | View your learned preferences & bio context | `Work: Remote, Sensitivities: Light` |
| `/patterns` | See discovered wellness rhythms | `Peak Symptom Hour: 10:00 AM` |
| `/bio <args>` | Simulate biometric data input | `/bio hr=110 sleep=60` |
| `/model` | Switch AI models dynamically | `Switched to Mistral AI` |
| `/history` | View recent conversation memories | `Last topic: Magnesium for relief` |
| `/clear` | Clear the terminal screen | *(Clears screen)* |
| `/exit` | End the session gracefully | *(Saves state and exits)* |

---

## 🧠 Multimodal Simulation

You can simulate wearable/sensor data directly from the CLI to test the **Real-Time Analytics** engine.

**Example: Simulating High Stress**
```text
/bio hr=120 sleep=50 steps=200
```
*System Response:* The analytics engine fuses this high heart rate data with your conversation. If you then say *"I feel anxious"*, the system triggers a **Reactive Alert** due to the correlation of physiological and verbal signals.

---

## 🔍 Search & Research

Migru automatically detects when you need external facts.

**Trigger Word:** `define`
> **You:** "Define prodrome phase."
>
> **Migru (Research Agent):**
> **## Key Findings**
> *   The **prodrome** is the "pre-headache" phase, occurring hours or days before pain.
> *   Symptoms include yawning, mood changes, and food cravings.
> *   Recognizing it can allow for **early intervention**.

---

## 🏗️ Architecture Highlights

*   **Local-First Privacy**: Your conversation history and patterns are stored in your own local Redis instance, ensuring your wellness data stays private.
*   **Adaptive Context**: Automatically adjusts persona (calm vs. energetic) based on your detected mood.
*   **Data Fusion**: Correlates chat logs with simulated biometric streams using **Pathway**.
*   **Redis Pipelining**: Atomic, low-latency updates for real-time pattern tracking.
*   **Dynamic Routing**: Intelligently switches between "Fast" (Cerebras) and "Smart" (Mistral) models based on query complexity.

👉 **[Read the End-to-End Architecture Deep Dive](HOW_IT_WORKS.md)**

For deep performance tuning, see [PERFORMANCE.md](PERFORMANCE.md).

---

## 📚 Documentation

- **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Detailed explanation of Pathway integration and data flow
- **[PERFORMANCE.md](PERFORMANCE.md)** - Performance optimization guide
- **[AGENTS.md](AGENTS.md)** - Agent development guidelines
- **[.env.example](.env.example)** - Configuration template
