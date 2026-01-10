# Migru

Migru is a warm, AI-powered companion designed to support you through migraines and stress with empathy and research-backed relief strategies.

## Setup

### Prerequisites

-   Python 3.12+ (if running locally)
-   [uv](https://astral.sh/uv) (recommended package manager)
-   Redis (running locally or accessible via URL)
-   Docker (optional, for containerized run)

### Configuration

The setup script creates a `.env` file for your API keys. You'll need to fill this in:

1.  **Mistral API Key**: Required for the AI personality.
    *   Get it here: [Mistral AI Console](https://console.mistral.ai/api-keys/)
2.  **Firecrawl API Key**: Required for web research capabilities.
    *   Get it here: [Firecrawl](https://www.firecrawl.dev/)
3.  **Redis**: The app uses Redis for memory.
    *   Ensure you have a local Redis instance running (`redis-server`), or update the `REDIS_URL` in `.env` to point to a cloud instance.

### Automatic Setup

Run the setup script to install dependencies and create the configuration file:

```bash
./setup.sh
```

Open the `.env` file and paste your keys:
```env
MISTRAL_API_KEY=your_actual_key_here
FIRECRAWL_API_KEY=your_actual_key_here
```

## Running the Application

### Option 1: Run Locally

Start the application with `uv`:

```bash
uv run -m app.main
```

### Option 2: Run with Docker

To run the entire stack (App + Redis) using Docker Compose:

```bash
docker-compose up --build
```

This ensures a consistent environment and handles the database connection automatically.

## Architecture

-   **Framework**: Agno
-   **Agents**:
    -   **Migru**: The empathetic frontend companion (Mistral Small).
    -   **Relief Researcher**: The tool-using backend researcher (Mistral Medium).
-   **Memory**: Redis-backed persistent memory and cultural context.
-   **Tools**: Firecrawl (web scraping), DuckDuckGo (search), YouTube.

## Troubleshooting

-   **Redis Connection Error**: Ensure Redis is running on port 6379 or your `REDIS_URL` is correct.
-   **API Key Errors**: Double-check your `.env` file.
