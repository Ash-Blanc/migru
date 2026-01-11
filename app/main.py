import argparse
import os
import sys
import warnings
from datetime import datetime
from typing import Any

# Suppress pkg_resources deprecation warning from fs package
warnings.filterwarnings("ignore", category=UserWarning, module="fs")

from rich.console import Console  # noqa: E402
from rich.markdown import Markdown  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.prompt import Prompt  # noqa: E402

from app.config import config  # noqa: E402
from app.exceptions import MigruError  # noqa: E402
from app.logger import get_logger, suppress_verbose_logging  # noqa: E402
from app.utils import (  # noqa: E402
    memory_usage_decorator,
    performance_monitor,
    timing_decorator,
)

# Suppress verbose logging from third-party libraries
suppress_verbose_logging()

logger = get_logger("migru.main")
console = Console()


def setup_environment() -> bool:
    """Setup environment variables and validate configuration."""
    performance_monitor.start_timer("environment_setup")

    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
    except MigruError as e:
        logger.error(f"Configuration Error: {e}")
        error_panel = Panel(
            f"[bold red]Configuration Error:[/bold red]\n\n"
            f"[white]{e}[/white]\n\n"
            "[dim]Please check your .env file and ensure all required API keys are set.[/dim]",
            title="[bold red]❌ Setup Failed[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)
        return False

    # Set environment variables
    env_vars = {
        "FIRECRAWL_API_KEY": config.FIRECRAWL_API_KEY,
        "MISTRAL_API_KEY": config.MISTRAL_API_KEY,
        "OPENWEATHER_API_KEY": config.OPENWEATHER_API_KEY,
        "CEREBRAS_API_KEY": config.CEREBRAS_API_KEY,
        "OPENROUTER_API_KEY": config.OPENROUTER_API_KEY,
    }

    for key, value in env_vars.items():
        if value:
            os.environ[key] = value
            logger.debug(f"Set {key}")
        else:
            logger.warning(f"{key} not configured")

    performance_monitor.end_timer("environment_setup")
    return True


def display_banner(show_welcome: bool = True) -> None:
    """Display ASCII art banner and welcome message."""
    performance_monitor.start_timer("banner_display")

    console.print()
    try:
        with open("app/ascii-text-art.txt") as f:
            banner = f.read().strip()
            console.print(f"[bold cyan]{banner}[/bold cyan]")
    except FileNotFoundError:
        logger.debug("Banner file not found, skipping")
        console.print("[bold cyan]MIGRU[/bold cyan]", justify="center")

    if show_welcome:
        console.print()
        welcome_panel = Panel(
            "[bold white]Welcome! I'm Migru, your wise and curious companion.[/bold white]\n\n"
            "[dim]I'm here to walk alongside you, exploring what brings comfort and clarity.\n"
            "Let's discover together what works for you.[/dim]\n\n"
            "[italic cyan]💭 Type your thoughts to begin our conversation\n"
            "🚪 Type 'exit' or press Ctrl+C to end[/italic cyan]",
            title="[bold magenta]🌸 A Gentle Space[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )
        console.print(welcome_panel)
        console.print()

    performance_monitor.end_timer("banner_display")


def run_cli_session(user_name: str = "Friend", team: Any = None, system_name: str = "Mistral AI") -> bool:
    """Run an improved CLI session with better UX."""
    performance_monitor.start_timer("cli_session")

    # Lazy load heavy dependencies
    from app.agents import personalization_engine, relief_team
    from app.services.realtime_analytics import insight_generator, pattern_detector
    from app.services.user_insights import insight_extractor
    from app.streaming import process_message_for_streaming

    if team is None:
        team = relief_team

    try:
        # Custom conversation loop with better UX
        conversation_count = 0

        while True:
            # Get user input with a calming prompt
            console.print()
            if conversation_count == 0:
                prompt_text = "[bold green]You[/bold green] [dim]✨[/dim]"
            else:
                prompt_text = "[bold green]You[/bold green] [dim]→[/dim]"

            user_input = Prompt.ask(prompt_text, console=console)

            # Handle exit commands
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                console.print()
                farewell = Panel(
                    f"[bold white]Thank you for sharing this time with me, {user_name}.[/bold white]\n\n"
                    "[dim]May you find comfort and clarity on your journey.[/dim]\n\n"
                    "[italic cyan]Take gentle care of yourself. 🌸[/italic cyan]",
                    title="[bold magenta]Until we meet again[/bold magenta]",
                    border_style="magenta",
                    padding=(1, 2),
                )
                console.print(farewell)
                console.print()
                break

            # Handle help command
            if user_input.lower() in ["help", "?"]:
                help_panel = Panel(
                    "[bold white]How to talk with Migru:[/bold white]\n\n"
                    "💭 Simply share what's on your mind - there's no wrong way to start\n"
                    "🔍 Ask questions about wellness, stress, or what might help\n"
                    "📖 Request research on techniques that interest you\n"
                    "🌤️  Mention how weather or environment affects you\n\n"
                    "[italic cyan]Commands:[/italic cyan]\n"
                    "  • [cyan]exit[/cyan], [cyan]quit[/cyan], [cyan]bye[/cyan] - End conversation\n"
                    "  • [cyan]help[/cyan], [cyan]?[/cyan] - Show this message",
                    title="[bold cyan]💡 Guidance[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2),
                )
                console.print(help_panel)
                continue

            # Skip empty inputs
            if not user_input.strip():
                continue

            # Extract insights from user message (background, non-blocking)
            try:
                insights = insight_extractor.extract_from_message(
                    user_id=user_name, message=user_input
                )
                if insights:
                    insight_extractor.update_user_profile_from_insights(
                        user_name, insights
                    )
            except Exception as e:
                logger.debug(f"Insight extraction failed (non-critical): {e}")

            # Real-time streaming analytics (Pathway integration)
            try:
                # Extract event type from message
                from app.streaming import live_monitor
                event_type = live_monitor.extract_event_type(user_input)

                # Get environmental context (weather, time, etc.)
                metadata = {
                    "hour": datetime.now().hour,
                    "day_of_week": datetime.now().weekday(),
                }

                # Try to get weather context if available
                # TODO: Implement a proper way to get weather data for analytics

                # Record to streaming analytics
                pattern_detector.record_event(
                    user_id=user_name,
                    event_type=event_type,
                    content=user_input,
                    metadata=metadata
                )

                # Process for Pathway streaming (low-latency)
                process_message_for_streaming(user_name, user_input, metadata)

            except Exception as e:
                logger.debug(f"Streaming analytics failed (non-critical): {e}")

            # Show thinking indicator briefly
            console.print()
            with console.status("[dim italic]🌸 Migru is reflecting...[/dim italic]", spinner="dots"):
                try:
                    # Get personalization context for this user
                    try:
                        user_context = personalization_engine.get_personalization_context(user_name)
                        if user_context and conversation_count > 0:
                            # Inject context for subsequent messages (not first)
                            logger.debug(f"Using personalized context for {user_name}")
                    except Exception as e:
                        logger.debug(f"Personalization context failed: {e}")

                    # Get response with streaming for better perceived speed
                    response = team.run(user_input, stream=config.STREAMING)

                    # Display response in a beautiful panel
                    console.print()

                    from types import GeneratorType
                    if isinstance(response, GeneratorType):
                        # Streaming response - show as it arrives
                        content = ""
                        # Create a placeholder panel that we'll update
                        with console.status("[dim]Generating response...[/dim]"):
                            for chunk in response:
                                if hasattr(chunk, "content") and chunk.content:
                                    content += chunk.content
                                elif isinstance(chunk, str):
                                    content += chunk

                        response_panel = Panel(
                            Markdown(content),
                            title="[bold magenta]🌸 Migru[/bold magenta]",
                            subtitle=f"[dim]{system_name}[/dim]",
                            border_style="magenta",
                            padding=(1, 2),
                        )
                        console.print(response_panel)
                    elif hasattr(response, 'content'):
                        # Non-streaming response object
                        response_panel = Panel(
                            Markdown(response.content),
                            title="[bold magenta]🌸 Migru[/bold magenta]",
                            subtitle=f"[dim]{system_name}[/dim]",
                            border_style="magenta",
                            padding=(1, 2),
                        )
                        console.print(response_panel)
                    else:
                        # Fallback for string or other types
                        response_panel = Panel(
                            Markdown(str(response)),
                            title="[bold magenta]🌸 Migru[/bold magenta]",
                            subtitle=f"[dim]{system_name}[/dim]",
                            border_style="magenta",
                            padding=(1, 2),
                        )
                        console.print(response_panel)

                    conversation_count += 1

                    # Check for proactive insights (every 3+ conversations)
                    if conversation_count >= 3 and conversation_count % 3 == 0:
                        try:
                            # Generate insights from patterns
                            proactive_insights = insight_generator.generate_insights(user_name)

                            # Share if appropriate
                            for insight in proactive_insights:
                                if insight_generator.should_share_now(user_name, insight):
                                    console.print()
                                    insight_panel = Panel(
                                        Markdown(
                                            f"**💡 A Pattern I've Noticed**\n\n{insight['message']}"
                                        ),
                                        title="[bold cyan]✨ Gentle Insight[/bold cyan]",
                                        subtitle="[dim]Discovered through our conversations[/dim]",
                                        border_style="cyan",
                                        padding=(1, 2),
                                    )
                                    console.print(insight_panel)
                                    insight_generator.mark_insight_shared(user_name)
                                    break  # Only share one insight at a time
                        except Exception as e:
                            logger.debug(f"Proactive insight sharing failed: {e}")
                except Exception as e:
                    logger.error(f"Error during conversation: {e}")
                    console.print()
                    console.print(
                        "[yellow]⚠️  I'm having trouble connecting right now. Let's try that again.[/yellow]"
                    )
                    continue

        performance_monitor.end_timer("cli_session")
        logger.info(f"Session ended by user: {user_name}")
        return True

    except KeyboardInterrupt:
        console.print()
        console.print("\n[dim]Session interrupted. Take care! 🌸[/dim]\n")
        logger.info(f"Session interrupted by user: {user_name}")
        performance_monitor.end_timer("cli_session")
        return True
    except Exception as e:
        logger.error(f"Session failed: {e}")
        console.print(f"\n[red]❌ Session error: {e}[/red]\n")
        performance_monitor.end_timer("cli_session")
        return False


@timing_decorator
@memory_usage_decorator
def run_app(args: argparse.Namespace | None = None) -> None:
    """Main application entry point with improved error handling and performance monitoring."""
    performance_monitor.start_timer("total_startup")

    try:
        # Lazy load agent teams for display
        from app.agents import cerebras_team, openrouter_team, relief_team

        # Ensure Redis is running for memory storage
        logger.info("Checking Redis connection...")
        from app.db import ensure_redis_running

        if not ensure_redis_running():
            console.print(
                "[yellow]⚠️  Warning: Redis is not available. Memory features will be limited.[/yellow]"
            )
            logger.warning("Redis not available")

        # Setup environment
        if not setup_environment():
            sys.exit(1)

        # Display banner (can be suppressed with --quiet flag)
        show_welcome = not (args and hasattr(args, "quiet") and args.quiet)
        display_banner(show_welcome)

        # Display available systems in a nice format
        systems = []
        if relief_team:
            systems.append("✓ Mistral AI (Primary)")
        if cerebras_team:
            systems.append("✓ Cerebras (High-speed backup)")
        if openrouter_team:
            systems.append("✓ OpenRouter (Emergency fallback)")

        if systems and show_welcome:
            systems_panel = Panel(
                "\n".join(f"[green]{s}[/green]" for s in systems),
                title="[bold cyan]🔧 Available Systems[/bold cyan]",
                border_style="cyan",
                padding=(0, 2),
            )
            console.print(systems_panel)

        # Primary execution loop with improved fallback UX
        user_name = getattr(args, "user", "Friend") if args else "Friend"

        # Optimized startup messages based on configuration
        if config.USE_TEAM:
            primary_name = "Mistral AI Team"
            fallback_name = "Cerebras AI Team"
        else:
            if config.CEREBRAS_API_KEY:
                primary_name = "Cerebras AI (Ultra-fast)"
                fallback_name = "Mistral AI (High-quality)"
            else:
                primary_name = "Mistral AI"
                fallback_name = "OpenRouter"

        # Try primary system
        if relief_team:
            if show_welcome:
                console.print(f"\n[dim]⚡ Connecting to {primary_name}...[/dim]\n")
            if run_cli_session(user_name, relief_team, primary_name):
                performance_monitor.end_timer("total_startup")
                return

        # Fallback to Tier 2
        if cerebras_team:
            console.print(
                f"\n[yellow]🔄 Switching to {fallback_name}...[/yellow]\n"
            )
            if run_cli_session(user_name, cerebras_team, fallback_name):
                performance_monitor.end_timer("total_startup")
                return

        # Fallback to Tier 3
        if openrouter_team:
            console.print(
                "\n[yellow]🌐 Using emergency backup (OpenRouter)...[/yellow]\n"
            )
            if run_cli_session(user_name, openrouter_team, "OpenRouter"):
                performance_monitor.end_timer("total_startup")
                return

        # No systems available
        error_panel = Panel(
            "[bold red]No AI systems are currently available.[/bold red]\n\n"
            "Please check your API configuration in the .env file:\n"
            "  • MISTRAL_API_KEY (required)\n"
            "  • CEREBRAS_API_KEY (optional backup)\n"
            "  • OPENROUTER_API_KEY (optional emergency)",
            title="[bold red]❌ Connection Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)
        logger.error("No AI systems available")

    except KeyboardInterrupt:
        console.print("\n[dim]👋 Session interrupted. Take care! 🌸[/dim]\n")
        logger.info("Application stopped by user during startup")
    except Exception as e:
        logger.exception(f"Unexpected error during startup: {e}")
        error_panel = Panel(
            f"[bold red]An unexpected error occurred:[/bold red]\n\n"
            f"[white]{e}[/white]\n\n"
            "[dim]Check the logs for detailed information.[/dim]",
            title="[bold red]❌ Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)
    finally:
        performance_monitor.end_timer("total_startup")

        # Print performance summary if verbose
        if args and hasattr(args, "verbose") and args.verbose:
            console.print("\n[bold cyan]Performance Metrics:[/bold cyan]")
            console.print(performance_monitor.get_report())


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Migru - Wise companion for wellness and relief",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run -m app.main                    # Start with default settings
  uv run -m app.main --user Alex        # Use custom username
  uv run -m app.main --quiet            # Skip welcome message
  uv run -m app.main --verbose          # Show performance metrics
        """,
    )

    parser.add_argument(
        "--user", "-u", default="Friend", help="Your preferred name (default: Friend)"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress welcome messages and banners",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed performance metrics and logs",
    )

    parser.add_argument("--version", action="version", version="Migru 0.1.0")

    return parser


def main() -> None:
    """Main entry point for Migru CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        import logging

        logging.getLogger("migru").setLevel(logging.INFO)
        logging.getLogger("app").setLevel(logging.INFO)

    run_app(args)


if __name__ == "__main__":
    main()
