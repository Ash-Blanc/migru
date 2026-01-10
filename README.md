# Migru

Migru is a warm, AI-powered companion designed to support you through migraines and stress with empathy and research-backed relief strategies.

## 🚀 Quick Start (Recommended)

The easiest way to get started.

**1. Setup (One-Liner)**
Run this script to automatically install tools (`uv`), dependencies, and create your config file:
```bash
./setup.sh
```

**2. Add Keys**
Open the newly created `.env` file and add your keys:
```env
MISTRAL_API_KEY=...    # Get from https://console.mistral.ai/
FIRECRAWL_API_KEY=...  # Get from https://www.firecrawl.dev/
OPENWEATHER_API_KEY=... # Get from https://openweathermap.org/api
CEREBRAS_API_KEY=...    # Optional: High-speed fallback (https://cerebras.ai)
OPENROUTER_API_KEY=...  # Optional: Multi-model fallback (https://openrouter.ai)
```

**3. Run**
```bash
uv run -m app.main
```

---

## 🐳 Docker Setup (Advanced)

For users who prefer containerization. This handles the Application and Redis database automatically.

**1. Configure**
Create your environment file:
```bash
cp .env.example .env
# Edit .env and add your API keys now
```

**2. Build & Run**
```bash
docker-compose up --build
```

---

## Architecture & Troubleshooting

### Stack
-   **Framework**: Agno
-   **Agents**: Migru (Companion) & Relief Researcher (Web/Data)
-   **Memory**: Redis (Persistent user bio-data & context)
-   **Tools**: Firecrawl, DuckDuckGo, YouTube

### Common Issues
-   **Redis Connection**: 
    -   *Local Mode*: The app attempts to start `redis-server` automatically. If it fails, ensure Redis is installed on your system.
    -   *Docker Mode*: Handled automatically by Docker Compose.
-   **API Key Errors**: Ensure your `.env` file is saved and contains valid keys (no quotes needed around values).