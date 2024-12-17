from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime
import meraki_api
from utilities import term_extra

def display_network_status(api_key, network_id):
    """Display network status overview"""
    status_data = meraki_api.get_network_status(api_key, network_id)
    
    if status_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Device Name")
        table.add_column("Status")
        table.add_column("Last Reported")
        table.add_column("Serial")
        table.add_column("Model")
        
        for device in status_data:
            status = device.get('status', 'unknown')
            status_color = {
                'online': 'green',
                'offline': 'red',
                'alerting': 'yellow'
            }.get(status.lower(), 'white')
            
            last_reported = device.get('lastReportedAt', '')
            if last_reported:
                last_reported = datetime.strptime(last_reported, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                device.get('name', 'N/A'),
                f"[{status_color}]{status}[/{status_color}]",
                last_reported,
                device.get('serial', 'N/A'),
                device.get('model', 'N/A')
            )
        
        console = Console()
        console.print("\nNetwork Status Overview:")
        console.print(table)
    else:
        print("No status data available")

def display_network_alerts(api_key, network_id):
    """Display network alerts"""
    alerts_data = meraki_api.get_network_alerts(api_key, network_id)
    
    if alerts_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Alert Type")
        table.add_column("Enabled")
        table.add_column("Alert Conditions")
        
        enabled_alerts = alerts_data.get('enabledAlerts', [])
        alert_configs = alerts_data.get('alertConfigs', [])
        
        for alert in alert_configs:
            table.add_row(
                alert.get('type', 'N/A'),
                '✓' if alert.get('type') in enabled_alerts else '✗',
                str(alert.get('conditions', {}))
            )
        
        console = Console()
        console.print("\nNetwork Alerts Configuration:")
        console.print(table)
    else:
        print("No alert data available")

def display_network_clients(api_key, network_id):
    """Display network clients"""
    clients_data = meraki_api.get_network_clients(api_key, network_id)
    
    if clients_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Client Name")
        table.add_column("IP Address")
        table.add_column("MAC Address")
        table.add_column("Description")
        table.add_column("First Seen")
        table.add_column("Last Seen")
        
        for client in clients_data:
            first_seen = datetime.fromtimestamp(client.get('firstSeen', 0)).strftime("%Y-%m-%d %H:%M")
            last_seen = datetime.fromtimestamp(client.get('lastSeen', 0)).strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                client.get('description', 'N/A'),
                client.get('ip', 'N/A'),
                client.get('mac', 'N/A'),
                client.get('notes', 'N/A'),
                first_seen,
                last_seen
            )
        
        console = Console()
        console.print("\nNetwork Clients:")
        console.print(table)
    else:
        print("No client data available")

def display_network_traffic(api_key, network_id):
    """Display network traffic analysis"""
    traffic_data = meraki_api.get_network_traffic(api_key, network_id)
    
    if traffic_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Application")
        table.add_column("Destination")
        table.add_column("Protocol")
        table.add_column("Total (MB)")
        
        for entry in traffic_data:
            table.add_row(
                entry.get('application', 'N/A'),
                entry.get('destination', 'N/A'),
                entry.get('protocol', 'N/A'),
                f"{entry.get('total', 0) / (1024*1024):.2f}"
            )
        
        console = Console()
        console.print("\nNetwork Traffic Analysis:")
        console.print(table)
    else:
        print("No traffic data available")

def display_network_settings(api_key, network_id):
    """Display network settings"""
    settings_data = meraki_api.get_network_settings(api_key, network_id)
    
    if settings_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Setting")
        table.add_column("Value")
        
        settings_map = {
            'localStatusPageEnabled': 'Local Status Page',
            'remoteStatusPageEnabled': 'Remote Status Page',
            'secureConnect': 'Secure Connect',
            'namedVlans': 'Named VLANs'
        }
        
        for key, display_name in settings_map.items():
            value = settings_data.get(key, None)
            table.add_row(
                display_name,
                '✓' if value else '✗'
            )
        
        console = Console()
        console.print("\nNetwork Settings:")
        console.print(table)
    else:
        print("No settings data available")