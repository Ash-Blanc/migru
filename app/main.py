import argparse
import os
import sys
import warnings
from datetime import datetime
from typing import Any

# Suppress pkg_resources deprecation warning from fs package
warnings.filterwarnings("ignore", category=UserWarning, module="fs")

# Prompt Toolkit imports for advanced CLI
from prompt_toolkit import PromptSession  # noqa: E402
from prompt_toolkit.completion import Completer  # noqa: E402
from prompt_toolkit.completion import WordCompleter  # noqa: E402
from prompt_toolkit.document import Document  # noqa: E402
from prompt_toolkit.formatted_text import HTML  # noqa: E402
from prompt_toolkit.key_binding import KeyBindings  # noqa: E402
from prompt_toolkit.shortcuts import CompleteStyle  # noqa: E402
from prompt_toolkit.styles import Style as PTStyle  # noqa: E402
from rich import box  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.console import Group  # noqa: E402
from rich.live import Live  # noqa: E402
from rich.markdown import Markdown  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.table import Table  # noqa: E402

from app.config import config  # noqa: E402
from app.exceptions import MigruError  # noqa: E402
from app.logger import get_logger  # noqa: E402
from app.logger import suppress_verbose_logging  # noqa: E402
from app.utils import memory_usage_decorator  # noqa: E402
from app.utils import performance_monitor  # noqa: E402
from app.utils import timing_decorator  # noqa: E402

# Suppress verbose logging from third-party libraries
suppress_verbose_logging()

logger = get_logger("migru.main")
console = Console()

# --- Advanced UI Components ---

class CommandPalette:
    """Fuzzy-searchable command palette."""

    def __init__(self):
        self.commands = [
            "/help", "/exit", "/clear", "/settings", "/about",
            "/history", "/profile", "/patterns", "/model", "/bio"
        ]
        self.base_completer = WordCompleter(self.commands, ignore_case=True)

    def get_completer(self):
        return self._ConditionalCompleter(self.base_completer)

    class _ConditionalCompleter(Completer):
        def __init__(self, completer: Completer):
            self.completer = completer

        def get_completions(self, document: Document, complete_event: Any):
            if document.text.startswith("/"):
                yield from self.completer.get_completions(document, complete_event)

class SafePromptSession:
    """Wrapper for prompt_toolkit session with custom styling."""

    def __init__(self, completer: Completer | None = None):
        self.style = PTStyle.from_dict({
            'prompt': config.UI.THEME['prompt'],
            'input': config.UI.THEME['input'],
            'toolbar': config.UI.THEME['toolbar'],
        })
        self.bindings = KeyBindings()
        self.completer = completer

        @self.bindings.add('c-c')
        def _(event):
            event.app.exit(result="exit")

    def prompt(self, message: str) -> str:
        session = PromptSession(
            style=self.style,
            key_bindings=self.bindings,
            completer=self.completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        return session.prompt(HTML(message))

# --- End UI Components ---

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
            box=box.ROUNDED,
            padding=(0, 1),
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
            "[italic cyan]Type your thoughts or use '/' for commands[/italic cyan]",
            title="[bold magenta]🌸 A Gentle Space[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED,
            padding=(0, 1),
        )
        console.print(welcome_panel)
        console.print()

    performance_monitor.end_timer("banner_display")


