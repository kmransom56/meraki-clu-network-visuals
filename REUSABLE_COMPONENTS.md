# Reusable Components Guide

This document explains how to reuse the AI agent and API key management code in other applications.

## Overview

The `reusable/` package contains two main components:

1. **SecureKeyManager** - Secure API key storage and retrieval
2. **AgentFrameworkWrapper** - AI agent framework wrapper

## Quick Integration

### Step 1: Copy the Package

```bash
# Copy the reusable directory to your project
cp -r reusable/ /path/to/your/project/
```

### Step 2: Install Dependencies

```bash
pip install cryptography
# Optional for agent framework:
pip install openai  # or magentic, pyautogen, docker
```

### Step 3: Use in Your Code

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

# Initialize key manager
key_manager = SecureKeyManager(app_name="your_app_name")

# Save API key
key_manager.save_key("openai_api_key", "sk-...", env_var_name="OPENAI_API_KEY")

# Initialize agent
agent = AgentFrameworkWrapper(
    backend=AgentBackend.OPENAI,
    api_key_manager=key_manager
)

# Use agent
response = agent.chat("Hello!")
```

## Package Structure

```
reusable/
├── __init__.py                    # Package exports
├── secure_key_manager.py          # API key management
├── agent_framework_wrapper.py     # Agent framework wrapper
├── README.md                      # Full documentation
├── QUICKSTART.md                  # Quick start guide
└── examples/
    ├── basic_usage.py             # Basic usage example
    └── code_analyzer.py           # Code analysis example
```

## Key Features

### SecureKeyManager

- ✅ Fernet encryption for secure storage
- ✅ SQLite database for persistence
- ✅ App-specific storage (isolated by app name)
- ✅ Environment variable fallback support
- ✅ Multiple key storage (not just one key)
- ✅ Simple, clean API

### AgentFrameworkWrapper

- ✅ Multi-backend support (OpenAI, Anthropic, AutoGen, Magentic One)
- ✅ Integrated with SecureKeyManager
- ✅ Simple chat interface
- ✅ Code analysis capabilities
- ✅ Easy to use in any application

## Usage Examples

See the [reusable/README.md](reusable/README.md) for detailed documentation and examples.

## Integration Patterns

### Pattern 1: Standalone Script

```python
#!/usr/bin/env python3
from reusable.secure_key_manager import SecureKeyManager

key_manager = SecureKeyManager(app_name="my_script")
api_key = key_manager.get_key("api_key", env_var_name="API_KEY")
# Use API key...
```

### Pattern 2: Web Application

```python
from flask import Flask
from reusable.secure_key_manager import SecureKeyManager

app = Flask(__name__)
key_manager = SecureKeyManager(app_name="my_web_app")

@app.route("/")
def index():
    api_key = key_manager.get_key("api_key")
    # Use API key...
```

### Pattern 3: CLI Tool

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

def main():
    key_manager = SecureKeyManager(app_name="my_cli")
    agent = AgentFrameworkWrapper(AgentBackend.OPENAI, key_manager)
    # Use agent...
```

## Security Notes

- All keys are encrypted using Fernet (symmetric encryption)
- Keys are stored in SQLite databases in the user's home directory
- Each application uses its own database (isolated by app name)
- Environment variables are checked first (highest priority)

## Dependencies

**Required:**
- `cryptography` - For encryption

**Optional (for agent framework):**
- `openai` - OpenAI backend
- `magentic` - Magentic One backend
- `pyautogen` - AutoGen backend
- `docker` - Docker Cagent backend

## Files to Copy

When integrating into another project, copy these files:

```
reusable/
├── __init__.py
├── secure_key_manager.py
├── agent_framework_wrapper.py
├── README.md
└── QUICKSTART.md
```

The `examples/` directory is optional but helpful for learning.

## License

Same license as the parent project (GNU General Public License v2).

## Support

For issues or questions:
1. Check [reusable/README.md](reusable/README.md) for detailed docs
2. See [reusable/examples/](reusable/examples/) for code examples
3. Review [reusable/QUICKSTART.md](reusable/QUICKSTART.md) for quick start
