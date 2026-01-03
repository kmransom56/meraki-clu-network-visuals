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
import socket
import dns.resolver
import dns.reversename
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from settings import term_extra

console = Console()

def nslookup_forward(hostname, record_type='A'):
    """Perform forward DNS lookup"""
    results = []
    try:
        # Try using dnspython first
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        
        answers = resolver.resolve(hostname, record_type)
        for rdata in answers:
            results.append({
                'type': record_type,
                'value': str(rdata),
                'ttl': answers.rrset.ttl if hasattr(answers, 'rrset') else 'N/A'
            })
    except dns.resolver.NXDOMAIN:
        results.append({'type': record_type, 'value': 'NXDOMAIN - Domain does not exist', 'ttl': 'N/A'})
    except dns.resolver.NoAnswer:
        results.append({'type': record_type, 'value': 'No answer for this record type', 'ttl': 'N/A'})
    except Exception as e:
        # Fallback to socket
        try:
            if record_type == 'A':
                ip = socket.gethostbyname(hostname)
                results.append({'type': 'A', 'value': ip, 'ttl': 'N/A'})
            else:
                results.append({'type': record_type, 'value': f'Error: {str(e)}', 'ttl': 'N/A'})
        except socket.gaierror as se:
            results.append({'type': record_type, 'value': f'Error: {str(se)}', 'ttl': 'N/A'})
    
    return results

def nslookup_reverse(ip_address):
    """Perform reverse DNS lookup (PTR record)"""
    results = []
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        
        addr = dns.reversename.from_address(ip_address)
        answers = resolver.resolve(addr, 'PTR')
        for rdata in answers:
            results.append({
                'type': 'PTR',
                'value': str(rdata),
                'ttl': answers.rrset.ttl if hasattr(answers, 'rrset') else 'N/A'
            })
    except Exception as e:
        try:
            # Fallback to socket
            hostname = socket.gethostbyaddr(ip_address)
            results.append({'type': 'PTR', 'value': hostname[0], 'ttl': 'N/A'})
        except socket.herror:
            results.append({'type': 'PTR', 'value': f'No reverse DNS record found', 'ttl': 'N/A'})
        except Exception as se:
            results.append({'type': 'PTR', 'value': f'Error: {str(se)}', 'ttl': 'N/A'})
    
    return results

def get_all_records(hostname):
    """Get multiple DNS record types"""
    all_results = []
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    
    for record_type in record_types:
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 3
            resolver.lifetime = 3
            answers = resolver.resolve(hostname, record_type)
            for rdata in answers:
                all_results.append({
                    'type': record_type,
                    'value': str(rdata),
                    'ttl': answers.rrset.ttl if hasattr(answers, 'rrset') else 'N/A'
                })
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            continue
        except Exception:
            continue
    
    return all_results

def display_results(query, results, query_type="forward"):
    """Display nslookup results in a table"""
    if not results:
        console.print(f"[yellow]No DNS records found for {query}[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("Record Type", style="cyan", width=15)
    table.add_column("Value", style="green")
    table.add_column("TTL", style="dim", width=10)
    
    for result in results:
        table.add_row(
            result.get('type', 'N/A'),
            result.get('value', 'N/A'),
            str(result.get('ttl', 'N/A'))
        )
    
    console.print(table)

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    console.print("\n[bold cyan]NSLookup Tool[/bold cyan]\n")
    console.print("[dim]Enter a hostname or IP address to perform DNS lookup.[/dim]\n")
    
    query = input("Enter hostname or IP address: ").strip()
    
    if not query:
        console.print("[red]No query entered.[/red]")
        input("\nPress Enter to continue...")
        return
    
    # Determine if it's an IP or hostname
    import ipaddress
    try:
        ipaddress.ip_address(query)
        is_ip = True
    except ValueError:
        is_ip = False
    
    console.print(f"\n[dim]Performing DNS lookup for {query}...[/dim]\n")
    
    if is_ip:
        # Reverse lookup
        results = nslookup_reverse(query)
        console.print(f"[bold]Reverse DNS Lookup (PTR):[/bold]")
    else:
        # Forward lookup - get all record types
        results = get_all_records(query)
        if not results:
            # Try basic A record
            results = nslookup_forward(query, 'A')
        console.print(f"[bold]DNS Lookup for {query}:[/bold]")
    
    display_results(query, results)
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
