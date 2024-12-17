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
import os
import webbrowser
from flask import Flask, render_template, jsonify
from pathlib import Path
from datetime import datetime
from termcolor import colored


# ==================================================
# IMPORT custom modules
# ==================================================
from modules.meraki import meraki_api 
from modules.meraki import meraki_ms_mr
from modules.meraki import meraki_mx
from modules.tools.dnsbl import dnsbl_check
from modules.tools.utilities import tools_ipcheck
from modules.tools.utilities import tools_passgen
from modules.tools.utilities import tools_subnetcalc

from settings import term_extra


# ==================================================
# VISUALIZE submenus for Appliance, Switches and APs
# ==================================================
def select_organization(api_key):
    selected_org = meraki_api.select_organization(api_key)
    return selected_org

def submenu_sw_and_ap(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        options = ["Select an Organization", "Return to Main Menu"]
        
        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                select_network(api_key, selected_org['id'])
        elif choice == '2':
            break

def submenu_mx(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        options = ["Select an Organization", "Return to Main Menu"]

        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                meraki_mx.select_mx_network(api_key, selected_org['id'])
        elif choice == '2':
            break

def submenu_network_wide(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        options = ["Select an Organization", "Return to Main Menu"]

        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                network_wide_operations(api_key, selected_org['id'])
        elif choice == '2':
            break

def create_web_visualization(topology_data):
    """Create and launch web visualization"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'web', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'web', 'static'))
    
    @app.route('/')
    def index():
        return render_template('topology.html')
    
    @app.route('/topology-data')
    def get_topology():
        return jsonify(topology_data)
    
    # Create web directory if it doesn't exist
    web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
    templates_dir = os.path.join(web_dir, 'templates')
    static_dir = os.path.join(web_dir, 'static')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Create HTML template
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Topology Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="controls">
            <div class="search-box">
                <input type="text" id="search" placeholder="Search devices...">
            </div>
            <div class="filter-box">
                <label>Filter by type:</label>
                <select id="deviceFilter">
                    <option value="all">All Devices</option>
                    <option value="switch">Switches</option>
                    <option value="wireless">Wireless</option>
                    <option value="appliance">Appliances</option>
                </select>
            </div>
            <div class="layout-box">
                <label>Layout:</label>
                <select id="layoutType">
                    <option value="force">Force Directed</option>
                    <option value="radial">Radial</option>
                    <option value="hierarchical">Hierarchical</option>
                </select>
            </div>
        </div>
        <div class="stats-panel">
            <h3>Network Statistics</h3>
            <div id="deviceStats"></div>
            <div id="connectionStats"></div>
            <div id="performanceStats"></div>
        </div>
        <div id="topology"></div>
        <div id="tooltip" class="tooltip"></div>
        <script src="{{ url_for('static', filename='topology.js') }}"></script>
    </body>
    </html>
    """

    # Create CSS
    css_content = """
    body {
        margin: 0;
        font-family: Arial, sans-serif;
        background-color: #f0f0f0;
        display: flex;
        flex-direction: column;
    }
    .controls {
        background-color: #fff;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        gap: 20px;
        align-items: center;
    }
    .search-box input {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        width: 200px;
    }
    .filter-box, .layout-box {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    select {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    .stats-panel {
        position: fixed;
        right: 0;
        top: 60px;
        width: 250px;
        background-color: white;
        padding: 15px;
        box-shadow: -2px 0 4px rgba(0,0,0,0.1);
        height: calc(100vh - 60px);
        overflow-y: auto;
    }
    #topology {
        width: calc(100vw - 250px);
        height: calc(100vh - 60px);
        background-color: white;
    }
    .tooltip {
        position: absolute;
        padding: 10px;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        border-radius: 5px;
        pointer-events: none;
        display: none;
    }
    .node circle {
        stroke: #fff;
        stroke-width: 2px;
    }
    .node text {
        font-size: 12px;
    }
    .link {
        stroke: #999;
        stroke-opacity: 0.6;
        stroke-width: 2px;
    }
    .hidden {
        opacity: 0.2;
    }
    """

    # Create JavaScript
    js_content = """
    let currentLayout = 'force';
    let simulation;
    let svg;
    let link;
    let node;
    
    fetch('/topology-data')
        .then(response => response.json())
        .then(data => {
            const width = window.innerWidth - 250;
            const height = window.innerHeight - 60;
            
            svg = d3.select('#topology')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Initialize force simulation
            simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links).id(d => d.id))
                .force('charge', d3.forceManyBody().strength(-1000))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            // Create links
            link = svg.append('g')
                .selectAll('line')
                .data(data.links)
                .join('line')
                .attr('class', 'link');
            
            // Create nodes
            node = svg.append('g')
                .selectAll('g')
                .data(data.nodes)
                .join('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            node.append('circle')
                .attr('r', 20)
                .style('fill', getNodeColor);
            
            node.append('text')
                .attr('dx', 25)
                .attr('dy', '.35em')
                .text(d => d.name);
            
            // Tooltip functionality
            const tooltip = d3.select('#tooltip');
            
            node.on('mouseover', (event, d) => {
                tooltip.style('display', 'block')
                    .html(`
                        <div>
                            <strong>${d.name}</strong><br>
                            Model: ${d.model}<br>
                            Type: ${d.type}<br>
                            Status: ${d.status}
                        </div>
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY + 10) + 'px');
            })
            .on('mouseout', () => {
                tooltip.style('display', 'none');
            });
            
            // Update statistics
            updateStatistics(data);
            
            // Search functionality
            d3.select('#search').on('input', function() {
                const searchTerm = this.value.toLowerCase();
                node.classed('hidden', d => !d.name.toLowerCase().includes(searchTerm));
                link.classed('hidden', d => {
                    const sourceHidden = !d.source.name.toLowerCase().includes(searchTerm);
                    const targetHidden = !d.target.name.toLowerCase().includes(searchTerm);
                    return sourceHidden && targetHidden;
                });
            });
            
            // Device type filter
            d3.select('#deviceFilter').on('change', function() {
                const filterValue = this.value;
                node.classed('hidden', d => filterValue !== 'all' && d.type !== filterValue);
                link.classed('hidden', d => {
                    const sourceHidden = filterValue !== 'all' && d.source.type !== filterValue;
                    const targetHidden = filterValue !== 'all' && d.target.type !== filterValue;
                    return sourceHidden && targetHidden;
                });
            });
            
            // Layout selection
            d3.select('#layoutType').on('change', function() {
                currentLayout = this.value;
                updateLayout();
            });
            
            // Initial layout
            updateLayout();
        });
    
    function getNodeColor(d) {
        switch(d.type) {
            case 'switch': return '#4CAF50';
            case 'wireless': return '#2196F3';
            case 'appliance': return '#F44336';
            default: return '#9E9E9E';
        }
    }
    
    function updateStatistics(data) {
        // Device statistics
        const deviceTypes = d3.group(data.nodes, d => d.type);
        const deviceStats = Array.from(deviceTypes, ([type, nodes]) => ({
            type: type || 'unknown',
            count: nodes.length
        }));
        
        const deviceStatsHtml = `
            <h4>Device Count</h4>
            ${deviceStats.map(stat => `
                <div>${stat.type}: ${stat.count}</div>
            `).join('')}
        `;
        
        // Connection statistics
        const connectionTypes = d3.group(data.links, d => d.type);
        const connectionStats = Array.from(connectionTypes, ([type, links]) => ({
            type: type || 'unknown',
            count: links.length
        }));
        
        const connectionStatsHtml = `
            <h4>Connection Types</h4>
            ${connectionStats.map(stat => `
                <div>${stat.type}: ${stat.count}</div>
            `).join('')}
        `;
        
        // Performance metrics
        const performanceStatsHtml = `
            <h4>Network Performance</h4>
            <div>Active Connections: ${data.links.length}</div>
            <div>Total Devices: ${data.nodes.length}</div>
        `;
        
        d3.select('#deviceStats').html(deviceStatsHtml);
        d3.select('#connectionStats').html(connectionStatsHtml);
        d3.select('#performanceStats').html(performanceStatsHtml);
    }
    
    function updateLayout() {
        simulation.stop();
        
        switch(currentLayout) {
            case 'radial':
                simulation
                    .force('link', d3.forceLink().id(d => d.id).distance(100))
                    .force('charge', d3.forceManyBody().strength(-1000))
                    .force('r', d3.forceRadial(200))
                    .force('center', d3.forceCenter(width / 2, height / 2));
                break;
                
            case 'hierarchical':
                simulation
                    .force('link', d3.forceLink().id(d => d.id).distance(100))
                    .force('charge', d3.forceManyBody().strength(-500))
                    .force('x', d3.forceX())
                    .force('y', d3.forceY().strength(0.1).y(d => d.depth * 100));
                break;
                
            default: // force
                simulation
                    .force('link', d3.forceLink().id(d => d.id))
                    .force('charge', d3.forceManyBody().strength(-1000))
                    .force('center', d3.forceCenter(width / 2, height / 2));
        }
        
        simulation.alpha(1).restart();
    }
    
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    """

    with open(os.path.join(templates_dir, 'topology.html'), 'w') as f:
        f.write(html_content)
    
    with open(os.path.join(static_dir, 'style.css'), 'w') as f:
        f.write(css_content)
    
    with open(os.path.join(static_dir, 'topology.js'), 'w') as f:
        f.write(js_content)
    
    # Open browser and start Flask app
    webbrowser.open('http://localhost:5000')
    app.run(debug=False)

def network_wide_operations(api_key, organization_id):
    while True:
        term_extra.clear_screen()
        print("\nNetwork-Wide Operations Menu")
        print("=" * 50)
        options = [
            "View Network Health",
            "Monitor Network Clients",
            "View Network Traffic",
            "View Network Latency Stats",
            "Monitor Device Performance",
            "Check Device Uplinks",
            "Generate Network Diagram",
            "Launch Web Visualization",
            "Return to Previous Menu"
        ]
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")

        choice = input(colored("\nChoose an option [1-9]: ", "cyan"))
        
        if choice == '9':
            break
        elif choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
            network_id = meraki_api.select_network(api_key, organization_id)
            if network_id:
                if choice == '1':
                    health = meraki_api.get_network_health(api_key, network_id)
                    if health:
                        print(colored("\nNetwork Health Status:", "cyan"))
                        for component, status in health.items():
                            print(f"{component}: {status}")
                elif choice == '2':
                    clients = meraki_api.get_network_clients(api_key, network_id)
                    if clients:
                        print(colored("\nActive Network Clients:", "cyan"))
                        for client in clients:
                            print(f"Description: {client.get('description', 'N/A')}")
                            print(f"IP: {client.get('ip', 'N/A')}")
                            print(f"MAC: {client.get('mac', 'N/A')}")
                            print(f"Status: {client.get('status', 'N/A')}")
                            print("-" * 30)
                elif choice == '3':
                    traffic = meraki_api.get_network_traffic(api_key, network_id)
                    if traffic:
                        print(colored("\nNetwork Traffic Analysis:", "cyan"))
                        for flow in traffic:
                            print(f"Application: {flow.get('application', 'N/A')}")
                            print(f"Destination: {flow.get('destination', 'N/A')}")
                            print(f"Protocol: {flow.get('protocol', 'N/A')}")
                            print(f"Usage: {flow.get('usage', {}).get('total', 0)} bytes")
                            print("-" * 30)
                elif choice == '4':
                    stats = meraki_api.get_network_latency_stats(api_key, network_id)
                    if stats:
                        print(colored("\nNetwork Latency Statistics:", "cyan"))
                        for stat in stats:
                            print(f"Type: {stat.get('type', 'N/A')}")
                            print(f"Latency: {stat.get('latencyMs', 'N/A')} ms")
                            print(f"Loss: {stat.get('lossPercentage', 'N/A')}%")
                            print("-" * 30)
                elif choice == '5':
                    devices = meraki_api.get_meraki_devices(api_key, network_id)
                    if devices:
                        print(colored("\nSelect a device:", "cyan"))
                        for i, device in enumerate(devices, 1):
                            print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                        device_choice = input(colored("\nChoose a device number: ", "cyan"))
                        if device_choice.isdigit() and 1 <= int(device_choice) <= len(devices):
                            device = devices[int(device_choice) - 1]
                            performance = meraki_api.get_device_performance(api_key, device['serial'])
                            if performance:
                                print(colored(f"\nPerformance stats for {device.get('name')}:", "cyan"))
                                print(f"CPU: {performance.get('cpu', 'N/A')}%")
                                print(f"Memory: {performance.get('memory', 'N/A')}%")
                                print(f"Disk: {performance.get('disk', 'N/A')}%")
                elif choice == '6':
                    devices = meraki_api.get_meraki_devices(api_key, network_id)
                    if devices:
                        print(colored("\nSelect a device:", "cyan"))
                        for i, device in enumerate(devices, 1):
                            print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                        device_choice = input(colored("\nChoose a device number: ", "cyan"))
                        if device_choice.isdigit() and 1 <= int(device_choice) <= len(devices):
                            device = devices[int(device_choice) - 1]
                            uplink = meraki_api.get_device_uplink(api_key, device['serial'])
                            if uplink:
                                print(colored(f"\nUplink info for {device.get('name')}:", "cyan"))
                                for interface in uplink:
                                    print(f"Interface: {interface.get('interface', 'N/A')}")
                                    print(f"Status: {interface.get('status', 'N/A')}")
                                    print(f"IP: {interface.get('ip', 'N/A')}")
                                    print("-" * 30)
                elif choice == '7':
                    topology = meraki_api.get_network_topology(api_key, network_id)
                    if topology:
                        print(colored("\nNetwork Topology:", "cyan"))
                        print("\nDevices:")
                        for node in topology['nodes']:
                            print(f"- {node['name']} ({node['model']})")
                            print(f"  Type: {node['type']}")
                            print(f"  Status: {node['status']}")
                            print("-" * 30)
                        
                        print("\nConnections:")
                        for link in topology['links']:
                            print(f"- {link['source']} -> {link['target']}")
                            print(f"  Interface: {link['interface']}")
                            print(f"  Type: {link['type']}")
                            print("-" * 30)
                elif choice == '8':
                    topology = meraki_api.get_network_topology(api_key, network_id)
                    if topology:
                        print(colored("\nLaunching web visualization...", "cyan"))
                        create_web_visualization(topology)
                input(colored("\nPress Enter to continue...", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


# ==================================================
# DEFINE how to process data inside Networks
# ==================================================
def select_network(api_key, organization_id):
    selected_network = meraki_api.select_network(api_key, organization_id)
    if selected_network:
        network_name = selected_network['name']
        network_id = selected_network['id']

        downloads_path = str(Path.home() / "Downloads")
        current_date = datetime.now().strftime("%Y-%m-%d")
        meraki_dir = os.path.join(downloads_path, f"Cisco-Meraki-CLU-Export-{current_date}")
        os.makedirs(meraki_dir, exist_ok=True)

        while True:
            term_extra.clear_screen()
            term_extra.print_ascii_art()

            options = [
                "Get Switches",
                "Get Access Points",
                "Get Switch Ports",
                "Get Devices Statuses",
                "Download Switches CSV",
                "Download Access Points CSV",
                "Download Devices Statuses CSV (under dev)",
                "Return to Main Menu"
            ]
            
            # Description header over the menu
            print("\n")
            print("┌" + "─" * 58 + "┐")
            print("│".ljust(59) + "│")
            for index, option in enumerate(options, start=1):
                print(f"│ {index}. {option}".ljust(59) + "│")
            print("│".ljust(59) + "│")
            print("└" + "─" * 58 + "┘")

            choice = input(colored("\nChoose a menu option [1-8]: ", "cyan"))

            if choice == '1':
                meraki_ms_mr.display_devices(api_key, network_id, 'switches')
            elif choice == '2':
                meraki_ms_mr.display_devices(api_key, network_id, 'access_points')
            elif choice == '3':
                serial_number = input("\nEnter the switch serial number: ")
                if serial_number:
                    print(f"Fetching switch ports for serial: {serial_number}")
                    meraki_ms_mr.display_switch_ports(api_key, serial_number)
                else:
                    print("[red]Invalid input. Please enter a valid serial number.[/red]")
            elif choice == '4':
                meraki_ms_mr.display_organization_devices_statuses(api_key, organization_id, network_id)
            elif choice == '5':
                switches = meraki_api.get_meraki_switches(api_key, network_id)
                if switches:
                    meraki_api.export_devices_to_csv(switches, network_name, 'switches', meraki_dir)
                else:
                    print("No switches to download.")
                choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))
                
            elif choice == '6':
                access_points = meraki_api.get_meraki_access_points(api_key, network_id)
                if access_points:
                    meraki_api.export_devices_to_csv(access_points, network_name, 'access_points', meraki_dir)
                else:
                    print("No access points to download.")
                choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))

            elif choice == '8':
                break
    else:
        print("[red]No network selected or invalid organization ID.[/red]")


# ==================================================
# DEFINE the Swiss Army Knife submenu
# ==================================================
def swiss_army_knife_submenu(fernet):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()

        options = [
            "DNSBL Check",
            "IP Check",
            "MTU Correct Size Calculator [under dev]",
            "Password Generator",
            "Subnet Calculator",
            "WiFi Spectrum Analyzer [under dev]",
            "WiFi Adapter Info [under dev]",
            "WiFi Neighbors [under dev]",
            "Return to Main Menu"
        ]

        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("Choose a menu option [1-9]: ", "cyan"))

        if choice == '1':
            dnsbl_check.main()
        elif choice == '2':
            tools_ipcheck.main(fernet)
        elif choice == '3':
            pass
        elif choice == '4':
            tools_passgen.main()
        elif choice == '5':
            tools_subnetcalc.main()
        elif choice == '6':
            pass
        elif choice == '7':
            pass
        elif choice == '8':
            pass
        elif choice == '9':
            break
        else:
            print(colored("Invalid input. Please enter a number between 1 and 9.", "red"))


