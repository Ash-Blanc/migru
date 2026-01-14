"""
Command palette and autocomplete for the CLI.
"""
from typing import Any, Dict, List, Optional, Tuple

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import (
    Completer,
    Completion,
    NestedCompleter,
    WordCompleter,
)
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style


from prompt_toolkit.validation import Validator, ValidationError

class CommandValidator(Validator):
    """Validator for Migru commands."""
    
    def __init__(self, commands: list[str]):
        self.commands = commands

    def validate(self, document: Document) -> None:
        text = document.text.strip()
        if text.startswith("/") and " " not in text:
            if text not in self.commands:
                # Find the closest command for better error message
                raise ValidationError(
                    message=f"Unknown command: {text}. Type /help for valid commands.",
                    cursor_position=len(text)
                )

class IntelligentCommandPalette:
    """Command palette with intelligent suggestions and nested completion."""

    def __init__(self):
        # ... existing code ...
        self.command_structure = {
            "/help": None,
            "/exit": None,
            "/quit": None,
            "/clear": None,
            "/profile": None,
            "/patterns": None,
            "/stats": None,
            "/insights": None,
            "/relief": None,
            "/breathe": None,
            "/research": None,
            "/mode": {
                "companion": None,
                "researcher": None,
                "advisor": None,
            },
            "/model": {
                "mistral-creative": None,
                "mistral-small": None,
                "mistral-medium": None,
                "mistral-large": None,
                "cerebras": None,
                "openai": None,
            },
        }
        self.valid_commands = list(self.command_structure.keys())

    def get_completer(self) -> Completer:
        """Get the nested completer."""
        return NestedCompleter.from_nested_dict(self.command_structure)

    def get_validator(self) -> Validator:
        """Get the command validator."""
        return CommandValidator(self.valid_commands)

    def get_style(self) -> Style:
        """Get the style for the completion menu."""
        return Style.from_dict({
            "completion-menu.completion": "bg:#008888 #ffffff",
            "completion-menu.completion.current": "bg:#00aaaa #000000",
            "scrollbar.background": "bg:#88aaaa",
            "scrollbar.button": "bg:#222222",
        })


# Legacy export for compatibility
CommandPalette = IntelligentCommandPalette
