"""
Optimization Agent - Optimizes application performance and code quality
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .agent_framework import AgentFramework, AgentBackend
from .code_analyzer import CodeAnalyzer
from .learning_agent import LearningAgent

logger = logging.getLogger(__name__)


class OptimizationAgent:
    """
    Optimizes application performance, code quality, and user experience
    """
    
    def __init__(self, agent_framework: Optional[AgentFramework] = None):
        self.agent = agent_framework or AgentFramework(AgentBackend.AUTOGEN)
        self.code_analyzer = CodeAnalyzer(agent_framework)
        self.learning_agent = LearningAgent(agent_framework)
    
    def optimize_application(self, optimization_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Optimize the application
        
        Args:
            optimization_types: Types of optimizations to perform
            
        Returns:
            Optimization results
        """
        optimization_types = optimization_types or ['code', 'performance', 'dependencies']
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations': [],
            'improvements': [],
            'metrics_before': {},
            'metrics_after': {}
        }
        
        # Analyze current state
        code_analysis = self.code_analyzer.analyze_codebase()
        results['metrics_before'] = code_analysis.get('metrics', {})
        
        # Perform optimizations
        if 'code' in optimization_types:
            code_optimizations = self._optimize_code(code_analysis)
            results['optimizations'].extend(code_optimizations)
        
        if 'performance' in optimization_types:
            perf_optimizations = self._optimize_performance()
            results['optimizations'].extend(perf_optimizations)
        
        if 'dependencies' in optimization_types:
            dep_optimizations = self._optimize_dependencies()
            results['optimizations'].extend(dep_optimizations)
        
        # Analyze after optimizations
        code_analysis_after = self.code_analyzer.analyze_codebase()
        results['metrics_after'] = code_analysis_after.get('metrics', {})
        
        # Calculate improvements
        results['improvements'] = self._calculate_improvements(
            results['metrics_before'],
            results['metrics_after']
        )
        
        return results
    
    def _optimize_code(self, analysis: Dict) -> List[Dict]:
        """Optimize code based on analysis"""
        optimizations = []
        
        for opt in analysis.get('optimizations', []):
            opt_type = opt.get('type')
            
            if opt_type == 'inefficient_iteration':
                optimization = self._optimize_iteration(opt)
                optimizations.append(optimization)
            elif opt_type == 'multiple_append':
                optimization = self._optimize_append(opt)
                optimizations.append(optimization)
        
        return optimizations
    
    def _optimize_iteration(self, optimization: Dict) -> Dict:
        """Optimize inefficient iteration patterns"""
        file_path = optimization.get('file')
        
        if not file_path or not os.path.exists(file_path):
            return {
                'type': 'iteration',
                'status': 'skipped',
                'reason': 'File not found'
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace range(len()) with enumerate()
            optimized_content = content.replace(
                'for i in range(len(',
                'for i, item in enumerate('
            )
            
            if optimized_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)
                
                return {
                    'type': 'iteration',
                    'status': 'success',
                    'action': f'Optimized iteration in {file_path}',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'type': 'iteration',
                'status': 'failed',
                'error': str(e)
            }
        
        return {
            'type': 'iteration',
            'status': 'skipped',
            'reason': 'No changes needed'
        }
    
    def _optimize_append(self, optimization: Dict) -> Dict:
        """Optimize multiple append operations"""
        # This would require more sophisticated pattern matching
        return {
            'type': 'append',
            'status': 'skipped',
            'reason': 'Requires manual review'
        }
    
    def _optimize_performance(self) -> List[Dict]:
        """Optimize application performance"""
        optimizations = []
        
        # Check for common performance issues
        # This is a placeholder - would need profiling data
        
        return optimizations
    
    def _optimize_dependencies(self) -> List[Dict]:
        """Optimize dependencies"""
        optimizations = []
        
        # Check for outdated dependencies
        if os.path.exists('requirements.txt'):
            try:
                import subprocess
                result = subprocess.run(
                    ['pip', 'list', '--outdated'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout:
                    optimizations.append({
                        'type': 'dependencies',
                        'status': 'suggested',
                        'action': 'Update outdated dependencies',
                        'details': result.stdout,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error checking dependencies: {e}")
        
        return optimizations
    
    def _calculate_improvements(self, before: Dict, after: Dict) -> List[Dict]:
        """Calculate improvements from optimizations"""
        improvements = []
        
        for metric in ['total_issues', 'high_severity', 'optimization_opportunities']:
            before_val = before.get(metric, 0)
            after_val = after.get(metric, 0)
            
            if before_val > after_val:
                improvement = ((before_val - after_val) / before_val) * 100
                improvements.append({
                    'metric': metric,
                    'improvement': f"{improvement:.1f}%",
                    'before': before_val,
                    'after': after_val
                })
        
        return improvements
