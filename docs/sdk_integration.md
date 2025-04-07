# Meraki SDK Integration

## Overview

The Cisco Meraki CLU now integrates the official Meraki Dashboard API Python SDK, providing enhanced functionality and performance while maintaining the robust security features of the original implementation.

## Features

### Dual API Mode

The application now supports two API modes:

1. **Custom API Implementation (Default)**
   - Uses the custom API implementation with robust error handling
   - Includes special handling for Windows proxy environments (like Zscaler)
   - Recommended for most users, especially in corporate environments with proxies

2. **Official Meraki SDK**
   - Uses the official Meraki Dashboard API Python SDK
   - Provides access to all API endpoints
   - May have limitations in some proxy environments

### Benefits of SDK Integration

- **Comprehensive API Coverage**: Access to all Meraki Dashboard API endpoints through the official SDK
- **Simplified API Calls**: The SDK handles authentication, pagination, and error handling
- **Future-Proof**: Automatic updates when new API features are released
- **Improved Performance**: Optimized API calls for better performance

### Maintaining Security Features

The SDK integration maintains all the robust security features of the original implementation:

- **SSL Certificate Handling**: Two-step SSL verification strategy
  - Primary: Attempts secure verification using system CA certificates
  - Fallback: For Windows proxy environments, disables verification if primary fails
  - Clear error messages for troubleshooting

- **API Key Security**:
  - Encrypted storage using Fernet
  - Keys stored in user's home directory
  - Environment variable support

## How to Use

### Switching Between API Modes

1. From the main menu, select the "API Mode" option
2. Choose between "Custom API Implementation" or "Official Meraki SDK"
3. The application will remember your preference for future sessions

### Using SDK-Enabled Features

All features work the same way regardless of which API mode you choose. The application automatically uses the appropriate implementation based on your selected mode.

## Implementation Details

The SDK integration is implemented through a wrapper class (`MerakiSDKWrapper`) that provides a consistent interface for both the custom API implementation and the SDK. This allows the application to switch between modes seamlessly without changing the core functionality.

### MerakiSDKWrapper

The `MerakiSDKWrapper` class encapsulates the SDK functionality and provides methods that match the interface of the custom API implementation. This allows the application to use either implementation interchangeably.

Key features of the wrapper:

- Handles authentication and initialization of the SDK
- Provides methods for all API endpoints used by the application
- Formats responses to match the custom API implementation
- Implements error handling and logging

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   - If you encounter SSL certificate errors when using the SDK mode, try switching back to the custom API implementation which has more robust SSL handling for proxy environments.

2. **API Rate Limiting**
   - The SDK has built-in rate limiting, but you may still encounter rate limit errors if making many requests. The application will handle these errors and retry as appropriate.

3. **Missing Features**
   - If you find that a feature is available in one mode but not the other, please report this as an issue.

## Future Enhancements

Future versions will continue to enhance the SDK integration:

1. **Complete Feature Parity**: Ensuring all features work identically in both modes
2. **Enhanced SDK Configuration**: More options for configuring the SDK behavior
3. **Performance Optimizations**: Further optimizations for improved performance
