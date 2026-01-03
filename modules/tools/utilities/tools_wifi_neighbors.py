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
import subprocess
import platform
import re
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from settings import term_extra

console = Console()

def get_wifi_networks_windows():
    """Get available WiFi networks on Windows"""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=Bssid"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith("SSID"):
                if current_network:
                    networks.append(current_network)
                parts = line.split(':', 1)
                if len(parts) == 2:
                    current_network = {"SSID": parts[1].strip()}
            elif ':' in line and current_network:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                current_network[key] = value
        
        if current_network:
            networks.append(current_network)
        
        return networks
    except Exception as e:
        console.print(f"[red]Error getting WiFi networks: {str(e)}[/red]")
        return []

def get_wifi_networks_linux():
    """Get available WiFi networks on Linux"""
    try:
        # Try using nmcli
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,BSSID", "device", "wifi", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            networks = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 4:
                        networks.append({
                            "SSID": parts[0] or "Hidden",
                            "Signal": f"{parts[1]}%",
                            "Security": parts[2] or "Open",
                            "BSSID": parts[3] if len(parts) > 3 else "N/A"
                        })
            return networks
    except FileNotFoundError:
        pass
    
    # Fallback to iwlist if available
    try:
        result = subprocess.run(
            ["iwlist", "scan"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            networks = []
            current_network = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if "ESSID:" in line:
                    if current_network:
                        networks.append(current_network)
                    essid = re.search(r'ESSID:"([^"]+)"', line)
                    current_network = {"SSID": essid.group(1) if essid else "Unknown"}
                elif "Signal level=" in line and current_network:
                    signal = re.search(r'Signal level=(-?\d+)', line)
                    if signal:
                        current_network["Signal"] = f"{signal.group(1)} dBm"
                elif "Encryption key:" in line and current_network:
                    encrypted = "on" in line.lower()
                    current_network["Security"] = "WPA/WPA2" if encrypted else "Open"
            
            if current_network:
                networks.append(current_network)
            
            return networks
    except FileNotFoundError:
        pass
    
    return []

def display_networks(networks):
    """Display WiFi networks in a table"""
    if not networks:
        console.print("[yellow]No WiFi networks found.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("SSID", style="cyan", width=25)
    table.add_column("Signal", style="green", width=15)
    table.add_column("Security", style="yellow", width=15)
    table.add_column("BSSID", style="dim", width=20)
    table.add_column("Channel", style="dim", width=10)
    
    for network in networks:
        table.add_row(
            network.get("SSID", "Unknown"),
            network.get("Signal", network.get("Signal level", "N/A")),
            network.get("Security", network.get("Authentication", "N/A")),
            network.get("BSSID", network.get("Network type", "N/A")),
            network.get("Radio type", network.get("Channel", "N/A"))
        )
    
    console.print(table)
    console.print(f"\n[dim]Found {len(networks)} network(s)[/dim]")

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    console.print("\n[bold cyan]WiFi Neighbors (Available Networks)[/bold cyan]\n")
    console.print("[dim]Scanning for available WiFi networks...[/dim]\n")
    
    system = platform.system()
    
    if system == "Windows":
        networks = get_wifi_networks_windows()
    elif system == "Linux":
        networks = get_wifi_networks_linux()
    else:
        console.print(f"[yellow]WiFi scanning is not supported on {system}.[/yellow]")
        console.print("[dim]This feature is currently available for Windows and Linux.[/dim]")
        input("\nPress Enter to continue...")
        return
    
    if networks:
        display_networks(networks)
    else:
        console.print("[yellow]No WiFi networks found or unable to scan.[/yellow]")
        console.print("[dim]Make sure WiFi is enabled and you have proper permissions.[/dim]")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
