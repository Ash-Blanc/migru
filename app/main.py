import os
import sys
from app.config import config
from app.agents import relief_team
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
        
        # Set environment variables for libraries that expect them
        if config.FIRECRAWL_API_KEY:
            os.environ["FIRECRAWL_API_KEY"] = config.FIRECRAWL_API_KEY
        if config.MISTRAL_API_KEY:
            os.environ["MISTRAL_API_KEY"] = config.MISTRAL_API_KEY
            
        print("\n👋 Hey! I'm Migru, your cheerful buddy. Let's chat!")
        print("Type 'exit' to end, 'bye' to say goodbye.\n")
        
        # We start the CLI app. 
        # Note: In a real deployment, we might run this as a service, 
        # but for this interactive CLI tool, we hand control to the agent.
        relief_team.cli_app(
            user="Friend",
            emoji="🌸",
            stream=True,
        )
        
    except KeyboardInterrupt:
        print("\nSee you later! Take care! 🌸")
        logger.info("Application stopped by user.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        print(f"\nOops! Something went wrong. Check the logs for details.")

if __name__ == "__main__":
    run_app()