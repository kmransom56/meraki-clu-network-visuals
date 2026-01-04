#!/usr/bin/env python3
"""
Import environment variables from a file with export KEY="VALUE" format
into Windows environment variables.

Usage:
    python scripts/import_env_vars.py <env_file> [--user|--system] [--dry-run]
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_export_file(file_path):
    """
    Parse a file with KEY="VALUE" or export KEY="VALUE" format and return a dict of key-value pairs.
    
    Supports:
    - export KEY="VALUE" (bash export format)
    - export KEY='VALUE' (bash export format with single quotes)
    - export KEY=VALUE (bash export format without quotes)
    - KEY="VALUE" (INI/simple format)
    - KEY='VALUE' (INI/simple format with single quotes)
    - KEY=VALUE (INI/simple format without quotes)
    - Lines starting with # are treated as comments
    - Empty lines are ignored
    
    Args:
        file_path: Path to the environment file
        
    Returns:
        dict: Dictionary of environment variable key-value pairs
    """
    env_vars = {}
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return env_vars
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Strip whitespace
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Match both formats:
            # 1. export KEY="VALUE" or export KEY='VALUE' or export KEY=VALUE
            # 2. KEY="VALUE" or KEY='VALUE' or KEY=VALUE (INI format)
            # Make export optional and handle various quote styles
            match = re.match(r'(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$', line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                
                # Remove surrounding quotes if present (handles both single and double quotes)
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Handle escaped characters
                value = value.replace('\\"', '"').replace("\\'", "'")
                
                env_vars[key] = value
            else:
                print(f"Warning: Skipping line {line_num} (not in KEY=\"VALUE\" format): {line}")
    
    return env_vars


def set_windows_env_var(key, value, scope='user', dry_run=False):
    """
    Set a Windows environment variable using setx command.
    
    Args:
        key: Environment variable name
        value: Environment variable value
        scope: 'user' (default) or 'system' (requires admin)
        dry_run: If True, only print what would be done
        
    Returns:
        bool: True if successful, False otherwise
    """
    if dry_run:
        print(f"[DRY RUN] Would set {scope} environment variable: {key}={value}")
        return True
    
    try:
        # Use setx for persistent environment variables
        # /M flag for system-wide (requires admin), no flag for user
        if scope == 'system':
            cmd = ['setx', key, value, '/M']
        else:
            cmd = ['setx', key, value]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✓ Set {scope} environment variable: {key}")
            # Also set for current session
            os.environ[key] = value
            return True
        else:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            print(f"✗ Failed to set {key}: {error_msg}")
            return False
            
    except Exception as e:
        print(f"✗ Error setting {key}: {str(e)}")
        return False


def import_env_file(file_path, scope='user', dry_run=False):
    """
    Import environment variables from a file into Windows environment variables.
    
    Args:
        file_path: Path to the environment file
        scope: 'user' (default) or 'system' (requires admin)
        dry_run: If True, only print what would be done
        
    Returns:
        tuple: (success_count, total_count)
    """
    env_vars = parse_export_file(file_path)
    
    if not env_vars:
        print("No environment variables found in file.")
        return (0, 0)
    
    print(f"\nFound {len(env_vars)} environment variable(s) to import:")
    for key in env_vars.keys():
        print(f"  - {key}")
    
    if dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")
    
    success_count = 0
    total_count = len(env_vars)
    
    print(f"\nImporting to {scope} environment variables...\n")
    
    for key, value in env_vars.items():
        # Mask sensitive values in output
        if 'key' in key.lower() or 'password' in key.lower() or 'secret' in key.lower() or 'token' in key.lower():
            display_value = '*' * min(len(value), 20) + ('...' if len(value) > 20 else '')
        else:
            display_value = value[:50] + ('...' if len(value) > 50 else '')
        
        print(f"Setting {key}={display_value}")
        
        if set_windows_env_var(key, value, scope=scope, dry_run=dry_run):
            success_count += 1
    
    return (success_count, total_count)


def main():
    parser = argparse.ArgumentParser(
        description='Import environment variables from KEY="VALUE" or export KEY="VALUE" format file into Windows environment variables',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import to user environment variables (default)
  python scripts/import_env_vars.py .env
  python scripts/import_env_vars.py apikeys.ini
  
  # Import to system environment variables (requires admin)
  python scripts/import_env_vars.py .env --system
  
  # Dry run to see what would be imported
  python scripts/import_env_vars.py apikeys.ini --dry-run
  
  # Import from custom file
  python scripts/import_env_vars.py /path/to/env_file.txt

Supported file formats:
  - export KEY="VALUE" (bash export format)
  - KEY="VALUE" (INI/simple format)
  - Both single and double quotes are supported
  - Values without quotes are also supported

Note:
  - System-wide variables require running as Administrator
  - After setting variables, you may need to restart your terminal/application
  - Use --dry-run to preview changes without applying them
        """
    )
    
    parser.add_argument(
        'file',
        help='Path to the environment file with export KEY="VALUE" format'
    )
    
    parser.add_argument(
        '--user',
        action='store_const',
        const='user',
        dest='scope',
        default='user',
        help='Set user environment variables (default)'
    )
    
    parser.add_argument(
        '--system',
        action='store_const',
        const='system',
        dest='scope',
        help='Set system-wide environment variables (requires Administrator)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Check for admin if system scope
    if args.scope == 'system' and not args.dry_run:
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                print("Warning: System-wide environment variables require Administrator privileges.")
                print("Please run this script as Administrator or use --user for user variables.")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    sys.exit(1)
        except Exception:
            pass  # Non-Windows or can't check admin status
    
    # Import the environment variables
    success_count, total_count = import_env_file(
        str(file_path),
        scope=args.scope,
        dry_run=args.dry_run
    )
    
    # Summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"[DRY RUN] Would import {success_count}/{total_count} environment variables")
    else:
        print(f"Imported {success_count}/{total_count} environment variables")
        if success_count == total_count:
            print("\n✓ All environment variables imported successfully!")
            print("\nNote: You may need to restart your terminal/application")
            print("      for the changes to take effect in new processes.")
        else:
            print(f"\n⚠ {total_count - success_count} environment variable(s) failed to import")
    
    sys.exit(0 if success_count == total_count else 1)


if __name__ == '__main__':
    main()
