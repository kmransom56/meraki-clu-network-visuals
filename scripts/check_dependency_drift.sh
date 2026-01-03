#!/bin/bash
# Dependency drift check script for pre-commit hook

if ! command -v pipreqs >/dev/null 2>&1; then
    echo "Error: pipreqs is not installed. Install it with: pip install pipreqs"
    exit 1
fi

# Packages that should be preserved (manually maintained)
PRESERVE_PACKAGES=("meraki==1.54.0" "pipreqs==0.4.13")

# Backup current requirements.txt
cp requirements.txt requirements.txt.bak

# Generate new requirements with pipreqs
pipreqs . --force --encoding=utf-8 --ignore .venv,scripts,tests

# Restore preserved packages
for package in "${PRESERVE_PACKAGES[@]}"; do
    pkg_name=$(echo "$package" | cut -d'=' -f1)
    # Remove any existing entry for this package
    grep -v "^${pkg_name}==" requirements.txt > requirements.txt.tmp
    mv requirements.txt.tmp requirements.txt
    # Add the preserved version
    echo "$package" >> requirements.txt
done

# Sort requirements.txt alphabetically
sort -o requirements.txt requirements.txt

# Check if there are any changes (excluding preserved packages differences)
git diff --exit-code requirements.txt
