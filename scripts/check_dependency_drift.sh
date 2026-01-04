#!/bin/bash
# Dependency drift check script for pre-commit hook

if ! command -v pipreqs >/dev/null 2>&1; then
    echo "Error: pipreqs is not installed. Install it with: pip install pipreqs"
    exit 1
fi

# Packages that should be preserved (manually maintained)
# These are optional dependencies that may be imported conditionally
PRESERVE_PACKAGES=("meraki==1.54.0" "pipreqs==0.4.13" "pyautogen==0.10.0" "docker==7.1.0" "magentic==0.41.0" "openai==2.14.0")

# Backup current requirements.txt
cp requirements.txt requirements.txt.bak

# Generate new requirements with pipreqs (suppress Python warnings and other noise)
# Suppress stderr warnings while allowing actual errors through
# On Windows (Git Bash), process substitution might not work, so use simpler approach
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows/Git Bash: redirect stderr to filter, discard filtered output
    pipreqs . --force --encoding=utf-8 --ignore .venv,scripts,tests 2>&1 | grep -vE "(SyntaxWarning|WARNING:|Please, verify manually)" || true
else
    # Unix/Linux: use process substitution for better stderr handling
    pipreqs . --force --encoding=utf-8 --ignore .venv,scripts,tests 2> >(grep -vE "(SyntaxWarning|WARNING:|Please, verify manually)" >&2) || true
fi

# Restore preserved packages
for package in "${PRESERVE_PACKAGES[@]}"; do
    pkg_name=$(echo "$package" | cut -d'=' -f1)
    # Remove any existing entry for this package (case-insensitive)
    grep -iv "^${pkg_name}==" requirements.txt > requirements.txt.tmp
    mv requirements.txt.tmp requirements.txt
    # Add the preserved version
    echo "$package" >> requirements.txt
done

# Sort requirements.txt alphabetically (case-insensitive for consistency)
# Use Python to normalize package names to lowercase for stable sorting
# Try python3 first, fall back to python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD=python
else
    echo "Error: Python is not installed. Cannot sort requirements.txt"
    exit 1
fi

$PYTHON_CMD << 'PYTHON_SCRIPT'
import sys

# Read requirements
with open('requirements.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

# Normalize package names to lowercase for consistent, deterministic sorting
# PyPI package names are case-insensitive, so this is safe and prevents
# unnecessary diffs when pipreqs generates packages in different orders
def normalize_package_name(line):
    if '==' in line:
        parts = line.split('==', 1)
        pkg_name = parts[0].strip()
        version = parts[1].strip() if len(parts) > 1 else ''
        return f"{pkg_name.lower()}=={version}"
    elif '>=' in line:
        parts = line.split('>=', 1)
        pkg_name = parts[0].strip()
        version = parts[1].strip() if len(parts) > 1 else ''
        return f"{pkg_name.lower()}>={version}"
    elif '<=' in line:
        parts = line.split('<=', 1)
        pkg_name = parts[0].strip()
        version = parts[1].strip() if len(parts) > 1 else ''
        return f"{pkg_name.lower()}<={version}"
    else:
        # No version specifier
        pkg_name = line.split()[0].strip() if line.split() else line.strip()
        return pkg_name.lower()

# Normalize and sort
normalized_lines = [normalize_package_name(line) for line in lines]
normalized_lines.sort()  # Simple alphabetical sort (all lowercase now)

# Write back with normalized package names
with open('requirements.txt', 'w') as f:
    for line in normalized_lines:
        f.write(line + '\n')
PYTHON_SCRIPT

# Check if there are any changes
git diff --exit-code requirements.txt
