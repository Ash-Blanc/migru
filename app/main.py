import os
from app.config import config
from app.agents import relief_team

def run_app():
    try:
        # Validate configuration
        config.validate()
        
        # Set environment variables for libraries that expect them
        if config.FIRECRAWL_API_KEY:
            os.environ["FIRECRAWL_API_KEY"] = config.FIRECRAWL_API_KEY
        if config.MISTRAL_API_KEY:
            os.environ["MISTRAL_API_KEY"] = config.MISTRAL_API_KEY
            
        print("👋 Hey! I'm Migru, your cheerful buddy. Let's chat!")
        print("Type 'exit' to end.\n")
        
        relief_team.cli_app(
            user="Friend",
            emoji="🌸",
            stream=True,
        )
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_app()

