#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.4                                                      *
#   Author:      Matia Zanella                                            *
#   Description: Cisco Meraki CLU (Command Line Utility) is an essential  *
#                tool crafted for Network Administrators managing Meraki  *
#   Github:      https://github.com/akamura/cisco-meraki-clu/             *
#                                                                         *
#   Icon Author:        Cisco Systems, Inc.                               *
#   Icon Author URL:    https://meraki.cisco.com/                         *
#                                                                         *
#   Copyright (C) 2024 Matia Zanella                                      *
#   https://www.matiazanella.com                                          *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU General Public License as published by  *
#   the Free Software Foundation; either version 2 of the License, or     *
#   (at your option) any later version.                                   *
#                                                                         *
#   This program is distributed in the hope that it will be useful,       *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU General Public License for more details.                          *
#                                                                         *
#   You should have received a copy of the GNU General Public License     *
#   along with this program; if not, write to the                         *
#   Free Software Foundation, Inc.,                                       *
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#**************************************************************************


# ==================================================
# IMPORT various libraries and modules
# ==================================================
import requests
import subprocess
import sys
import logging
import json
import csv
import os
try:
    from tabulate import tabulate
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
    from tabulate import tabulate
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
    from tabulate import tabulate
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
import ssl
import certifi
from datetime import datetime
try:
    from termcolor import colored
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "termcolor"])

import json
from pathlib import Path
try:
    from cryptography.fernet import Fernet
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure requests to use system CA certificates and disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_ssl_context():
    """Create and return a secure SSL context"""
    try:
        # Create SSL context with strong security settings
        context = ssl.create_default_context()
        
        # Use system's certificate store
        context.load_default_certs()
        
        # Additionally load certifi's certificates (belt and suspenders approach)
        context.load_verify_locations(certifi.where())
        
        return context
    except Exception as e:
        logging.error(f"Error creating SSL context: {e}")
        return None

