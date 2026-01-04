"""
Agent Framework Wrapper - Reusable AI Agent Framework

A reusable wrapper around the agent framework that can be easily integrated
into other applications.

Usage:
    from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend
    
    # Initialize with backend
    agent = AgentFrameworkWrapper(
        backend=AgentBackend.OPENAI,
        api_key_manager=key_manager  # Your SecureKeyManager instance
    )
    
    # Use the agent
    response = agent.chat("Analyze this code for bugs...")
"""

import os
import sys
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

# Add parent directory to path to import agents module
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from agents.agent_framework import AgentFramework, AgentBackend as OriginalAgentBackend
    from reusable.secure_key_manager import SecureKeyManager
except ImportError:
    # Fallback if agents module not available
    AgentFramework = None
    OriginalAgentBackend = None

logger = logging.getLogger(__name__)


class AgentBackend(Enum):
    """Supported agent backends"""
    AUTOGEN = "autogen"
    MAGENTIC_ONE = "magentic_one"
    DOCKER_CAGENT = "docker_cagent"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AgentFrameworkWrapper:
    """
    Wrapper around the agent framework for easy reuse in other applications.
    
    This wrapper provides a simplified interface to the agent framework
    and integrates with SecureKeyManager for API key management.
    """
    
    def __init__(self, backend: AgentBackend = AgentBackend.OPENAI,
                 api_key_manager: Optional[SecureKeyManager] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent framework wrapper.
        
        Args:
            backend: The agent backend to use
            api_key_manager: SecureKeyManager instance for API key management
            config: Additional configuration for the agent
        """
        self.backend = backend
        self.api_key_manager = api_key_manager
        self.config = config or {}
        self.agent_framework = None
        
        # Map our backend enum to the original
        if OriginalAgentBackend:
            backend_map = {
                AgentBackend.AUTOGEN: OriginalAgentBackend.AUTOGEN,
                AgentBackend.MAGENTIC_ONE: OriginalAgentBackend.MAGENTIC_ONE,
                AgentBackend.DOCKER_CAGENT: OriginalAgentBackend.DOCKER_CAGENT,
                AgentBackend.OPENAI: OriginalAgentBackend.OPENAI,
                AgentBackend.ANTHROPIC: OriginalAgentBackend.ANTHROPIC,
            }
            original_backend = backend_map.get(backend, OriginalAgentBackend.OPENAI)
        else:
            original_backend = None
        
        # Set up API keys from key manager
        self._setup_api_keys()
        
        # Initialize the agent framework
        if AgentFramework and original_backend:
            try:
                self.agent_framework = AgentFramework(original_backend, self.config)
            except Exception as e:
                logger.error(f"Failed to initialize agent framework: {e}")
                self.agent_framework = None
    
    def _setup_api_keys(self):
        """Set up API keys from the key manager"""
        if not self.api_key_manager:
            return
        
        # Common API key names to check
        api_keys = {
            'OPENAI_API_KEY': 'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY': 'ANTHROPIC_API_KEY',
        }
        
        for key_name, env_var in api_keys.items():
            api_key = self.api_key_manager.get_key(key_name, env_var_name=env_var)
            if api_key:
                os.environ[env_var] = api_key
                logger.info(f"Set {env_var} from key manager")
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Send a chat message to the agent.
        
        Args:
            message: The user message
            system_prompt: Optional system prompt
            
        Returns:
            Agent response or None if failed
        """
        if not self.agent_framework:
            logger.error("Agent framework not initialized")
            return None
        
        try:
            return self.agent_framework.chat(message, system_prompt)
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return None
    
    def analyze_code(self, code: str, task: str = "analyze") -> Optional[str]:
        """
        Analyze code using the agent.
        
        Args:
            code: The code to analyze
            task: Analysis task (e.g., "analyze", "optimize", "debug")
            
        Returns:
            Analysis result or None if failed
        """
        prompt = f"Please {task} the following code:\n\n```python\n{code}\n```"
        return self.chat(prompt)
    
    def is_available(self) -> bool:
        """Check if the agent framework is available and initialized"""
        return self.agent_framework is not None
    
    def get_backend_name(self) -> str:
        """Get the name of the current backend"""
        return self.backend.value
