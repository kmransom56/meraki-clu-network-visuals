# Reusable Components Package

This package provides reusable components for API key management and AI agent frameworks that can be easily integrated into other Python applications.

## Installation

### Option 1: Copy the `reusable/` directory

Simply copy the `reusable/` directory to your project:

```bash
cp -r reusable/ /path/to/your/project/
```

### Option 2: Add as a Git Submodule

```bash
git submodule add <repository-url>/reusable /path/to/your/project/reusable
```

### Option 3: Install as a Package

If you want to install it as a package, add a `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="reusable-components",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=3.0.0",
    ],
)
```

Then install with:
```bash
pip install -e .
```

## Dependencies

Required:
- `cryptography` - For Fernet encryption

Optional (for agent framework):
- `openai` - For OpenAI backend
- `magentic` - For Magentic One backend
- `pyautogen` - For AutoGen backend
- `docker` - For Docker Cagent backend

## Usage

### Secure Key Manager

The `SecureKeyManager` provides secure storage and retrieval of API keys and sensitive data.

#### Basic Usage

```python
from reusable.secure_key_manager import SecureKeyManager

# Initialize with your app name
key_manager = SecureKeyManager(app_name="my_app")

# Save an API key
key_manager.save_key("openai_api_key", "sk-...")

# Retrieve an API key
api_key = key_manager.get_key("openai_api_key")

# Check if key exists
if key_manager.has_key("openai_api_key"):
    print("Key exists")

# Delete a key
key_manager.delete_key("openai_api_key")

# List all keys
all_keys = key_manager.list_keys()
```

#### With Environment Variable Fallback

```python
# Save a key
key_manager.save_key(
    "openai_api_key", 
    "sk-...",
    env_var_name="OPENAI_API_KEY"  # Check env var first
)

# Get key (checks env var first, then storage)
api_key = key_manager.get_key(
    "openai_api_key",
    env_var_name="OPENAI_API_KEY",  # Priority: env var > storage > default
    default="default-key"  # Fallback if not found
)
```

#### Custom Encryption Password

```python
# Use a custom encryption password
key_manager = SecureKeyManager(
    app_name="my_app",
    encryption_password="my-secret-password-32-chars-long!!"
)
```

#### Custom Database Path

```python
# Use a custom database path
key_manager = SecureKeyManager(
    app_name="my_app",
    db_path="/custom/path/to/keys.db"
)
```

### Agent Framework Wrapper

The `AgentFrameworkWrapper` provides a simplified interface to the AI agent framework.

#### Basic Usage

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

# Initialize key manager
key_manager = SecureKeyManager(app_name="my_app")

# Save your API key
key_manager.save_key("openai_api_key", "sk-...", env_var_name="OPENAI_API_KEY")

# Initialize agent framework
agent = AgentFrameworkWrapper(
    backend=AgentBackend.OPENAI,
    api_key_manager=key_manager
)

# Check if agent is available
if agent.is_available():
    # Send a chat message
    response = agent.chat("What is Python?")
    print(response)
    
    # Analyze code
    code = """
    def hello():
        print("Hello, World!")
    """
    analysis = agent.analyze_code(code, task="optimize")
    print(analysis)
else:
    print("Agent framework not available")
```

#### Different Backends

```python
# OpenAI
agent = AgentFrameworkWrapper(
    backend=AgentBackend.OPENAI,
    api_key_manager=key_manager
)

# Anthropic
agent = AgentFrameworkWrapper(
    backend=AgentBackend.ANTHROPIC,
    api_key_manager=key_manager
)

# AutoGen
agent = AgentFrameworkWrapper(
    backend=AgentBackend.AUTOGEN,
    api_key_manager=key_manager
)

# Magentic One
agent = AgentFrameworkWrapper(
    backend=AgentBackend.MAGENTIC_ONE,
    api_key_manager=key_manager
)
```

#### With Custom Configuration

```python
agent = AgentFrameworkWrapper(
    backend=AgentBackend.OPENAI,
    api_key_manager=key_manager,
    config={
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    }
)
```

## Complete Example

Here's a complete example showing how to use both components together:

```python
#!/usr/bin/env python3
"""
Example: Using reusable components in your application
"""

from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend


def main():
    # Initialize key manager
    key_manager = SecureKeyManager(app_name="my_application")
    
    # Try to get API key (from env var, storage, or prompt user)
    api_key = key_manager.get_key(
        "openai_api_key",
        env_var_name="OPENAI_API_KEY"
    )
    
    if not api_key:
        # Prompt user for API key
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            key_manager.save_key("openai_api_key", api_key, env_var_name="OPENAI_API_KEY")
    
    if not api_key:
        print("No API key available. Exiting.")
        return
    
    # Initialize agent
    agent = AgentFrameworkWrapper(
        backend=AgentBackend.OPENAI,
        api_key_manager=key_manager
    )
    
    if not agent.is_available():
        print("Agent framework not available. Check dependencies.")
        return
    
    # Use the agent
    print("Agent ready! Backend:", agent.get_backend_name())
    
    # Chat example
    response = agent.chat("Explain Python decorators in one sentence.")
    print(f"\nResponse: {response}")
    
    # Code analysis example
    code = """
    def calculate_sum(numbers):
        total = 0
        for num in numbers:
            total = total + num
        return total
    """
    
    analysis = agent.analyze_code(code, task="optimize")
    print(f"\nOptimization suggestions:\n{analysis}")


if __name__ == "__main__":
    main()
```

## Integration into Other Projects

### Step 1: Copy the reusable package

```bash
# Copy to your project
cp -r /path/to/meraki-cli-network-visuals/reusable /path/to/your/project/
```

### Step 2: Install dependencies

```bash
pip install cryptography
# Optional: pip install openai magentic pyautogen docker
```

### Step 3: Import and use

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

# Your code here...
```

## Security Notes

1. **Encryption**: All keys are encrypted using Fernet (symmetric encryption)
2. **Storage**: Keys are stored in SQLite databases in the user's home directory
3. **Isolation**: Each application uses its own database (isolated by app name)
4. **Environment Variables**: The manager checks environment variables first (highest priority)
5. **Password**: If no encryption password is provided, a default is generated based on app name and user home directory

## File Structure

```
reusable/
├── __init__.py                 # Package initialization
├── secure_key_manager.py       # API key management
├── agent_framework_wrapper.py  # Agent framework wrapper
└── README.md                   # This file
```

## API Reference

### SecureKeyManager

- `__init__(app_name, encryption_password=None, db_path=None)` - Initialize manager
- `save_key(key_name, key_value, env_var_name=None)` - Save a key
- `get_key(key_name, env_var_name=None, default=None)` - Get a key
- `has_key(key_name)` - Check if key exists
- `delete_key(key_name)` - Delete a key
- `list_keys()` - List all stored keys
- `get_fernet()` - Get Fernet instance for advanced usage

### AgentFrameworkWrapper

- `__init__(backend, api_key_manager=None, config=None)` - Initialize wrapper
- `chat(message, system_prompt=None)` - Send chat message
- `analyze_code(code, task="analyze")` - Analyze code
- `is_available()` - Check if agent is available
- `get_backend_name()` - Get backend name

## License

Same license as the parent project (GNU General Public License v2).