def get_organization_summary(api_key, organization_id):
    """Get summary information about an organization"""
    try:
        url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/summary"
        headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Content-Type": "application/json"
        }
        # Add verify=False for development/testing - in production, proper SSL cert verification should be implemented
        response = requests.get(url, headers=headers, verify=False)
        
        # Get SSL context
        ssl_context = get_ssl_context()
        if ssl_context is None:
            raise Exception("Failed to create SSL context")
            
        # Use the SSL context with requests
        response = requests.get(
            url, 
            headers=headers,
            verify=certifi.where()  # Use certifi's certificate bundle
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError as ssl_err:
        logging.error(f"SSL Error: {ssl_err}")
        # Provide detailed error information
        logging.error(f"Certificate verification failed. Please ensure certificates are properly installed.")
        logging.error(f"System certificate paths: {ssl.get_default_verify_paths()}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting organization summary: {e}")
        return None

# Update other API request functions to include verify=False
# Update other API request functions similarly
def get_organization_inventory(api_key, organization_id):
    """Get inventory information for an organization"""
    try:
        url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/inventory"
        headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, verify=False)
        response = requests.get(
            url, 
            headers=headers,
            verify=certifi.where()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError as ssl_err:
        logging.error(f"SSL Error: {ssl_err}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting organization inventory: {e}")
        return None

def get_organization_licenses(api_key, organization_id):
    """Get license information for an organization"""
    try:
        url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/licenses"
        headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting organization licenses: {e}")
        return None

def get_organization_devices_statuses(api_key, organization_id):
    """Get device status information for an organization"""
    try:
        url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/devices/statuses"
        headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting device statuses: {e}")
        return None

BASE_URL = "https://api.meraki.com/api/v1"


# ==================================================
# EXPORT device list in a beautiful table format
# ==================================================
def export_devices_to_csv(devices, network_name, device_type, base_folder_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{network_name}_{current_date}_{device_type}.csv"
    file_path = os.path.join(base_folder_path, filename)

    if devices:
        # Priority columns
        priority_columns = ['name', 'mac', 'lanIp', 'serial', 'model', 'firwmare', 'tags']

        # Gather all columns from the devices
        all_columns = set(key for device in devices for key in device.keys())
        
        # Reorder columns so that priority columns come first
        ordered_columns = priority_columns + [col for col in all_columns if col not in priority_columns]

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            # Convert fieldnames to uppercase
            fieldnames = [col.upper() for col in ordered_columns]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for device in devices:
                # Convert keys to uppercase to match fieldnames
                row = {col.upper(): device.get(col, '') for col in ordered_columns}
                writer.writerow(row)
            
        print(f"Data exported to {file_path}")
    else:
        print("No data to export.")


# ==================================================
# EXPORT firewall rules in a beautiful table format
# ==================================================
def export_firewall_rules_to_csv(firewall_rules, network_name, base_folder_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{network_name}_{current_date}_MX_Firewall_Rules.csv"
    file_path = os.path.join(base_folder_path, filename)

    if firewall_rules:
        # Priority columns, adjust these based on your data
        priority_columns = ['policy', 'protocol', 'srcport', 'srccidr', 'destport','destcidr','comments']

        # Gather all columns from the firewall rules
        all_columns = set(key for rule in firewall_rules for key in rule.keys())
        
        # Reorder columns so that priority columns come first
        ordered_columns = priority_columns + [col for col in all_columns if col not in priority_columns]

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            # Convert fieldnames to uppercase
            fieldnames = [col.upper() for col in ordered_columns]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for rule in firewall_rules:
                # Convert keys to uppercase to match fieldnames
                row = {col.upper(): rule.get(col, '') for col in ordered_columns}
                writer.writerow(row)
            
        print(f"Data exported to {file_path}")
    else:
        print("No data to export.")


# ==================================================
# GET a list of Organizations
# ==================================================
def get_meraki_organizations(api_key):
    """Get list of organizations accessible by the API key"""
    url = f"{BASE_URL}/organizations"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def select_organization(api_key):
    """Interactive selection of an organization"""
    organizations = get_meraki_organizations(api_key)
    if organizations:
        print(colored("\nAvailable Organizations:", "cyan"))
        for idx, org in enumerate(organizations, 1):
            print(f"{idx}. {org['name']}")

        choice = input(colored("\nSelect an Organization (enter the number): ", "cyan"))
        try:
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(organizations):
                return organizations[selected_index]
            else:
                print(colored("Invalid selection.", "red"))
        except ValueError:
            print(colored("Please enter a number.", "red"))

    return None


# ==================================================
# GET a list of Networks in an Organization
# ==================================================
def get_meraki_networks(api_key, organization_id, per_page=5000):
    url = f"{BASE_URL}/organizations/{organization_id}/networks"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    params = {
        "perPage": per_page
    }
    return make_meraki_request(url, headers, params)


# ==================================================
# SELECT a Network in an Organization
# ==================================================
def select_network(api_key, organization_id):
    networks = get_meraki_networks(api_key, organization_id)
    if networks:
        print("\nAvailable Networks:")
        for idx, network in enumerate(networks, 1):
            print(f"{idx}. {network['name']}")
        
        while True:
            try:
                choice = input(colored("\nSelect a Network (enter the number): ", "cyan"))
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(networks):
                    return networks[selected_index]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            except IndexError:
                print("Invalid selection. Please try again.")
    return None


# ==================================================
# GET a list of Switches in an Network
# ==================================================
def get_meraki_switches(api_key, network_id):
    url = f"{BASE_URL}/networks/{network_id}/devices"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def display_switches(api_key, network_id):
    devices = get_meraki_switches(api_key, network_id)
    if devices:
        # Filter to include only switches
        switches = [device for device in devices if device['model'].startswith('MS')]
        for switch in switches:
            print(f"Name: {switch.get('name', 'N/A')}")
            print(f"Serial: {switch.get('serial', 'N/A')}")
            print(f"Model: {switch.get('model', 'N/A')}")
            print("------------------------")
        return switches
    return None


# ==================================================
# GET a list of Switch Ports and their Status
# ==================================================
def get_switch_ports(api_key, serial):
    url = f"{BASE_URL}/devices/{serial}/switch/ports"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def get_switch_ports_statuses_with_timespan(api_key, serial, timespan=1800):
    url = f"{BASE_URL}/devices/{serial}/switch/ports/statuses"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "timespan": timespan
    }
    return make_meraki_request(url, headers, params)


# ==================================================
# GET a list of Access Points in an Network
# ==================================================
def get_meraki_access_points(api_key, network_id):
    url = f"{BASE_URL}/networks/{network_id}/devices"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)


# =======================================================================
# [UNDER DEVELOPMENT] GET a list of VLANs and Static Routes in an Network
# =======================================================================
def get_meraki_vlans(api_key, network_id):
    url = f"{BASE_URL}/networks/{network_id}/appliance/vlans"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def get_meraki_static_routes(api_key, network_id):
    url = f"{BASE_URL}/networks/{network_id}/appliance/staticRoutes"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

# ==================================================
# SELECT a Network in an Organization
# ==================================================
def select_mx_network(api_key, organization_id):
    networks = get_meraki_networks(api_key, organization_id)
    if networks:
        mx_networks = []
        print("\nAvailable Networks with MX:")
        idx = 1
        for network in networks:
            if any(device['model'].startswith('MX') for device in get_meraki_switches(api_key, network['id'])):
                print(f"{idx}. {network['name']}")
                mx_networks.append(network)
                idx += 1
        
        while True:
            try:
                choice = input(colored("\nSelect a Network (enter the number): ", "cyan"))
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(mx_networks):
                    return mx_networks[selected_index]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            except IndexError:
                print("Invalid selection. Please try again.")
    return None


# ==================================================
# GET Layer 3 Firewall Rules for a Network
# ==================================================
def get_l3_firewall_rules(api_key, network_id):
    url = f"{BASE_URL}/networks/{network_id}/appliance/firewall/l3FirewallRules"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

# ==================================================
# DISPLAY Firewall Rules in a Table Format
# ==================================================
def display_firewall_rules(firewall_rules):
    if firewall_rules:
        print("\nLayer 3 Firewall Rules:")
        print(tabulate(firewall_rules, headers="keys", tablefmt="pretty"))
    else:
        print("No firewall rules found in the selected network.")


# ==============================================================
# FETCH Organization policy and group objects for Firewall Rules
# ==============================================================
def get_organization_policy_objects(api_key, organization_id):
    url = f"{BASE_URL}/organizations/{organization_id}/policyObjects"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return make_meraki_request(url, headers)

def get_organization_policy_objects_groups(api_key, organization_id):
    url = f"{BASE_URL}/organizations/{organization_id}/policyObjects/groups"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return make_meraki_request(url, headers)

# ==============================================================
# FETCH Organization Devices Statuses
# ==============================================================
def get_organization_devices_statuses(api_key, organization_id):
    url = f"{BASE_URL}/organizations/{organization_id}/devices/statuses"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)


