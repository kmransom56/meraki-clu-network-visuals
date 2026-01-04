"""
Meraki SDK Wrapper Module

This module provides a wrapper around the official Meraki Dashboard API Python SDK.
It implements the same interface as the custom meraki_api module but uses the official SDK under the hood.
This allows for a gradual transition from the custom API implementation to the SDK.
"""

import logging
import os
import ssl
import certifi
import time
import sys
import platform
from datetime import datetime
from termcolor import colored

# Try to import the Meraki SDK, install if not available
try:
    import meraki
except ImportError:
    print(colored("Meraki SDK not found. Installing...", "yellow"))
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "meraki"])
        import meraki
        print(colored("Meraki SDK installed successfully.", "green"))
    except Exception as e:
        print(colored(f"Error installing Meraki SDK: {str(e)}", "red"))
        print(colored("Please install it manually using: pip install meraki", "red"))
        # Fall back to custom API if SDK can't be installed
        print(colored("Falling back to custom API implementation.", "yellow"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Global variables
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

class MerakiSDKWrapper:
    """
    Wrapper class for the Meraki Dashboard API Python SDK.
    Implements the same interface as the custom meraki_api module.
    """
    
    def __init__(self, api_key):
        """
        Initialize the Meraki SDK wrapper with the API key.
        
        Args:
            api_key (str): Meraki API key
        """
        self.api_key = api_key
        self.dashboard = self._initialize_dashboard()
        self.check_api_version()
        
    def _initialize_dashboard(self):
        """
        Initialize the Meraki Dashboard API with proper SSL configuration.
        
        Returns:
            meraki.DashboardAPI: Initialized Meraki Dashboard API instance
        """
        # For Windows environments with proxies (like Zscaler), we need special handling
        is_windows = platform.system() == 'Windows'
        
        # Clear any conflicting environment variables
        if 'REQUESTS_CA_BUNDLE' in os.environ:
            del os.environ['REQUESTS_CA_BUNDLE']
        if 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
        
        # Configure SSL verification based on the platform
        if is_windows:
            # On Windows, especially with proxies like Zscaler, we might need to disable verification
            logging.info("Windows detected, configuring special SSL handling")
            try:
                # First try with verification enabled
                dashboard = meraki.DashboardAPI(
                    api_key=self.api_key,
                    base_url='https://api.meraki.com/api/v1',
                    output_log=False,
                    print_console=False,
                    suppress_logging=False,
                    maximum_retries=MAX_RETRIES,
                    wait_on_rate_limit=True,
                    retry_4xx_error=True,
                    retry_4xx_error_wait_time=RETRY_DELAY,
                    use_iterator_for_get_pages=False
                )
                # Test the connection
                dashboard.organizations.getOrganizations()
                return dashboard
            except Exception as e:
                logging.warning(f"SSL verification failed on Windows: {str(e)}")
                logging.warning("Trying with SSL verification disabled")
                # If that fails, try with verification disabled
                dashboard = meraki.DashboardAPI(
                    api_key=self.api_key,
                    base_url='https://api.meraki.com/api/v1',
                    output_log=False,
                    print_console=False,
                    suppress_logging=False,
                    maximum_retries=MAX_RETRIES,
                    wait_on_rate_limit=True,
                    retry_4xx_error=True,
                    retry_4xx_error_wait_time=RETRY_DELAY,
                    use_iterator_for_get_pages=False,
                    verify=False  # Disable SSL verification
                )
                return dashboard
        else:
            # For non-Windows platforms, use system certificates
            return meraki.DashboardAPI(
                api_key=self.api_key,
                base_url='https://api.meraki.com/api/v1',
                output_log=False,
                print_console=False,
                suppress_logging=False,
                maximum_retries=MAX_RETRIES,
                wait_on_rate_limit=True,
                retry_4xx_error=True,
                retry_4xx_error_wait_time=RETRY_DELAY,
                use_iterator_for_get_pages=False,
                verify=certifi.where()  # Use certifi for certificate verification
            )
    
    def check_api_version(self):
        """
        Check the Meraki API version and log compatibility information.
        """
        try:
            # Get the current API version from the Meraki SDK
            api_status = self.dashboard.organizations.getOrganizationApiRequests(
                organizationId='1',  # This is just a placeholder, the request will fail but we'll get version info
                total_pages='all',
                timespan=1
            )
        except meraki.exceptions.APIError as e:
            # Extract API version from the error message
            error_message = str(e)
            if 'API version' in error_message:
                version_info = error_message.split('API version')[1].strip()
                logging.info(f"Connected to Meraki API {version_info}")
                print(colored(f"Connected to Meraki API {version_info}", "green"))
            else:
                logging.info("Could not determine Meraki API version")
        except Exception as e:
            logging.warning(f"Error checking API version: {str(e)}")
    
    # === Organization Operations ===
    
    def get_organizations(self):
        """
        Get a list of organizations accessible by the user.
        
        Returns:
            list: List of organization dictionaries
        """
        try:
            # First attempt with default settings
            return self.dashboard.organizations.getOrganizations()
        except Exception as e:
            logging.error(f"Error getting organizations with SDK: {str(e)}")
            
            # Try fallback method with direct API call
            try:
                import requests
                import platform
                
                logging.info("Attempting fallback method for getting organizations")
                
                # Configure SSL verification based on the platform
                if platform.system() == 'Windows':
                    # On Windows, especially with proxies like Zscaler, we might need to disable verification
                    verify = False
                else:
                    # For non-Windows platforms, use system certificates
                    verify = certifi.where()
                
                # Make direct API call
                headers = {
                    "X-Cisco-Meraki-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    "https://api.meraki.com/api/v1/organizations",
                    headers=headers,
                    verify=verify
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"Fallback API request failed: {response.status_code} - {response.text}")
                    return []
            except Exception as fallback_error:
                logging.error(f"Fallback method also failed: {str(fallback_error)}")
                return []
    
    def get_organization_networks(self, org_id):
        """
        Get a list of networks for an organization.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            list: List of network dictionaries
        """
        try:
            return self.dashboard.organizations.getOrganizationNetworks(organizationId=org_id)
        except Exception as e:
            logging.error(f"Error getting organization networks: {str(e)}")
            
            # Try fallback method with direct API call
            try:
                import requests
                import platform
                
                logging.info("Attempting fallback method for getting organization networks")
                
                # Configure SSL verification based on the platform
                if platform.system() == 'Windows':
                    # On Windows, especially with proxies like Zscaler, we might need to disable verification
                    verify = False
                else:
                    # For non-Windows platforms, use system certificates
                    verify = certifi.where()
                
                # Make direct API call
                headers = {
                    "X-Cisco-Meraki-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    f"https://api.meraki.com/api/v1/organizations/{org_id}/networks",
                    headers=headers,
                    verify=verify
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"Fallback API request failed: {response.status_code} - {response.text}")
                    return []
            except Exception as fallback_error:
                logging.error(f"Fallback method also failed: {str(fallback_error)}")
                return []
    
    def get_organization_devices(self, org_id):
        """
        Get a list of devices for an organization.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            list: List of device dictionaries
        """
        try:
            return self.dashboard.organizations.getOrganizationDevices(organizationId=org_id)
        except Exception as e:
            logging.error(f"Error getting organization devices: {str(e)}")
            
            # Try fallback method with direct API call
            try:
                import requests
                import platform
                
                logging.info("Attempting fallback method for getting organization devices")
                
                # Configure SSL verification based on the platform
                if platform.system() == 'Windows':
                    # On Windows, especially with proxies like Zscaler, we might need to disable verification
                    verify = False
                else:
                    # For non-Windows platforms, use system certificates
                    verify = certifi.where()
                
                # Make direct API call
                headers = {
                    "X-Cisco-Meraki-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    f"https://api.meraki.com/api/v1/organizations/{org_id}/devices",
                    headers=headers,
                    verify=verify
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"Fallback API request failed: {response.status_code} - {response.text}")
                    return []
            except Exception as fallback_error:
                logging.error(f"Fallback method also failed: {str(fallback_error)}")
                return []
    
    def get_organization_admins(self, org_id):
        """
        Get a list of admins for an organization.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            list: List of admin dictionaries
        """
        try:
            return self.dashboard.organizations.getOrganizationAdmins(organizationId=org_id)
        except Exception as e:
            logging.error(f"Error getting organization admins: {str(e)}")
            
            # Try fallback method with direct API call
            try:
                import requests
                import platform
                
                logging.info("Attempting fallback method for getting organization admins")
                
                # Configure SSL verification based on the platform
                if platform.system() == 'Windows':
                    # On Windows, especially with proxies like Zscaler, we might need to disable verification
                    verify = False
                else:
                    # For non-Windows platforms, use system certificates
                    verify = certifi.where()
                
                # Make direct API call
                headers = {
                    "X-Cisco-Meraki-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    f"https://api.meraki.com/api/v1/organizations/{org_id}/admins",
                    headers=headers,
                    verify=verify
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"Fallback API request failed: {response.status_code} - {response.text}")
                    return []
            except Exception as fallback_error:
                logging.error(f"Fallback method also failed: {str(fallback_error)}")
                return []
    
    def get_organization_licenses(self, org_id):
        """
        Get a list of licenses for an organization.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            list: List of license dictionaries
        """
        try:
            return self.dashboard.organizations.getOrganizationLicenses(organizationId=org_id)
        except Exception as e:
            logging.error(f"Error getting organization licenses: {str(e)}")
            
            # Try fallback method with direct API call
            try:
                import requests
                import platform
                
                logging.info("Attempting fallback method for getting organization licenses")
                
                # Configure SSL verification based on the platform
                if platform.system() == 'Windows':
                    # On Windows, especially with proxies like Zscaler, we might need to disable verification
                    verify = False
                else:
                    # For non-Windows platforms, use system certificates
                    verify = certifi.where()
                
                # Make direct API call
                headers = {
                    "X-Cisco-Meraki-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    f"https://api.meraki.com/api/v1/organizations/{org_id}/licenses",
                    headers=headers,
                    verify=verify
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"Fallback API request failed: {response.status_code} - {response.text}")
                    return []
            except Exception as fallback_error:
                logging.error(f"Fallback method also failed: {str(fallback_error)}")
                return []
    
    def get_organization_inventory(self, org_id):
        """
        Get inventory information for an organization.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            list: List of inventory item dictionaries
        """
        try:
            return self.dashboard.organizations.getOrganizationInventoryDevices(org_id)
        except Exception as e:
            logging.error(f"Error getting inventory for organization {org_id}: {str(e)}")
            return []
    
    def get_organization_licenses(self, org_id):
        """
        Get license information for an organization.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            list: List of license dictionaries
        """
        try:
            return self.dashboard.organizations.getOrganizationLicenses(org_id)
        except Exception as e:
            logging.error(f"Error getting licenses for organization {org_id}: {str(e)}")
            return []
    
    def get_organization_summary(self, org_id):
        """
        Get summary information about an organization.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            dict: Organization summary
        """
        try:
            # The SDK doesn't have a direct equivalent, so we'll build a summary
            networks = self.dashboard.organizations.getOrganizationNetworks(org_id)
            devices = self.dashboard.organizations.getOrganizationDevices(org_id)
            licenses = self.dashboard.organizations.getOrganizationLicenses(org_id)
            
            return {
                'networks': len(networks),
                'devices': len(devices),
                'licenses': len(licenses)
            }
        except Exception as e:
            logging.error(f"Error getting summary for organization {org_id}: {str(e)}")
            return {}
    
    def get_organization_devices_statuses(self, org_id):
        """
        Get device status information for an organization with enhanced data.
        
        Args:
            org_id (str): Organization ID
            
        Returns:
            list: List of device status dictionaries with enhanced information
        """
        try:
            devices_statuses = self.dashboard.organizations.getOrganizationDevicesStatuses(org_id)
            if devices_statuses:
                # Enrich device status data
                for device in devices_statuses:
                    # Ensure status is properly set
                    if not device.get('status') or device.get('status') == 'unknown':
                        # Try to determine status from lastReportedAt
                        last_reported = device.get('lastReportedAt')
                        if last_reported:
                            try:
                                from datetime import datetime, timezone
                                if isinstance(last_reported, str):
                                    if 'T' in last_reported:
                                        # ISO format with 'T' separator
                                        last_reported_dt = datetime.fromisoformat(last_reported.replace('Z', '+00:00'))
                                    else:
                                        # Try alternative formats without 'T'
                                        try:
                                            last_reported_dt = datetime.strptime(last_reported, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
                                        except ValueError:
                                            try:
                                                last_reported_dt = datetime.strptime(last_reported, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                                            except ValueError:
                                                # Fallback to fromisoformat which is more flexible
                                                last_reported_dt = datetime.fromisoformat(last_reported.replace('Z', '+00:00'))
                                    # Ensure timezone-aware datetime (handle naive datetimes)
                                    if last_reported_dt.tzinfo is None:
                                        last_reported_dt = last_reported_dt.replace(tzinfo=timezone.utc)
                                else:
                                    last_reported_dt = last_reported
                                    # Ensure timezone-aware datetime if it's a datetime object
                                    if isinstance(last_reported_dt, datetime) and last_reported_dt.tzinfo is None:
                                        last_reported_dt = last_reported_dt.replace(tzinfo=timezone.utc)
                                
                                now = datetime.now(timezone.utc)
                                time_diff = abs((now - last_reported_dt).total_seconds())  # Use abs to handle clock skew
                                
                                if time_diff < 300:  # 5 minutes
                                    device['status'] = 'online'
                                elif time_diff < 3600:  # 1 hour
                                    device['status'] = 'dormant'
                                else:
                                    device['status'] = 'offline'
                            except Exception as e:
                                logging.debug(f"Could not determine status from lastReportedAt: {str(e)}")
                                device['status'] = 'unknown'
            return devices_statuses or []
        except Exception as e:
            logging.error(f"Error getting device statuses for organization {org_id}: {str(e)}")
            return []
    
    # === Network Operations ===
    
    def get_network_devices(self, network_id):
        """
        Get all devices in a network.
        
        Args:
            network_id (str): Network ID
            
        Returns:
            list: List of device dictionaries
        """
        try:
            return self.dashboard.networks.getNetworkDevices(network_id)
        except Exception as e:
            logging.error(f"Error getting devices for network {network_id}: {str(e)}")
            return []
    
    def get_network_clients(self, network_id, timespan=10800):
        """
        Get clients connected to a network with enhanced data retrieval.
        
        Args:
            network_id (str): Network ID
            timespan (int): Timespan in seconds for which clients are fetched (default: 10800 = 3 hours)
            
        Returns:
            list: List of client dictionaries with enhanced information
        """
        try:
            clients = self.dashboard.networks.getNetworkClients(network_id, timespan=timespan)
            if clients:
                # Enrich client data with better field mapping
                for client in clients:
                    # Ensure status is properly set
                    if not client.get('status'):
                        # Determine status based on lastSeen if status is missing
                        last_seen = client.get('lastSeen')
                        if last_seen:
                            try:
                                from datetime import datetime, timezone
                                if isinstance(last_seen, str):
                                    if 'T' in last_seen:
                                        # ISO format with 'T' separator
                                        last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                                    else:
                                        # Try alternative formats without 'T'
                                        try:
                                            last_seen_dt = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
                                        except ValueError:
                                            try:
                                                last_seen_dt = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                                            except ValueError:
                                                # Fallback to fromisoformat which is more flexible
                                                last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                                    # Ensure timezone-aware datetime (handle naive datetimes)
                                    if last_seen_dt.tzinfo is None:
                                        last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)
                                else:
                                    last_seen_dt = last_seen
                                    # Ensure timezone-aware datetime if it's a datetime object
                                    if isinstance(last_seen_dt, datetime) and last_seen_dt.tzinfo is None:
                                        last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)
                                now = datetime.now(timezone.utc)
                                time_diff = abs((now - last_seen_dt).total_seconds())  # Use abs to handle clock skew
                                if time_diff < 300:  # 5 minutes
                                    client['status'] = 'online'
                                elif time_diff < 3600:  # 1 hour
                                    client['status'] = 'dormant'
                                else:
                                    client['status'] = 'offline'
                            except Exception:
                                client['status'] = 'unknown'
            return clients or []
        except Exception as e:
            logging.error(f"Error getting clients for network {network_id}: {str(e)}")
            return []
    
    def get_network_traffic(self, network_id, timespan=3600):
        """
        Get network traffic data.
        
        Args:
            network_id (str): Network ID
            timespan (int): Timespan in seconds for which traffic is fetched (default: 3600 = 1 hour)
            
        Returns:
            list: List of traffic flow dictionaries with application, destination, protocol, and usage data
        """
        try:
            traffic_data = self.dashboard.networks.getNetworkTraffic(network_id, timespan=timespan)
            
            # Transform the response to match expected format
            if isinstance(traffic_data, list):
                return traffic_data
            elif isinstance(traffic_data, dict):
                # If the API returns a dict, extract the flows
                return traffic_data.get('flows', []) if 'flows' in traffic_data else []
            else:
                return []
        except Exception as e:
            logging.warning(f"Could not get network traffic: {str(e)}")
            return []
    
    def get_network_topology(self, network_id):
        """
        Get network topology data.
        
        Args:
            network_id (str): Network ID
            
        Returns:
            dict: Network topology data with nodes and links
        """
        try:
            # Get network devices
            devices = self.get_network_devices(network_id)
            
            # Get network clients
            clients = self.get_network_clients(network_id, timespan=10800)
            
            # Get topology links directly from Meraki API
            try:
                topology_links = self.dashboard.networks.getNetworkTopologyLinkLayer(network_id)
            except Exception as e:
                logging.warning(f"Could not get topology links from API, building manually: {str(e)}")
                topology_links = []
            
            # Initialize topology data
            topology_data = {
                'network_name': self.get_network_name(network_id),
                'nodes': [],
                'links': []
            }
            
            # Add devices as nodes
            device_map = {}  # Map serial numbers to node indices
            for i, device in enumerate(devices):
                device_type = 'unknown'
                if 'model' in device and device['model'] is not None:
                    model = device['model'].lower()
                    if 'mx' in model:
                        device_type = 'security_appliance'
                    elif 'ms' in model:
                        device_type = 'switch'
                    elif 'mr' in model:
                        device_type = 'wireless'
                    elif 'mv' in model:
                        device_type = 'camera'
                
                node = {
                    'id': device.get('serial', f"device_{i}"),
                    'label': device.get('name', 'Unknown Device'),
                    'type': device_type,
                    'model': device.get('model', 'Unknown'),
                    'ip': device.get('lanIp', 'No IP'),
                    'mac': device.get('mac', 'No MAC'),
                    'serial': device.get('serial', 'No Serial'),
                    'firmware': device.get('firmware', 'Unknown'),
                    'status': device.get('status', 'unknown')
                }
                
                topology_data['nodes'].append(node)
                device_map[device.get('serial')] = len(topology_data['nodes']) - 1
            
            # Add clients as nodes
            for i, client in enumerate(clients):
                # Determine client type based on available information
                client_type = 'unknown'
                if 'deviceTypePrediction' in client and client['deviceTypePrediction'] is not None:
                    client_type = client['deviceTypePrediction'].lower()
                elif 'manufacturer' in client and client['manufacturer'] is not None:
                    manufacturer = client['manufacturer'].lower()
                    if any(mobile in manufacturer for mobile in ['apple', 'samsung', 'lg', 'motorola', 'xiaomi']):
                        client_type = 'mobile'
                    elif any(pc in manufacturer for pc in ['dell', 'hp', 'lenovo', 'microsoft', 'asus']):
                        client_type = 'desktop'
                
                # Get the connection details
                connection_details = {
                    'type': client.get('recentDeviceConnection', 'Unknown'),
                    'vlan': client.get('vlan', 'Unknown'),
                    'port': client.get('switchport', 'Unknown'),
                    'last_seen': client.get('lastSeen', 'Unknown')
                }
                
                node = {
                    'id': client.get('id', f"client_{i}"),
                    'label': client.get('description', client.get('mac', 'Unknown Client')),
                    'type': 'client',
                    'client_type': client_type,
                    'ip': client.get('ip', 'No IP'),
                    'mac': client.get('mac', 'No MAC'),
                    'vlan': client.get('vlan', 'Unknown'),
                    'connection': connection_details,
                    'usage': client.get('usage', {})
                }
                
                topology_data['nodes'].append(node)
            
            # Add links from the topology endpoint if available
            if topology_links:
                for link in topology_links:
                    source_serial = link.get('source', {}).get('serial')
                    dest_serial = link.get('destination', {}).get('serial')
                    
                    if source_serial in device_map and dest_serial in device_map:
                        topology_data['links'].append({
                            'source': device_map[source_serial],
                            'target': device_map[dest_serial],
                            'type': link.get('linkType', 'unknown'),
                            'status': link.get('status', 'unknown')
                        })
            else:
                # Fallback: build links based on device relationships
                # Connect switches to security appliances
                security_appliances = [i for i, node in enumerate(topology_data['nodes']) 
                                    if node['type'] == 'security_appliance']
                switches = [i for i, node in enumerate(topology_data['nodes']) 
                            if node['type'] == 'switch']
                
                # Connect all switches to the first security appliance if available
                if security_appliances and switches:
                    for switch in switches:
                        topology_data['links'].append({
                            'source': security_appliances[0],
                            'target': switch,
                            'type': 'wired',
                            'status': 'active'
                        })
                
                # Connect switches to each other in a chain
                for i in range(len(switches) - 1):
                    topology_data['links'].append({
                        'source': switches[i],
                        'target': switches[i + 1],
                        'type': 'wired',
                        'status': 'active'
                    })
            
            # Connect clients to their parent devices
            for i, node in enumerate(topology_data['nodes']):
                if node['type'] == 'client':
                    # Find the device this client is connected to
                    connected_to = None
                    
                    # For wireless clients
                    if node.get('connection', {}).get('type') == 'wireless':
                        # Find wireless APs
                        wireless_aps = [j for j, d in enumerate(topology_data['nodes']) 
                                        if d['type'] == 'wireless']
                        if wireless_aps:
                            # Connect to the first AP (could be improved with actual connection data)
                            connected_to = wireless_aps[0]
                    
                    # For wired clients
                    elif node.get('connection', {}).get('type') == 'wired':
                        # Try to find the switch with matching port
                        client_port = node.get('connection', {}).get('port')
                        client_vlan = node.get('connection', {}).get('vlan')
                        
                        for j, device in enumerate(topology_data['nodes']):
                            if device['type'] == 'switch':
                                # In a real implementation, you would check if this switch has the port
                                # the client is connected to. For now, connect to any switch.
                                connected_to = j
                                break
                    
                    # If we found a device to connect to
                    if connected_to is not None:
                        topology_data['links'].append({
                            'source': connected_to,
                            'target': i,
                            'type': node.get('connection', {}).get('type', 'unknown'),
                            'status': 'active'
                        })
            
            return topology_data
            
        except Exception as e:
            logging.error(f"Error getting topology for network {network_id}: {str(e)}")
            return {'nodes': [], 'links': [], 'network_name': 'Unknown Network'}
    
    def get_network_name(self, network_id):
        """
        Get the name of a network by its ID.
        
        Args:
            network_id (str): Network ID
            
        Returns:
            str: Network name or 'Unknown Network' if not found
        """
        try:
            network = self.dashboard.networks.getNetwork(network_id)
            return network.get('name', 'Unknown Network')
        except Exception as e:
            logging.error(f"Error getting network name: {str(e)}")
            return "Unknown Network"
    
    def get_network_health(self, network_id):
        """
        Get health information for a network.
        
        Args:
            network_id (str): Network ID
            
        Returns:
            dict: Network health information
        """
        try:
            return self.dashboard.networks.getNetworkHealthAlerts(network_id)
        except Exception as e:
            logging.error(f"Error getting health for network {network_id}: {str(e)}")
            return {}
    
    # === Device Operations ===
    
    def get_device_details(self, serial):
        """
        Get detailed information about a device.
        
        Args:
            serial (str): Device serial number
            
        Returns:
            dict: Device details
        """
        try:
            return self.dashboard.devices.getDevice(serial)
        except Exception as e:
            logging.error(f"Error getting details for device {serial}: {str(e)}")
            return {}
    
    def get_device_clients(self, serial, timespan=10800):
        """
        Get clients connected to a device with enhanced data retrieval.
        
        Args:
            serial (str): Device serial number
            timespan (int): Timespan in seconds for which clients are fetched (default: 10800 = 3 hours)
            
        Returns:
            list: List of client dictionaries with enhanced information
        """
        try:
            return self.dashboard.devices.getDeviceClients(serial, timespan=timespan)
        except Exception as e:
            logging.error(f"Error getting clients for device {serial}: {str(e)}")
            return []
    
    def get_device_uplink(self, serial):
        """
        Get uplink information for a device.
        
        Args:
            serial (str): Device serial number
            
        Returns:
            list: List of uplink dictionaries
        """
        try:
            return self.dashboard.devices.getDeviceUplink(serial)
        except Exception as e:
            logging.error(f"Error getting uplink for device {serial}: {str(e)}")
            return []
    
    # === Switch Operations ===
    
    def get_switch_ports(self, serial):
        """
        Get port information for a switch.
        
        Args:
            serial (str): Switch serial number
            
        Returns:
            list: List of port dictionaries
        """
        try:
            return self.dashboard.switch.getDeviceSwitchPorts(serial)
        except Exception as e:
            logging.error(f"Error getting ports for switch {serial}: {str(e)}")
            return []
    
    def get_switch_port_statuses(self, serial):
        """
        Get port status information for a switch.
        
        Args:
            serial (str): Switch serial number
            
        Returns:
            list: List of port status dictionaries
        """
        try:
            return self.dashboard.switch.getDeviceSwitchPortsStatuses(serial)
        except Exception as e:
            logging.error(f"Error getting port statuses for switch {serial}: {str(e)}")
            return []
    
    # === Helper Methods ===
    
    def select_organization(self):
        """
        Interactive selection of an organization.
        
        Returns:
            str: Organization ID or None if not selected
        """
        organizations = self.get_organizations()
        if organizations:
            print(colored("\nAvailable Organizations:", "cyan"))
            for idx, org in enumerate(organizations, 1):
                print(f"{idx}. {org['name']}")
            
            choice = input(colored("\nSelect an Organization (enter the number): ", "cyan"))
            try:
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(organizations):
                    return organizations[selected_index]['id']
                else:
                    print(colored("Invalid selection.", "red"))
            except ValueError:
                print(colored("Please enter a number.", "red"))
        
        return None
    
    def select_network(self, organization_id):
        """
        Interactive selection of a network.
        
        Args:
            organization_id (str): Organization ID
            
        Returns:
            str: Network ID or None if not selected
        """
        networks = self.get_organization_networks(organization_id)
        if networks:
            print("\nAvailable Networks:")
            for idx, network in enumerate(networks, 1):
                print(f"{idx}. {network['name']}")
            
            while True:
                try:
                    choice = input(colored("\nSelect a Network (enter the number): ", "cyan"))
                    selected_index = int(choice) - 1
                    if 0 <= selected_index < len(networks):
                        return networks[selected_index]['id']
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
                except IndexError:
                    print("Invalid selection. Please try again.")
        return None
    
    def select_device(self, network_id):
        """
        Interactive selection of a device.
        
        Args:
            network_id (str): Network ID
            
        Returns:
            str: Device serial number or None if not selected
        """
        devices = self.get_network_devices(network_id)
        if devices:
            print("\nAvailable Devices:")
            for idx, device in enumerate(devices, 1):
                print(f"{idx}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
            
            while True:
                try:
                    choice = input(colored("\nSelect a Device (enter the number): ", "cyan"))
                    selected_index = int(choice) - 1
                    if 0 <= selected_index < len(devices):
                        return devices[selected_index]['serial']
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
                except IndexError:
                    print("Invalid selection. Please try again.")
        return None
