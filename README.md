# Cisco Meraki API Integration Tool

A Python-based tool for interacting with the Cisco Meraki API, featuring:
- Network topology visualization
- Device management
- SSL proxy support (Zscaler compatible)
- Secure API key management
- Official Meraki Dashboard API SDK integration

## Features
- Interactive network topology visualization using D3.js
- Device status monitoring
- Network health metrics
- Proxy-aware SSL handling
- Secure API key storage
- Dual API mode: Custom implementation or Official SDK

## Installation

### Prerequisites
- Python 3.7+
- `uv` package manager (install with: `pip install uv`)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/kmransom56/meraki-clu-network-visuals.git
   cd meraki-clu-network-visuals
   ```

2. Install `uv` (if not already installed):
   
   **Windows (using winget):**
   ```pwsh
   winget install --id=astral-sh.uv -e
   ```
   
   **Using pipx (recommended for isolated installation):**
   ```bash
   pipx install uv
   ```
   
   **Using pip (alternative):**
   ```bash
   pip install uv
   ```

3. Create a virtual environment using `uv`:
   ```bash
   uv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On Unix/macOS:
     ```bash
     source .venv/bin/activate
     ```

5. Install the required packages using `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```

6. Run the application:
   ```bash
   python main.py
   ```

### Alternative: Using `uv` without activating venv
You can also run commands directly with `uv` without activating the virtual environment:
```bash
uv run python main.py
```

## API Mode Selection
The application now supports two API modes:

1. **Custom API Implementation (Default)**
   - Uses the custom API implementation with robust error handling
   - Includes special handling for Windows proxy environments (like Zscaler)
   - Recommended for most users, especially in corporate environments with proxies

2. **Official Meraki SDK**
   - Uses the official Meraki Dashboard API Python SDK
   - Provides access to all API endpoints
   - May have limitations in some proxy environments

You can switch between modes in the main menu.

## SSL Certificate Handling
The application implements a robust SSL verification strategy:
- Primary: Attempts secure verification using system CA certificates
- Fallback: For Windows proxy environments, disables verification if primary fails
- Clear error messages for troubleshooting

## Security Features
- API keys are stored securely using Fernet encryption
- SSL certificate handling with proxy support
- Environment variable support for API keys
- Comprehensive error handling and logging

## Requirements
- Python 3.7+
- `uv` package manager (install with: `pip install uv`)
- See `requirements.txt` for Python dependencies

Dependency Governance & Drift Protection
This project includes a full, automated dependency‑governance workflow designed to ensure:

deterministic builds

reproducible environments

drift detection before merge

runtime validation

rollback safety

compliance‑ready signed artifacts

Workflow Overview
Stage	Description
1. Pre‑Commit Drift Check	Prevents developers from committing code that introduces new imports without updating requirements.txt.
2. CI Regeneration	CI regenerates requirements.txt using pipreqs, reinstalls dependencies, and freezes a deterministic requirements.lock.
3. Drift Detection	CI compares the regenerated lock file to the committed version. Any mismatch fails the pipeline.
4. Runtime Validation	FastAPI validates required imports at startup and exposes a /admin/dependencies endpoint for live drift monitoring.
5. Rollback Workflow	A PowerShell script restores the last known‑good dependency set.
6. Signed Artifacts	CI signs the requirements.lock file for compliance and auditing.
Key Files
Code
Makefile                     → Automated dependency regeneration
.pre-commit-config.yaml      → Pre-commit drift prevention
.github/workflows/           → CI dependency audit pipeline
scripts/bootstrap.ps1        → Environment bootstrap
scripts/rollback_requirements.ps1 → Rollback workflow
scripts/sign_requirements.py → Signed artifact generator
api/dependency_dashboard.py  → JSON emitter for admin panel
api/dependency_validator.py  → Runtime dependency validator
