"""
Reusable Components Package

This package provides reusable components for API key management and AI agent frameworks
that can be easily integrated into other applications.

Modules:
    - secure_key_manager: Secure API key storage and retrieval
    - agent_framework: Multi-backend AI agent framework
"""

from .secure_key_manager import SecureKeyManager
from .agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend

__all__ = ['SecureKeyManager', 'AgentFrameworkWrapper', 'AgentBackend']

__version__ = '1.0.0'
