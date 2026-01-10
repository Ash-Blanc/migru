import os
import sys
from app.config import config
from app.agents import relief_team, cerebras_team, openrouter_team
from app.logger import get_logger
from app.exceptions import MigruError

logger = get_logger("migru.main")

def run_app():
    try:
        # Ensure Redis is running for memory storage
        from app.db import ensure_redis_running
        ensure_redis_running()
        
        # Validate configuration
        try:
            config.validate()
        except MigruError as e:
            logger.error(f"Configuration Error: {e}")
            sys.exit(1)
        
        # Set environment variables
        if config.FIRECRAWL_API_KEY:
            os.environ["FIRECRAWL_API_KEY"] = config.FIRECRAWL_API_KEY
        if config.MISTRAL_API_KEY:
            os.environ["MISTRAL_API_KEY"] = config.MISTRAL_API_KEY
        if config.OPENWEATHER_API_KEY:
            os.environ["OPENWEATHER_API_KEY"] = config.OPENWEATHER_API_KEY
        if config.CEREBRAS_API_KEY:
            os.environ["CEREBRAS_API_KEY"] = config.CEREBRAS_API_KEY
        if config.OPENROUTER_API_KEY:
            os.environ["OPENROUTER_API_KEY"] = config.OPENROUTER_API_KEY
            
        print("\n👋 Hey! I'm Migru, your cheerful buddy. Let's chat!")
        print("Type 'exit' to end, 'bye' to say goodbye.\n")
        
        # Primary execution loop with multi-tier fallback
        try:
            relief_team.cli_app(user="Friend", emoji="🌸", stream=True)
        except Exception as e:
            logger.error(f"Primary team (Mistral) failed: {e}")
            
            # Tier 2: Cerebras
            if cerebras_team:
                print("\n⚠️  Primary system down. Switching to Backup Tier 1 (Cerebras)...")
                try:
                    cerebras_team.cli_app(user="Friend", emoji="⚡", stream=True)
                except Exception as e2:
                    logger.error(f"Backup Tier 1 (Cerebras) failed: {e2}")
                    
                    # Tier 3: OpenRouter
                    if openrouter_team:
                        print("\n⚠️  Secondary system down. Switching to Backup Tier 2 (OpenRouter)...")
                        openrouter_team.cli_app(user="Friend", emoji="🌐", stream=True)
                    else:
                        print("No more fallbacks available.")
                        raise e2
            elif openrouter_team:
                # Direct to Tier 3 if Tier 2 not configured
                print("\n⚠️  Primary system down. Switching to Backup (OpenRouter)...")
                openrouter_team.cli_app(user="Friend", emoji="🌐", stream=True)
            else:
                print("No fallbacks configured.")
                raise e

    except KeyboardInterrupt:
        print("\nSee you later! Take care! 🌸")
        logger.info("Application stopped by user.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        print(f"\nOops! Something went wrong. Check the logs for details.")

if __name__ == "__main__":
    run_app()