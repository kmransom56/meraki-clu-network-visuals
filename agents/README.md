# Self-Auditing and Self-Healing Agent System

A comprehensive AI-powered agent system that automatically audits, repairs, optimizes, and learns from your Meraki CLI application.

## Features

- **Log Analysis**: Automatically analyzes application logs to identify errors and patterns
- **Code Analysis**: Scans codebase for issues, bugs, and optimization opportunities
- **Auto-Repair**: Automatically fixes common issues found in logs and code
- **Optimization**: Optimizes code performance and quality
- **Learning**: Learns from patterns to improve over time
- **Multi-Backend Support**: Supports AutoGen, Magentic One, Docker Cagent, OpenAI, and Ollama (local LLM)

## Installation

### Required Dependencies

```bash
# Core dependencies (already in requirements.txt)
pip install -r requirements.txt

# Optional: Agent backends (choose one or more)
pip install pyautogen          # Microsoft AutoGen
pip install magentic           # Magentic One
pip install docker             # Docker Cagent
pip install openai             # OpenAI Direct
```

### Configuration

1. Copy the example config:
```bash
cp agents/config.example.json agents/config.json
```

2. Edit `agents/config.json` and set your API keys:
```json
{
  "backend": "autogen",
  "model": "gpt-4",
  "config_list": [
    {
      "model": "gpt-4",
      "api_key": "your-api-key-here"
    }
  ]
}
```

3. Set environment variable (alternative):
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### From Main Menu

1. Run the application: `python main.py`
2. Select option `11. Self-Healing Agent System`
3. Choose from the agent menu options

### From Command Line

```bash
# Run full audit
python -m agents.cli audit

# Run auto-repair
python -m agents.cli repair --types logs code dependencies

# Run optimization
python -m agents.cli optimize --types code performance dependencies

# View insights
python -m agents.cli insights

# Check status
python -m agents.cli status
```

## Agent Components

### 1. Log Analyzer (`log_analyzer.py`)
- Analyzes `meraki_clu_debug.log` and `log/error.log`
- Identifies error patterns and frequencies
- Generates recommendations using AI

### 2. Code Analyzer (`code_analyzer.py`)
- Scans Python files for issues
- Detects common anti-patterns
- Finds optimization opportunities

### 3. Repair Agent (`repair_agent.py`)
- Automatically fixes import errors
- Repairs code issues (bare except, syntax errors, etc.)
- Updates dependencies
- Creates backups before modifications

### 4. Learning Agent (`learning_agent.py`)
- Learns from errors and fixes
- Builds knowledge base of patterns
- Suggests fixes based on learned patterns

### 5. Optimization Agent (`optimization_agent.py`)
- Optimizes code performance
- Improves code quality
- Updates dependencies

### 6. Agent Manager (`agent_manager.py`)
- Main interface for all agents
- Coordinates agent activities
- Manages agent status and history

## Supported Backends

### Microsoft AutoGen
```python
from agents.agent_framework import AgentBackend
manager = AgentManager(AgentBackend.AUTOGEN)
```

### Magentic One
```python
manager = AgentManager(AgentBackend.MAGENTIC_ONE)
```

### Docker Cagent
```python
manager = AgentManager(AgentBackend.DOCKER_CAGENT)
```

### OpenAI Direct
```python
manager = AgentManager(AgentBackend.OPENAI)
```

### Ollama (Local LLM)
The OpenAI Direct backend also supports Ollama, a local LLM server. This allows you to run models locally without API costs.

**Installation & Setup:**

For detailed installation instructions, please refer to the [official Ollama documentation](https://github.com/ollama/ollama/blob/main/docs/README.md).

**Quick Setup:**
1. **Install Ollama** - Follow the [official installation guide](https://github.com/ollama/ollama#installation)
2. **Pull a model:**
   ```bash
   ollama pull llama2
   # See available models: https://ollama.ai/library
   ```
3. **Configure `agents/config.json`:**
   ```json
   {
     "backend": "openai",
     "base_url": "http://localhost:11434/v1",
     "model": "llama2",
     "api_key": "ollama"
   }
   ```

**Quick Start:**
```bash
# Copy Ollama example config
cp agents/config.ollama.example.json agents/config.json
```

**Available Models:**
Ollama supports many models. Popular choices include:
- `llama2`, `llama2:13b`, `llama2:70b` - General purpose
- `mistral`, `mixtral` - High performance
- `codellama` - Optimized for code tasks
- `phi`, `neural-chat`, `starling-lm` - Smaller, faster models
- `gemma`, `llava` - Google models

**See all available models:** [https://ollama.ai/library](https://ollama.ai/library)

**How It Works:**
The OpenAI backend automatically detects Ollama when `base_url` contains `localhost:11434` or `ollama`. Ollama uses an OpenAI-compatible API, so it works seamlessly with the existing backend.

**Benefits:**
- ✅ No API costs - runs completely locally
- ✅ Complete privacy - data never leaves your machine  
- ✅ Works offline - no internet connection required
- ✅ Supports many models - see [ollama.ai/library](https://ollama.ai/library)

## Knowledge Base

The agent system maintains a knowledge base in `agent_knowledge.json` that includes:
- Error patterns and frequencies
- Fix patterns and success rates
- Optimization patterns
- Learned rules

## Backup System

All repairs create backups in the `agent_backups/` directory before modifying files. Backups are timestamped and can be restored if needed.

## Status File

Agent status is saved to `agent_status.json` after each run, including:
- Last run timestamp
- Results summary
- Status (completed/failed/running)

## Examples

### Example 1: Full Audit
```python
from agents.agent_manager import AgentManager

manager = AgentManager()
results = manager.run_full_audit()

print(f"Errors found: {len(results['log_analysis']['errors'])}")
print(f"Issues found: {results['code_analysis']['metrics']['total_issues']}")
```

### Example 2: Auto-Repair
```python
manager = AgentManager()
results = manager.run_auto_repair(['logs', 'code'])

print(f"Repairs successful: {results['success']}")
print(f"Repairs failed: {results['failed']}")
```

### Example 3: Get Insights
```python
manager = AgentManager()
insights = manager.get_insights()

for error in insights['common_errors']:
    print(f"{error['type']}: {error['count']} occurrences")
```

## Troubleshooting

### Agent Not Initialized
- Check that required dependencies are installed
- Verify API key is set in config or environment
- Check logs for initialization errors

### Repairs Failing
- Check that files are writable
- Verify backups directory exists and is writable
- Review error logs for specific failure reasons

### No Recommendations
- Ensure AI backend is properly configured
- Check API key validity
- Review agent logs for API errors

## Security Notes

- API keys should be stored securely (use environment variables or encrypted config)
- Backups are created before any file modifications
- All repairs can be reviewed before application (set `auto_apply: false` in config)

## Future Enhancements

- Real-time monitoring and auto-repair
- Integration with CI/CD pipelines
- Custom agent plugins
- Multi-agent collaboration
- Performance profiling integration
