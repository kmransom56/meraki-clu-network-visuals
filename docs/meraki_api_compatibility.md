# Meraki API Compatibility

## Overview

The Cisco Meraki CLU integrates with the Meraki Dashboard API using two different methods:

1. **Custom API Implementation** - A custom implementation with enhanced SSL handling for Windows environments with proxies like Zscaler
2. **Official Meraki SDK** - The official Meraki Dashboard API Python SDK

## API Version Compatibility

The application is designed to work with the Meraki Dashboard API v1, specifically targeting compatibility with version 1.56.0 and above. The API specification can be found at:

```
https://pubhub.devnetcloud.com/media/Meraki-Dashboard-API-v1-Documentation/docs/docs/meraki_dashboard_api_1_56_0.json
```

## API Mode Selection

You can switch between the custom API implementation and the official SDK using the API Mode Selection option in the main menu. Each mode has its advantages:

### Custom API Implementation

- Enhanced SSL handling for Windows environments with proxies (e.g., Zscaler)
- Robust error handling with fallback mechanisms
- Special handling for endpoints that might return 404 for some devices

### Official Meraki SDK

- Direct integration with the official Meraki Dashboard API Python SDK
- Access to all API endpoints and features
- Automatic handling of pagination and rate limiting

## SSL Verification

The application implements robust SSL verification strategies:

1. **Windows with Proxies**: Special handling for Windows environments with proxies like Zscaler
   - Attempts connection with verification first
   - Falls back to disabled verification if needed
   - Clears conflicting environment variables

2. **Other Environments**: Uses system CA certificates and certifi for SSL verification

## Troubleshooting

If you encounter SSL verification issues:

1. Check your proxy settings
2. Try switching between API modes
3. Check the log file for detailed error messages

## Logging

The application logs detailed information about API interactions, including:

- API version information
- SSL verification status
- Error messages and exceptions

Log files are stored in the application directory and can be helpful for troubleshooting.
