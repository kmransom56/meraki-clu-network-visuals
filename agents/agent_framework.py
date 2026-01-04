"""
Agent Framework - Supports multiple agent backends
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentBackend(Enum):
    """Supported agent backends"""
    AUTOGEN = "autogen"
    MAGENTIC_ONE = "magentic_one"
    DOCKER_CAGENT = "docker_cagent"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AgentFramework:
    """
    Unified agent framework supporting multiple backends
    """
    
    def __init__(self, backend: AgentBackend = AgentBackend.AUTOGEN, config: Optional[Dict] = None):
        self.backend = backend
        self.config = config or {}
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the appropriate agent backend"""
        try:
            if self.backend == AgentBackend.AUTOGEN:
                self.agent = self._init_autogen()
            elif self.backend == AgentBackend.MAGENTIC_ONE:
                self.agent = self._init_magentic_one()
            elif self.backend == AgentBackend.DOCKER_CAGENT:
                self.agent = self._init_docker_cagent()
            elif self.backend == AgentBackend.OPENAI:
                self.agent = self._init_fallback()
            else:
                logger.warning(f"Backend {self.backend} not fully implemented, using fallback")
                self.agent = self._init_fallback()
            
            # If agent initialization failed, try fallback
            if self.agent is None:
                logger.warning(f"Backend {self.backend} initialization returned None, using fallback")
                self.agent = self._init_fallback()
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.backend}: {e}")
            self.agent = self._init_fallback()
    
    def _init_autogen(self):
        """Initialize Microsoft AutoGen agent"""
        try:
            # AutoGen 0.10.0+ has a different API structure
            # For now, we'll use the fallback OpenAI approach
            # AutoGen integration can be enhanced later with the new API
            logger.info("AutoGen backend requested, using OpenAI fallback for compatibility")
            return self._init_fallback()
        except Exception as e:
            logger.warning(f"AutoGen initialization failed: {e}, using fallback")
            return self._init_fallback()
    
    def _init_magentic_one(self):
        """Initialize Magentic One agent"""
        try:
            from magentic import ChatModel, FunctionCall
            
            # Get API key from config or environment
            api_key = None
            
            # Try config_list first
            if self.config.get('config_list'):
                api_key = self.config['config_list'][0].get('api_key', '')
            
            # Try direct config.api_key
            if not api_key:
                api_key = self.config.get('api_key', '')
            
            # Fallback to environment variable
            if not api_key:
                api_key = os.getenv('OPENAI_API_KEY', '')
            
            if not api_key:
                logger.error("No API key found for Magentic One in config or environment")
                return None
            
            model = ChatModel(
                model=self.config.get('model', 'gpt-4'),
                api_key=api_key
            )
            
            return model
        except ImportError:
            logger.warning("Magentic One not installed. Install with: pip install magentic")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Magentic One: {e}")
            return None
    
    def _init_docker_cagent(self):
        """Initialize Docker Cagent agent"""
        try:
            import docker
            from docker import DockerClient
            
            client = docker.from_env()
            # Cagent typically runs in a container
            # This is a placeholder - adjust based on your Cagent setup
            return client
        except ImportError:
            logger.warning("Docker SDK not installed. Install with: pip install docker")
            return None
    
    def _init_fallback(self):
        """Fallback agent using basic OpenAI API (supports OpenAI and Ollama)"""
        try:
            import openai
            
            # Get base_url from config (for Ollama support)
            base_url = None
            if self.config.get('config_list'):
                base_url = self.config['config_list'][0].get('base_url', '')
            if not base_url:
                base_url = self.config.get('base_url', '')
            if not base_url:
                base_url = os.getenv('OPENAI_BASE_URL', '')
            
            # Check if using Ollama (default local endpoint)
            is_ollama = False
            if base_url and ('ollama' in base_url.lower() or 'localhost:11434' in base_url):
                is_ollama = True
                if not base_url.startswith('http'):
                    base_url = 'http://localhost:11434/v1'
                elif '/v1' not in base_url:
                    base_url = base_url.rstrip('/') + '/v1'
            elif base_url == 'ollama' or self.config.get('backend', '').lower() == 'ollama':
                is_ollama = True
                base_url = 'http://localhost:11434/v1'
            
            # Get API key from config or environment
            api_key = None
            if not is_ollama:  # Ollama doesn't require API key
                # Try config_list first
                if self.config.get('config_list'):
                    api_key = self.config['config_list'][0].get('api_key', '')
                
                # Try direct config.api_key
                if not api_key:
                    api_key = self.config.get('api_key', '')
                
                # Fallback to environment variable
                if not api_key:
                    api_key = os.getenv('OPENAI_API_KEY', '')
                
                if not api_key:
                    logger.error("No OpenAI API key found in config or environment variables")
                    return None
            else:
                # Ollama doesn't require API key, but some setups use "ollama" as placeholder
                api_key = os.getenv('OLLAMA_API_KEY', 'ollama')
            
            # Initialize OpenAI client with optional base_url for Ollama
            client_kwargs = {}
            if base_url:
                client_kwargs['base_url'] = base_url
            if api_key:
                client_kwargs['api_key'] = api_key
            
            client = openai.OpenAI(**client_kwargs)
            
            if is_ollama:
                logger.info(f"Initialized Ollama client (base_url: {base_url})")
            else:
                logger.info("Initialized OpenAI client")
            
            return client
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI/Ollama client: {e}")
            return None
    
    def analyze(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze a prompt with context and return results
        
        Args:
            prompt: The analysis prompt
            context: Additional context (logs, code, etc.)
            
        Returns:
            Analysis results dictionary
        """
        if not self.agent:
            return {"error": "Agent not initialized", "backend": self.backend.value}
        
        try:
            if self.backend == AgentBackend.AUTOGEN:
                return self._analyze_autogen(prompt, context)
            elif self.backend == AgentBackend.MAGENTIC_ONE:
                return self._analyze_magentic_one(prompt, context)
            else:
                return self._analyze_fallback(prompt, context)
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {"error": str(e), "backend": self.backend.value}
    
    def _analyze_autogen(self, prompt: str, context: Optional[Dict]) -> Dict:
        """Analyze using AutoGen"""
        if not self.agent:
            return {"error": "AutoGen agent not initialized"}
        
        full_prompt = prompt
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        response = self.agent.generate_reply([{"role": "user", "content": full_prompt}])
        
        return {
            "response": response,
            "backend": "autogen",
            "status": "success"
        }
    
    def _analyze_magentic_one(self, prompt: str, context: Optional[Dict]) -> Dict:
        """Analyze using Magentic One"""
        if not self.agent:
            return {"error": "Magentic One agent not initialized"}
        
        full_prompt = prompt
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        response = self.agent.complete(full_prompt)
        
        return {
            "response": response,
            "backend": "magentic_one",
            "status": "success"
        }
    
    def _analyze_fallback(self, prompt: str, context: Optional[Dict]) -> Dict:
        """Fallback analysis using OpenAI directly (supports OpenAI and Ollama)"""
        if not self.agent:
            return {"error": "Fallback agent not initialized"}
        
        full_prompt = prompt
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        # Get model from config (default to llama2 for Ollama, gpt-4 for OpenAI)
        model = self.config.get('model', 'gpt-4')
        
        # If base_url suggests Ollama and model is still gpt-4, try common Ollama models
        base_url = self.config.get('base_url', '')
        if 'ollama' in base_url.lower() or 'localhost:11434' in base_url:
            if model == 'gpt-4':
                # Try to detect Ollama model from config or use default
                model = self.config.get('ollama_model', 'llama2')
        
        response = self.agent.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        backend_name = "ollama" if ('ollama' in base_url.lower() or 'localhost:11434' in base_url) else "openai"
        
        return {
            "response": response.choices[0].message.content,
            "backend": f"{backend_name}_fallback",
            "status": "success"
        }
    
    def execute_action(self, action: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute an action (repair, update, optimize, etc.)
        
        Args:
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Execution results
        """
        # This will be implemented by specific agent types
        return {"status": "not_implemented", "action": action}
