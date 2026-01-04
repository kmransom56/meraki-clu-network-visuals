"""
Agent Manager - Main interface for the self-healing agent system
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .agent_framework import AgentFramework, AgentBackend
from .log_analyzer import LogAnalyzer
from .code_analyzer import CodeAnalyzer
from .repair_agent import RepairAgent
from .learning_agent import LearningAgent
from .optimization_agent import OptimizationAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Main manager for the self-auditing and self-healing agent system
    """
    
    def __init__(self, backend: AgentBackend = None, config: Optional[Dict] = None):
        # Load config if not provided
        if config is None:
            config = self._load_config()
        
        # Determine backend from config if not provided
        if backend is None:
            backend_str = config.get('backend', 'autogen').lower()
            backend_map = {
                'autogen': AgentBackend.AUTOGEN,
                'magentic_one': AgentBackend.MAGENTIC_ONE,
                'docker_cagent': AgentBackend.DOCKER_CAGENT,
                'openai': AgentBackend.OPENAI,
                'ollama': AgentBackend.OPENAI  # Ollama uses OpenAI-compatible API
            }
            backend = backend_map.get(backend_str, AgentBackend.AUTOGEN)
        
        # Expand environment variables in config
        config = self._expand_env_vars(config)
        
        self.agent_framework = AgentFramework(backend, config)
        self.log_analyzer = LogAnalyzer(self.agent_framework)
        self.code_analyzer = CodeAnalyzer(self.agent_framework)
        self.repair_agent = RepairAgent(self.agent_framework)
        self.learning_agent = LearningAgent(self.agent_framework)
        self.optimization_agent = OptimizationAgent(self.agent_framework)
        self.status_file = Path('agent_status.json')
    
    def _load_config(self) -> Dict:
        """Load configuration from config.json"""
        config_path = Path('agents/config.json')
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        # Return default config
        return {
            'backend': 'autogen',
            'model': 'gpt-4',
            'config_list': [{
                'model': 'gpt-4',
                'api_key': os.getenv('OPENAI_API_KEY', '')
            }]
        }
    
    def _expand_env_vars(self, config: Dict) -> Dict:
        """Expand environment variables in config (e.g., ${VAR})"""
        import re
        
        def expand_value(value):
            if isinstance(value, str):
                # Replace ${VAR} with environment variable
                def replace_env(match):
                    var_name = match.group(1)
                    return os.getenv(var_name, match.group(0))
                return re.sub(r'\$\{([^}]+)\}', replace_env, value)
            elif isinstance(value, dict):
                return {k: expand_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [expand_value(item) for item in value]
            return value
        
        return expand_value(config)
    
    def run_full_audit(self) -> Dict[str, Any]:
        """
        Run a full audit of the application
        
        Returns:
            Complete audit results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'log_analysis': {},
            'code_analysis': {},
            'recommendations': []
        }
        
        try:
            # Analyze logs
            logger.info("Analyzing logs...")
            results['log_analysis'] = self.log_analyzer.analyze_logs(hours=24)
            
            # Analyze code
            logger.info("Analyzing code...")
            results['code_analysis'] = self.code_analyzer.analyze_codebase()
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
            results['status'] = 'completed'
        
        except Exception as e:
            logger.error(f"Audit failed: {e}", exc_info=True)
            results['status'] = 'failed'
            results['error'] = str(e)
        
        self._save_status(results)
        return results
    
    def run_auto_repair(self, repair_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run automatic repairs
        
        Args:
            repair_types: Types of repairs to perform
            
        Returns:
            Repair results
        """
        logger.info("Starting auto-repair...")
        results = self.repair_agent.auto_repair(repair_types)
        
        # Learn from repairs
        for repair in results.get('repairs', []):
            if repair.get('status') == 'success':
                self.learning_agent.learn_from_error(
                    {'type': repair.get('type')},
                    repair
                )
        
        self._save_status(results)
        return results
    
    def run_optimization(self, optimization_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run optimizations
        
        Args:
            optimization_types: Types of optimizations to perform
            
        Returns:
            Optimization results
        """
        logger.info("Starting optimization...")
        results = self.optimization_agent.optimize_application(optimization_types)
        
        # Learn from optimizations
        for opt in results.get('optimizations', []):
            self.learning_agent.learn_from_optimization(opt, opt)
        
        self._save_status(results)
        return results
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get insights from learned patterns
        
        Returns:
            Insights dictionary
        """
        return self.learning_agent.generate_insights()
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations from audit results"""
        recommendations = []
        
        # From log analysis
        log_recs = results.get('log_analysis', {}).get('recommendations', [])
        recommendations.extend(log_recs)
        
        # From code analysis
        code_recs = results.get('code_analysis', {}).get('recommendations', [])
        recommendations.extend(code_recs)
        
        # From learning agent
        insights = self.learning_agent.generate_insights()
        recommendations.extend(insights.get('recommendations', []))
        
        return list(set(recommendations))  # Remove duplicates
    
    def _save_status(self, results: Dict):
        """Save agent status to file"""
        try:
            status = {
                'last_run': datetime.now().isoformat(),
                'results': results
            }
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving status: {e}")
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        status = {
            'status': 'ready' if self.agent_framework.agent is not None else 'not_available',
            'agent_available': self.agent_framework.agent is not None,
            'backend': self.agent_framework.backend.value,
            'config_loaded': True
        }
        
        # Check if API key is configured
        if self.agent_framework.agent:
            status['api_key_configured'] = True
        else:
            status['api_key_configured'] = False
            status['error'] = 'Agent not initialized. Check API key configuration.'
        
        # Merge with saved status if exists
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    saved_status = json.load(f)
                    # Merge but keep current agent state
                    status.update({k: v for k, v in saved_status.items() 
                                  if k not in ['agent_available', 'backend', 'config_loaded', 'api_key_configured']})
            except Exception as e:
                logger.error(f"Error reading status: {e}")
        
        return status
