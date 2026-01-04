# Outset Solutions - Meraki Management Utility

**A professional network management tool by Outset Solutions**

A Python-based tool for interacting with the Cisco Meraki API, featuring:
- Network topology visualization
- Device management
- SSL proxy support (Zscaler compatible)
- Secure API key management
- Official Meraki Dashboard API SDK integration
- **Reusable Components** - API key management and AI agent framework for other applications

## About Outset Solutions

**Outset Solutions** is a professional software development company specializing in network management and automation tools. This Meraki Management Utility is part of our suite of enterprise-grade network administration solutions.

**Company Website:** https://www.outsetsolutions.com

## 🚀 Reusable Components

This repository includes a **reusable components package** that can be easily integrated into other Python applications:

### Quick Integration

```python
from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

# Secure API key management
key_manager = SecureKeyManager(app_name="my_app")
key_manager.save_key("api_key", "sk-...", env_var_name="API_KEY")
api_key = key_manager.get_key("api_key")

# AI agent framework
agent = AgentFrameworkWrapper(AgentBackend.OPENAI, key_manager)
response = agent.chat("Hello!")
```

**📖 See [REUSABLE_COMPONENTS.md](REUSABLE_COMPONENTS.md) for full integration guide**

**⚡ Quick Start: [reusable/QUICKSTART.md](reusable/QUICKSTART.md)**

**📚 Full Docs: [reusable/README.md](reusable/README.md)**

**🤖 AI Agent Instructions: [AGENTS.md](AGENTS.md)** - Guidelines for AI agents working with this codebase

### What's Included

- **SecureKeyManager** - Encrypted API key storage with environment variable fallback
- **AgentFrameworkWrapper** - Multi-backend AI agent framework (OpenAI, Anthropic, AutoGen, etc.)

**To use in your project:** Simply copy the `reusable/` directory to your project!

## Features
- Interactive network topology visualization using D3.js
- Device status monitoring
- Network health metrics
- Proxy-aware SSL handling
- Secure API key storage
- Dual API mode: Custom implementation or Official SDK
- **Reusable components for API key management and AI agents**
- **Self-healing agent system** with multi-backend support (OpenAI, Ollama, AutoGen, etc.)

## Installation

### Prerequisites
- Python 3.7+
- `uv` package manager (install with: `pip install uv`)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/kmransom56/meraki-clu-network-visuals.git
   cd meraki-clu-network-visuals
   ```

2. Install `uv` (if not already installed):
   
   **Windows (using winget):**
   ```pwsh
   winget install --id=astral-sh.uv -e
   ```
   
   **Using pipx (recommended for isolated installation):**
   ```bash
   pipx install uv
   ```
   
   **Using pip (alternative):**
   ```bash
   pip install uv
   ```

3. Create a virtual environment using `uv`:
   ```bash
   uv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On Unix/macOS:
     ```bash
     source .venv/bin/activate
     ```

5. Install the required packages using `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```

6. Run the application:
   ```bash
   python main.py
   ```

### Alternative: Using `uv` without activating venv
You can also run commands directly with `uv` without activating the virtual environment:
```bash
uv run python main.py
```

## API Mode Selection
The application now supports two API modes:

1. **Custom API Implementation (Default)**
   - Uses the custom API implementation with robust error handling
   - Includes special handling for Windows proxy environments (like Zscaler)
   - Recommended for most users, especially in corporate environments with proxies

2. **Official Meraki SDK**
   - Uses the official Meraki Dashboard API Python SDK
   - Provides access to all API endpoints
   - May have limitations in some proxy environments

You can switch between modes in the main menu.

## SSL Certificate Handling
The application implements a robust SSL verification strategy:
- Primary: Attempts secure verification using system CA certificates
- Fallback: For Windows proxy environments, disables verification if primary fails
- Clear error messages for troubleshooting

## Security Features
- API keys are stored securely using Fernet encryption
- SSL certificate handling with proxy support
- Environment variable support for API keys
- Comprehensive error handling and logging

## Reusable Components

This project includes a **reusable components package** (`reusable/`) that provides:

### SecureKeyManager
- 🔐 Fernet encryption for secure storage
- 💾 SQLite database for persistence
- 🔄 Environment variable fallback support
- 🏷️ App-specific storage isolation
- 📦 Multiple key storage support