# ==================================================
# GET Environmental Sensor Data
# ==================================================
def get_network_sensor_alerts(api_key, network_id):
    url = f"{BASE_URL}/networks/{network_id}/sensor/alerts/current/overview/byMetric"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None

def get_device_sensor_data(api_key, serial):
    url = f"{BASE_URL}/devices/{serial}/sensor/readings/latest"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None

def get_device_sensor_relationships(api_key, serial):
    url = f"{BASE_URL}/devices/{serial}/sensor/relationships"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None

# ==================================================
# GET Organization Details
# ==================================================
def get_organization_inventory(api_key, organization_id):
    url = f"{BASE_URL}/organizations/{organization_id}/inventory/devices"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None

def get_organization_licenses(api_key, organization_id):
    url = f"{BASE_URL}/organizations/{organization_id}/licenses"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None

def get_organization_summary(api_key, organization_id):
    url = f"{BASE_URL}/organizations/{organization_id}/summary"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None


# ==================================================
# GET Network Health and Performance
# ==================================================
def get_network_health(api_key, network_id):
    url = f"{BASE_URL}/networks/{network_id}/health"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def get_network_clients(api_key, network_id, timespan=3600):
    url = f"{BASE_URL}/networks/{network_id}/clients?timespan={timespan}"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def get_network_traffic(api_key, network_id, timespan=3600):
    url = f"{BASE_URL}/networks/{network_id}/traffic?timespan={timespan}"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def get_network_latency_stats(api_key, network_id, timespan=3600):
    url = f"{BASE_URL}/networks/{network_id}/latencyStats?timespan={timespan}"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

# ==================================================
# GET Device Specific Stats
# ==================================================
def get_device_clients(api_key, serial, timespan=3600):
    url = f"{BASE_URL}/devices/{serial}/clients?timespan={timespan}"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def get_device_performance(api_key, serial):
    url = f"{BASE_URL}/devices/{serial}/performance"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

def get_device_uplink(api_key, serial):
    url = f"{BASE_URL}/devices/{serial}/uplink"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(url, headers)

# ==================================================
# GET Network Topology
# ==================================================
def get_network_topology(api_key, network_id):
    """Get network topology data for visualization"""
    try:
        # Get devices in the network
        url = f"https://api.meraki.com/api/v1/networks/{network_id}/devices"
        headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        devices = make_meraki_request(url, headers)
        if devices:
            # Get uplink information for each device
            topology_data = {
                'nodes': [],
                'links': []
            }
            
            # Add devices as nodes
            for device in devices:
                topology_data['nodes'].append({
                    'id': device.get('serial', ''),
                    'name': device.get('name', 'Unknown Device'),
                    'model': device.get('model', ''),
                    'type': device.get('productType', 'unknown'),
                    'status': device.get('status', 'unknown')
                })
                
                # Get uplink info for this device
                uplink = get_device_uplink(api_key, device['serial'])
                if uplink:
                    for interface in uplink:
                        if interface.get('status') == 'Active':
                            topology_data['links'].append({
                                'source': device['serial'],
                                'target': interface.get('gateway', ''),
                                'interface': interface.get('interface', ''),
                                'type': interface.get('connectionType', '')
                            })
            
            return topology_data
        return None
    except Exception as e:
        print(f"Error getting network topology: {str(e)}")
        return None

