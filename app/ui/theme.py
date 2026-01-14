from dataclasses import dataclass
from typing import Dict, Optional
import random
from datetime import datetime

@dataclass
class UITheme:
    name: str
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    dim: str
    success: str
    warning: str
    error: str
    panel_border: str
    prompt: str
    input: str
    
    # Enhanced visual properties
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None
    animation_speed: str = "normal"  # slow, normal, fast
    mood_association: Optional[str] = None  # calm, energized, focused, relaxed
    
    # Rich specific styles
    spinner_style: str = "dots"
    refresh_rate: int = 12
    
    # Wellness-specific colors
    wellness_color: Optional[str] = None
    insight_color: Optional[str] = None
    pattern_color: Optional[str] = None

class Themes:
    # Enhanced Ocean Theme
    OCEAN = UITheme(
        name="Ocean",
        primary="cyan",
        secondary="magenta",
        accent="cyan",
        background="black",
        text="white",
        dim="dim white",
        success="green",
        warning="yellow",
        error="red",
        panel_border="blue",
        prompt="#00ffff bold",
        input="#ffffff",
        gradient_start="#006994",
        gradient_end="#00ffff",
        animation_speed="normal",
        mood_association="calm",
        spinner_style="dots",
        refresh_rate=12,
        wellness_color="#40e0d0",
        insight_color="#87ceeb",
        pattern_color="#4682b4"
    )

    # New Wellness-Focused Themes
    SUNRISE = UITheme(
        name="Sunrise",
        primary="yellow",
        secondary="orange3",
        accent="bright_yellow",
        background="black",
        text="white",
        dim="dim yellow",
        success="yellow",
        warning="orange1",
        error="red",
        panel_border="yellow",
        prompt="#ffd700 bold",
        input="#ffffe0",
        gradient_start="#ff6b35",
        gradient_end="#ffd700",
        animation_speed="slow",
        mood_association="energized",
        spinner_style="line",
        refresh_rate=8,
        wellness_color="#ffa500",
        insight_color="#ffeb3b",
        pattern_color="#ff9800"
    )
    
    FOREST = UITheme(
        name="Forest",
        primary="green",
        secondary="spring_green",
        accent="bright_green",
        background="black",
        text="white",
        dim="dim green",
        success="bright_green",
        warning="yellow",
        error="red",
        panel_border="green",
        prompt="#00ff00 bold",
        input="#e8ffe8",
        gradient_start="#228b22",
        gradient_end="#90ee90",
        animation_speed="slow",
        mood_association="focused",
        spinner_style="bouncingBar",
        refresh_rate=6,
        wellness_color="#32cd32",
        insight_color="#98fb98",
        pattern_color="#2e8b57"
    )
    
    LAVENDER = UITheme(
        name="Lavender",
        primary="magenta",
        secondary="purple",
        accent="bright_magenta",
        background="black",
        text="white",
        dim="dim magenta",
        success="magenta",
        warning="orchid",
        error="red",
        panel_border="magenta",
        prompt="#ff00ff bold",
        input="#ffe8ff",
        gradient_start="#8b008b",
        gradient_end="#dda0dd",
        animation_speed="normal",
        mood_association="relaxed",
        spinner_style="pipe",
        refresh_rate=10,
        wellness_color="#da70d6",
        insight_color="#e6e6fa",
        pattern_color="#9370db"
    )

    DAYLIGHT = UITheme(
        name="Daylight",
        primary="blue",
        secondary="magenta",
        accent="cyan",
        background="white",
        text="black",
        dim="dim black",
        success="green",
        warning="yellow",
        error="red",
        panel_border="blue",
        prompt="#0000ff bold",
        input="#000000",
        gradient_start="#87ceeb",
        gradient_end="#ffffff",
        animation_speed="fast",
        mood_association="focused",
        spinner_style="dots",
        refresh_rate=12
    )

    HIGH_CONTRAST = UITheme(
        name="High Contrast",
        primary="white",
        secondary="white",
        accent="yellow",
        background="black",
        text="white",
        dim="white",
        success="green",
        warning="yellow",
        error="red",
        panel_border="white",
        prompt="#ffffff bold",
        input="#ffffff",
        animation_speed="normal",
        mood_association="focused",
        spinner_style="simpleDots",
        refresh_rate=4
    )

    # Theme collection for easy access
    WELLNESS_THEMES = [OCEAN, SUNRISE, FOREST, LAVENDER]
    ALL_THEMES = [OCEAN, SUNRISE, FOREST, LAVENDER, DAYLIGHT, HIGH_CONTRAST]
    
    @classmethod
    def get_theme_by_mood(cls, mood: str) -> UITheme:
        """Get theme based on user mood."""
        mood_themes = {
            "calm": cls.OCEAN,
            "relaxed": cls.LAVENDER,
            "energized": cls.SUNRISE,
            "focused": cls.FOREST,
            "stressed": cls.OCEAN,  # Calming theme for stress
            "happy": cls.SUNRISE,   # Bright theme for happiness
            "tired": cls.LAVENDER,  # Gentle theme for tiredness
        }
        return mood_themes.get(mood, cls.OCEAN)
    
    @classmethod
    def get_time_based_theme(cls) -> UITheme:
        """Get theme based on time of day."""
        hour = datetime.now().hour
        
        if 5 <= hour < 8:   # Early morning
            return cls.SUNRISE
        elif 8 <= hour < 12:  # Morning
            return cls.FOREST
        elif 12 <= hour < 17:  # Afternoon
            return cls.DAYLIGHT
        elif 17 <= hour < 20:  # Evening
            return cls.LAVENDER
        else:  # Night
            return cls.OCEAN
    
    @classmethod
    def get_random_wellness_theme(cls) -> UITheme:
        """Get a random wellness-focused theme."""
        return random.choice(cls.WELLNESS_THEMES)

class Layout:
    PADDING_TIGHT = (0, 1)
    PADDING_NORMAL = (1, 2)
    MARGIN_NONE = 0
    MARGIN_SMALL = 1
    
    # Panel box styles
    BOX_DEFAULT = "ROUNDED"
    BOX_MINIMAL = "SQUARE"
