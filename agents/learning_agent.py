"""
Learning Agent - Learns from patterns and improves over time
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from .agent_framework import AgentFramework, AgentBackend

logger = logging.getLogger(__name__)


class LearningAgent:
    """
    Learns from application patterns, errors, and fixes to improve over time
    """
    
    def __init__(self, agent_framework: Optional[AgentFramework] = None):
        self.agent = agent_framework or AgentFramework(AgentBackend.AUTOGEN)
        self.knowledge_base = Path('agent_knowledge.json')
        self.patterns = self._load_knowledge()
        self.learning_history = []
    
    def _load_knowledge(self) -> Dict:
        """Load knowledge base from file"""
        if self.knowledge_base.exists():
            try:
                with open(self.knowledge_base, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading knowledge base: {e}")
        
        return {
            'error_patterns': {},
            'fix_patterns': {},
            'optimization_patterns': {},
            'user_preferences': {},
            'learned_rules': []
        }
    
    def _save_knowledge(self):
        """Save knowledge base to file"""
        try:
            with open(self.knowledge_base, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def learn_from_error(self, error: Dict, fix: Optional[Dict] = None):
        """
        Learn from an error and its fix
        
        Args:
            error: Error information
            fix: Fix information (if available)
        """
        error_type = error.get('type', 'unknown')
        error_message = error.get('message', '')
        
        # Update error patterns
        if error_type not in self.patterns['error_patterns']:
            self.patterns['error_patterns'][error_type] = {
                'count': 0,
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'messages': []
            }
        
        pattern = self.patterns['error_patterns'][error_type]
        pattern['count'] += 1
        pattern['last_seen'] = datetime.now().isoformat()
        
        if error_message and error_message not in pattern['messages']:
            pattern['messages'].append(error_message)
        
        # Learn fix pattern if available
        if fix:
            fix_key = f"{error_type}_{fix.get('action', 'unknown')}"
            if fix_key not in self.patterns['fix_patterns']:
                self.patterns['fix_patterns'][fix_key] = {
                    'error_type': error_type,
                    'fix_action': fix.get('action'),
                    'success_count': 0,
                    'failure_count': 0
                }
            
            fix_pattern = self.patterns['fix_patterns'][fix_key]
            if fix.get('status') == 'success':
                fix_pattern['success_count'] += 1
            else:
                fix_pattern['failure_count'] += 1
        
        self._save_knowledge()
    
    def learn_from_optimization(self, optimization: Dict, result: Dict):
        """
        Learn from optimization attempts
        
        Args:
            optimization: Optimization information
            result: Result of optimization
        """
        opt_type = optimization.get('type', 'unknown')
        
        if opt_type not in self.patterns['optimization_patterns']:
            self.patterns['optimization_patterns'][opt_type] = {
                'attempts': 0,
                'successes': 0,
                'improvements': []
            }
        
        pattern = self.patterns['optimization_patterns'][opt_type]
        pattern['attempts'] += 1
        
        if result.get('status') == 'success':
            pattern['successes'] += 1
            if 'improvement' in result:
                pattern['improvements'].append(result['improvement'])
        
        self._save_knowledge()
    
    def get_suggested_fix(self, error: Dict) -> Optional[Dict]:
        """
        Get suggested fix based on learned patterns
        
        Args:
            error: Error information
            
        Returns:
            Suggested fix or None
        """
        error_type = error.get('type', 'unknown')
        
        # Look for learned fix patterns
        for fix_key, fix_pattern in self.patterns['fix_patterns'].items():
            if fix_pattern['error_type'] == error_type:
                # Check success rate
                total = fix_pattern['success_count'] + fix_pattern['failure_count']
                if total > 0:
                    success_rate = fix_pattern['success_count'] / total
                    if success_rate > 0.7:  # 70% success rate threshold
                        return {
                            'action': fix_pattern['fix_action'],
                            'confidence': success_rate,
                            'source': 'learned_pattern'
                        }
        
        return None
    
    def generate_insights(self) -> Dict[str, Any]:
        """
        Generate insights from learned patterns
        
        Returns:
            Insights dictionary
        """
        insights = {
            'timestamp': datetime.now().isoformat(),
            'common_errors': [],
            'effective_fixes': [],
            'optimization_opportunities': [],
            'recommendations': []
        }
        
        # Find most common errors
        error_patterns = sorted(
            self.patterns['error_patterns'].items(),
            key=lambda x: x[1].get('count', 0),
            reverse=True
        )[:5]
        
        for error_type, pattern in error_patterns:
            insights['common_errors'].append({
                'type': error_type,
                'count': pattern.get('count', 0),
                'first_seen': pattern.get('first_seen'),
                'last_seen': pattern.get('last_seen')
            })
        
        # Find most effective fixes
        fix_patterns = sorted(
            self.patterns['fix_patterns'].items(),
            key=lambda x: x[1].get('success_count', 0),
            reverse=True
        )[:5]
        
        for fix_key, pattern in fix_patterns:
            total = pattern['success_count'] + pattern['failure_count']
            if total > 0:
                insights['effective_fixes'].append({
                    'error_type': pattern['error_type'],
                    'fix_action': pattern['fix_action'],
                    'success_rate': pattern['success_count'] / total,
                    'total_attempts': total
                })
        
        # Generate recommendations using AI
        insights['recommendations'] = self._generate_ai_recommendations(insights)
        
        return insights
    
    def _generate_ai_recommendations(self, insights: Dict) -> List[str]:
        """Generate recommendations using AI agent"""
        prompt = f"""Based on these learned patterns, provide recommendations:
        
Common Errors: {json.dumps(insights['common_errors'], indent=2)}
Effective Fixes: {json.dumps(insights['effective_fixes'], indent=2)}

Provide actionable recommendations to prevent recurring issues."""
        
        try:
            analysis = self.agent.analyze(prompt, insights)
            if 'response' in analysis:
                return self._parse_recommendations(analysis['response'])
        except Exception as e:
            logger.error(f"Failed to generate AI recommendations: {e}")
        
        return []
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """Parse recommendations from AI response"""
        recommendations = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or 
                        line[0].isdigit()):
                recommendations.append(line.lstrip('-* ').lstrip('0123456789.) '))
        return recommendations if recommendations else [response]
