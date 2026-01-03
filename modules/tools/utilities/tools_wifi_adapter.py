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

def get_wifi_adapters_windows():
    """Get WiFi adapter information on Windows"""
    try:
        # Get adapter information using netsh
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return []
        
        adapters = []
        current_adapter = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == "Name":
                    if current_adapter:
                        adapters.append(current_adapter)
                    current_adapter = {"Name": value}
                elif current_adapter:
                    current_adapter[key] = value
        
        if current_adapter:
            adapters.append(current_adapter)
        
        return adapters
    except Exception as e:
        console.print(f"[red]Error getting WiFi adapters: {str(e)}[/red]")
        return []

def get_wifi_adapters_linux():
    """Get WiFi adapter information on Linux"""
    try:
        # Try using iwconfig
        result = subprocess.run(
            ["iwconfig"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            adapters = []
            current_adapter = {}
            
            for line in result.stdout.split('\n'):
                if line and not line.startswith(' '):
                    if current_adapter:
                        adapters.append(current_adapter)
                    # Extract adapter name
                    match = re.match(r'^(\S+)', line)
                    if match:
                        current_adapter = {"Name": match.group(1)}
                elif current_adapter:
                    # Parse additional info
                    if "ESSID:" in line:
                        essid = re.search(r'ESSID:"([^"]+)"', line)
                        if essid:
                            current_adapter["SSID"] = essid.group(1)
                    if "Access Point:" in line:
                        ap = re.search(r'Access Point: ([0-9A-Fa-f:]{17})', line)
                        if ap:
                            current_adapter["BSSID"] = ap.group(1)
            
            if current_adapter:
                adapters.append(current_adapter)
            
            return adapters
    except FileNotFoundError:
        pass
    
    return []

def display_adapters(adapters):
    """Display WiFi adapter information in a table"""
    if not adapters:
        console.print("[yellow]No WiFi adapters found.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="green")
    
    for i, adapter in enumerate(adapters, 1):
        if i > 1:
            table.add_row("", "")
        table.add_row(f"[bold]Adapter {i}[/bold]", adapter.get("Name", "Unknown"))
        
        for key, value in adapter.items():
            if key != "Name":
                table.add_row(f"  {key}", str(value))
    
    console.print(table)

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    console.print("\n[bold cyan]WiFi Adapter Information[/bold cyan]\n")
    
    system = platform.system()
    
    if system == "Windows":
        adapters = get_wifi_adapters_windows()
    elif system == "Linux":
        adapters = get_wifi_adapters_linux()
    else:
        console.print(f"[yellow]WiFi adapter detection is not supported on {system}.[/yellow]")
        console.print("[dim]This feature is currently available for Windows and Linux.[/dim]")
        input("\nPress Enter to continue...")
        return
    
    if adapters:
        display_adapters(adapters)
    else:
        console.print("[yellow]No WiFi adapters found or unable to retrieve adapter information.[/yellow]")
        console.print("[dim]Make sure you have WiFi adapters installed and drivers are loaded.[/dim]")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
