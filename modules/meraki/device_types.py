"""
Meraki Device Type Detection Module

This module provides functions to identify Cisco Meraki device types based on
serial numbers, model numbers, and other identifiers.

Device types include:
- MX: Security Appliances
- MS: Switches
- MR: Wireless Access Points
- MG: Cellular Gateways
- MV: Cameras
- MT: Sensors
- Z: Teleworker Gateways
"""

import logging
import re

# Serial number prefixes by device type
SERIAL_PREFIXES = {
    'MX': ['Q2QN', 'Q2QP', 'Q2HP', 'Q2HN'],  # Security Appliances
    'MS': ['Q2HW', 'Q2EK', 'Q2HP', 'Q2JN'],  # Switches
    'MR': ['Q2LD', 'Q2MD', 'Q2PD', 'Q2HD'],  # Wireless Access Points
    'MG': ['Q2GD'],                          # Cellular Gateways
    'MV': ['Q2AV', 'Q2DV', 'Q2BV'],          # Cameras
    'MT': ['Q2ET'],                          # Sensors
    'Z': ['Z1', 'Z3']                        # Teleworker Gateways
}

# Model number patterns by device type
MODEL_PATTERNS = {
    'MX': [r'MX\d+', r'Z\d+'],
    'MS': [r'MS\d+'],
    'MR': [r'MR\d+'],
    'MG': [r'MG\d+'],
    'MV': [r'MV\d+'],
    'MT': [r'MT\d+'],
    'Z': [r'Z\d+']
}

# Features supported by device type
SUPPORTED_FEATURES = {
    'MX': ['uplink', 'firewall', 'vpn', 'traffic_shaping', 'content_filtering'],
    'MS': ['ports', 'vlans', 'stp', 'qos'],
    'MR': ['ssids', 'rf_profiles', 'bluetooth'],
    'MG': ['uplink', 'cellular'],
    'MV': ['video', 'motion_detection'],
    'MT': ['sensor_readings'],
    'Z': ['uplink', 'firewall', 'vpn']
}

def get_device_type_from_serial(serial):
    """
    Determine device type based on serial number prefix
    
    Args:
        serial (str): Device serial number
        
    Returns:
        str: Device type (MX, MS, MR, MG, MV, MT, Z) or None if unknown
    """
    if not serial:
        return None
        
    for device_type, prefixes in SERIAL_PREFIXES.items():
        if any(serial.startswith(prefix) for prefix in prefixes):
            return device_type
            
    # If no match found, try to infer from first two characters
    if serial.startswith('Q2'):
        logging.warning(f"Unknown Q2 serial prefix for {serial}, assuming generic Meraki device")
        return "UNKNOWN"
        
    logging.warning(f"Could not determine device type for serial: {serial}")
    return None

def get_device_type_from_model(model):
    """
    Determine device type based on model number pattern
    
    Args:
        model (str): Device model number
        
    Returns:
        str: Device type (MX, MS, MR, MG, MV, MT, Z) or None if unknown
    """
    if not model:
        return None
        
    for device_type, patterns in MODEL_PATTERNS.items():
        if any(re.match(pattern, model, re.IGNORECASE) for pattern in patterns):
            return device_type
            
    logging.warning(f"Could not determine device type for model: {model}")
    return None

def get_device_type(device_info):
    """
    Determine device type from device information dictionary
    
    Args:
        device_info (dict): Device information containing model and/or serial
        
    Returns:
        str: Device type (MX, MS, MR, MG, MV, MT, Z) or None if unknown
    """
    # Try to get type from model first (more reliable)
    if 'model' in device_info and device_info['model']:
        device_type = get_device_type_from_model(device_info['model'])
        if device_type:
            return device_type
            
    # Fall back to serial number
    if 'serial' in device_info and device_info['serial']:
        return get_device_type_from_serial(device_info['serial'])
        
    return None

def supports_feature(device_type, feature):
    """
    Check if a device type supports a specific feature
    
    Args:
        device_type (str): Device type (MX, MS, MR, MG, MV, MT, Z)
        feature (str): Feature name to check
        
    Returns:
        bool: True if the device type supports the feature, False otherwise
    """
    if not device_type or device_type not in SUPPORTED_FEATURES:
        return False
        
    return feature in SUPPORTED_FEATURES.get(device_type, [])

def supports_uplink(device_info):
    """
    Check if a device supports uplink information
    
    Args:
        device_info (dict): Device information containing model and/or serial
        
    Returns:
        bool: True if the device supports uplink information, False otherwise
    """
    device_type = get_device_type(device_info)
    return supports_feature(device_type, 'uplink')
