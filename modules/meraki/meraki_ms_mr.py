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
import logging
from datetime import datetime
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE 

 
# ==================================================
# IMPORT custom modules
# ==================================================
from modules.meraki import meraki_api 
from settings import term_extra


# ==================================================
# DEFINE how to retrieve Switch Ports data
# ==================================================
def display_switch_ports(api_key, serial_number):
    port_statuses = []
    
    try:
        switch_ports = meraki_api.get_switch_ports(api_key, serial_number)
    except Exception as e:
        print(f"[red]Failed to fetch switch port configurations: {e}[/red]")
        return

    try:
        port_statuses = meraki_api.get_switch_ports_statuses_with_timespan(api_key, serial_number) or []
    except Exception as e:
        print(f"[red]Failed to fetch real-time port statuses/packets: {e}[/red]")

    if switch_ports:
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)

        columns = [
            ("Port", 5), ("Name", 30), ("Enabled", 5),
            ("PoE", 5), ("Type", 10), ("VLAN", 5),
            ("Allowed VLANs", 8), ("RSTP", 5), ("STP Guard", 10),
            ("Storm Cont", 5), ("In (Gbps)", 8), ("Out (Gbps)", 8),
            ("powerUsageInWh", 8), ("warnings", 30), ("errors", 30)
        ]
        for col_name, col_width in columns:
            table.add_column(col_name, style="dim", width=col_width)

        for port in switch_ports:
            port_id = port.get('portId', 'N/A')
            status = next((item for item in port_statuses if item.get("portId") == port_id), {})

            row_data = [
                port.get('portId', 'N/A'),
                port.get('name', 'N/A'),
                "Yes" if port.get('enabled') else "No",
                "Yes" if port.get('poeEnabled') else "No",
                port.get('type', 'N/A'),
                str(port.get('vlan', 'N/A')),
                port.get('allowedVlans', 'N/A'),
                "Yes" if port.get('rstpEnabled') else "No",
                port.get('stpGuard', 'N/A'),
                "Yes" if port.get('stormControlEnabled') else "No",
                f"{float(status.get('usageInKb', {}).get('recv', 'N/A')) / 1000000:.2f}" if status.get('usageInKb', {}).get('recv', 'N/A') != 'N/A' else 'N/A',
                f"{float(status.get('usageInKb', {}).get('sent', 'N/A')) / 1000000:.2f}" if status.get('usageInKb', {}).get('sent', 'N/A') != 'N/A' else 'N/A',
                str(status.get('powerUsageInWh', 'N/A')),
                str(status.get('warnings', 'N/A')),
                str(status.get('errors', 'N/A'))
            ]
            table.add_row(*row_data)

        console = Console()
        console.print("\nSwitch Ports:")
        console.print(table)
    else:
        print("[red]No ports found for the given serial number or failed to fetch ports.[/red]")

    input("Press Enter to continue...")


# ==================================================
# DISPLAY device list in a beautiful table format
# ==================================================
def display_devices(api_key, network_id, device_type):
    devices = None
    if device_type == 'switches':
        devices = meraki_api.get_meraki_switches(api_key, network_id)
    elif device_type == 'access_points':
        devices = meraki_api.get_meraki_access_points(api_key, network_id)

    term_extra.clear_screen()
    term_extra.print_ascii_art()

    if devices:
        devices = sorted(devices, key=lambda x: x.get('name', '').lower())
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)

        priority_columns = ['name', 'mac', 'lanIp', 'serial', 'model']
        excluded_columns = ['networkId', 'details', 'lat', 'lng', 'firmware']
        other_columns = [key for key in devices[0].keys() if key not in priority_columns and key not in excluded_columns]

        for key in priority_columns:
            table.add_column(key.upper(), no_wrap=True)

        for key in other_columns:
            table.add_column(key.upper(), no_wrap=False)

        for device in devices:
            row_data = [str(device.get(key, "")) for key in priority_columns + other_columns]
            table.add_row(*row_data)

        console = Console()
        console.print(table)
    else:
        print(colored(f"No {device_type} found in the selected network.", "red"))

    choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))


