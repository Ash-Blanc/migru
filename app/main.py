"""
Migru - Revolutionary AI Companion for Migraine & Stress Relief
Complete redesign focusing on therapeutic UX, speed, and deep research capabilities.
"""
import argparse
import os
import sys
import warnings
from datetime import datetime
from typing import Any, Optional
import typer

# Suppress ALL warnings early - keep CLI clean
warnings.filterwarnings("ignore")
import logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL, force=True)

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style as PTStyle
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from app.config import config
from app.exceptions import MigruError
from app.logger import get_logger, suppress_verbose_logging
from app.ui.theme import Themes

# Suppress verbose logging
suppress_verbose_logging()

logger = get_logger("migru.main")
console = Console()


class TherapeuticCLI:
    """
    Revolutionary CLI that balances minimalism with rich interactions.
    Designed for therapeutic wellness support with power-user capabilities.
    """
    
    def __init__(self, user_name: str = "Friend"):
        self.user_name = user_name
        self.console = console
        self.conversation_count = 0
        self.session_start = datetime.now()
        
        # Lazy load heavy dependencies
        self._migru_core = None
        self._services = {}
        
        # Key bindings for power users
        self.kb = KeyBindings()
        self._setup_keybindings()
        
        # Therapeutic color palette
        self.colors = {
            "primary": "magenta",
            "calm": "cyan",
            "warmth": "yellow",
            "nature": "green",
            "alert": "red",
            "neutral": "white",
            "whisper": "dim"
        }
    
    def _setup_keybindings(self) -> None:
        """Setup keyboard shortcuts for power users."""
        # Ctrl+R for research mode
        @self.kb.add('c-r')
        def _(event):
            event.app.exit(result='/research ')
        
        # Ctrl+P for patterns
        @self.kb.add('c-p')
        def _(event):
            event.app.exit(result='/patterns')
        
        # Ctrl+H for help
        @self.kb.add('c-h')
        def _(event):
            event.app.exit(result='/help')
            
        @self.kb.add('c-w')
        def _(event):
            event.app.exit(result='/work')

        @self.kb.add('c-m')
        def _(event):
            event.app.exit(result='/med ')

    @property
    async def migru_core(self):
        """Lazy load the Migru core system."""
        if self._migru_core is None:
            from app.agents import migru_core
            self._migru_core = migru_core
        return self._migru_core
    
    def get_service(self, service_name: str):
        """Lazy load and cache services."""
        if service_name not in self._services:
            if service_name == "personalization":
                from app.agents import personalization_engine
                self._services[service_name] = personalization_engine
            elif service_name == "pattern_detector":
                from app.services.realtime_analytics import pattern_detector
                self._services[service_name] = pattern_detector
            elif service_name == "insight_extractor":
                from app.services.user_insights import insight_extractor
                self._services[service_name] = insight_extractor
            elif service_name == "context_manager":
                from app.services.context import context_manager
                self._services[service_name] = context_manager
        
        return self._services.get(service_name)
    
    def display_welcome(self) -> None:
        """Display a calm, therapeutic welcome screen."""
        self.console.clear()
        self.console.print()
        
        # Minimalist banner
        banner = Align.center(Panel(
            Align.center(
                "[bold cyan]M I G R U[/bold cyan]\n\n"
                f"[dim]Welcome, {self.user_name}[/dim]\n\n"
                "[white]Your companion for migraine relief & stress support[/white]",
                vertical="middle"
            ),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(1, 4)
        ))
        
        self.console.print(banner)
        self.console.print()
        
        # Gentle guidance
        guidance = Panel(
            Group(
                "[white]I'm here to:[/white]\n",
                "  [cyan]•[/cyan] Listen and support you\n",
                "  [cyan]•[/cyan] Research evidence-based relief strategies\n",
                "  [cyan]•[/cyan] Help you discover your patterns\n",
                "\n[dim]Type your thoughts, or use [bold]/help[/bold] for commands[/dim]"
            ),
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        self.console.print(Align.center(guidance))
        self.console.print()
    
    def create_prompt_session(self) -> PromptSession:
        """Create an enhanced prompt session with custom styling."""
        from app.cli.command_palette import IntelligentCommandPalette
        
        self.palette = IntelligentCommandPalette()
        
        # Base style dictionary
        style_dict = {
            'prompt': '#00FFFF bold',
            '': '#FFFFFF',
            "completion-menu.completion": "bg:#008888 #ffffff",
            "completion-menu.completion.current": "bg:#00aaaa #000000",
            "scrollbar.background": "bg:#88aaaa",
            "scrollbar.button": "bg:#222222",
        }
        
        # Add palette styles (simple merge)
        try:
            palette_style = self.palette.get_style()
            # In prompt_toolkit > 3.0, accessing style rules might differ, 
            # so we'll trust the direct definition above for now.
        except Exception:
            pass

        style = PTStyle.from_dict(style_dict)
        
        from prompt_toolkit.history import InMemoryHistory
        
        if not hasattr(self, 'history'):
            self.history = InMemoryHistory()
        
        session = PromptSession(
            style=style,
            key_bindings=self.kb,
            completer=self.palette.get_completer(),
            validator=self.palette.get_validator(),
            validate_while_typing=False,
            history=self.history,
            complete_style=CompleteStyle.MULTI_COLUMN,
            mouse_support=True,
        )
        
        return session
    
    def get_dynamic_prompt(self) -> HTML:
        """Get a context-aware prompt that evolves with the conversation."""
        if self.conversation_count == 0:
            icon = "🌸"
            text = "Share what's on your mind"
        elif self.conversation_count < 3:
            icon = "💭"
            text = "Continue"
        else:
            icon = "•"
            text = ""
        
        if text:
            return HTML(f'<b><style fg="#00FFFF">{icon}</style></b> <style fg="#888888">{text}</style> › ')
        else:
            return HTML(f'<b><style fg="#00FFFF">{icon}</style></b> › ')
    
    def handle_command(self, command: str) -> Optional[bool]:
        """
        Handle slash commands with power-user features.
        
        Returns:
            None to continue conversation
            True to exit
            False to skip this turn
        """
        cmd = command.lower().strip()
        
        # Exit commands
        if cmd in ['/exit', '/quit', '/bye']:
            self._display_farewell()
            return True
        
        # Help
        if cmd in ['/help', '/?']:
            self._display_help()
            return False
        
        # Clear screen
        if cmd == '/clear':
            self.console.clear()
            return False
        
        # Profile & Patterns
        if cmd == '/profile':
            self._display_profile()
            return False
        
        if cmd == '/patterns':
            self._display_patterns()
            return False
        
        # Mode switching (power user feature)
        if cmd.startswith('/mode'):
            parts = cmd.split()
            if len(parts) > 1:
                self._switch_mode(parts[1])
            else:
                self._display_current_mode()
            return False
        
        # Model switching
        if cmd.startswith('/model'):
            parts = cmd.split(maxsplit=1)
            if len(parts) > 1:
                self._switch_model(parts[1])
            else:
                self._display_available_models()
            return False
        
        # Research trigger
        if cmd.startswith('/research'):
            query = cmd[len('/research'):].strip()
            if query:
                return self._handle_research(query)
            else:
                self.console.print("[yellow]Usage: /research <your question>[/yellow]")
                return False
        
        # Breathing exercise
        if cmd in ['/breathe', '/breath']:
            await self._guided_breathing()
            return False
        
        # Quick relief
        if cmd == '/relief':
            self._quick_relief_menu()
            return False
        
        # Session insights
        if cmd == '/insights':
            self._show_session_insights()
            return False
        
        # Quick stats (power user)
        if cmd == '/stats':
            self._display_stats()
            return False
        
        if cmd.startswith('/med'):
            query = cmd[len('/med'):].strip()
            if query:
                # Prefix with explicit intent to ensure routing
                return await self._handle_med_gemma(query)
            else:
                self.console.print("[yellow]Usage: /med <symptom description>[/yellow]")
                return False
        
        return None  # Unknown command, continue
    
    def _display_help(self) -> None:
        """Display comprehensive help with organized commands."""
        help_table = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 2),
            collapse_padding=True
        )
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        
        # Organize by category
        help_table.add_row("[bold]💬 Core[/bold]", "")
        help_table.add_row("/help", "Show this help")
        help_table.add_row("/exit", "End session gracefully")
        help_table.add_row("/clear", "Clear screen")
        
        help_table.add_row("", "")
        help_table.add_row("[bold]🌿 Wellness[/bold]", "")
        help_table.add_row("/work", "Toggle Work Mode (Stealth/Discreet)")
        help_table.add_row("/breathe", "Guided breathing (3 min)")
        help_table.add_row("/relief", "Quick relief menu")
        help_table.add_row("/med <q>", "Med-Gemma clinical insight")
        help_table.add_row("/privacy [mode]", "Switch privacy (local/hybrid/flexible)")
        help_table.add_row("/research <q>", "Deep research")
        help_table.add_row("/exit", "End session")
        
        help_table.add_row("", "")
        help_table.add_row("[bold]📊 Personal[/bold]", "")
        help_table.add_row("/profile", "View your profile")
        help_table.add_row("/patterns", "See wellness patterns")
        help_table.add_row("/stats", "Session statistics")
        
        help_table.add_row("", "")
        help_table.add_row("[bold]🔍 Research[/bold]", "")
        help_table.add_row("/research <query>", "Deep research mode")
        help_table.add_row("/mode [name]", "View/switch agent mode")
        help_table.add_row("/model [name]", "View/switch AI model")
        
        help_table.add_row("", "")
        help_table.add_row("[bold]⚡ Shortcuts[/bold]", "")
        help_table.add_row("Ctrl+R", "Quick research")
        help_table.add_row("Ctrl+P", "Show patterns")
        help_table.add_row("Ctrl+H", "Quick help")
        
        panel = Panel(
            Group(
                help_table,
                "\n[dim]💡 Tip: Just type naturally - I'll understand your intent[/dim]"
            ),
            title="[bold cyan]💡 Commands & Shortcuts[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _display_farewell(self) -> None:
        """Display a warm, therapeutic farewell."""
        session_duration = datetime.now() - self.session_start
        minutes = int(session_duration.total_seconds() / 60)
        
        farewell = Panel(
            Align.center(
                f"[bold white]Thank you for sharing this time, {self.user_name}[/bold white]\n\n"
                f"[dim]We connected for {minutes} minutes[/dim]\n\n"
                "[white]May you find relief and peace[/white]\n\n"
                "[cyan]🌸[/cyan]"
            ),
            border_style="magenta",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(farewell)
        self.console.print()
    
    def _display_profile(self) -> None:
        """Display user profile with therapeutic presentation."""
        personalization = self.get_service("personalization")
        if not personalization:
            self.console.print("[yellow]Profile not available[/yellow]")
            return
        
        try:
            profile = personalization.get_user_profile(self.user_name).get_profile()
            
            # Create a gentle, organized display
            content = []
            
            if profile.get("preferences"):
                content.append("[bold cyan]Preferences[/bold cyan]")
                for key, value in profile["preferences"].items():
                    content.append(f"  • {key.replace('_', ' ').title()}: [white]{value}[/white]")
                content.append("")
            
            if profile.get("sensitivities"):
                content.append("[bold cyan]Sensitivities[/bold cyan]")
                for key, value in profile["sensitivities"].items():
                    content.append(f"  • {key.replace('_', ' ').title()}: [white]{value}[/white]")
                content.append("")
            
            panel = Panel(
                "\n".join(content) if content else "[dim]Building your profile as we talk...[/dim]",
                title=f"[bold magenta]👤 {self.user_name}'s Profile[/bold magenta]",
                border_style="magenta",
                box=box.ROUNDED,
                padding=(1, 2)
            )
            
            self.console.print(panel)
        
        except Exception as e:
            logger.error(f"Failed to display profile: {e}")
            self.console.print("[yellow]Couldn't load profile[/yellow]")
    
    def _display_patterns(self) -> None:
        """Display discovered wellness patterns."""
        pattern_detector = self.get_service("pattern_detector")
        if not pattern_detector:
            self.console.print("[yellow]Pattern detection not available[/yellow]")
            return
        
        try:
            patterns = pattern_detector.get_temporal_patterns(self.user_name)
            
            if patterns:
                content = ["[white]Patterns I've noticed:[/white]\n"]
                for pattern in patterns[:5]:  # Show top 5
                    content.append(f"[cyan]•[/cyan] {pattern.get('description', 'Pattern detected')}")
                
                panel = Panel(
                    "\n".join(content),
                    title="[bold cyan]📊 Your Wellness Patterns[/bold cyan]",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2)
                )
                self.console.print(panel)
            else:
                self.console.print(Panel(
                    "[dim]Still learning your patterns...\nCheck back after a few conversations![/dim]",
                    border_style="cyan",
                    box=box.ROUNDED
                ))
        
        except Exception as e:
            logger.error(f"Failed to display patterns: {e}")
            self.console.print("[yellow]Couldn't load patterns[/yellow]")
    
    def _display_current_mode(self) -> None:
        """Display the current agent mode (power user feature)."""
        from app.agents import AgentMode
        
        mode = self.migru_core.get_current_mode()
        
        mode_descriptions = {
            AgentMode.COMPANION: ("🌸 Companion", "Empathetic support and listening"),
            AgentMode.RESEARCHER: ("🔍 Researcher", "Deep evidence-based research"),
            AgentMode.ADVISOR: ("💡 Advisor", "Practical guidance and protocols")
        }
        
        name, description = mode_descriptions.get(mode, ("Unknown", ""))
        
        panel = Panel(
            f"[bold white]{name}[/bold white]\n\n"
            f"[dim]{description}[/dim]\n\n"
            "[cyan]Available modes:[/cyan] companion, researcher, advisor\n"
            "[dim]Switch with: /mode <name>[/dim]",
            title="[bold cyan]Current Mode[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
        
        self.console.print(panel)
    
    def _switch_mode(self, mode_name: str) -> None:
        """Switch agent mode manually (power user feature)."""
        from app.agents import AgentMode
        
        mode_map = {
            "companion": AgentMode.COMPANION,
            "researcher": AgentMode.RESEARCHER,
            "advisor": AgentMode.ADVISOR
        }
        
        mode = mode_map.get(mode_name.lower())
        if mode:
            self.migru_core.switch_mode(mode)
            self.console.print(f"[green]✓[/green] Switched to [bold]{mode_name}[/bold] mode")
        else:
            self.console.print(f"[yellow]Unknown mode: {mode_name}[/yellow]")
            self.console.print("[dim]Available: companion, researcher, advisor[/dim]")
    
    def _display_available_models(self) -> None:
        """Display available AI models."""
        models_table = Table(
            show_header=True,
            box=box.ROUNDED,
            title="[bold cyan]🤖 Available AI Models[/bold cyan]",
            title_style="bold cyan"
        )
        models_table.add_column("Model", style="cyan", no_wrap=True)
        models_table.add_column("Provider", style="white")
        models_table.add_column("Speed", style="yellow")
        models_table.add_column("Intelligence", style="magenta")
        
        # Define available models
        models = [
            ("mistral-creative", "Mistral AI", "⚡⚡⚡", "🧠🧠🧠🧠"),
            ("mistral-small", "Mistral AI", "⚡⚡⚡", "🧠🧠🧠"),
            ("mistral-medium", "Mistral AI", "⚡⚡", "🧠🧠🧠🧠"),
            ("mistral-large", "Mistral AI", "⚡⚡", "🧠🧠🧠🧠🧠"),
            ("cerebras", "Cerebras", "⚡⚡⚡⚡⚡", "🧠🧠"),
            ("openai-gpt4", "OpenAI", "⚡⚡", "🧠🧠🧠🧠🧠"),
        ]
        
        for model, provider, speed, intel in models:
            models_table.add_row(model, provider, speed, intel)
        
        self.console.print()
        self.console.print(models_table)
        self.console.print()
        self.console.print("[dim]Usage: /model <name> (e.g., /model cerebras)[/dim]")
        self.console.print("[dim]Current configuration in config.py[/dim]")
    
    def _switch_model(self, model_name: str) -> None:
        """Switch AI model dynamically."""
        model_map = {
            "mistral-creative": config.MODEL_MISTRAL_CREATIVE,
            "mistral-small": config.MODEL_MISTRAL_SMALL,
            "mistral-medium": config.MODEL_MISTRAL_MEDIUM,
            "mistral-large": config.MODEL_MISTRAL_LARGE,
            "cerebras": config.MODEL_FAST,
            "openai": "openai:gpt-4o",
            "openai-gpt4": "openai:gpt-4o",
        }
        
        model = model_map.get(model_name.lower())
        if model:
            # Update the agents with new model
            from app.agents import AgentMode
            
            # Recreate agents with new model
            current_mode = self.migru_core.get_current_mode()
            
            # For simplicity, update the config and reinitialize
            self.console.print(f"[green]✓[/green] Switched to [bold]{model_name}[/bold]")
            self.console.print(f"[dim]Model: {model}[/dim]")
            self.console.print("[yellow]Note: Model switching takes effect on next message[/yellow]")
            
            # Store preference for this session
            if not hasattr(self, '_preferred_model'):
                self._preferred_model = {}
            self._preferred_model[current_mode] = model
        else:
            self.console.print(f"[yellow]Unknown model: {model_name}[/yellow]")
            self.console.print("[dim]Use /model to see available models[/dim]")
    
    async def _handle_research(self, query: str) -> bool:
        """Handle research."""
        core = await self.migru_core
        # Force research mode if possible, or just let router handle it
        # Since core.run handles routing, we just pass the query
        self.console.print("[dim]Researching...[/dim]")
        try:
            response = await core.run(query, stream=config.STREAMING)
            self._display_response(response, "Research", "results")
        except Exception as e:
            self.console.print(f"[red]Research failed: {e}[/red]")
        return False

    async def _handle_med_gemma(self, query: str) -> bool:
        """Handle Med-Gemma queries."""
        core = await self.migru_core
        self.console.print("[dim]Consulting Med-Gemma (HAI-DEF)...[/dim]")
        try:
            # We prefix to ensure the router catches the medical intent if the user just types /med symptom
            full_query = f"Med-Gemma analysis: {query}"
            response = await core.run(full_query, stream=config.STREAMING)
            self._display_response(response, "Med-Gemma", "clinical insight")
        except Exception as e:
            self.console.print(f"[red]Med-Gemma analysis failed: {e}[/red]")
        return False

    def _display_stats(self) -> None:
        """Display session statistics (power user feature)."""
        duration = datetime.now() - self.session_start
        minutes = int(duration.total_seconds() / 60)
        seconds = int(duration.total_seconds() % 60)
        
        stats = Table(show_header=False, box=box.SIMPLE)
        stats.add_column("Metric", style="cyan")
        stats.add_column("Value", style="white")
        
        stats.add_row("Session Duration", f"{minutes}m {seconds}s")
        stats.add_row("Messages Exchanged", str(self.conversation_count))
        stats.add_row("Current Mode", self.migru_core.get_current_mode().value.title())
        
        panel = Panel(
            stats,
            title="[bold cyan]📈 Session Stats[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
        
        self.console.print(panel)
    
    def _guided_breathing(self) -> None:
        """Interactive guided breathing exercise."""
        import time
        
        self.console.print()
        self.console.print(Panel(
            Align.center(
                "[bold white]Guided Breathing[/bold white]\n\n"
                "[dim]Let's take a moment together[/dim]\n\n"
                "[cyan]Press Enter when ready...[/cyan]"
            ),
            border_style="green",
            box=box.ROUNDED
        ))
        
        input()  # Wait for user
        
        self.console.print()
        
        # 4-7-8 breathing pattern (calming)
        cycles = 3
        for cycle in range(cycles):
            # Inhale
            self.console.print(f"\n[bold cyan]Cycle {cycle + 1}/{cycles}[/bold cyan]")
            self.console.print("[green]Breathe in slowly...[/green] [dim](4 seconds)[/dim]")
            for i in range(4):
                time.sleep(1)
                self.console.print("  " + "●" * (i + 1))
            
            # Hold
            self.console.print("[yellow]Hold gently...[/yellow] [dim](7 seconds)[/dim]")
            for i in range(7):
                time.sleep(1)
                self.console.print("  " + "○" * (i + 1))
            
            # Exhale
            self.console.print("[blue]Breathe out slowly...[/blue] [dim](8 seconds)[/dim]")
            for i in range(8):
                time.sleep(1)
                self.console.print("  " + "~" * (i + 1))
            
            if cycle < cycles - 1:
                time.sleep(1)
        
        self.console.print()
        self.console.print(Panel(
            Align.center(
                "[bold green]✓ Complete[/bold green]\n\n"
                "[white]Notice how you feel now[/white]\n\n"
                "[dim]You can return here anytime with /breathe[/dim]"
            ),
            border_style="green",
            box=box.ROUNDED
        ))
    
    def _quick_relief_menu(self) -> None:
        """Display quick relief options."""
        relief_table = Table(
            show_header=False,
            box=box.ROUNDED,
            title="[bold green]🌿 Quick Relief Options[/bold green]"
        )
        relief_table.add_column("Action", style="green", no_wrap=True)
        relief_table.add_column("Description", style="white")
        
        relief_table.add_row("🫁 /breathe", "Guided breathing exercise (3 min)")
        relief_table.add_row("🌊 /patterns", "View your wellness patterns")
        relief_table.add_row("💭 Ask me", "Share what you're feeling")
        relief_table.add_row("🔍 /research", "Find relief techniques")
        
        self.console.print()
        self.console.print(relief_table)
        self.console.print()
        self.console.print("[dim]Or just tell me what you need...[/dim]")
    
    def _show_session_insights(self) -> None:
        """Show insights gathered during this session."""
        if self.conversation_count < 3:
            self.console.print(Panel(
                "[dim]Keep talking with me to discover insights...\n\n"
                "After a few messages, I'll be able to identify patterns[/dim]",
                border_style="cyan",
                box=box.ROUNDED
            ))
            return
        
        # Generate session insights
        insights = []
        
        # Basic insights based on conversation
        if self.conversation_count >= 5:
            insights.append("You're exploring your wellness deeply today")
        
        if self.conversation_count >= 10:
            insights.append("Your openness to understanding is remarkable")
        
        duration_mins = int((datetime.now() - self.session_start).total_seconds() / 60)
        if duration_mins >= 10:
            insights.append(f"We've spent {duration_mins} minutes together—that's meaningful")
        
        # Display insights
        content = ["[bold cyan]Session Insights[/bold cyan]\n"]
        
        if insights:
            for insight in insights:
                content.append(f"[green]•[/green] {insight}")
        else:
            content.append("[dim]Building insights as we talk...[/dim]")
        
        content.append("\n[dim]These observations help me support you better[/dim]")
        
        self.console.print()
        self.console.print(Panel(
            "\n".join(content),
            border_style="cyan",
            box=box.ROUNDED
        ))
        

    
    def _display_response(self, response: Any, title: str = "Migru", subtitle: str = "companion") -> None:
        """Display response."""
        self.console.print()
        
        # Print header
        self.console.print(f"[bold magenta]🌸 {title}[/bold magenta] [dim]({subtitle})[/dim]")
        self.console.print("─" * 60)
        
        content = ""
        
        # Handle streaming responses
        from types import GeneratorType
        
        if isinstance(response, GeneratorType):
            # Stream directly to terminal (no Live lock - allows scrolling and copy/paste)
            for chunk in response:
                chunk_text = ""
                
                if hasattr(chunk, "content") and chunk.content:
                    chunk_text = chunk.content
                elif isinstance(chunk, str):
                    chunk_text = chunk
                
                if chunk_text:
                    content += chunk_text
                    # Print chunk immediately (no buffering, allows interaction)
                    self.console.print(chunk_text, end="", markup=False)
            
            # Print newline after streaming completes
            self.console.print()
        
        elif hasattr(response, 'content'):
            # Non-streaming response
            content = response.content
            self.console.print(Markdown(content))
        else:
            # Fallback
            content = str(response)
            self.console.print(content)
        
        # Print footer
        self.console.print("─" * 60)
        self.console.print()
    
    def run(self) -> None:
        """Main conversation loop."""
        self.display_welcome()
        
        # Create prompt session
        session = self.create_prompt_session()
        
        try:
            while True:
                # Get user input with dynamic prompt
                try:
                    user_input = session.prompt(self.get_dynamic_prompt())
                except KeyboardInterrupt:
                    user_input = "/exit"
                
                # Handle empty input
                if not user_input.strip():
                    continue
                
                # Check for exit words (bye, goodbye, etc.)
                exit_words = ["bye", "goodbye", "farewell", "see you", "gotta go", "have to go"]
                user_lower = user_input.lower().strip()
                if any(word in user_lower for word in exit_words):
                    self._display_farewell()
                    break
                
                # Handle commands
                if user_input.startswith('/'):
                    result = self.handle_command(user_input)
                    if result is True:
                        break  # Exit
                    elif result is False:
                        continue  # Skip this turn
                
                # Process message through Migru
                try:
                    # Detect mood and update context
                    context_manager = self.get_service("context_manager")
                    if context_manager:
                        mood = context_manager.detect_mood(user_input)
                        if mood:
                            context_manager.update_user_state(self.user_name, detected_mood=mood)
                    
                    # Track patterns (non-blocking)
                    pattern_detector = self.get_service("pattern_detector")
                    if pattern_detector:
                        try:
                            pattern_detector.record_event(
                                user_id=self.user_name,
                                event_type="message",
                                content=user_input,
                                metadata={"hour": datetime.now().hour}
                            )
                        except Exception as e:
                            logger.debug(f"Pattern tracking failed: {e}")
                    
                    # Get response from Migru (COMPLETELY suppress all logs/warnings)
                    import logging
                    import warnings
                    import sys
                    import os
                    
                    # Save stderr
                    old_stderr = sys.stderr
                    
                    try:
                        # NUCLEAR OPTION: Suppress everything
                        sys.stderr = open(os.devnull, 'w')
                        warnings.filterwarnings("ignore")
                        logging.disable(logging.CRITICAL)
                        
                        response = self.migru_core.run(
                            user_input,
                            stream=config.STREAMING,
                            user_id=self.user_name
                        )
                        
                    finally:
                        # Restore stderr and logging
                        sys.stderr = old_stderr
                        logging.disable(logging.NOTSET)
                    
                    # Display response (after restoring output)
                    mode = self.migru_core.get_current_mode()
                    self._display_response(response, "Migru", mode.value)
                    
                    self.conversation_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    self.console.print()
                    self.console.print(Panel(
                        "[yellow]I'm having a moment of difficulty[/yellow]\n\n"
                        "[white]Let's try that again, or rephrase if needed[/white]\n\n"
                        "[dim]Your message is important to me 🌸[/dim]",
                        border_style="yellow",
                        box=box.ROUNDED
                    ))
        
        except Exception as e:
            logger.error(f"Fatal error in conversation loop: {e}", exc_info=True)
            self.console.print(f"\n[red]Session error: {e}[/red]\n")


def setup_environment() -> bool:
    """Setup and validate environment."""
    try:
        config.validate()
        logger.info("Configuration validated")
        
        # Set environment variables
        env_vars = {
            "FIRECRAWL_API_KEY": config.FIRECRAWL_API_KEY,
            "MISTRAL_API_KEY": config.MISTRAL_API_KEY,
            "OPENWEATHER_API_KEY": config.OPENWEATHER_API_KEY,
            "CEREBRAS_API_KEY": config.CEREBRAS_API_KEY,
        }
        
        for key, value in env_vars.items():
            if value:
                os.environ[key] = value
        
        return True
    
    except MigruError as e:
        logger.error(f"Configuration error: {e}")
        console.print(Panel(
            f"[red]Configuration Error[/red]\n\n{str(e)}\n\n"
            "[dim]Check your .env file[/dim]",
            border_style="red",
            box=box.ROUNDED
        ))
        return False


def version_callback(value: bool):
    if value:
        print("Migru 2.0.0")
        raise typer.Exit()

app = typer.Typer(
    name="migru",
    help="Migru - AI companion for migraine and stress relief",
    add_completion=True,
)

@app.command()
def chat(
    user: str = typer.Option("Friend", "--user", "-u", help="Your name"),
):
    """Start an interactive therapeutic chat session."""
    try:
        cli = TherapeuticCLI(user_name=user)
        cli.run()
    except KeyboardInterrupt:
        console.print("\n[dim]Session interrupted. Take care! 🌸[/dim]\n")

@app.command()
def profile(
    user: str = typer.Option("Friend", "--user", "-u", help="Your name"),
):
    """View your wellness profile."""
    cli = TherapeuticCLI(user_name=user)
    cli._display_profile()

@app.command()
def breathe():
    """Start a guided breathing exercise."""
    cli = TherapeuticCLI()
    cli._guided_breathing()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    user: str = typer.Option("Friend", "--user", "-u", help="Your name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Detailed logging"),
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version"),
):
    """
    Migru - Revolutionary AI Companion for Migraine & Stress Relief.
    """
    # Setup logging
    if verbose:
        import logging
        logging.getLogger("migru").setLevel(logging.INFO)
    else:
        import logging
        logging.basicConfig(level=logging.CRITICAL)
        suppress_verbose_logging()
        logging.getLogger().setLevel(logging.CRITICAL)
        import warnings
        warnings.filterwarnings("ignore")
    
    # Setup environment
    if not setup_environment():
        raise typer.Exit(code=1)

    # Ensure Redis is available
    from app.db import ensure_redis_running
    if not ensure_redis_running():
        logger.debug("Redis not available, memory features limited")

    if ctx.invoked_subcommand is None:
        # Launch default chat
        try:
            cli = TherapeuticCLI(user_name=user)
            cli.run()
        except KeyboardInterrupt:
            console.print("\n[dim]Session interrupted. Take care! 🌸[/dim]\n")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            console.print(f"\n[red]Error: {e}[/red]\n")
            raise typer.Exit(code=1)

if __name__ == "__main__":
    app()