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