# ==================================================
# DISPLAY organization devices statuses in table
# ==================================================
def display_organization_devices_statuses(api_key, organization_id, network_id):
    devices_statuses = meraki_api.get_organization_devices_statuses(api_key, organization_id)
    term_extra.clear_screen()
    term_extra.print_ascii_art()

    filtered_devices_statuses = [device for device in devices_statuses if device.get('networkId') == network_id]
    filtered_devices_statuses = [device for device in filtered_devices_statuses if device.get('productType') in ["switch", "wireless"]]

    if devices_statuses:
        devices_statuses = [device for device in devices_statuses if device.get('productType') in ["switch", "wireless"]]
        devices_statuses = sorted(devices_statuses, key=lambda x: x.get('name', '').lower())
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)

        priority_columns = ['name', 'serial', 'mac', 'ipType', 'lanIp', 'gateway', 'primaryDns', 'secondaryDns', 'PSU 1', 'PSU 2', 'status', 'lastReportedAt']
        
        for key in priority_columns:
            formatted_key = key if not key.startswith("PSU") else key.replace(" ", "")
            table.add_column(formatted_key.upper(), no_wrap=True)
        
        for device in devices_statuses:
            row_data = []
            for key in priority_columns[:-4]:
                value = str(device.get(key, "N/A"))
                row_data.append(value)

            add_power_supply_statuses(device, row_data)

            status_value = device.get('status', 'unknown')
            
            # Enhanced status determination with better fallback
            if not status_value or status_value == 'unknown':
                # Try to determine from lastReportedAt if status is missing
                last_reported = device.get('lastReportedAt')
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
                            status_value = 'online'
                        elif time_diff < 3600:  # 1 hour
                            status_value = 'dormant'
                        else:
                            status_value = 'offline'
                    except Exception:
                        pass
            
            # Display status with color coding
            if status_value and status_value.lower() == 'online':
                row_data.append(f"[green]{status_value}[/green]")
            elif status_value and status_value.lower() == 'dormant':
                row_data.append(f"[yellow]{status_value}[/yellow]")
            elif status_value and (status_value.lower() == 'offline' or status_value.lower() == 'alerting'):
                row_data.append(f"[red]{status_value}[/red]")
            else:
                row_data.append(status_value or "N/A")

            last_reported_at = device.get('lastReportedAt')
            if last_reported_at:
                original_datetime = datetime.strptime(last_reported_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_datetime = original_datetime.strftime("%Y-%m-%d %H:%M")
                row_data.append(formatted_datetime)
            else:
                row_data.append("N/A")

            table.add_row(*row_data)

        console = Console()
        console.print(table)

    else:
        print("[red]No 'switch' devices found in the selected network.[/red]")
    choice = input("\nPress Enter to return to the previous menu... ")


# ==================================================
# INTEGRATE additional JSON data for PSU's details
# ==================================================
def add_power_supply_statuses(device, row_data):
    power_statuses = []
    if 'components' in device and 'powerSupplies' in device['components']:
        for slot in [1, 2]:
            power_supply = next((ps for ps in device['components']['powerSupplies'] if ps.get('slot') == slot), None)
            if power_supply:
                status = power_supply.get('status', 'N/A')
                if status.lower() == 'powering':
                    power_statuses.append(f"[green]{status}[/green]")
                elif status.lower() == 'disconnected':
                    power_statuses.append(f"[red]{status}[/red]")
                else:
                    power_statuses.append(status)
            else:
                power_statuses.append("N/A")
    else:
        power_statuses = ["N/A", "N/A"]
    row_data.extend(power_statuses)


# ==================================================
# DISPLAY network clients in a beautiful table format
# ==================================================
def display_clients(api_key_or_sdk, network_id):
    """
    Display network clients in a table format with enhanced information retrieval.
    
    Args:
        api_key_or_sdk: Either an API key (str) or SDK wrapper object
        network_id: Network ID to get clients from
    """
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    print(colored("Fetching client information...", "cyan"))
    
    # Use longer timespan (3 hours) for better client discovery
    timespan = 10800
    
    # Determine if we're using SDK wrapper or API key
    if hasattr(api_key_or_sdk, 'get_network_clients'):
        # SDK wrapper
        clients = api_key_or_sdk.get_network_clients(network_id, timespan=timespan)
    else:
        # API key
        clients = meraki_api.get_network_clients(api_key_or_sdk, network_id, timespan=timespan)
    
    # Try to get device information to enrich client data
    devices = []
    try:
        if hasattr(api_key_or_sdk, 'get_network_devices'):
            devices = api_key_or_sdk.get_network_devices(network_id)
        elif hasattr(api_key_or_sdk, 'dashboard'):
            devices = api_key_or_sdk.dashboard.networks.getNetworkDevices(network_id)
        else:
            devices = meraki_api.get_network_devices(api_key_or_sdk, network_id)
    except Exception as e:
        logging.debug(f"Could not fetch devices for enrichment: {str(e)}")
    
    # Create device lookup by serial for enrichment
    device_lookup = {dev.get('serial'): dev for dev in devices if dev.get('serial')}
    
    if clients:
        # Enrich client data with device information
        for client in clients:
            # Enhanced client name extraction with multiple fallbacks
            client_name = (
                client.get('description') or 
                client.get('dhcpHostname') or 
                client.get('hostname') or 
                client.get('user') or
                client.get('name') or
                'Unknown'
            )
            client['_display_name'] = client_name
            
            # Enhanced connected device information
            connected_device_serial = client.get('recentDeviceSerial') or client.get('deviceSerial')
            connected_device_name = client.get('recentDeviceName') or client.get('deviceName')
            
            if connected_device_serial and connected_device_serial in device_lookup:
                device_info = device_lookup[connected_device_serial]
                if not connected_device_name:
                    connected_device_name = device_info.get('name', 'Unknown Device')
                client['_connected_device'] = connected_device_name
            else:
                client['_connected_device'] = connected_device_name or 'N/A'
            
            # Enhanced status determination
            status = client.get('status')
            if not status or status == 'unknown':
                # Try to determine status from lastSeen
                last_seen = client.get('lastSeen')
                if last_seen:
                    try:
                        from datetime import datetime, timezone
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
                        now = datetime.now(timezone.utc)
                        time_diff = abs((now - last_seen_dt).total_seconds())  # Use abs to handle clock skew
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
            client['_status'] = status
            
            # Enhanced port/switchport information
            port = client.get('switchport') or client.get('port') or 'N/A'
            if port != 'N/A' and client.get('switchportDesc'):
                port = f"{port} ({client.get('switchportDesc')})"
            client['_port'] = port
        
        clients = sorted(clients, key=lambda x: x.get('_display_name', x.get('mac', '')).lower())
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)
        
        table.add_column("Client Name", style="cyan", width=30)
        table.add_column("MAC Address", style="green", width=18)
        table.add_column("IP Address", style="yellow", width=15)
        table.add_column("Connected Device", style="blue", width=25)
        table.add_column("Port", style="dim", width=12)
        table.add_column("VLAN", style="blue", width=8)
        table.add_column("Status", style="magenta", width=10)
        table.add_column("Last Seen", style="dim", width=16)
        
        for client in clients:
            # Format last seen timestamp
            last_seen = client.get('lastSeen', '')
            if last_seen:
                try:
                    last_seen_dt = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%fZ")
                    last_seen = last_seen_dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    try:
                        last_seen_dt = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%SZ")
                        last_seen = last_seen_dt.strftime("%Y-%m-%d %H:%M")
                    except ValueError:
                        try:
                            # Try ISO format with timezone
                            from datetime import datetime, timezone
                            last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                            last_seen = last_seen_dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            last_seen = "Unknown"
            else:
                last_seen = "N/A"
            
            # Get status with color coding
            status = client.get('_status', client.get('status', 'unknown'))
            if status and status.lower() == 'online':
                status_display = f"[green]{status}[/green]"
            elif status and status.lower() == 'offline':
                status_display = f"[red]{status}[/red]"
            elif status and status.lower() == 'dormant':
                status_display = f"[yellow]{status}[/yellow]"
            else:
                status_display = status or "N/A"
            
            table.add_row(
                client.get('_display_name', 'Unknown'),
                client.get('mac', 'N/A'),
                client.get('ip', 'N/A'),
                client.get('_connected_device', 'N/A'),
                client.get('_port', 'N/A'),
                str(client.get('vlan', 'N/A')),
                status_display,
                last_seen
            )
        
        console = Console()
        console.print(f"\nNetwork Clients ({len(clients)} total):")
        console.print(table)
    else:
        print(colored("No clients found in the selected network.", "red"))
        print(colored("Try increasing the timespan or check network connectivity.", "yellow"))
    
    choice = input(colored("\nPress Enter to return to the previous menu...", "green"))


