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
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.box import SIMPLE
from settings import term_extra

console = Console()

def calculate_mtu(overhead, protocol="IPv4"):
    """
    Calculate the correct MTU size based on overhead
    
    Args:
        overhead (int): Protocol overhead in bytes
        protocol (str): Network protocol (IPv4 or IPv6)
    
    Returns:
        dict: MTU calculation results
    """
    # Standard Ethernet MTU
    ethernet_mtu = 1500
    
    # Protocol overheads
    overheads = {
        "IPv4": {
            "Ethernet": 14,
            "IP": 20,
            "TCP": 20,
            "UDP": 8,
            "ICMP": 8,
            "GRE": 24,
            "IPsec": 50,
            "VXLAN": 50,
            "MPLS": 4
        },
        "IPv6": {
            "Ethernet": 14,
            "IP": 40,
            "TCP": 20,
            "UDP": 8,
            "ICMPv6": 8,
            "GRE": 24,
            "IPsec": 50,
            "VXLAN": 50
        }
    }
    
    # Calculate payload size
    payload = ethernet_mtu - overhead
    
    # Recommended MTU values
    recommendations = {
        "Standard Ethernet": 1500,
        "Jumbo Frames": 9000,
        "Internet Standard": 1500,
        "VPN (PPTP)": 1400,
        "VPN (L2TP)": 1400,
        "VPN (IPsec)": 1400,
        "DSL": 1492,
        "PPPoE": 1492
    }
    
    return {
        "ethernet_mtu": ethernet_mtu,
        "overhead": overhead,
        "payload": payload,
        "recommendations": recommendations
    }

def display_mtu_table(results):
    """Display MTU calculation results in a table"""
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("Item", style="cyan", width=25)
    table.add_column("Value", style="green", width=20)
    table.add_column("Description", style="dim")
    
    table.add_row("Ethernet MTU", str(results["ethernet_mtu"]), "Standard Ethernet frame size")
    table.add_row("Protocol Overhead", f"{results['overhead']} bytes", "Total protocol headers")
    table.add_row("Payload Size", f"{results['payload']} bytes", "Available data space")
    table.add_row("", "", "")
    
    table.add_row("Recommended MTU Values", "", "")
    for name, value in results["recommendations"].items():
        table.add_row(f"  {name}", str(value), "Common use case")
    
    console.print(table)

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    console.print("\n[bold cyan]MTU Correct Size Calculator[/bold cyan]")
    console.print("This tool helps calculate the correct MTU size based on protocol overhead.\n")
    
    # Protocol selection
    protocol = Prompt.ask(
        "[cyan]Select protocol[/cyan]",
        choices=["IPv4", "IPv6"],
        default="IPv4"
    )
    
    # Overhead calculation options
    console.print("\n[bold]Protocol Overhead Options:[/bold]")
    console.print("1. Standard IPv4 (20 bytes IP + 20 bytes TCP = 40 bytes)")
    console.print("2. Standard IPv6 (40 bytes IP + 20 bytes TCP = 60 bytes)")
    console.print("3. With GRE (add 24 bytes)")
    console.print("4. With IPsec (add 50 bytes)")
    console.print("5. With VXLAN (add 50 bytes)")
    console.print("6. Custom overhead")
    
    choice = Prompt.ask("\n[cyan]Select overhead option[/cyan]", choices=["1", "2", "3", "4", "5", "6"], default="1")
    
    overhead_values = {
        "1": 40 if protocol == "IPv4" else 60,
        "2": 60 if protocol == "IPv4" else 60,
        "3": 64 if protocol == "IPv4" else 84,
        "4": 90 if protocol == "IPv4" else 110,
        "5": 90 if protocol == "IPv4" else 110,
        "6": None
    }
    
    if choice == "6":
        overhead = Prompt.ask("[cyan]Enter custom overhead in bytes[/cyan]", default="40")
        try:
            overhead = int(overhead)
        except ValueError:
            console.print("[red]Invalid input. Using default 40 bytes.[/red]")
            overhead = 40
    else:
        overhead = overhead_values[choice]
    
    # Calculate MTU
    results = calculate_mtu(overhead, protocol)
    
    # Display results
    console.print("\n")
    display_mtu_table(results)
    
    # Additional information
    console.print(f"\n[bold]Calculation Details:[/bold]")
    console.print(f"Protocol: {protocol}")
    console.print(f"Total Overhead: {overhead} bytes")
    console.print(f"Maximum Payload: {results['payload']} bytes")
    console.print(f"\n[dim]Note: MTU = Ethernet Frame (1500) - Protocol Overhead ({overhead}) = {results['payload']} bytes[/dim]")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