def run_onboarding(user_name: str, console: Console, prompt_session: SafePromptSession, personalization_engine: Any) -> None:
    """Run a gentle onboarding wizard for new users."""
    try:
        profile = personalization_engine.get_user_profile(user_name).get_profile()
        if profile.get("metadata", {}).get("onboarding_completed", False):
            return

        console.print()
        console.print(Panel(
            f"[bold white]Hi {user_name}, I'm glad you're here.[/bold white]\n\n"
            "[dim]To help me support you best, I'd love to ask just two quick questions.[/dim]",
            title="[bold cyan]✨ Getting Started[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        ))
        console.print()

        # Question 1: Goal
        console.print("[bold cyan]1.[/bold cyan] What primarily brings you here today?")
        console.print("[dim](e.g., Managing migraines, Reducing stress, Curiosity)[/dim]")
        goal = prompt_session.prompt("   > ")

        # Question 2: Sensitivities
        console.print()
        console.print("[bold cyan]2.[/bold cyan] Is there anything specific that tends to trigger discomfort for you?")
        console.print("[dim](e.g., bright lights, loud noises, weather changes, none)[/dim]")
        triggers = prompt_session.prompt("   > ")

        # Save insights
        from app.services.user_insights import insight_extractor

        # Process goal
        if goal:
            # Extract insights from the goal text
            insights = insight_extractor.extract_from_message(user_name, goal)
            if insights:
                insight_extractor.update_user_profile_from_insights(user_name, insights)
            
            # Also store raw goal if not captured
            # (In a real app, we might have a specific 'goals' field, but we'll leverage 'interests' for now)
            # insight_extractor.update_user_profile_from_insights(user_name, {"interests": [goal]})

        # Process triggers
        if triggers:
            # Manual mapping for robustness + NLP extraction
            sensitivities = {}
            t_lower = triggers.lower()
            if "light" in t_lower or "bright" in t_lower:
                sensitivities["light_sensitive"] = True
            if "noise" in t_lower or "loud" in t_lower:
                sensitivities["noise_sensitive"] = True
            if "weather" in t_lower or "pressure" in t_lower:
                sensitivities["weather_sensitive"] = True

            if sensitivities:
                insight_extractor.update_user_profile_from_insights(
                    user_name, {"sensitivities": {"sensitivities": sensitivities}} # Nested to match structure if needed, or flat
                )
                # Actually extract_from_message returns flat "sensitivities" dict key, but update expects structure
                # Let's trust extract_from_message mainly, but manual update:
                
                # Re-reading user_insights.py: update_user_profile_from_insights takes dict with keys like "sensitivities"
                # which maps to the inner dict. 
                # So passing {"sensitivities": {"weather_sensitive": True}} is correct.
                # My manual mapping above created a flat dict 'sensitivities'. 
                # The update function expects: if "sensitivities" in insights -> update profile["sensitivities"]
                
                # Let's just use the update method directly with correct structure
                current_profile = personalization_engine.get_user_profile(user_name).get_profile()
                sens_update = {}
                if "light_sensitive" in sensitivities:
                    sens_update["light_sensitivity"] = "high"
                if "noise_sensitive" in sensitivities:
                    sens_update["noise_sensitivity"] = "high"
                if "weather_sensitive" in sensitivities:
                    sens_update["weather_sensitivity"] = "high"
                
                if sens_update:
                     # Safe merge with existing sensitivities
                     current_sensitivities = current_profile.get("sensitivities", {})
                     current_sensitivities.update(sens_update)
                     personalization_engine.get_user_profile(user_name).update_profile({"sensitivities": current_sensitivities})


            # Also run extraction
            more_insights = insight_extractor.extract_from_message(user_name, triggers)
            if more_insights:
                insight_extractor.update_user_profile_from_insights(user_name, more_insights)

        # Mark as complete
        profile = personalization_engine.get_user_profile(user_name).get_profile() # Reload
        profile["metadata"]["onboarding_completed"] = True
        personalization_engine.get_user_profile(user_name).update_profile(profile)

        console.print()
        console.print("[italic green]Thank you. I'll keep that in mind.[/italic green]")
        console.print()

    except Exception as e:
        logger.error(f"Onboarding failed: {e}")
        # Don't crash, just continue to main chat


def run_cli_session(user_name: str = "Friend", team: Any = None, system_name: str = "Mistral AI") -> bool:
    """Run an improved CLI session with better UX."""
    performance_monitor.start_timer("cli_session")

    # Lazy load heavy dependencies
    # Fallback teams
    from app.agents import create_migru_agent
    from app.agents import cerebras_team as fallback_team_1
    from app.agents import openrouter_team as fallback_team_2
    from app.agents import personalization_engine
    from app.agents import relief_team
    from app.agents import research_agent  # Import research agent
    from app.services.realtime_analytics import insight_generator
    from app.services.realtime_analytics import pattern_detector
    from app.services.user_insights import insight_extractor
    from app.streaming import process_message_for_streaming

    if team is None:
        team = relief_team

    # Initialize UI components
    command_palette = CommandPalette()
    prompt_session = SafePromptSession(completer=command_palette.get_completer())

    # --- Onboarding ---
    run_onboarding(user_name, console, prompt_session, personalization_engine)

    # --- Command Handlers ---
    def show_profile(user_name: str) -> None:
        try:
            profile = personalization_engine.get_user_profile(user_name).get_profile()

            # Create a table for the profile
            table = Table(title=f"User Profile: {user_name}", box=box.ROUNDED, show_header=True, header_style="bold magenta")
            table.add_column("Category", style="cyan")
            table.add_column("Details", style="white")

            # Flatten and add rows
            for category, data in profile.items():
                if isinstance(data, dict):
                    details = "\n".join([f"[bold]{k}:[/bold] {v}" for k, v in data.items() if v])
                    if details:
                        table.add_row(category.replace("_", " ").title(), details)
                        table.add_section()

            console.print(table)
        except Exception as e:
            console.print(f"[red]Could not load profile: {e}[/red]")

    def show_patterns(user_name: str) -> None:
        try:
            temporal = pattern_detector.get_temporal_patterns(user_name)
            environmental = pattern_detector.get_environmental_correlations(user_name)

            if not temporal and not environmental:
                console.print(Panel("No patterns detected yet. Keep chatting!", title="Patterns", border_style="cyan", box=box.ROUNDED, padding=(0, 1)))
                return

            grid = Table.grid(expand=True, padding=(0, 2))
            grid.add_column()

            if temporal:
                # Create a simple ASCII bar chart for hourly distribution
                hourly_dist = temporal.get("hourly_distribution", {})
                if hourly_dist:
                    chart_table = Table(title="Daily Symptom Rhythm", box=None, show_header=False, padding=(0, 1))
                    chart_table.add_column("Hour", justify="right", style="dim white")
                    chart_table.add_column("Intensity", width=40)

                    max_count = max(hourly_dist.values()) if hourly_dist else 1

                    for i in range(0, 24):
                        count = hourly_dist.get(i, 0)
                        if count > 0:
                            bar_len = int((count / max_count) * 20)
                            bar = "█" * bar_len
                            # Color based on intensity
                            color = "green" if bar_len < 5 else "yellow" if bar_len < 10 else "red"
                            time_label = f"{i:02d}:00"
                            chart_table.add_row(time_label, f"[{color}]{bar}[/{color}] ({count})")

                    grid.add_row(chart_table)
                    grid.add_row("") # Spacer

                t_table = Table(title="Temporal Insights", box=box.ROUNDED, show_edge=False)
                t_table.add_column("Metric")
                t_table.add_column("Value")
                peak_hour = temporal.get("peak_hour")
                peak_str = f"{peak_hour:02d}:00 - {peak_hour+1:02d}:00" if peak_hour is not None else "N/A"

                t_table.add_row("Peak Hour", peak_str)
                t_table.add_row("Pattern Strength", str(temporal.get("peak_count", 0)))
                grid.add_row(t_table)

            if environmental:
                e_table = Table(title="Environmental Correlations", box=box.ROUNDED, show_edge=False)
                e_table.add_column("Metric")
                e_table.add_column("Value")
                e_table.add_row("Weather Sensitivity", str(environmental.get("weather_sensitivity")))
                e_table.add_row("Correlation Strength", f"{environmental.get('correlation_strength', 0):.2f}")
                grid.add_row(e_table)

            console.print(Panel(grid, title=f"Patterns for {user_name}", border_style="magenta", box=box.ROUNDED, padding=(0, 1)))

        except Exception as e:
            console.print(f"[red]Could not load patterns: {e}[/red]")

    def show_history(user_name: str) -> None:
        try:
            from app.memory import memory_manager
            memories = memory_manager.get_user_memories(user_name)

            if not memories:
                console.print(Panel("No memories found.", title="History", border_style="cyan", box=box.ROUNDED, padding=(0, 1)))
                return

            table = Table(title=f"Memories & Insights: {user_name}", box=box.ROUNDED)
            table.add_column("Memory", style="white")
            table.add_column("Topics", style="dim cyan")

            for mem in memories[-10:]: # Show last 10
                topics = ", ".join(mem.topics) if mem.topics else "-"
                table.add_row(mem.memory, topics)

            console.print(table)
        except Exception as e:
            console.print(f"[red]Could not load history: {e}[/red]")

    def show_about() -> None:
        from redis import Redis
        redis_status = "[bold green]Online[/bold green]"
        try:
            client = Redis.from_url(config.REDIS_URL)
            if not client.ping():
                redis_status = "[bold red]Offline[/bold red]"
        except Exception:
            redis_status = "[bold red]Offline[/bold red]"

        about_grid = Table.grid(expand=True, padding=(0, 1))
        about_grid.add_column(style="cyan", justify="right")
        about_grid.add_column(style="white")
        about_grid.add_row("Version", "1.0.0")
        about_grid.add_row("Framework", "Agno AI")
        about_grid.add_row("Database", f"Redis ({redis_status})")
        about_grid.add_row("Mission", "Wise companion for migraine and stress support")

        console.print(Panel(about_grid, title="🌸 About Migru", border_style="magenta", box=box.ROUNDED, padding=(0, 1)))

    def show_settings() -> None:
        settings_grid = Table.grid(expand=True, padding=(0, 1))
        settings_grid.add_column(style="cyan", justify="right")
        settings_grid.add_column(style="white")
        settings_grid.add_row("Model", getattr(team, "model", config.MODEL_PRIMARY))
        settings_grid.add_row("Streaming", "Enabled" if config.STREAMING else "Disabled")
        settings_grid.add_row("Team Mode", "Enabled" if config.USE_TEAM else "Disabled")
        settings_grid.add_row("User ID", user_name)

        console.print(Panel(settings_grid, title="⚙️ Settings", border_style="cyan", box=box.ROUNDED, padding=(0, 1)))

    def handle_model_switch(args: str) -> None:
        nonlocal team, system_name
        
        available_models = {
            "mistral": ("mistral:mistral-small-latest", "Mistral AI"),
            "cerebras": ("cerebras:llama3.1-8b", "Cerebras AI"),
            "openrouter": ("openrouter:arcee-ai/trinity-mini:free", "OpenRouter"),
        }

        if not args:
            # Show available models
            grid = Table.grid(expand=True, padding=(0, 1))
            grid.add_column(style="cyan", justify="right")
            grid.add_column(style="white")
            
            current_model = getattr(team, "model", "Unknown")
            
            for name, (model_id, _) in available_models.items():
                prefix = "✓ " if model_id == current_model else "  "
                grid.add_row(f"{prefix}{name}", model_id)
            
            console.print(Panel(
                grid, 
                title="🤖 Available Models", 
                subtitle="Use '/model <name>' to switch",
                border_style="cyan", 
                box=box.ROUNDED, 
                padding=(0, 1)
            ))
            return

        target = args.lower().strip()
        if target in available_models:
            model_id, new_system_name = available_models[target]
            try:
                console.print(f"[dim]🔄 Switching to {new_system_name}...[/dim]")
                # We use create_migru_agent to create a new agent with the requested model
                # This preserves the 'Direct Agent' preference unless team mode is explicitly on
                # TODO: Support switching team models if config.USE_TEAM is True
                team = create_migru_agent(model=model_id)
                system_name = new_system_name
                console.print(f"[green]✓ Switched to {new_system_name}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to switch model: {e}[/red]")
        else:
            console.print(f"[yellow]⚠️ Unknown model '{target}'. Available: {', '.join(available_models.keys())}[/yellow]")

    try:
        # Custom conversation loop with better UX
        conversation_count = 0

        while True:
            # Get user input with a calming prompt
            console.print()
            if conversation_count == 0:
                prompt_text = "<b>You</b> <style color='#555555'>✨</style> "
            else:
                prompt_text = "<b>You</b> <style color='#555555'>→</style> "

            try:
                user_input = prompt_session.prompt(prompt_text)
            except KeyboardInterrupt:
                user_input = "exit"

            # Handle exit commands
            # Constraint: "if a user query contains anywhere the word 'bye', then terminate session"
            if "bye" in user_input.lower() or user_input.lower() in ["exit", "quit", "goodbye"]:
                console.print()
                farewell = Panel(
                    f"[bold white]Thank you for sharing this time with me, {user_name}.[/bold white]\n\n"
                    "[dim]May you find comfort and clarity on your journey.[/dim]\n\n"
                    "[italic cyan]Take gentle care of yourself. 🌸[/italic cyan]",
                    title="[bold magenta]Until we meet again[/bold magenta]",
                    border_style="magenta",
                    box=box.ROUNDED,
                    padding=(0, 1),
                )
                console.print(farewell)
                console.print()
                break

            # Handle knowledge retrieval
            # Constraint: "if a user query contains anywhere the word 'define', trigger knowledge retrieval"
            if "define" in user_input.lower():
                console.print()
                with console.status("[dim italic]📚 Consulting the library...[/dim italic]", spinner=config.UI.SPINNER_STYLE):
                    try:
                        # Use the Research Agent for definition/knowledge tasks
                        response = research_agent.run(user_input, stream=config.STREAMING)
                    except Exception as e:
                         logger.error(f"Research agent failed: {e}")
                         response = "I apologize, I'm having trouble accessing my library right now."

                # Render response
                if response:
                    console.print()
                    content = ""
                    if hasattr(response, 'content'): # Handle non-streaming response object
                         content = response.content
                    else: # Handle streaming generator or string
                        for chunk in response:
                             if hasattr(chunk, "content") and chunk.content:
                                 content += chunk.content
                             elif isinstance(chunk, str):
                                 content += chunk
                    
                    console.print(Panel(
                        Markdown(content),
                        title="[bold cyan]📚 Knowledge Retrieval[/bold cyan]",
                        border_style="cyan",
                        box=box.ROUNDED,
                        padding=(0, 1),
                    ))
                continue # Skip the main chat loop for this turn

            # Handle help command
            if user_input.lower() in ["help", "?", "/help"]:
                help_grid = Table.grid(expand=True, padding=(0, 1))
                help_grid.add_column(style="cyan", justify="right")
                help_grid.add_column(style="white")

                help_grid.add_row("/model", "Switch between available AI models")
                help_grid.add_row("/profile", "View your learned profile & bio factors")
                help_grid.add_row("/patterns", "Explore your wellness rhythms")
                help_grid.add_row("/history", "See recent session memories")
                help_grid.add_row("/clear", "Clear the terminal screen")
                help_grid.add_row("/exit", "End our conversation")

                help_panel = Panel(
                    Group(
                        "\n[bold white]I'm here to walk alongside you. Share whatever is on your mind, or use these commands to explore what we've discovered together:[/bold white]\n",
                        help_grid,
                        "\n[dim italic]Type your thoughts directly to chat normally.[/dim italic]"
                    ),
                    title="[bold cyan]💡 Guidance[/bold cyan]",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(0, 1),
                )
                console.print(help_panel)
                continue

            if user_input.lower() in ["/profile", "profile"]:
                show_profile(user_name)
                continue

            if user_input.lower() in ["/patterns", "patterns"]:
                show_patterns(user_name)
                continue

            if user_input.lower() in ["/history", "history"]:
                show_history(user_name)
                continue

            if user_input.lower() in ["/about", "about"]:
                show_about()
                continue

            if user_input.lower() in ["/settings", "settings"]:
                show_settings()
                continue

            if user_input.lower().startswith("/model"):
                parts = user_input.split(" ", 1)
                args = parts[1] if len(parts) > 1 else ""
                handle_model_switch(args)
                continue

            if user_input.lower().startswith("/bio"):
                # Simulation command: /bio hr=110 sleep=60
                try:
                    parts = user_input.split()
                    data = {"heart_rate": 70, "sleep_score": 80, "step_count": 5000} # Defaults
                    
                    for part in parts[1:]:
                        if "=" in part:
                            key, val = part.split("=", 1)
                            if key == "hr": key = "heart_rate"
                            if key == "sleep": key = "sleep_score"
                            if key == "steps": key = "step_count"
                            if key in data:
                                data[key] = int(val)
                    
                    pattern_detector.record_biometric(
                        user_id=user_name,
                        heart_rate=data["heart_rate"],
                        sleep_score=data["sleep_score"],
                        step_count=data["step_count"]
                    )
                    
                    console.print(Panel(
                        f"Heart Rate: {data['heart_rate']} bpm\nSleep Score: {data['sleep_score']}\nSteps: {data['step_count']}",
                        title="[bold green]Biometric Signal Received[/bold green]",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                    
                    # If HR is high, trigger an immediate reaction from the agent?
                    # For now, just logging it. The Pathway stream will pick it up and generate alerts.
                    
                except Exception as e:
                    console.print(f"[red]Invalid bio format. Use: /bio hr=100 sleep=80[/red]")
                continue

            if user_input.lower() in ["/clear", "clear"]:
                console.clear()
                continue

            # Skip empty inputs
            if not user_input.strip():
                continue

            # Detect Mood & Update Context (Adaptive Persona)
            from app.services.context import context_manager
            detected_mood = context_manager.detect_mood(user_input)
            if detected_mood:
                context_manager.update_user_state(user_name, detected_mood=detected_mood)
                logger.debug(f"Adaptive Context: Detected mood '{detected_mood}'")

            # Show thinking indicator briefly
            console.print()
            response = None

            with console.status("[dim italic]🌸 Migru is reflecting...[/dim italic]", spinner=config.UI.SPINNER_STYLE):
                # Background processing (Insights & Patterns)
                # Moved inside status for better UX/Feedback
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

                try:
                    # Real-time streaming analytics (Pathway integration)
                    from app.streaming import live_monitor
                    event_type = live_monitor.extract_event_type(user_input)
                    metadata = {
                        "hour": datetime.now().hour,
                        "day_of_week": datetime.now().weekday(),
                    }
                    pattern_detector.record_event(
                        user_id=user_name,
                        event_type=event_type,
                        content=user_input,
                        metadata=metadata
                    )
                    process_message_for_streaming(user_name, user_input, metadata)
                except Exception as e:
                    logger.debug(f"Streaming analytics failed (non-critical): {e}")

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
                    try:
                        response = team.run(user_input, stream=config.STREAMING, user_id=user_name)
                    except Exception as e:
                        error_str = str(e)
                        if "400" in error_str and ("context_length_exceeded" in error_str or "limit is" in error_str):
                            logger.warning("Context length exceeded with primary model. Switching to fallback.")
                            # Try fallback team 1
                            if fallback_team_1 and fallback_team_1 != team:
                                logger.info("Using Fallback Team 1")
                                response = fallback_team_1.run(user_input, stream=config.STREAMING)
                            elif fallback_team_2 and fallback_team_2 != team:
                                logger.info("Using Fallback Team 2")
                                response = fallback_team_2.run(user_input, stream=config.STREAMING)
                            else:
                                raise e # Re-raise if no fallback
                        else:
                            raise e

                except Exception as e:
                    logger.error(f"Error during conversation: {e}")
                    console.print()
                    console.print(
                        "[yellow]⚠️  I'm having trouble connecting right now. Let's try that again.[/yellow]"
                    )
                    continue

            if response:
                try:
                    # Display response in a beautiful panel using Live for smooth updates
                    console.print()

                    content = ""
                    # Initial empty panel
                    response_panel = Panel(
                        Markdown(""),
                        title="[bold magenta]🌸 Migru[/bold magenta]",
                        subtitle=f"[dim]{system_name}[/dim]",
                        border_style="magenta",
                        box=box.ROUNDED,
                        padding=(0, 1),
                    )

                    from types import GeneratorType
                    if isinstance(response, GeneratorType):
                        with Live(response_panel, console=console, refresh_per_second=config.UI.REFRESH_RATE) as live:
                            for chunk in response:
                                chunk_text = ""
                                if hasattr(chunk, "content") and chunk.content:
                                    chunk_text = chunk.content
                                elif isinstance(chunk, str):
                                    chunk_text = chunk

                                content += chunk_text
                                # Update the panel content
                                live.update(Panel(
                                    Markdown(content),
                                    title="[bold magenta]🌸 Migru[/bold magenta]",
                                    subtitle=f"[dim]{system_name}[/dim]",
                                    border_style="magenta",
                                    box=box.ROUNDED,
                                    padding=(0, 1),
                                ))
                    elif hasattr(response, 'content'):
                        # Non-streaming response object
                        console.print(Panel(
                            Markdown(response.content),
                            title="[bold magenta]🌸 Migru[/bold magenta]",
                            subtitle=f"[dim]{system_name}[/dim]",
                            border_style="magenta",
                            box=box.ROUNDED,
                            padding=(0, 1),
                        ))
                    else:
                        # Fallback for string or other types
                        console.print(Panel(
                            Markdown(str(response)),
                            title="[bold magenta]🌸 Migru[/bold magenta]",
                            subtitle=f"[dim]{system_name}[/dim]",
                            border_style="magenta",
                            box=box.ROUNDED,
                            padding=(0, 1),
                        ))

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
                                        box=box.ROUNDED,
                                        padding=(0, 1),
                                    )
                                    console.print(insight_panel)
                                    insight_generator.mark_insight_shared(user_name)
                                    break  # Only share one insight at a time
                        except Exception as e:
                            logger.debug(f"Proactive insight sharing failed: {e}")
                except Exception as e:
                    logger.error(f"Error during response rendering: {e}")
                    console.print()
                    console.print("[yellow]⚠️  Something went wrong while displaying the response.[/yellow]")
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
        # Ensure Redis is running BEFORE importing agents that might use it on initialization
        logger.info("Checking Redis connection...")
        from app.db import ensure_redis_running

        if not ensure_redis_running():
            # Suppress user-facing warning to keep CLI clean as requested
            # console.print(
            #     "[yellow]⚠️  Warning: Redis is not available. Memory features will be limited.[/yellow]"
            # )
            logger.debug("Redis not available")

        # Lazy load agent teams for display
        from app.agents import cerebras_team
        from app.agents import openrouter_team
        from app.agents import relief_team

        # Re-apply suppression after imports to catch new loggers
        if not (args and hasattr(args, "verbose") and args.verbose):
             suppress_verbose_logging()

        # Handle Accessibility Mode
        if args and hasattr(args, "accessible") and args.accessible:
            config.ACCESSIBILITY_MODE = True
            config.UI.REFRESH_RATE = 1  # Minimal updates
            config.UI.SPINNER_STYLE = "simpleDots" # Simpler spinner
            config.UI.THEME = {
                'prompt': 'bold white',
                'input': 'white',
                'toolbar': 'white italic',
                'panel_border': 'white',
                'title': 'bold white',
            }
            logger.info("Accessibility mode enabled")

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
                box=box.ROUNDED,
                padding=(0, 1),
            )
            console.print(systems_panel)

        # Primary execution loop with improved fallback UX
        user_name = getattr(args, "user", "Friend") if args else "Friend"

        # Optimized startup messages based on configuration
        if config.USE_TEAM:
            primary_name = "Mistral AI Team"
            fallback_name = "Cerebras AI Team"
        else:
            primary_name = "Mistral AI"
            if config.CEREBRAS_API_KEY:
                fallback_name = "Cerebras AI (Ultra-fast)"
            else:
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
            box=box.ROUNDED,
            padding=(0, 1),
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
            box=box.ROUNDED,
            padding=(0, 1),
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
        "--accessible",
        "-a",
        action="store_true",
        help="Enable accessibility mode (reduced motion, high contrast)",
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
        # Force all migru loggers to INFO
        logging.getLogger("migru").setLevel(logging.INFO)
        logging.getLogger("app").setLevel(logging.INFO)
        # Also ensure handlers of the root logger or specific loggers are updated if needed
        # but our get_logger already sets level on the logger instance.
    else:
        # Extra insurance to keep things quiet
        import logging
        logging.basicConfig(level=logging.CRITICAL) # Suppress root logger
        suppress_verbose_logging()

    run_app(args)


if __name__ == "__main__":
    main()
