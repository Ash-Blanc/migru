"""
CLI session helper functions - Simplified for new architecture.
Most CLI logic has been moved to app.main.TherapeuticCLI.
"""
from typing import Any, Tuple

from rich.console import Console
from rich.panel import Panel
from rich import box

from app.config import config
from app.logger import get_logger

logger = get_logger("migru.cli.session")


def run_onboarding(user_name: str, console: Console, prompt_session: Any, personalization_engine: Any) -> None:
    """
    Run a gentle onboarding wizard for new users.
    
    Note: This is a legacy function maintained for compatibility.
    The new architecture handles onboarding through the TherapeuticCLI.
    """
    try:
        profile = personalization_engine.get_user_profile(user_name).get_profile()
        if profile.get("metadata", {}).get("onboarding_completed", False):
            return

        console.print()
        console.print(Panel(
            f"[bold white]Hi {user_name}, welcome to Migru.[/bold white]\n\n"
            "[dim]I'm here to support you through migraines and stress.[/dim]",
            title="[bold cyan]🌸 Welcome[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        ))
        console.print()

        # Mark as complete
        profile = personalization_engine.get_user_profile(user_name).get_profile()
        if "metadata" not in profile:
            profile["metadata"] = {}
        profile["metadata"]["onboarding_completed"] = True
        personalization_engine.get_user_profile(user_name).update_profile(profile)

    except Exception as e:
        logger.error(f"Onboarding failed: {e}")


def show_enhanced_profile(user_name: str, console: Console) -> None:
    """Display enhanced user profile - Legacy compatibility function."""
    console.print("[dim]Use /profile command in the main CLI[/dim]")


def show_enhanced_patterns(user_name: str, console: Console) -> None:
    """Display wellness patterns - Legacy compatibility function."""
    console.print("[dim]Use /patterns command in the main CLI[/dim]")


def show_history(user_name: str, console: Console) -> None:
    """Display conversation history - Legacy compatibility function."""
    console.print("[dim]Use /history command in the main CLI[/dim]")


def show_about(console: Console) -> None:
    """Display about information."""
    about_text = """
    **Migru** - AI Companion for Migraine & Stress Relief
    
    Version: 2.0.0
    
    A revolutionary companion combining:
    • Ultra-fast empathetic support
    • Deep evidence-based research
    • Pattern detection and insights
    
    Local-first. Private. Always there for you.
    """
    
    console.print(Panel(
        about_text,
        title="[bold cyan]About Migru[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))


def show_enhanced_tips(console: Console) -> None:
    """Display helpful tips."""
    tips_text = """
    **Quick Tips**
    
    • Type naturally - I'll understand your intent
    • Use /research for deep investigations
    • Use /mode to switch between companion/researcher/advisor
    • Press Ctrl+R for quick research mode
    • Press Ctrl+P to see your patterns
    
    **Remember**: I'm here to listen and support you.
    """
    
    console.print(Panel(
        tips_text,
        title="[bold cyan]💡 Tips[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))


def show_wellness_nudges(user_name: str, console: Console) -> None:
    """Display wellness nudges - Legacy compatibility."""
    console.print(Panel(
        "[white]Take a moment to breathe deeply[/white]\n\n"
        "[dim]Inhale for 4... Hold for 4... Exhale for 6...[/dim]",
        title="[bold green]🌿 Wellness Nudge[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 1)
    ))


def show_settings(console: Console) -> None:
    """Display current settings."""
    from rich.table import Table
    
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Streaming", "Enabled" if config.STREAMING else "Disabled")
    table.add_row("Primary Model", config.MODEL_PRIMARY)
    table.add_row("Smart Model", config.MODEL_SMART)
    table.add_row("Fast Model", config.MODEL_FAST)
    
    console.print(Panel(
        table,
        title="[bold cyan]⚙️ Settings[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))


def handle_theme_switch(args: str, console: Console) -> bool:
    """Handle theme switching."""
    from app.ui.theme import Themes
    
    if not args:
        # Show current theme
        console.print(f"[cyan]Current theme:[/cyan] {config.UI.ACTIVE_THEME.name}")
        console.print("[dim]Available themes: ocean, sunrise, forest, lavender[/dim]")
        return True
    
    theme_map = {
        "ocean": Themes.OCEAN,
        "sunrise": Themes.SUNRISE,
        "forest": Themes.FOREST,
        "lavender": Themes.LAVENDER,
    }
    
    theme = theme_map.get(args.lower())
    if theme:
        config.UI.ACTIVE_THEME = theme
        console.print(f"[green]✓[/green] Switched to [bold]{args}[/bold] theme")
        return True
    else:
        console.print(f"[yellow]Unknown theme: {args}[/yellow]")
        return False


def handle_model_switch(args: str, console: Console) -> Tuple[Any, str]:
    """Handle model switching - Returns (agent, system_name) for compatibility."""
    from app.agents import migru_core
    
    if not args:
        # Show current mode
        mode = migru_core.get_current_mode()
        console.print(f"[cyan]Current mode:[/cyan] {mode.value}")
        console.print("[dim]Available modes: companion, researcher, advisor[/dim]")
        return migru_core, mode.value
    
    # This is handled by /mode command in new CLI
    console.print("[dim]Use /mode command to switch agent modes[/dim]")
    return migru_core, "migru"