# ==================================================
# Helper function for making Meraki API requests
# ==================================================
def get_meraki_cert():
    """Get the Meraki API certificate configuration"""
    import platform
    import certifi
    import ssl
    import os
    import requests.adapters
    
    # For Windows with proxy (like Zscaler)
    if platform.system() == 'Windows':
        try:
            # Create custom adapter that accepts proxy certificates
            class ProxyAdapter(requests.adapters.HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs):
                    ctx = ssl.create_default_context()
                    # Accept proxy certificates
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    kwargs['ssl_context'] = ctx
                    return super(ProxyAdapter, self).init_poolmanager(*args, **kwargs)
            
            return ProxyAdapter()
        except Exception:
            return False
    
    return certifi.where()

def make_meraki_request(url, headers, params=None, max_retries=3, retry_delay=1):
    """
    Make a request to the Meraki API with enhanced error handling, rate limiting, and retries
    
    Args:
        url (str): The API endpoint URL
        headers (dict): Request headers including API key
        params (dict, optional): Query parameters
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
    
    Returns:
        dict: JSON response from the API
    """
    import time
    from requests.exceptions import RequestException, SSLError
    import urllib3
    
    # Disable SSL verification warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Create a session
    session = requests.Session()
    
    # Get SSL configuration
    ssl_config = get_meraki_cert()
    
    if isinstance(ssl_config, requests.adapters.HTTPAdapter):
        # If we got an adapter (Windows with proxy), use it
        session.mount('https://', ssl_config)
        verify = False  # Disable verification since we're going through a proxy
        print("Using proxy-aware SSL configuration")
    else:
        # Otherwise use the certificate path
        verify = ssl_config
    
    if not verify:
        print("Warning: SSL verification disabled. Connection is not secure.")
        session.verify = False
    
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers, params=params)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', retry_delay))
                time.sleep(retry_after)
                continue
            
            # Handle common error codes
            if response.status_code == 401:
                raise Exception("Unauthorized: Please check your API key")
            elif response.status_code == 403:
                raise Exception("Forbidden: Your API key doesn't have access to this resource")
            elif response.status_code == 404:
                raise Exception("Not Found: The requested resource doesn't exist")
            
            response.raise_for_status()
            return response.json()
            
        except SSLError as ssl_err:
            if verify:
                print(f"SSL Error: {str(ssl_err)}")
                print("Falling back to insecure connection...")
                session.verify = False
                verify = False
                continue
            raise Exception("SSL verification failed and insecure connection not allowed")
        except RequestException as e:
            if attempt == max_retries - 1:
                raise Exception(f"API request failed after {max_retries} attempts: {str(e)}")
            time.sleep(retry_delay)
            continue
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    raise Exception("Maximum retry attempts reached")


# Secure API key management functions
def generate_key():
    """Generate a new encryption key"""
    return Fernet.generate_key()

def get_key_path():
    """Get the path to store the encrypted API key"""
    home = str(Path.home())
    config_dir = os.path.join(home, '.meraki_clu')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, '.meraki_key')

def get_encryption_key():
    """Get or create the encryption key"""
    key_file = os.path.join(str(Path.home()), '.meraki_clu', '.encryption_key')
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = generate_key()
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def store_api_key(api_key):
    """
    Securely store the Meraki API key
    
    Args:
        api_key (str): The Meraki API key to store
    """
    try:
        # Get encryption key
        encryption_key = get_encryption_key()
        f = Fernet(encryption_key)
        
        # Encrypt the API key
        encrypted_key = f.encrypt(api_key.encode())
        
        # Store the encrypted key
        key_path = get_key_path()
        with open(key_path, 'wb') as file:
            file.write(encrypted_key)
        
        print("API key stored securely")
        return True
    except Exception as e:
        print(f"Error storing API key: {str(e)}")
        return False

def load_api_key():
    """
    Load the stored Meraki API key
    
    Returns:
        str: The decrypted API key or None if not found
    """
    try:
        key_path = get_key_path()
        if not os.path.exists(key_path):
            return None
            
        # Get encryption key
        encryption_key = get_encryption_key()
        f = Fernet(encryption_key)
        
        # Read and decrypt the API key
        with open(key_path, 'rb') as file:
            encrypted_key = file.read()
        
        decrypted_key = f.decrypt(encrypted_key)
        return decrypted_key.decode()
    except Exception as e:
        print(f"Error loading API key: {str(e)}")
        return None

def initialize_api_key():
    """
    Initialize API key from environment variable or stored key
    
    Returns:
        str: The API key or None if not found
    """
    # First try environment variable
    api_key = os.getenv('MERAKI_DASHBOARD_API_KEY')
    if api_key:
        # Store it securely if found in environment
        store_api_key(api_key)
        return api_key
    
    # Try to load stored key
    api_key = load_api_key()
    if api_key:
        return api_key
    
    print("No API key found. Please set the MERAKI_DASHBOARD_API_KEY environment variable or use store_api_key() function.")
    return None
    return None
    return None