# ==================================================
# DISPLAY network SSIDs in a beautiful table format
# ==================================================
def display_ssid(api_key_or_sdk, network_id):
    """
    Display network SSIDs in a table format.
    
    Args:
        api_key_or_sdk: Either an API key (str) or SDK wrapper object
        network_id: Network ID to get SSIDs from
    """
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    # Determine if we're using SDK wrapper or API key
    if hasattr(api_key_or_sdk, 'dashboard'):
        # SDK wrapper - use dashboard API
        try:
            ssids = api_key_or_sdk.dashboard.wireless.getNetworkWirelessSsids(network_id)
        except Exception as e:
            print(colored(f"Error fetching SSIDs: {str(e)}", "red"))
            logging.error(f"Error fetching SSIDs: {str(e)}", exc_info=True)
            ssids = []
    else:
        # API key - use custom API
        try:
            ssids = meraki_api.make_meraki_request(api_key_or_sdk, f"/networks/{network_id}/wireless/ssids")
        except Exception as e:
            print(colored(f"Error fetching SSIDs: {str(e)}", "red"))
            logging.error(f"Error fetching SSIDs: {str(e)}", exc_info=True)
            ssids = []
    
    if ssids:
        # Filter out disabled SSIDs or show all based on preference
        ssids = sorted(ssids, key=lambda x: x.get('number', 0))
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)
        
        table.add_column("SSID #", style="cyan", width=8)
        table.add_column("Name", style="green", width=30)
        table.add_column("Enabled", style="yellow", width=10)
        table.add_column("Auth Mode", style="blue", width=15)
        table.add_column("Encryption", style="magenta", width=15)
        table.add_column("Visible", style="dim", width=10)
        
        for ssid in ssids:
            # Get SSID number
            ssid_num = ssid.get('number', 'N/A')
            
            # Get SSID name
            ssid_name = ssid.get('name', 'N/A')
            
            # Get enabled status
            enabled = ssid.get('enabled', False)
            enabled_display = f"[green]Yes[/green]" if enabled else f"[red]No[/red]"
            
            # Get auth mode
            auth_mode = ssid.get('authMode', 'N/A')
            
            # Get encryption mode
            encryption_mode = ssid.get('encryptionMode', 'N/A')
            
            # Get visibility (broadcast SSID)
            visible = ssid.get('visible', True)
            visible_display = f"[green]Yes[/green]" if visible else f"[red]No[/red]"
            
            table.add_row(
                str(ssid_num),
                ssid_name,
                enabled_display,
                auth_mode,
                encryption_mode,
                visible_display
            )
        
        console = Console()
        console.print("\nNetwork SSIDs:")
        console.print(table)
    else:
        print(colored("No SSIDs found in the selected network.", "red"))
    
    choice = input(colored("\nPress Enter to return to the previous menu...", "green"))