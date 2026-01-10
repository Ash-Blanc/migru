import os
import sys
from app.config import config
from app.agents import relief_team, fallback_team
from app.logger import get_logger
from app.exceptions import MigruError

logger = get_logger("migru.main")

def run_app():
    try:
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
            
        print("\n👋 Hey! I'm Migru, your cheerful buddy. Let's chat!")
        print("Type 'exit' to end, 'bye' to say goodbye.\n")
        
        # Determine which team to run
        active_team = relief_team
        
        # NOTE: Agno's cli_app is an interactive loop. We cannot easily wrap individual turns
        # for fallback within the CLI app itself without overriding the app logic.
        # However, we can choose to start the fallback team if the primary fails to init 
        # or if explicitly requested.
        # Ideally, we'd use a custom loop to handle per-turn fallback, but sticking to CLI app:
        
        try:
            active_team.cli_app(
                user="Friend",
                emoji="🌸",
                stream=True,
            )
        except Exception as e:
            logger.error(f"Primary team crashed: {e}")
            if fallback_team:
                print("\n⚠️  Primary system unavailable. Switching to Backup (Cerebras)...")
                logger.warning("Switching to Cerebras fallback team.")
                fallback_team.cli_app(
                    user="Friend",
                    emoji="⚡", # Different emoji to indicate fallback
                    stream=True,
                )
            else:
                print("No fallback available. Exiting.")
                raise e

    except KeyboardInterrupt:
        print("\nSee you later! Take care! 🌸")
        logger.info("Application stopped by user.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        print(f"\nOops! Something went wrong. Check the logs for details.")

if __name__ == "__main__":
    run_app()
