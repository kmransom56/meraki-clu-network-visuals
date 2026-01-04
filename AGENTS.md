# AI Agent Instructions for Meraki CLI Network Visuals

This document provides instructions for AI agents (like Claude Code, Cursor AI, etc.) when working with this codebase.

## Reusable Components Package

### Overview

This repository includes a **reusable components package** (`reusable/`) that provides:
- **SecureKeyManager**: Encrypted API key storage with environment variable fallback
- **AgentFrameworkWrapper**: Multi-backend AI agent framework

### Key Information for Agents

**IMPORTANT**: When working with this codebase, be aware that:

1. **Reusable Components Location**: `reusable/` directory contains standalone, reusable modules
2. **Integration Pattern**: The `reusable/` package is designed to be copied to other projects
3. **API Key Management**: Use `SecureKeyManager` for all API key storage needs
4. **Agent Framework**: Use `AgentFrameworkWrapper` for AI agent functionality

### Using Reusable Components

#### SecureKeyManager Usage

```python
from reusable.secure_key_manager import SecureKeyManager

# Initialize with app name (creates isolated storage)
key_manager = SecureKeyManager(app_name="my_app")

# Save API key (checks env var first if specified)
key_manager.save_key("api_key", "sk-...", env_var_name="API_KEY")

# Retrieve API key (priority: env var > storage > default)
api_key = key_manager.get_key("api_key", env_var_name="API_KEY", default=None)

# Check if key exists
if key_manager.has_key("api_key"):
    # Key exists
    pass

# Delete a key
key_manager.delete_key("api_key")

# List all keys
all_keys = key_manager.list_keys()
```

#### AgentFrameworkWrapper Usage

```python
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend
from reusable.secure_key_manager import SecureKeyManager

# Initialize key manager
key_manager = SecureKeyManager(app_name="my_app")
key_manager.save_key("openai_api_key", "sk-...", env_var_name="OPENAI_API_KEY")

# Initialize agent
agent = AgentFrameworkWrapper(
    backend=AgentBackend.OPENAI,
    api_key_manager=key_manager
)

# Use agent
if agent.is_available():
    response = agent.chat("Hello!")
    analysis = agent.analyze_code(code, task="optimize")
```

### When Adding New Features

1. **If creating reusable functionality**: Add to `reusable/` package
2. **If project-specific**: Add to appropriate module (e.g., `api/`, `modules/`, etc.)
3. **If managing API keys**: Always use `SecureKeyManager` instead of hardcoding
4. **If using AI agents**: Use `AgentFrameworkWrapper` for consistency

### File Structure

```
reusable/
├── __init__.py                    # Package exports
├── secure_key_manager.py          # API key management
├── agent_framework_wrapper.py     # Agent framework wrapper
├── README.md                      # Full documentation
├── QUICKSTART.md                  # Quick start guide
└── examples/                      # Usage examples
    ├── basic_usage.py
    └── code_analyzer.py
```

### Documentation Files

- **Main Integration Guide**: `REUSABLE_COMPONENTS.md`
- **Quick Start**: `reusable/QUICKSTART.md`
- **Full Documentation**: `reusable/README.md`
- **Examples**: `reusable/examples/`

### Environment Variable Import

The project includes `scripts/import_env_vars.py` for importing environment variables from files with `KEY="VALUE"` or `export KEY="VALUE"` format.

**Usage**:
```bash
python scripts/import_env_vars.py apikeys.ini
```

**Supported formats**:
- `export KEY="VALUE"` (bash export format)
- `KEY="VALUE"` (INI/simple format)
- Both single and double quotes supported
- Comments (lines starting with #) are ignored

### Security Guidelines

1. **Never commit API keys**: All API keys should be in `.gitignore`
2. **Use SecureKeyManager**: Always use `SecureKeyManager` for key storage
3. **Environment variables**: Check environment variables first, then storage
4. **Encryption**: All keys are encrypted using Fernet (symmetric encryption)
5. **Isolation**: Each app uses its own database (isolated by app name)

### Common Patterns

#### Pattern 1: CLI Application

```python
from reusable.secure_key_manager import SecureKeyManager

def main():
    key_manager = SecureKeyManager(app_name="my_cli")
    api_key = key_manager.get_key("api_key", env_var_name="API_KEY")
    
    if not api_key:
        api_key = input("Enter API key: ")
        key_manager.save_key("api_key", api_key)
    
    # Use API key...
```

#### Pattern 2: Web Application

```python
from flask import Flask
from reusable.secure_key_manager import SecureKeyManager

app = Flask(__name__)
key_manager = SecureKeyManager(app_name="my_web_app")

@app.route("/")
def index():
    api_key = key_manager.get_key("api_key", env_var_name="API_KEY")
    # Use API key...
```

#### Pattern 3: Script with AI Agent

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

key_manager = SecureKeyManager(app_name="my_script")
key_manager.save_key("openai_api_key", "sk-...", env_var_name="OPENAI_API_KEY")

agent = AgentFrameworkWrapper(AgentBackend.OPENAI, key_manager)
response = agent.chat("Analyze this code...")
```

### Integration into Other Projects

When helping users integrate these components:

1. **Copy the package**: `cp -r reusable/ /path/to/other/project/`
2. **Install dependencies**: `pip install cryptography` (required), `pip install openai` (optional for agents)
3. **Import and use**: `from reusable.secure_key_manager import SecureKeyManager`

### Code Quality Standards

- Follow existing code style
- Use type hints where appropriate
- Include docstrings for all functions
- Handle errors gracefully
- Use `SecureKeyManager` for all API key operations
- Never hardcode API keys or sensitive data

### Testing

- Test with example files in `reusable/examples/`
- Verify encryption/decryption works correctly
- Test environment variable fallback
- Test agent framework initialization

### Dependencies

**Required**:
- `cryptography` - For Fernet encryption

**Optional** (for agent framework):
- `openai` - OpenAI backend
- `magentic` - Magentic One backend
- `pyautogen` - AutoGen backend
- `docker` - Docker Cagent backend

## Additional Notes

- The `reusable/` package is self-contained and can be copied to other projects
- All API keys are stored in SQLite databases in the user's home directory
- Database files follow the pattern: `~/.{app_name}_keys.db`
- Environment variables take precedence over stored keys
- The agent framework supports multiple backends for flexibility
