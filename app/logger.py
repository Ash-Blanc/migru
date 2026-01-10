import logging
import sys
from app.config import config

def get_logger(name: str):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.WARNING)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
    return logger


def suppress_verbose_logging():
    """Suppress verbose logging from third-party libraries and Agno tools."""
    # Suppress Agno's verbose tool execution logs
    logging.getLogger("agno.tools").setLevel(logging.ERROR)
    logging.getLogger("agno.agent").setLevel(logging.ERROR)
    logging.getLogger("agno.team").setLevel(logging.ERROR)
    
    # Suppress third-party library logs
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("ddgs").setLevel(logging.ERROR)
    logging.getLogger("firecrawl").setLevel(logging.ERROR)
    
    # Suppress all function execution warnings
    logging.getLogger("agno.tools.function").setLevel(logging.CRITICAL)
    
    # Keep only critical errors visible
    logging.getLogger().setLevel(logging.ERROR)
