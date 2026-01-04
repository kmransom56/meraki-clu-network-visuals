#!/usr/bin/env python3
"""
Code Analyzer Example - Using Agent Framework for Code Analysis

This example shows how to use the agent framework to analyze code.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend


def analyze_code_example():
    """Example of analyzing code with the agent framework"""
    
    # Initialize components
    key_manager = SecureKeyManager(app_name="code_analyzer")
    
    # Get API key
    api_key = key_manager.get_key("openai_api_key", env_var_name="OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable or save it using SecureKeyManager")
        return
    
    # Initialize agent
    agent = AgentFrameworkWrapper(
        backend=AgentBackend.OPENAI,
        api_key_manager=key_manager
    )
    
    if not agent.is_available():
        print("Agent framework not available")
        return
    
    # Example code to analyze
    code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Usage
result = calculate_fibonacci(35)
print(result)
"""
    
    print("Analyzing code...")
    print("=" * 60)
    print(code)
    print("=" * 60)
    
    # Analyze for bugs
    print("\n1. Bug Analysis:")
    bug_analysis = agent.analyze_code(code, task="find bugs and potential issues")
    if bug_analysis:
        print(bug_analysis)
    
    # Analyze for optimization
    print("\n2. Optimization Suggestions:")
    opt_analysis = agent.analyze_code(code, task="suggest optimizations")
    if opt_analysis:
        print(opt_analysis)
    
    # General analysis
    print("\n3. General Analysis:")
    general = agent.analyze_code(code, task="analyze")
    if general:
        print(general)


if __name__ == "__main__":
    analyze_code_example()