### AgentFrameworkWrapper
- 🤖 Multi-backend support (OpenAI, Anthropic, AutoGen, Magentic One, Ollama)
- 🔑 Integrated with SecureKeyManager
- 💬 Simple chat interface
- 🔍 Code analysis capabilities
- 🏠 **Local LLM support** via Ollama (no API costs, complete privacy)

**Integration is simple:** Copy the `reusable/` directory to your project and import!

See [REUSABLE_COMPONENTS.md](REUSABLE_COMPONENTS.md) for detailed integration instructions.

## 🤖 Self-Healing Agent System

This application includes a comprehensive **self-auditing and self-healing agent system** that automatically:
- Analyzes logs and identifies issues
- Scans codebase for bugs and optimization opportunities
- Automatically repairs common issues
- Learns from patterns to improve over time
- Optimizes code performance and quality

### Quick Start

1. **Install agent dependencies:**
   ```bash
   pip install pyautogen magentic docker openai
   ```

2. **Configure the agent system:**
   ```bash
   cp agents/config.example.json agents/config.json
   # Edit agents/config.json with your API keys
   ```

3. **Use from main menu:**
   - Run `python main.py`
   - Select option `11. Self-Healing Agent System`

**📖 Full documentation: [agents/README.md](agents/README.md)**

### Using Ollama (Local LLM)

The agent system supports **Ollama** for running local LLM models without API costs:

1. **Install Ollama:**
   - Visit [https://ollama.ai](https://ollama.ai) for installation instructions
   - Follow the official Ollama documentation for your platform

2. **Pull a model:**
   ```bash
   ollama pull llama2
   # Or other models: mistral, codellama, phi, etc.
   ```

3. **Configure for Ollama:**
   ```bash
   cp agents/config.ollama.example.json agents/config.json
   ```
   
   Or manually edit `agents/config.json`:
   ```json
   {
     "backend": "openai",
     "base_url": "http://localhost:11434/v1",
     "model": "llama2",
     "api_key": "ollama"
   }
   ```

**📚 For detailed Ollama setup, see the [official Ollama documentation](https://github.com/ollama/ollama/blob/main/docs/README.md)**

**Benefits of Ollama:**
- ✅ No API costs - runs completely locally
- ✅ Complete privacy - data never leaves your machine
- ✅ Works offline - no internet connection required
- ✅ Supports many models - llama2, mistral, codellama, and more

## Requirements
- Python 3.7+
- `uv` package manager (install with: `pip install uv`)
- See `requirements.txt` for Python dependencies

Dependency Governance & Drift Protection
This project includes a full, automated dependency‑governance workflow designed to ensure:

deterministic builds

reproducible environments

drift detection before merge

runtime validation

rollback safety

compliance‑ready signed artifacts

Workflow Overview
Stage	Description
1. Pre‑Commit Drift Check	Prevents developers from committing code that introduces new imports without updating requirements.txt.
2. CI Regeneration	CI regenerates requirements.txt using pipreqs, reinstalls dependencies, and freezes a deterministic requirements.lock.
3. Drift Detection	CI compares the regenerated lock file to the committed version. Any mismatch fails the pipeline.
4. Runtime Validation	FastAPI validates required imports at startup and exposes a /admin/dependencies endpoint for live drift monitoring.
5. Rollback Workflow	A PowerShell script restores the last known‑good dependency set.
6. Signed Artifacts	CI signs the requirements.lock file for compliance and auditing.
Key Files
Code
Makefile                     → Automated dependency regeneration
.pre-commit-config.yaml      → Pre-commit drift prevention
.github/workflows/           → CI dependency audit pipeline
scripts/bootstrap.ps1        → Environment bootstrap
scripts/rollback_requirements.ps1 → Rollback workflow
scripts/sign_requirements.py → Signed artifact generator
api/dependency_dashboard.py  → JSON emitter for admin panel
api/dependency_validator.py  → Runtime dependency validator

## About Outset Solutions

**Outset Solutions** is a professional software development company specializing in network management and automation tools. This Meraki Management Utility is part of our suite of enterprise-grade network administration solutions.

### Contact Information

- **Website:** https://www.outsetsolutions.com
- **Application:** Meraki Management Utility v2.0
- **Maintained by:** Outset Solutions

### License

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.

Original work by Matia Zanella and Keith Ransom. Maintained and enhanced by Outset Solutions.
