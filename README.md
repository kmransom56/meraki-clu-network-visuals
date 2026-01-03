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
1. Clone the repository:
   ```bash
   git clone https://github.com/keransom56/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
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
- See requirements.txt for dependencies# cisco-meraki-clu

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
api/dependency_validator.py  → Runtime dependency validator# meraki-clu-network-visuals
