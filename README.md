# Migru

Welcome to Migru! Follow these simple steps to get started.

## How to Start

First, run this command to set everything up automatically:

```bash
./setup.sh
```

This will check for necessary tools and install them for you.

## Configuration

The setup script creates a `.env` file for your API keys. You'll need to fill this in:

1.  **Mistral API Key**: Required for the AI personality.
    *   Get it here: [Mistral AI Console](https://console.mistral.ai/api-keys/)
2.  **Firecrawl API Key**: Required for web research capabilities.
    *   Get it here: [Firecrawl](https://www.firecrawl.dev/)
3.  **Redis**: The app uses Redis for memory.
    *   Ensure you have a local Redis instance running (`redis-server`), or update the `REDIS_URL` in `.env` to point to a cloud instance.

Open the `.env` file and paste your keys:
```env
MISTRAL_API_KEY=your_actual_key_here
FIRECRAWL_API_KEY=your_actual_key_here
```

## Run the App

Once the setup is done, you can start the application with:

```bash
uv run -m app.main
```

That's it!