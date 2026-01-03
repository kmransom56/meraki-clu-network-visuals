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
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from settings import term_extra

console = Console()

def run_whois(query):
    """Run whois command and return results"""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Try using whois.exe if available, or use online service
            try:
                result = subprocess.run(
                    ["whois", query],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return result.stdout
                else:
                    # Fallback: use python-whois if available
                    try:
                        import whois
                        w = whois.whois(query)
                        return str(w)
                    except ImportError:
                        return f"Error: whois command not found. Install 'python-whois' package or use online whois service."
            except FileNotFoundError:
                # Try python-whois
                try:
                    import whois
                    w = whois.whois(query)
                    return str(w)
                except ImportError:
                    return "Error: whois not available. Please install 'python-whois' package:\npip install python-whois"
        else:
            # Linux/Mac - use system whois
            result = subprocess.run(
                ["whois", query],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return result.stderr or "Error: whois command failed"
    except subprocess.TimeoutExpired:
        return "Error: whois query timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def display_whois_results(query, results):
    """Display whois results in a formatted table"""
    if results.startswith("Error:"):
        console.print(f"[red]{results}[/red]")
        return
    
    # Parse and display key information
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("Field", style="cyan", width=25)
    table.add_column("Value", style="green")
    
    lines = results.split('\n')
    current_section = None
    
    for line in lines[:100]:  # Limit to first 100 lines
        line = line.strip()
        if not line or line.startswith('%') or line.startswith('#'):
            continue
        
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if value:
                    table.add_row(key, value)
        else:
            # Add as continuation or section header
            if line and not line.startswith(' '):
                table.add_row("", line)
    
    console.print(table)
    
    # Show full output option
    if len(lines) > 100:
        console.print(f"\n[dim]Showing first 100 lines. Full output has {len(lines)} lines.[/dim]")
        show_full = input("\nShow full output? [y/N]: ").lower()
        if show_full == 'y':
            console.print("\n[bold]Full Whois Output:[/bold]")
            console.print(results)

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    console.print("\n[bold cyan]Whois Lookup Tool[/bold cyan]\n")
    console.print("[dim]Enter an IP address or domain name to look up whois information.[/dim]\n")
    
    query = input("Enter IP address or domain name: ").strip()
    
    if not query:
        console.print("[red]No query entered.[/red]")
        input("\nPress Enter to continue...")
        return
    
    console.print(f"\n[dim]Looking up whois information for {query}...[/dim]\n")
    
    results = run_whois(query)
    display_whois_results(query, results)
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
