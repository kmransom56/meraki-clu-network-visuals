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

def analyze_wifi_spectrum_windows():
    """Analyze WiFi spectrum on Windows"""
    try:
        # Get detailed network information
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=Bssid"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        # Parse networks and extract channel information
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
        console.print(f"[red]Error analyzing WiFi spectrum: {str(e)}[/red]")
        return []

def analyze_wifi_spectrum_linux():
    """Analyze WiFi spectrum on Linux"""
    try:
        # Try using iw
        result = subprocess.run(
            ["iw", "dev"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Get interface name
            interface_match = re.search(r'Interface (\w+)', result.stdout)
            if interface_match:
                interface = interface_match.group(1)
                
                # Scan for networks
                scan_result = subprocess.run(
                    ["iw", "dev", interface, "scan"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if scan_result.returncode == 0:
                    networks = []
                    current_network = {}
                    
                    for line in scan_result.stdout.split('\n'):
                        line = line.strip()
                        if "BSS" in line:
                            if current_network:
                                networks.append(current_network)
                            current_network = {}
                        elif "SSID:" in line and current_network is not None:
                            ssid = line.split(':', 1)[1].strip()
                            current_network["SSID"] = ssid
                        elif "freq:" in line and current_network is not None:
                            freq_match = re.search(r'freq: (\d+)', line)
                            if freq_match:
                                freq = int(freq_match.group(1))
                                # Convert frequency to channel
                                if 2412 <= freq <= 2484:
                                    channel = (freq - 2412) // 5 + 1
                                    current_network["Channel"] = str(channel)
                                    current_network["Band"] = "2.4 GHz"
                                elif 5170 <= freq <= 5825:
                                    channel = (freq - 5000) // 5
                                    current_network["Channel"] = str(channel)
                                    current_network["Band"] = "5 GHz"
                        elif "signal:" in line and current_network is not None:
                            signal_match = re.search(r'signal: (-?\d+)', line)
                            if signal_match:
                                current_network["Signal"] = f"{signal_match.group(1)} dBm"
                    
                    if current_network:
                        networks.append(current_network)
                    
                    return networks
    except FileNotFoundError:
        pass
    
    return []

def display_spectrum_analysis(networks):
    """Display WiFi spectrum analysis"""
    if not networks:
        console.print("[yellow]No WiFi networks found for spectrum analysis.[/yellow]")
        return
    
    # Group by channel/band
    channels_24 = {}
    channels_5 = {}
    
    for network in networks:
        channel = network.get("Channel", network.get("Radio type", "Unknown"))
        band = network.get("Band", "Unknown")
        ssid = network.get("SSID", "Unknown")
        signal = network.get("Signal", network.get("Signal level", "N/A"))
        
        if "2.4" in band or "2.4" in str(channel):
            if channel not in channels_24:
                channels_24[channel] = []
            channels_24[channel].append({"SSID": ssid, "Signal": signal})
        elif "5" in band or (channel.isdigit() and int(channel) > 14):
            if channel not in channels_5:
                channels_5[channel] = []
            channels_5[channel].append({"SSID": ssid, "Signal": signal})
    
    # Display 2.4 GHz spectrum
    if channels_24:
        console.print("\n[bold cyan]2.4 GHz Band Spectrum Analysis[/bold cyan]")
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)
        table.add_column("Channel", style="cyan", width=10)
        table.add_column("Networks", style="green", width=10)
        table.add_column("SSIDs", style="yellow")
        
        for channel in sorted(channels_24.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            networks_list = channels_24[channel]
            ssids = ", ".join([n["SSID"] for n in networks_list[:5]])
            if len(networks_list) > 5:
                ssids += f" ... (+{len(networks_list) - 5} more)"
            table.add_row(str(channel), str(len(networks_list)), ssids)
        
        console.print(table)
    
    # Display 5 GHz spectrum
    if channels_5:
        console.print("\n[bold cyan]5 GHz Band Spectrum Analysis[/bold cyan]")
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)
        table.add_column("Channel", style="cyan", width=10)
        table.add_column("Networks", style="green", width=10)
        table.add_column("SSIDs", style="yellow")
        
        for channel in sorted(channels_5.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            networks_list = channels_5[channel]
            ssids = ", ".join([n["SSID"] for n in networks_list[:5]])
            if len(networks_list) > 5:
                ssids += f" ... (+{len(networks_list) - 5} more)"
            table.add_row(str(channel), str(len(networks_list)), ssids)
        
        console.print(table)
    
    if not channels_24 and not channels_5:
        console.print("[yellow]Could not determine channel information for networks.[/yellow]")

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    console.print("\n[bold cyan]WiFi Spectrum Analyzer[/bold cyan]\n")
    console.print("[dim]Analyzing WiFi spectrum and channel usage...[/dim]\n")
    
    system = platform.system()
    
    if system == "Windows":
        networks = analyze_wifi_spectrum_windows()
    elif system == "Linux":
        networks = analyze_wifi_spectrum_linux()
    else:
        console.print(f"[yellow]WiFi spectrum analysis is not supported on {system}.[/yellow]")
        console.print("[dim]This feature is currently available for Windows and Linux.[/dim]")
        input("\nPress Enter to continue...")
        return
    
    if networks:
        display_spectrum_analysis(networks)
    else:
        console.print("[yellow]No WiFi networks found or unable to analyze spectrum.[/yellow]")
        console.print("[dim]Make sure WiFi is enabled and you have proper permissions.[/dim]")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
