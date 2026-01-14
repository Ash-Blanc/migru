# CLI Module Documentation

This module contains the command-line interface components for the Migru application.

## Structure

```
app/cli/
├── command_palette.py  # Command palette and UI components
├── session.py          # CLI session management and command handlers
└── README.md           # This documentation
```

## Command Palette

The `CommandPalette` class provides a fuzzy-searchable command palette for the CLI interface.

### Features

- **Command Completion**: Auto-complete commands starting with `/`
- **Fuzzy Search**: Case-insensitive command matching
- **Extensible**: Easy to add new commands

### Available Commands

- `/help` - Show available commands and usage
- `/exit` - Exit the application
- `/clear` - Clear the terminal screen
- `/settings` - Show application settings
- `/about` - Show application information
- `/history` - Show conversation history
- `/profile` - Show user profile
- `/patterns` - Show user patterns and insights
- `/model` - Switch between AI models
- `/bio` - Simulate biometric data input

## Safe Prompt Session

The `SafePromptSession` class provides a wrapper around `prompt_toolkit` with custom styling and error handling.

### Features

- **Custom Styling**: Themed prompts based on UI configuration
- **Key Bindings**: Ctrl+C handling for graceful exit
- **Accessibility**: High-contrast themes for accessibility mode

## Session Management

The `session.py` module contains the main CLI session handlers:

### Functions

- `run_onboarding()` - Gentle onboarding wizard for new users
- `show_profile()` - Display user profile information
- `show_patterns()` - Display user patterns and insights
- `show_history()` - Display conversation history
- `show_about()` - Display application information
- `show_settings()` - Display application settings
- `handle_model_switch()` - Handle AI model switching

### Error Handling

All session handlers include comprehensive error handling:

- **Graceful Degradation**: Continue operation when non-critical services fail
- **User-Friendly Messages**: Clear error messages for users
- **Logging**: Detailed logging for debugging
- **Exception Safety**: Prevent crashes from service failures

## Usage

### Basic Usage

```python
from app.cli.command_palette import CommandPalette, SafePromptSession
from app.cli.session import run_onboarding, show_profile

# Initialize command palette
command_palette = CommandPalette()
prompt_session = SafePromptSession(completer=command_palette.get_completer())

# Run onboarding
run_onboarding("UserName", console, prompt_session, personalization_engine)

# Show user profile
show_profile("UserName", console)
```

### Model Switching

```python
from app.cli.session import handle_model_switch

# Show available models
team, system_name = handle_model_switch("", console)

# Switch to Mistral AI
team, system_name = handle_model_switch("mistral", console)

# Switch to custom model
team, system_name = handle_model_switch("custom:model-id", console)
```

## Testing

The CLI module includes comprehensive unit tests:

```bash
# Run CLI tests
pytest tests/unit/test_cli.py

# Run all tests
pytest tests/
```

## Best Practices

### Error Handling

- Always handle exceptions gracefully
- Provide user-friendly error messages
- Log detailed error information for debugging
- Ensure handlers never crash the application

### Performance

- Use lazy loading for heavy dependencies
- Cache frequently accessed services
- Minimize blocking operations in the main loop
- Use async/await where appropriate

### User Experience

- Provide clear feedback for all operations
- Use appropriate status indicators
- Handle edge cases gracefully
- Maintain consistent UI/UX patterns

## Architecture

The CLI module follows a modular architecture:

1. **Command Palette**: Handles user input and command completion
2. **Session Management**: Manages the conversation flow and state
3. **Service Integration**: Connects to core application services
4. **Error Handling**: Provides robust error handling and recovery

This separation of concerns makes the CLI module easy to maintain and extend.