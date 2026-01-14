from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
try:
    from rich.gauge import Gauge
except ImportError:
    # Gauge might not be available in all rich versions
    class Gauge:
        def __init__(self, percentage, style="white"):
            self.percentage = percentage
            self.style = style
        
        def __str__(self):
            return f"█{' ' * int(self.percentage)} {self.percentage:.0f}%"
from rich.markdown import Markdown
from typing import Optional, Any, Callable
import time
import threading
from app.config import config
from app.ui.theme import Layout, Themes

console = Console()

def get_theme():
    return config.UI.ACTIVE_THEME

class AnimatedPanel:
    """Enhanced panel with smooth animations and visual feedback."""
    
    def __init__(self, content: str, title: str = None, subtitle: str = None, 
                 border_style: str = None, animation_type: str = "fade"):
        self.content = content
        self.title = title
        self.subtitle = subtitle
        self.border_style = border_style or get_theme().panel_border
        self.animation_type = animation_type
        self.theme = get_theme()
        
    def render(self, animated: bool = True) -> Panel:
        """Render panel with optional animation."""
        if animated and self.animation_type == "fade":
            # Simulate fade-in effect with brief delay
            time.sleep(0.1)
            
        return Panel(
            self.content,
            title=f"[{self.theme.primary} bold]{self.title}[/]" if self.title else None,
            subtitle=f"[{self.theme.dim}]{self.subtitle}[/]" if self.subtitle else None,
            border_style=self.border_style,
            box=box.ROUNDED if not config.ACCESSIBILITY_MODE else box.SQUARE,
            padding=Layout.PADDING_NORMAL,
        )

class TypingIndicator:
    """Animated typing indicator for showing Migru is thinking."""
    
    def __init__(self, message: str = "Thinking", style: str = None):
        self.message = message
        self.style = style or get_theme().dim
        self.theme = get_theme()
        self._stop_event = threading.Event()
        
    def __call__(self) -> str:
        """Generate animated typing indicator."""
        if self.theme.animation_speed == "slow":
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            delay = 0.2
        elif self.theme.animation_speed == "fast":
            frames = [".", "o", "O", "0", "@", "*"]
            delay = 0.08
        else:  # normal
            frames = ["⠋", "⠙", "⠹", "⠸"]
            delay = 0.15
            
        while not self._stop_event.is_set():
            for frame in frames:
                if self._stop_event.is_set():
                    break
                yield f"[{self.style}]{self.message}{frame}[/]"
                time.sleep(delay)
    
    def stop(self):
        """Stop the animation."""
        self._stop_event.set()

class WellnessProgress:
    """Visual progress indicators for wellness activities."""
    
    @staticmethod
    def create_circular_progress(label: str, value: float, total: float = 100.0, 
                                color: str = None) -> Panel:
        """Create a circular progress indicator."""
        theme = get_theme()
        color = color or theme.wellness_color or theme.primary
        
        percentage = min((value / total) * 100, 100)
        gauge = Gauge(percentage, style=color)
        
        content = Align.center(
            f"[{theme.text} bold]{label}[/]\n"
            f"[{color}]{gauge}[/]\n"
            f"[{theme.dim}]{percentage:.1f}%[/]"
        )
        
        return Panel(
            content,
            border_style=color,
            box=box.ROUNDED,
            padding=Layout.PADDING_TIGHT,
        )
    
    @staticmethod
    def create_wellness_bar(title: str, items: list[tuple[str, float, str]]) -> Panel:
        """Create a wellness progress bar with multiple items."""
        theme = get_theme()
        
        progress_table = Table(show_header=False, box=None, padding=(0, 1))
        progress_table.add_column("Label", style=theme.text)
        progress_table.add_column("Bar", width=20)
        progress_table.add_column("Value", style=theme.dim, justify="right")
        
        for label, value, color in items:
            bar_length = int(min(value / 100 * 20, 20))
            bar = "█" * bar_length + "░" * (20 - bar_length)
            progress_table.add_row(
                label,
                f"[{color}]{bar}[/]",
                f"{value:.0f}%"
            )
        
        return Panel(
            progress_table,
            title=f"[{theme.secondary} bold]{title}[/]",
            border_style=theme.panel_border,
            box=box.ROUNDED,
            padding=Layout.PADDING_NORMAL,
        )

