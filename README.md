# Migru

Migru is a warm, AI-powered companion designed to support you through migraines and stress with empathy and research-backed relief strategies. It combines ultra-fast responses with deep, personalized wisdom.

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

### 1. Automatic Setup (Recommended)
Run the setup script to install dependencies and create your configuration:
```bash
./setup.sh
```

### 2. Configure Environment
Edit the generated `.env` file with your API keys:
```env
MISTRAL_API_KEY=...     # Primary Intelligence
FIRECRAWL_API_KEY=...   # Deep Research
OPENWEATHER_API_KEY=... # Environmental Context
CEREBRAS_API_KEY=...    # Ultra-Fast Responses (Recommended)
```

---

## 💻 Usage & Commands

Migru is primarily a CLI application. Here is how to use it effectively.

### Basic Start
Launch the default interactive session:
```bash
uv run -m app.main
```

### Custom User Profile
Start with a specific user context (loads your personal history/patterns):
```bash
uv run -m app.main --user "Alex"
```

### Accessibility Mode
Launch with high-contrast UI and reduced motion/animations:
```bash
uv run -m app.main --accessible
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

## 🐳 Docker Usage

Run the full stack (App + Redis) in a container:

```bash
# 1. Create config
cp .env.example .env

# 2. Build and Run
docker-compose up --build
```

---

## 🏗️ Architecture Highlights

*   **Adaptive Context**: Automatically adjusts persona (calm vs. energetic) based on your detected mood.
*   **Data Fusion**: Correlates chat logs with simulated biometric streams using **Pathway**.
*   **Redis Pipelining**: Atomic, low-latency updates for real-time pattern tracking.
*   **Dynamic Routing**: Intelligently switches between "Fast" (Cerebras) and "Smart" (Mistral) models based on query complexity.

For deep performance tuning, see [PERFORMANCE.md](PERFORMANCE.md).
