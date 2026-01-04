# Quick Start Guide

Get started with reusable components in 5 minutes!

## Installation

1. **Copy the reusable package** to your project:
   ```bash
   cp -r reusable/ /path/to/your/project/
   ```

2. **Install dependencies**:
   ```bash
   pip install cryptography
   # Optional for agent framework:
   pip install openai
   ```

## Quick Examples

### Example 1: Store and Retrieve API Keys

```python
from reusable.secure_key_manager import SecureKeyManager

# Create manager
key_manager = SecureKeyManager(app_name="my_app")

# Save a key
key_manager.save_key("my_api_key", "sk-1234567890")

# Get the key
api_key = key_manager.get_key("my_api_key")
print(api_key)  # Output: sk-1234567890
```

### Example 2: Use with Environment Variables

```python
from reusable.secure_key_manager import SecureKeyManager
import os

# Set environment variable (or it might already be set)
os.environ["OPENAI_API_KEY"] = "sk-1234567890"

# Create manager
key_manager = SecureKeyManager(app_name="my_app")

# Get key (checks env var first, then storage)
api_key = key_manager.get_key(
    "openai_api_key",
    env_var_name="OPENAI_API_KEY"  # Checks this env var first
)
print(api_key)  # Output: sk-1234567890
```

### Example 3: Use AI Agent Framework

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

# Setup key manager
key_manager = SecureKeyManager(app_name="my_app")
key_manager.save_key("openai_api_key", "sk-...", env_var_name="OPENAI_API_KEY")

# Create agent
agent = AgentFrameworkWrapper(
    backend=AgentBackend.OPENAI,
    api_key_manager=key_manager
)

# Use agent
if agent.is_available():
    response = agent.chat("Hello, how are you?")
    print(response)
```

## Integration Checklist

- [ ] Copy `reusable/` directory to your project
- [ ] Install `cryptography`: `pip install cryptography`
- [ ] (Optional) Install agent dependencies: `pip install openai`
- [ ] Import and use in your code
- [ ] Test with a simple example

## Common Use Cases

### Use Case 1: CLI Application

```python
#!/usr/bin/env python3
from reusable.secure_key_manager import SecureKeyManager

def main():
    key_manager = SecureKeyManager(app_name="my_cli_app")
    
    # Get API key
    api_key = key_manager.get_key("api_key", env_var_name="MY_API_KEY")
    
    if not api_key:
        api_key = input("Enter API key: ")
        key_manager.save_key("api_key", api_key)
    
    # Use API key...
    print(f"Using API key: {api_key[:10]}...")

if __name__ == "__main__":
    main()
```

### Use Case 2: Web Application

```python
from flask import Flask
from reusable.secure_key_manager import SecureKeyManager

app = Flask(__name__)
key_manager = SecureKeyManager(app_name="my_web_app")

@app.route("/")
def index():
    api_key = key_manager.get_key("api_key", env_var_name="API_KEY")
    # Use API key...
    return "OK"
```

### Use Case 3: Script with AI Agent

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

key_manager = SecureKeyManager(app_name="my_script")
key_manager.save_key("openai_api_key", "sk-...", env_var_name="OPENAI_API_KEY")

agent = AgentFrameworkWrapper(AgentBackend.OPENAI, key_manager)

# Analyze some code
code = "def hello(): print('world')"
analysis = agent.analyze_code(code, task="optimize")
print(analysis)
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples/](examples/) for more examples
- See API reference in README.md
