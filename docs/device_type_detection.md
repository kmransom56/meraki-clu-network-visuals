# Meraki Device Type Detection

## Overview

The Cisco Meraki CLU implements a comprehensive device type detection system that identifies device capabilities based on serial numbers, model numbers, and other identifiers. This system enables more intelligent API interactions and enhanced visualization capabilities.

## Device Types

The system recognizes the following Meraki device types:

| Device Type | Description | Serial Prefix Examples | Uplink Support |
|-------------|-------------|------------------------|----------------|
| MX | Security Appliances | Q2QN, Q2QP, Q2HP, Q2HN | Yes |
| MS | Switches | Q2HW, Q2EK, Q2HP, Q2JN | No |
| MR | Wireless Access Points | Q2LD, Q2MD, Q2PD, Q2HD | No |
| MG | Cellular Gateways | Q2GD | Yes |
| MV | Cameras | Q2AV, Q2DV, Q2BV | No |
| MT | Sensors | Q2ET | No |
| Z | Teleworker Gateways | Z1, Z3 | Yes |

## Feature Support by Device Type

Different Meraki device types support different API endpoints and features:

### MX (Security Appliances)
- Uplink information
- Firewall rules
- VPN settings
- Traffic shaping
- Content filtering

### MS (Switches)
- Port configurations
- VLANs
- STP settings
- QoS settings

### MR (Wireless Access Points)
- SSIDs
- RF profiles
- Bluetooth settings

### MG (Cellular Gateways)
- Uplink information
- Cellular settings

### MV (Cameras)
- Video settings
- Motion detection

### MT (Sensors)
- Sensor readings

### Z (Teleworker Gateways)
- Uplink information
- Firewall rules
- VPN settings

## Implementation Details

The device type detection system uses multiple methods to identify device types:

1. **Serial Number Prefix**: Identifies device types based on the prefix of the serial number.
2. **Model Number Pattern**: Uses regex patterns to match model numbers to device types.
3. **Feature Support Checking**: Determines which features a device supports based on its identified type.

## Usage in the Application

The device type detection system is used throughout the application to:

1. **Prevent Unnecessary API Calls**: By knowing which device types support which features, the application avoids making API calls that would result in 404 errors.
2. **Enhance Visualization**: Different device types are represented with appropriate icons in the network topology visualization.
3. **Provide Better User Information**: The application can now show more detailed information about device capabilities.

## API Integration

The device type detection system integrates with the Meraki API module to provide more intelligent API interactions:

```python
# Example: Check if a device supports uplink information
from modules.meraki.device_types import supports_uplink

if supports_uplink(device_info):
    # Make API call to get uplink information
    uplink_data = get_device_uplink(api_key, device_info['serial'])
else:
    # Skip API call for unsupported device types
    logging.info(f"Device {device_info['serial']} does not support uplink information")
```

## Future Enhancements

Potential future enhancements to the device type detection system include:

1. **More Device Types**: Adding support for new Meraki device types as they become available.
2. **More Feature Checks**: Expanding the list of features that can be checked for each device type.
3. **Dynamic Updates**: Implementing a system to update device type information from the Meraki API documentation.
