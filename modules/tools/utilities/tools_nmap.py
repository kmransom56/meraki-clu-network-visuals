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
import socket
import os
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from settings import term_extra

console = Console()

def get_nmap_path():
    """Get the path to nmap executable"""
    # Check common Windows installation paths
    windows_paths = [
        r"C:\Program Files (x86)\Nmap\nmap.exe",
        r"C:\Program Files\Nmap\nmap.exe",
        r"C:\Nmap\nmap.exe"
    ]
    
    # First try system PATH
    try:
        result = subprocess.run(
            ["nmap", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return "nmap"  # Use from PATH
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Check Windows installation paths
    for path in windows_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_nmap_available():
    """Check if nmap is available on the system"""
    return get_nmap_path() is not None

def run_nmap_scan(target, scan_type="quick"):
    """Run nmap scan with specified type"""
    try:
        nmap_path = get_nmap_path()
        if not nmap_path:
            return None, "Nmap is not installed. Please install nmap:\nWindows: Download from https://nmap.org/download.html\nLinux: sudo apt-get install nmap (or equivalent)\nMac: brew install nmap"
        
        # Build nmap command based on scan type
        if scan_type == "quick":
            cmd = [nmap_path, "-F", target]  # Fast scan
        elif scan_type == "standard":
            cmd = [nmap_path, target]  # Standard scan
        elif scan_type == "stealth":
            cmd = [nmap_path, "-sS", target]  # SYN stealth scan
        elif scan_type == "version":
            cmd = [nmap_path, "-sV", target]  # Version detection
        elif scan_type == "full":
            cmd = [nmap_path, "-sS", "-sV", "-O", target]  # Full scan
        else:
            cmd = [nmap_path, target]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            return result.stdout, None
        else:
            return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return None, "Scan timed out after 2 minutes"
    except Exception as e:
        return None, f"Error running nmap: {str(e)}"

def simple_port_scan(target, ports="common"):
    """Simple port scan using socket (fallback if nmap not available)"""
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3389, 8080]
    
    if ports == "common":
        port_list = common_ports
    else:
        try:
            port_list = [int(p) for p in ports.split(',')]
        except ValueError:
            port_list = common_ports
    
    open_ports = []
    
    console.print(f"[dim]Scanning {len(port_list)} ports on {target}...[/dim]")
    
    for port in port_list:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception:
            pass
    
    return open_ports

def display_nmap_results(output, error):
    """Display nmap scan results"""
    if error:
        console.print(f"[red]{error}[/red]")
        return
    
    if not output:
        console.print("[yellow]No output from nmap scan.[/yellow]")
        return
    
    # Parse and display key information
    lines = output.split('\n')
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("Port", style="cyan", width=10)
    table.add_column("State", style="green", width=10)
    table.add_column("Service", style="yellow", width=20)
    table.add_column("Version", style="dim")
    
    in_port_section = False
    for line in lines:
        line = line.strip()
        if 'PORT' in line and 'STATE' in line:
            in_port_section = True
            continue
        if in_port_section and line and not line.startswith('-') and not line.startswith('Nmap'):
            parts = line.split()
            if len(parts) >= 3:
                port_info = parts[0]
                state = parts[1]
                service = parts[2] if len(parts) > 2 else 'unknown'
                version = ' '.join(parts[3:]) if len(parts) > 3 else ''
                table.add_row(port_info, state, service, version)
    
    if table.rows:
        console.print(table)
    else:
        # Show raw output if parsing failed
        console.print("\n[bold]Scan Results:[/bold]")
        console.print(output)

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    console.print("\n[bold cyan]Nmap Network Scanner[/bold cyan]\n")
    
    if not check_nmap_available():
        console.print("[yellow]Nmap is not installed on this system.[/yellow]")
        console.print("[dim]Falling back to simple port scan...[/dim]\n")
        use_simple = True
    else:
        console.print("[green]Nmap is available.[/green]\n")
        use_simple = False
    
    target = input("Enter target (IP address or hostname): ").strip()
    
    if not target:
        console.print("[red]No target entered.[/red]")
        input("\nPress Enter to continue...")
        return
    
    if use_simple:
        # Use simple socket-based port scan
        console.print(f"\n[dim]Scanning common ports on {target}...[/dim]\n")
        open_ports = simple_port_scan(target)
        
        if open_ports:
            table = Table(show_header=True, header_style="bold green", box=SIMPLE)
            table.add_column("Port", style="cyan")
            table.add_column("Status", style="green")
            
            for port in open_ports:
                table.add_row(str(port), "OPEN")
            
            console.print(table)
            console.print(f"\n[green]Found {len(open_ports)} open port(s)[/green]")
        else:
            console.print("[yellow]No open ports found on common ports.[/yellow]")
    else:
        # Use nmap
        console.print("\n[cyan]Scan Types:[/cyan]")
        console.print("1. Quick scan (fast, top 100 ports)")
        console.print("2. Standard scan (default)")
        console.print("3. Stealth scan (SYN)")
        console.print("4. Version detection")
        console.print("5. Full scan (slow but comprehensive)")
        
        choice = input("\nSelect scan type [1-5] (default: 1): ").strip() or "1"
        
        scan_types = {
            "1": "quick",
            "2": "standard",
            "3": "stealth",
            "4": "version",
            "5": "full"
        }
        
        scan_type = scan_types.get(choice, "quick")
        
        console.print(f"\n[dim]Running {scan_type} scan on {target}...[/dim]")
        console.print("[yellow]This may take a while...[/yellow]\n")
        
        output, error = run_nmap_scan(target, scan_type)
        display_nmap_results(output, error)
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