class EnhancedStatus:
    """Enhanced status indicators with multi-stage progress."""
    
    def __init__(self, stages: list[str], theme_style: str = None):
        self.stages = stages
        self.current_stage = 0
        self.theme_style = theme_style or get_theme().primary
        self.theme = get_theme()
        
    def create_progress_status(self) -> Progress:
        """Create a multi-stage progress indicator."""
        progress = Progress(
            SpinnerColumn(style=self.theme_style),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(style=self.theme_style),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True,
        )
        
        for i, stage in enumerate(self.stages):
            progress.add_task(
                stage, 
                total=100, 
                completed=100 if i < self.current_stage else 0
            )
        
        return progress
    
    def advance_stage(self):
        """Advance to the next stage."""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1

class InsightHighlight:
    """Special highlighting for wellness insights and patterns."""
    
    @staticmethod
    def create_insight_panel(insight: str, insight_type: str = "wellness") -> Panel:
        """Create a highlighted panel for insights."""
        theme = get_theme()
        
        # Choose color based on insight type
        colors = {
            "wellness": theme.wellness_color or theme.primary,
            "pattern": theme.pattern_color or theme.secondary,
            "research": theme.insight_color or theme.accent,
            "nudge": theme.success
        }
        
        color = colors.get(insight_type, theme.primary)
        icons = {
            "wellness": "🌿",
            "pattern": "🔍", 
            "research": "📚",
            "nudge": "💡"
        }
        
        icon = icons.get(insight_type, "✨")
        
        return Panel(
            Markdown(f"**{icon} {insight}**"),
            title=f"[{color} bold]Insight[/]",
            border_style=color,
            box=box.ROUNDED,
            padding=Layout.PADDING_NORMAL,
        )
    
    @staticmethod
    def create_pattern_visualization(pattern_data: dict) -> Panel:
        """Create a visual representation of patterns."""
        theme = get_theme()
        
        # Create a simple ASCII visualization
        pattern_table = Table(show_header=False, box=None, padding=(0, 1))
        pattern_table.add_column("Time", style=theme.dim)
        pattern_table.add_column("Intensity", style=theme.pattern_color)
        
        for time_point, intensity in pattern_data.get("data", []).items():
            bar_length = int(intensity * 10)
            bar = "█" * bar_length
            pattern_table.add_row(time_point, f"[{theme.pattern_color}]{bar}[/]")
        
        return Panel(
            pattern_table,
            title=f"[{theme.pattern_color} bold]{pattern_data.get('title', 'Pattern')}[/]",
            subtitle=f"[{theme.dim}]{pattern_data.get('description', '')}[/]",
            border_style=theme.pattern_color,
            box=box.ROUNDED,
            padding=Layout.PADDING_NORMAL,
        )

# Enhanced versions of original functions
def create_animated_panel(content, title: str = None, subtitle: str = None, 
                         border_style: str = None, animation_type: str = "fade") -> AnimatedPanel:
    """Create an animated panel with enhanced visual feedback."""
    return AnimatedPanel(content, title, subtitle, border_style, animation_type)

def create_table(title: str, columns: list[str]) -> Table:
    """Create a standardized table with theme support."""
    theme = get_theme()
    table = Table(
        title=f"[{theme.secondary} bold]{title}[/]",
        box=box.ROUNDED if not config.ACCESSIBILITY_MODE else box.SQUARE,
        header_style=f"{theme.accent} bold",
        border_style=theme.dim,
        show_header=True
    )
    for col in columns:
        table.add_column(col)
    return table

def render_success(message: str) -> None:
    """Render success message with animation."""
    theme = get_theme()
    console.print(f"[{theme.success}]✓ {message}[/]")

def render_error(message: str) -> None:
    """Render error message with animation."""
    theme = get_theme()
    console.print(f"[{theme.error}]✗ {message}[/]")

def render_warning(message: str) -> None:
    """Render warning message with animation."""
    theme = get_theme()
    console.print(f"[{theme.warning}]⚠ {message}[/]")

def render_typing_indicator(message: str = "Thinking") -> TypingIndicator:
    """Create a typing indicator for showing processing."""
    return TypingIndicator(message)

def create_wellness_progress(label: str, value: float, total: float = 100.0) -> Panel:
    """Create a wellness progress indicator."""
    return WellnessProgress.create_circular_progress(label, value, total)

def highlight_insight(insight: str, insight_type: str = "wellness") -> Panel:
    """Create a highlighted insight panel."""
    return InsightHighlight.create_insight_panel(insight, insight_type)