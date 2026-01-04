from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime
from modules.meraki import meraki_api
from settings import term_extra
import os
from pathlib import Path
from termcolor import colored
import logging

def display_network_status(status_data, api_key_or_sdk=None, organization_id=None):
    """
    Display network status overview with enhanced status information.
    
    Args:
        status_data: List of device dictionaries
        api_key_or_sdk: Optional API key or SDK wrapper for status enrichment
        organization_id: Optional organization ID for fetching device statuses
    """
    if status_data:
        # Try to enrich with device statuses if API/organization info is provided
        device_statuses = {}
        if api_key_or_sdk and organization_id:
            try:
                if hasattr(api_key_or_sdk, 'get_organization_devices_statuses'):
                    # SDK wrapper
                    statuses = api_key_or_sdk.get_organization_devices_statuses(organization_id)
                elif hasattr(api_key_or_sdk, 'dashboard'):
                    # SDK wrapper direct
                    statuses = api_key_or_sdk.dashboard.organizations.getOrganizationDevicesStatuses(organization_id)
                else:
                    # API key
                    statuses = meraki_api.get_organization_devices_statuses(api_key_or_sdk, organization_id)
                
                # Create lookup by serial
                if statuses:
                    for status_info in statuses:
                        serial = status_info.get('serial')
                        if serial:
                            device_statuses[serial] = status_info
            except Exception as e:
                logging.debug(f"Could not fetch device statuses for enrichment: {str(e)}")
        
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Device Name")
        table.add_column("Status")
        table.add_column("Last Reported")
        table.add_column("Serial")
        table.add_column("Model")
        
        for device in status_data:
            serial = device.get('serial')
            
            # Try to get status from enriched data first
            status_info = device_statuses.get(serial) if serial else None
            status = None
            last_reported = None
            
            if status_info:
                status = status_info.get('status')
                last_reported = status_info.get('lastReportedAt')
            else:
                # Fall back to device data
                status = device.get('status')
                last_reported = device.get('lastReportedAt')
            
            # Enhanced status determination
            if not status or status == 'unknown':
                # Try to determine from lastReportedAt if available
                if last_reported:
                    try:
                        from datetime import datetime, timezone
                        if isinstance(last_reported, str):
                            try:
                                last_reported_dt = datetime.strptime(last_reported, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                            except ValueError:
                                try:
                                    last_reported_dt = datetime.strptime(last_reported, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                                except ValueError:
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
                            status = 'online'
                        elif time_diff < 3600:  # 1 hour
                            status = 'dormant'
                        else:
                            status = 'offline'
                    except Exception:
                        status = 'unknown'
                else:
                    status = 'unknown'
            
            # Format last reported timestamp
            if last_reported:
                try:
                    if isinstance(last_reported, str):
                        try:
                            last_reported_dt = datetime.strptime(last_reported, "%Y-%m-%dT%H:%M:%S.%fZ")
                            last_reported = last_reported_dt.strftime("%Y-%m-%d %H:%M")
                        except ValueError:
                            try:
                                last_reported_dt = datetime.strptime(last_reported, "%Y-%m-%dT%H:%M:%SZ")
                                last_reported = last_reported_dt.strftime("%Y-%m-%d %H:%M")
                            except ValueError:
                                from datetime import datetime, timezone
                                last_reported_dt = datetime.fromisoformat(last_reported.replace('Z', '+00:00'))
                                last_reported = last_reported_dt.strftime("%Y-%m-%d %H:%M")
                    else:
                        last_reported = last_reported.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    last_reported = "Unknown format"
            else:
                last_reported = "N/A"
            
            # Status color coding
            status_color = {
                'online': 'green',
                'offline': 'red',
                'alerting': 'yellow',
                'dormant': 'yellow'
            }.get(status.lower() if status else 'unknown', 'white')
            
            table.add_row(
                device.get('name', 'N/A'),
                f"[{status_color}]{status or 'unknown'}[/{status_color}]",
                last_reported,
                device.get('serial', 'N/A'),
                device.get('model', 'N/A')
            )
        
        console = Console()
        console.print("\nNetwork Status Overview:")
        console.print(table)
    else:
        print("No status data available")

def display_network_alerts(api_key_or_sdk, network_id):
    """Display network alerts"""
    # Check if api_key_or_sdk is an SDK wrapper instance or an API key
    if isinstance(api_key_or_sdk, str):
        # It's an API key, use the custom implementation
        alerts_data = meraki_api.get_network_alerts(api_key_or_sdk, network_id)
    else:
        # It's an SDK wrapper instance
        alerts_data = api_key_or_sdk.get_network_alerts(network_id)
    
    if alerts_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Alert Type")
        table.add_column("Severity")
        table.add_column("Time")
        table.add_column("Device")
        table.add_column("Description")
        
        for alert in alerts_data:
            severity_color = {
                'critical': 'red',
                'warning': 'yellow',
                'info': 'blue'
            }.get(alert.get('severity', '').lower(), 'white')
            
            alert_time = alert.get('occurredAt', '')
            if alert_time:
                alert_time = datetime.strptime(alert_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                alert.get('type', 'N/A'),
                f"[{severity_color}]{alert.get('severity', 'N/A')}[/{severity_color}]",
                alert_time,
                alert.get('deviceName', 'N/A'),
                alert.get('description', 'N/A')
            )
        
        console = Console()
        console.print("\nNetwork Alerts:")
        console.print(table)
    else:
        print("No alerts data available")

def display_network_clients(clients_data):
    """Display network clients with detailed connection information"""
    if clients_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Client Name")
        table.add_column("MAC Address")
        table.add_column("IP Address")
        table.add_column("VLAN")
        table.add_column("Connected Device")
        table.add_column("Port")
        table.add_column("Status")
        table.add_column("Last Seen")
        
        for client in clients_data:
            last_seen = client.get('lastSeen', '')
            if last_seen:
                try:
                    last_seen = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    # Handle alternative date formats
                    try:
                        last_seen = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
                    except ValueError:
                        last_seen = "Unknown format"
            
            # Get client status with color coding
            status = client.get('status', 'unknown')
            status_colors = {
                'online': 'green',
                'offline': 'red',
                'dormant': 'yellow'
            }
            status_color = status_colors.get(status.lower() if status else 'unknown', 'white')
            
            # Get connection details
            vlan = client.get('vlan', 'N/A')
            connected_device = client.get('recentDeviceName', client.get('deviceName', 'N/A'))
            
            # Get switchport information with port number
            port = 'N/A'
            if client.get('switchport'):
                port = f"{client.get('switchport', 'N/A')}"
                # Add port description if available
                if client.get('switchportDesc'):
                    port += f" ({client.get('switchportDesc')})"
                # Add adaptive policy group if available
                elif client.get('adaptivePolicyGroup'):
                    port += f" ({client.get('adaptivePolicyGroup')})"
            
            table.add_row(
                client.get('description', client.get('dhcpHostname', client.get('hostname', 'Unknown'))),
                client.get('mac', 'N/A'),
                client.get('ip', 'N/A'),
                str(vlan),
                connected_device,
                port,
                colored(status, status_color),
                last_seen
            )
        
        console = Console()
        console.print(f"\nNetwork Clients ({len(clients_data)}):")
        console.print(table)
        
        # Add option to export client data
        export_choice = input(f"{colored('Export client data to CSV? (y/n): ', 'cyan')}")
        if export_choice.lower() == 'y':
            try:
                import csv
                
                # Create export directory in user's Downloads folder
                downloads_path = str(Path.home() / "Downloads")
                current_date = datetime.now().strftime("%Y-%m-%d")
                export_dir = os.path.join(downloads_path, f"Cisco-Meraki-CLU-Export-{current_date}")
                os.makedirs(export_dir, exist_ok=True)
                
                # Create CSV file
                csv_path = os.path.join(export_dir, f"network_clients_{current_date}.csv")
                with open(csv_path, 'w', newline='') as csvfile:
                    fieldnames = ['Name', 'MAC Address', 'IP Address', 'VLAN', 'Connected Device', 
                                 'Port', 'Status', 'Last Seen']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for client in clients_data:
                        last_seen = client.get('lastSeen', '')
                        if last_seen:
                            try:
                                last_seen = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
                            except ValueError:
                                try:
                                    last_seen = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
                                except ValueError:
                                    last_seen = "Unknown format"
                        
                        writer.writerow({
                            'Name': client.get('description', client.get('dhcpHostname', client.get('hostname', 'Unknown'))),
                            'MAC Address': client.get('mac', 'N/A'),
                            'IP Address': client.get('ip', 'N/A'),
                            'VLAN': client.get('vlan', 'N/A'),
                            'Connected Device': client.get('recentDeviceName', client.get('deviceName', 'N/A')),
                            'Port': client.get('switchport', 'N/A'),
                            'Status': client.get('status', 'unknown'),
                            'Last Seen': last_seen
                        })
                
                print(f"{colored('Client data exported to ', 'green')}{csv_path}")
            except Exception as e:
                print(f"{colored('Error exporting client data: ', 'red')}{str(e)}")
    else:
        print("No client data available")

def display_network_traffic(api_key_or_sdk, network_id):
    """Display network traffic analysis"""
    # Check if api_key_or_sdk is an SDK wrapper instance or an API key
    if isinstance(api_key_or_sdk, str):
        # It's an API key, use the custom implementation
        traffic_data = meraki_api.get_network_traffic(api_key_or_sdk, network_id)
    else:
        # It's an SDK wrapper instance
        traffic_data = api_key_or_sdk.get_network_traffic(network_id)
    
    if traffic_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Application")
        table.add_column("Protocol")
        table.add_column("Destination")
        table.add_column("Port")
        table.add_column("Usage (MB)")
        
        for app in traffic_data:
            table.add_row(
                app.get('application', 'N/A'),
                app.get('protocol', 'N/A'),
                app.get('destination', 'N/A'),
                str(app.get('port', 'N/A')),
                str(round(app.get('usage', 0) / 1024 / 1024, 2))
            )
        
        console = Console()
        console.print("\nNetwork Traffic Analysis:")
        console.print(table)
    else:
        print("No traffic data available")

def display_network_devices(devices_data):
    """Display network devices"""
    if devices_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Device Name")
        table.add_column("Model")
        table.add_column("Serial")
        table.add_column("MAC Address")
        table.add_column("Status")
        
        for device in devices_data:
            status = device.get('status', 'unknown')
            status_color = {
                'online': 'green',
                'offline': 'red',
                'alerting': 'yellow'
            }.get(status.lower() if status else 'unknown', 'white')
            
            table.add_row(
                device.get('name', 'N/A'),
                device.get('model', 'N/A'),
                device.get('serial', 'N/A'),
                device.get('mac', 'N/A'),
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        console = Console()
        console.print(f"\nNetwork Devices ({len(devices_data)}):")
        console.print(table)
    else:
        print("No device data available")

def display_network_settings(api_key_or_sdk, network_id):
    """Display network settings"""
    # Check if api_key_or_sdk is an SDK wrapper instance or an API key
    if isinstance(api_key_or_sdk, str):
        # It's an API key, use the custom implementation
        settings_data = meraki_api.get_network_settings(api_key_or_sdk, network_id)
    else:
        # It's an SDK wrapper instance
        settings_data = api_key_or_sdk.get_network_settings(network_id)
    
    if settings_data:
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Setting")
        table.add_column("Value")
        
        settings_to_display = [
            ('Name', 'name'),
            ('Type', 'type'),
            ('Time Zone', 'timeZone'),
            ('Tags', 'tags'),
            ('Notes', 'notes')
        ]
        
        for display_name, key in settings_to_display:
            value = settings_data.get(key, 'N/A')
            if isinstance(value, list):
                value = ', '.join(value)
            table.add_row(display_name, str(value))
        
        console = Console()
        console.print("\nNetwork Settings:")
        console.print(table)
    else:
        print("No settings data available")

def display_organization_status(api_key, organization_id):
    """Display organization status overview"""
    try:
        # Get organization details
        organization = meraki_api.get_meraki_organization_details(api_key, organization_id)
        
        if organization:
            console = Console()
            console.print(f"\n[bold green]Organization Status:[/bold green] {organization.get('name', 'N/A')}")
            console.print(f"ID: {organization.get('id', 'N/A')}")
            console.print(f"URL: {organization.get('url', 'N/A')}")
            
            try:
                # Get organization inventory
                inventory = meraki_api.get_meraki_organization_inventory(api_key, organization_id)
                
                if inventory:
                    # Count devices by status
                    status_counts = {'online': 0, 'offline': 0, 'alerting': 0, 'dormant': 0, 'other': 0}
                    
                    for device in inventory:
                        status = device.get('networkConnectionStatus', 'other').lower()
                        if status in status_counts:
                            status_counts[status] += 1
                        else:
                            status_counts['other'] += 1
                    
                    # Create a table for status summary
                    table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
                    table.add_column("Status")
                    table.add_column("Count")
                    
                    table.add_row("[green]Online[/green]", str(status_counts['online']))
                    table.add_row("[red]Offline[/red]", str(status_counts['offline']))
                    table.add_row("[yellow]Alerting[/yellow]", str(status_counts['alerting']))
                    table.add_row("Dormant", str(status_counts['dormant']))
                    table.add_row("Other", str(status_counts['other']))
                    
                    console.print("\n[bold]Device Status Summary:[/bold]")
                    console.print(table)
                else:
                    console.print("[yellow]No inventory data available[/yellow]")
            except Exception as inventory_error:
                console.print(f"[yellow]Unable to retrieve inventory data: {str(inventory_error)}[/yellow]")
                
                # Try to get devices directly as a fallback
                try:
                    devices = meraki_api.get_meraki_organization_devices(api_key, organization_id)
                    if devices:
                        console.print("\n[bold]Organization Devices:[/bold]")
                        console.print(f"Total devices: {len(devices)}")
                    else:
                        console.print("[yellow]No device data available[/yellow]")
                except Exception as devices_error:
                    console.print(f"[yellow]Unable to retrieve device data: {str(devices_error)}[/yellow]")
        else:
            print("Organization details not available")
    except Exception as e:
        print(f"Error displaying organization status: {str(e)}")

def display_organization_networks(api_key, organization_id):
    """Display organization networks"""
    try:
        # Get organization networks
        networks = meraki_api.get_meraki_organization_networks(api_key, organization_id)
        
        if networks:
            table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
            table.add_column("Network Name")
            table.add_column("Network ID")
            table.add_column("Time Zone")
            table.add_column("Product Types")
            
            for network in networks:
                product_types = ', '.join(network.get('productTypes', []))
                
                table.add_row(
                    network.get('name', 'N/A'),
                    network.get('id', 'N/A'),
                    network.get('timeZone', 'N/A'),
                    product_types
                )
            
            console = Console()
            console.print("\nOrganization Networks:")
            console.print(table)
        else:
            print("No networks available for this organization")
    except Exception as e:
        print(f"Error displaying organization networks: {str(e)}")

def display_organization_devices(api_key, organization_id):
    """Display organization devices"""
    try:
        # Get organization devices
        devices = meraki_api.get_meraki_organization_devices(api_key, organization_id)
        
        if devices:
            table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
            table.add_column("Name")
            table.add_column("Serial")
            table.add_column("Model")
            table.add_column("Network")
            table.add_column("Status")
            
            for device in devices:
                status = device.get('status', 'unknown')
                status_color = {
                    'online': 'green',
                    'offline': 'red',
                    'alerting': 'yellow'
                }.get(status.lower() if status else 'unknown', 'white')
                
                table.add_row(
                    device.get('name', 'N/A'),
                    device.get('serial', 'N/A'),
                    device.get('model', 'N/A'),
                    device.get('networkId', 'N/A'),
                    f"[{status_color}]{status}[/{status_color}]"
                )
            
            console = Console()
            console.print("\nOrganization Devices:")
            console.print(table)
        else:
            print("No devices available for this organization")
    except Exception as e:
        print(f"Error displaying organization devices: {str(e)}")