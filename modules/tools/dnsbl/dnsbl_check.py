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
import dns.resolver
import json

from pathlib import Path
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.box import SIMPLE
from settings import term_extra

def reverse_ip(ip_address):
    """Reverse the IP address for DNSBL queries."""
    return '.'.join(ip_address.split('.')[::-1])

def check_dnsbl(ip_address, services, progress):
    """Check if an IP address is listed in the specified DNSBL services."""
    reversed_ip = reverse_ip(ip_address)
    results = {}
    
    # Configure DNS resolver with timeout
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3  # 3 second timeout
    resolver.lifetime = 3  # 3 second lifetime

    for service_name, service_domain in progress.track(services.items(), description="☕ Time to take a coffee."):
        query = f"{reversed_ip}.{service_domain}"
        try:
            resolver.resolve(query, 'A')
            results[service_name] = colored("Listed: YES", "red")
        except dns.resolver.NoAnswer:
            results[service_name] = colored("Listed: NO [NO ANSWER]", "green")
        except dns.resolver.NXDOMAIN:
            results[service_name] = colored("Listed: NO", "green")
        except dns.resolver.Timeout:
            results[service_name] = colored("Error: Timeout", "yellow")
        except dns.resolver.NoNameservers:
            results[service_name] = colored("Error: DNS server failure", "yellow")
        except dns.exception.DNSException as e:
            # Extract just the error type for cleaner messages
            error_type = type(e).__name__
            if "timeout" in str(e).lower() or "lifetime" in str(e).lower():
                results[service_name] = colored("Error: Timeout", "yellow")
            elif "servfail" in str(e).lower():
                results[service_name] = colored("Error: Server failure", "yellow")
            else:
                results[service_name] = colored(f"Error: {error_type}", "yellow")
        except Exception as e:
            # Generic error - show shortened message
            error_msg = str(e)
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."
            results[service_name] = colored(f"Error: {error_msg}", "yellow")
    return results

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    current_script_path = Path(__file__).parent
    dnsbl_json_path = current_script_path / 'dnsbl_services.json'

    with open(dnsbl_json_path, "r") as file:
        services_to_check = json.load(file)

    ip_to_check = input("Please enter an IP address to check: ")

    console = Console()
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("Service", style="dim", width=50)
    table.add_column("Result")

    with Progress() as progress:
        results = check_dnsbl(ip_to_check, services_to_check, progress)

    # Count results
    listed_count = sum(1 for r in results.values() if "Listed: YES" in str(r))
    not_listed_count = sum(1 for r in results.values() if "Listed: NO" in str(r))
    error_count = sum(1 for r in results.values() if "Error:" in str(r))
    
    for service, result in results.items():
        table.add_row(service, result)

    console.print(table)
    
    # Print summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [red]Listed: {listed_count}[/red]")
    console.print(f"  [green]Not Listed: {not_listed_count}[/green]")
    console.print(f"  [yellow]Errors: {error_count}[/yellow]")
    console.print(f"  [dim]Total Services: {len(results)}[/dim]")
    
    if listed_count > 0:
        console.print(f"\n[bold red]⚠ WARNING: IP address is listed in {listed_count} blacklist(s)![/bold red]")
    elif error_count > 0:
        console.print(f"\n[yellow]Note: {error_count} service(s) returned errors (timeouts or DNS issues).[/yellow]")
        console.print("[dim]This is normal - some DNSBL services may be slow or unreachable.[/dim]")
    else:
        console.print(f"\n[green]✓ IP address is not listed in any checked blacklists.[/green]")
    
    input("\nPress Enter to return to the submenu...")


if __name__ == "__main__":
    main()