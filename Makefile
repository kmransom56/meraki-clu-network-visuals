# ============================
# Dependency Management
# ============================

VENV=.venv
PYTHON=$(VENV)/Scripts/python.exe
PIP=$(VENV)/Scripts/pip.exe

.PHONY: venv deps freeze regen clean

# Create virtual environment
venv:
    python -m venv $(VENV)

# Install dependencies from requirements.txt
deps: venv
    $(PIP) install -r requirements.txt

# Freeze current environment into requirements.txt
freeze:
    $(PIP) freeze > requirements.txt

# Regenerate requirements.txt from imports (pipreqs)
regen:
    pipreqs . --force --encoding=utf-8 --ignore .venv,scripts,tests
    $(PIP) install -r requirements.txt
    $(PIP) freeze > requirements.txt

# Remove venv
clean:
    rmdir /s /q $(VENV)
