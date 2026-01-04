"""
Configuration Loader - Read values from apikeys.ini file

This module provides functionality to read configuration values
from the apikeys.ini file.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict


def parse_apikeys_ini(file_path: str = "apikeys.ini") -> Dict[str, str]:
    """
    Parse apikeys.ini file and return a dictionary of key-value pairs.
    
    Supports:
    - KEY="VALUE"
    - KEY='VALUE'
    - KEY=VALUE (without quotes)
    - Lines starting with # are treated as comments
    - Empty lines are ignored
    
    Args:
        file_path: Path to the apikeys.ini file (default: "apikeys.ini")
        
    Returns:
        dict: Dictionary of key-value pairs
    """
    config = {}
    
    # Try to find the file in current directory or project root
    if not os.path.exists(file_path):
        # Try project root
        project_root = Path(__file__).parent.parent
        file_path = project_root / file_path
        if not file_path.exists():
            return config
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Strip whitespace
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Match KEY="VALUE" or KEY='VALUE' or KEY=VALUE
                match = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$', line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()
                    
                    # Remove surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    # Handle escaped characters
                    value = value.replace('\\"', '"').replace("\\'", "'")
                    
                    config[key] = value
    except Exception as e:
        print(f"Warning: Could not read apikeys.ini: {e}")
    
    return config


def get_config_value(key: str, default: Optional[str] = None, 
                     file_path: str = "apikeys.ini") -> Optional[str]:
    """
    Get a configuration value from apikeys.ini file.
    
    Args:
        key: Configuration key name
        default: Default value if key not found
        file_path: Path to apikeys.ini file
        
    Returns:
        Configuration value or default
    """
    config = parse_apikeys_ini(file_path)
    return config.get(key, default)


def get_database_password(file_path: str = "apikeys.ini", 
                         default: str = "letsencrypt") -> str:
    """
    Get database password from apikeys.ini file.
    
    Checks for these keys in order:
    1. DB_PASSWORD
    2. DATABASE_PASSWORD
    3. CA_PASSWORD (if exists)
    4. Default: "letsencrypt"
    
    Args:
        file_path: Path to apikeys.ini file
        default: Default password if not found
        
    Returns:
        Database password string
    """
    config = parse_apikeys_ini(file_path)
    
    # Check for database password keys
    if 'DB_PASSWORD' in config:
        return config['DB_PASSWORD']
    elif 'DATABASE_PASSWORD' in config:
        return config['DATABASE_PASSWORD']
    elif 'CA_PASSWORD' in config:
        # Use CA_PASSWORD if available
        return config['CA_PASSWORD']
    else:
        return default
