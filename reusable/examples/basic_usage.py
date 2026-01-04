#!/usr/bin/env python3
"""
Basic Usage Example - Reusable Components

This example demonstrates how to use the reusable components
in a simple application.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reusable.secure_key_manager import SecureKeyManager
from reusable.agent_framework_wrapper import AgentFrameworkWrapper, AgentBackend


def main():
    print("=" * 60)
    print("Reusable Components - Basic Usage Example")
    print("=" * 60)
    
    # Step 1: Initialize key manager
    print("\n1. Initializing Secure Key Manager...")
    key_manager = SecureKeyManager(app_name="example_app")
    print(f"   Database location: {key_manager.db_path}")
    
    # Step 2: Check for existing API key
    print("\n2. Checking for API key...")
    api_key = key_manager.get_key(
        "openai_api_key",
        env_var_name="OPENAI_API_KEY"
    )
    
    if not api_key:
        print("   No API key found. Please enter one:")
        api_key = input("   OpenAI API Key: ").strip()
        if api_key:
            if key_manager.save_key("openai_api_key", api_key, env_var_name="OPENAI_API_KEY"):
                print("   ✓ API key saved securely")
            else:
                print("   ✗ Failed to save API key")
                return
        else:
            print("   No API key provided. Exiting.")
            return
    else:
        print("   ✓ API key found (from environment or storage)")
    
    # Step 3: Initialize agent framework
    print("\n3. Initializing Agent Framework...")
    agent = AgentFrameworkWrapper(
        backend=AgentBackend.OPENAI,
        api_key_manager=key_manager
    )
    
    if not agent.is_available():
        print("   ✗ Agent framework not available")
        print("   Install dependencies: pip install openai")
        return
    
    print(f"   ✓ Agent framework ready (Backend: {agent.get_backend_name()})")
    
    # Step 4: Use the agent
    print("\n4. Testing Agent...")
    print("   Sending test message...")
    
    response = agent.chat("Say 'Hello, World!' in a creative way.")
    if response:
        print(f"   Response: {response}")
    else:
        print("   ✗ No response received")
    
    # Step 5: List stored keys
    print("\n5. Stored Keys:")
    keys = key_manager.list_keys()
    if keys:
        for key in keys:
            print(f"   - {key}")
    else:
        print("   (no keys stored)")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