def submenu_environmental(api_key):
    while True:
        term_extra.clear_screen()
        print("\nEnvironmental Monitoring Menu")
        print("=" * 50)
        options = [
            "View Current Sensor Alerts",
            "View Sensor Readings",
            "View Sensor Relationships",
            "Return to Main Menu"
        ]
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")

        choice = input(colored("\nChoose an option [1-4]: ", "cyan"))
        
        if choice == '4':
            break
        elif choice in ['1', '2', '3']:
            organization_id = meraki_api.select_organization(api_key)
            if organization_id:
                network_id = meraki_api.select_network(api_key, organization_id)
                if network_id:
                    if choice == '1':
                        alerts = meraki_api.get_network_sensor_alerts(api_key, network_id)
                        if alerts:
                            print(colored("\nCurrent Sensor Alerts:", "cyan"))
                            for metric, count in alerts.items():
                                print(f"{metric}: {count} alerts")
                    elif choice == '2':
                        devices = meraki_api.get_meraki_devices(api_key, network_id)
                        if devices:
                            print(colored("\nSelect a sensor device:", "cyan"))
                            sensor_devices = [d for d in devices if d.get('model', '').startswith('MT')]
                            for i, device in enumerate(sensor_devices, 1):
                                print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                            device_choice = input(colored("\nChoose a device number: ", "cyan"))
                            if device_choice.isdigit() and 1 <= int(device_choice) <= len(sensor_devices):
                                device = sensor_devices[int(device_choice) - 1]
                                readings = meraki_api.get_device_sensor_data(api_key, device['serial'])
                                if readings:
                                    print(colored(f"\nLatest readings for {device.get('name')}:", "cyan"))
                                    for metric, value in readings.items():
                                        print(f"{metric}: {value}")
                    elif choice == '3':
                        devices = meraki_api.get_meraki_devices(api_key, network_id)
                        if devices:
                            print(colored("\nSelect a sensor device:", "cyan"))
                            sensor_devices = [d for d in devices if d.get('model', '').startswith('MT')]
                            for i, device in enumerate(sensor_devices, 1):
                                print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                            device_choice = input(colored("\nChoose a device number: ", "cyan"))
                            if device_choice.isdigit() and 1 <= int(device_choice) <= len(sensor_devices):
                                device = sensor_devices[int(device_choice) - 1]
                                relationships = meraki_api.get_device_sensor_relationships(api_key, device['serial'])
                                if relationships:
                                    print(colored(f"\nSensor relationships for {device.get('name')}:", "cyan"))
                                    for rel in relationships:
                                        print(f"Role: {rel.get('role')}")
                                        print(f"Target: {rel.get('target')}")
                    input(colored("\nPress Enter to continue...", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


def submenu_organization(api_key):
    while True:
        term_extra.clear_screen()
        print("\nOrganization Management Menu")
        print("=" * 50)
        options = [
            "View Organization Summary",
            "View Organization Inventory",
            "View Organization Licenses",
            "View Organization Device Status",
            "View Policy Objects",
            "View Policy Object Groups",
            "Return to Main Menu"
        ]
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")

        choice = input(colored("\nChoose an option [1-7]: ", "cyan"))
        
        if choice == '7':
            break
        elif choice in ['1', '2', '3', '4', '5', '6']:
            organization_id = meraki_api.select_organization(api_key)
            if organization_id:
                if choice == '1':
                    summary = meraki_api.get_organization_summary(api_key, organization_id)
                    if summary:
                        print(colored("\nOrganization Summary:", "cyan"))
                        print(f"Total Networks: {summary.get('networks', 0)}")
                        print(f"Total Devices: {summary.get('devices', 0)}")
                        print(f"Total Licenses: {summary.get('licenses', 0)}")
                elif choice == '2':
                    inventory = meraki_api.get_organization_inventory(api_key, organization_id)
                    if inventory:
                        print(colored("\nOrganization Inventory:", "cyan"))
                        for device in inventory:
                            print(f"Name: {device.get('name', 'N/A')}")
                            print(f"Model: {device.get('model', 'N/A')}")
                            print(f"Serial: {device.get('serial', 'N/A')}")
                            print("-" * 30)
                elif choice == '3':
                    licenses = meraki_api.get_organization_licenses(api_key, organization_id)
                    if licenses:
                        print(colored("\nOrganization Licenses:", "cyan"))
                        for license in licenses:
                            print(f"Status: {license.get('status', 'N/A')}")
                            print(f"Type: {license.get('licenseType', 'N/A')}")
                            print(f"Expires: {license.get('expirationDate', 'N/A')}")
                            print("-" * 30)
                elif choice == '4':
                    statuses = meraki_api.get_organization_devices_statuses(api_key, organization_id)
                    if statuses:
                        print(colored("\nDevice Statuses:", "cyan"))
                        for status in statuses:
                            print(f"Name: {status.get('name', 'N/A')}")
                            print(f"Status: {status.get('status', 'N/A')}")
                            print(f"Last Reported: {status.get('lastReportedAt', 'N/A')}")
                            print("-" * 30)
                elif choice == '5':
                    objects = meraki_api.get_organization_policy_objects(api_key, organization_id)
                    if objects:
                        print(colored("\nPolicy Objects:", "cyan"))
                        for obj in objects:
                            print(f"Name: {obj.get('name', 'N/A')}")
                            print(f"Category: {obj.get('category', 'N/A')}")
                            print(f"Type: {obj.get('type', 'N/A')}")
                            print("-" * 30)
                elif choice == '6':
                    groups = meraki_api.get_organization_policy_objects_groups(api_key, organization_id)
                    if groups:
                        print(colored("\nPolicy Object Groups:", "cyan"))
                        for group in groups:
                            print(f"Name: {group.get('name', 'N/A')}")
                            print(f"Object IDs: {', '.join(group.get('objectIds', []))}")
                            print("-" * 30)
                input(colored("\nPress Enter to continue...", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))