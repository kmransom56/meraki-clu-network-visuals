"""
Network Topology Visualization Module

This module provides functions to visualize Meraki network topology
with different device types and connection types.
"""

import os
import json
import logging
import webbrowser
from pathlib import Path
import uuid

# Device type to icon mapping
DEVICE_ICONS = {
    'switch': 'router',
    'wireless': 'wifi',
    'appliance': 'router',
    'camera': 'videocam',
    'phone': 'phone_iphone',
    'desktop': 'desktop_windows',
    'mobile': 'smartphone',
    'printer': 'print',
    'server': 'dns',
    'voip': 'call',
    'tablet': 'tablet_mac',
    'gateway': 'router',
    'client': 'devices_other',
    'unknown': 'device_unknown'
}

# Connection type to style mapping
CONNECTION_STYLES = {
    'uplink': {'color': '#00C853', 'width': 3, 'dashes': False, 'label': 'Uplink', 'highlight': '#00C853', 'arrow': True},
    'switch': {'color': '#2196F3', 'width': 2, 'dashes': False, 'label': 'Switch Connection', 'highlight': '#2196F3', 'arrow': True},
    'wireless': {'color': '#FF9800', 'width': 2, 'dashes': True, 'label': 'Wireless Connection', 'highlight': '#FF9800', 'arrow': False},
    'wired': {'color': '#607D8B', 'width': 1, 'dashes': False, 'label': 'Wired Client', 'highlight': '#607D8B', 'arrow': True},
    'unknown': {'color': '#9E9E9E', 'width': 1, 'dashes': True, 'label': 'Unknown Connection', 'highlight': '#9E9E9E', 'arrow': False}
}

def generate_topology_html(topology_data, network_name=None, output_path=None):
    """
    Generate an HTML file to visualize network topology
    
    Args:
        topology_data (dict): Network topology data with nodes and links
        network_name (str, optional): Name of the network. If None, will use from topology_data.
        output_path (str, optional): Path to save the HTML file. Defaults to None.
        
    Returns:
        str: Path to the generated HTML file
    """
    # Use network name from topology data if not provided
    if network_name is None and 'network_name' in topology_data:
        network_name = topology_data['network_name']
    elif network_name is None:
        network_name = "Unknown Network"
        
    if not output_path:
        # Create a directory for topology visualizations if it doesn't exist
        output_dir = Path(os.path.expanduser("~")) / "meraki_visualizations"
        os.makedirs(output_dir, exist_ok=True)
        output_path = output_dir / f"{network_name.replace(' ', '_')}_topology.html"
    
    # Convert topology data to vis.js format
    vis_data = create_vis_network_data(topology_data)
    vis_nodes = vis_data['nodes']
    vis_edges = vis_data['edges']
    connection_types = vis_data['connection_types']
    
    # Generate HTML with vis.js
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Network Topology: {network_name}</title>
    <meta charset="utf-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css">
    <style type="text/css">
        body, html {{
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1e1e1e;
            color: #e0e0e0;
        }}
        #topology-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        #topology-header {{
            background-color: #2d2d2d;
            color: #ffffff;
            padding: 10px 20px;
            border-bottom: 1px solid #3d3d3d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        #topology-title {{
            font-size: 20px;
            font-weight: bold;
        }}
        #topology-stats {{
            font-size: 14px;
        }}
        #topology-content {{
            display: flex;
            flex: 1;
            overflow: hidden;
        }}
        #topology-sidebar {{
            width: 250px;
            background-color: #252525;
            padding: 15px;
            overflow-y: auto;
            border-right: 1px solid #3d3d3d;
        }}
        #topology-network {{
            flex: 1;
            position: relative;
        }}
        .legend {{
            margin-bottom: 20px;
        }}
        .legend h3 {{
            font-size: 16px;
            margin-bottom: 10px;
            color: #ffffff;
            border-bottom: 1px solid #3d3d3d;
            padding-bottom: 5px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .legend-dash {{
            width: 20px;
            height: 0;
            border-top: 2px dashed;
            margin-right: 8px;
        }}
        .device-count {{
            margin-top: 20px;
        }}
        .device-count h3 {{
            font-size: 16px;
            margin-bottom: 10px;
            color: #ffffff;
            border-bottom: 1px solid #3d3d3d;
            padding-bottom: 5px;
        }}
        .device-type {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 14px;
        }}
        .controls {{
            margin-top: 20px;
        }}
        .controls h3 {{
            font-size: 16px;
            margin-bottom: 10px;
            color: #ffffff;
            border-bottom: 1px solid #3d3d3d;
            padding-bottom: 5px;
        }}
        .control-button {{
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            text-align: left;
        }}
        .control-button:hover {{
            background-color: #106ebe;
        }}
        .vis-network {{
            background-color: #121212;
        }}
        .vis-tooltip {{
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
            border: 1px solid #3d3d3d !important;
            border-radius: 4px !important;
            padding: 10px !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5) !important;
            max-width: 300px !important;
        }}
    </style>
</head>
<body>
    <div id="topology-container">
        <div id="topology-header">
            <div id="topology-title">Network Topology: {network_name}</div>
            <div id="topology-stats">
                Devices: {len([n for n in vis_nodes if 'group' in n and n['group'] != 'client'])} | 
                Clients: {len([n for n in vis_nodes if 'group' in n and n['group'] == 'client'])} | 
                Connections: {len(vis_edges)}
            </div>
        </div>
        <div id="topology-content">
            <div id="topology-sidebar">
                <div class="legend">
                    <h3>Connection Types</h3>
"""

    # Dynamically generate legend based on connection types present in the data
    for conn_type in connection_types:
        style = CONNECTION_STYLES.get(conn_type, CONNECTION_STYLES['unknown'])
        if style['dashes']:
            html_content += f"""
                    <div class="legend-item">
                        <div class="legend-dash" style="border-color: {style['color']};"></div>
                        <span>{style['label']}</span>
                    </div>"""
        else:
            html_content += f"""
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: {style['color']};"></div>
                        <span>{style['label']}</span>
                    </div>"""

    # Add device type legend
    device_types = set(node.get('group', 'Unknown') for node in vis_nodes)
    client_types = set(node.get('group', 'Unknown') for node in vis_nodes 
                      if node.get('group') == 'client')
    
    if device_types:
        html_content += """
                </div>
                <div class="legend">
                    <h3>Device Types</h3>"""
        for device_type in device_types:
            if device_type != 'client':
                html_content += f"""
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #4CAF50;"></div>
                        <span>{device_type}</span>
                    </div>"""
    
    # Add client type legend if we have client devices
    if 'client' in device_types:
        html_content += """
                </div>
                <div class="legend">
                    <h3>Client Types</h3>"""
        html_content += f"""
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #2196F3;"></div>
                        <span>client</span>
                    </div>"""

    # Add device count summary
    device_count = {}
    for node in vis_nodes:
        group = node.get('group', 'Unknown')
        if group in device_count:
            device_count[group] += 1
        else:
            device_count[group] = 1
    
    html_content += """
                </div>
                <div class="device-count">
                    <h3>Device Count</h3>"""
    
    for device_type, count in device_count.items():
        html_content += f"""
                    <div class="device-type">
                        <span>{device_type}</span>
                        <span>{count}</span>
                    </div>"""
    
    # Add controls
    html_content += """
                </div>
                <div class="controls">
                    <h3>Controls</h3>
                    <button class="control-button" onclick="fitNetwork()">Fit All Nodes</button>
                    <button class="control-button" onclick="togglePhysics()">Toggle Physics</button>
                    <button class="control-button" onclick="toggleEdgeLabels()">Toggle Edge Labels</button>
                    <button class="control-button" onclick="toggleNodeLabels()">Toggle Node Labels</button>
                </div>
            </div>
            <div id="topology-network"></div>
        </div>
    </div>

    <script type="text/javascript">
        // Create a network
        var container = document.getElementById('topology-network');
        
        // Parse the JSON data
        var nodes = new vis.DataSet("""
    
    # Convert nodes and edges to JSON
    html_content += json.dumps(vis_nodes)
    
    html_content += """);
        var edges = new vis.DataSet("""
    
    html_content += json.dumps(vis_edges)
    
    html_content += """);
        
        // Provide the data in the vis format
        var data = {
            nodes: nodes,
            edges: edges
        };
        
        // Options for the network visualization
        var options = {
            nodes: {
                shape: 'circularImage',
                font: {
                    color: '#ffffff',
                    strokeWidth: 3,
                    strokeColor: '#121212'
                },
                shadow: {
                    enabled: true,
                    color: 'rgba(0,0,0,0.5)',
                    size: 10,
                    x: 5,
                    y: 5
                }
            },
            edges: {
                font: {
                    color: '#ffffff',
                    strokeWidth: 3,
                    strokeColor: '#121212',
                    size: 12
                },
                shadow: {
                    enabled: true,
                    color: 'rgba(0,0,0,0.5)',
                    size: 10,
                    x: 5,
                    y: 5
                }
            },
            physics: {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -3000,
                    centralGravity: 0.3,
                    springLength: 200,
                    springConstant: 0.05,
                    damping: 0.09
                },
                stabilization: {
                    enabled: true,
                    iterations: 1000,
                    updateInterval: 100
                }
            },
            interaction: {
                navigationButtons: true,
                keyboard: true,
                tooltipDelay: 200,
                hover: true
            },
            groups: {
                switch: {
                    color: {
                        background: '#4CAF50',
                        border: '#2E7D32',
                        highlight: {
                            background: '#81C784',
                            border: '#4CAF50'
                        }
                    }
                },
                wireless: {
                    color: {
                        background: '#FF9800',
                        border: '#F57C00',
                        highlight: {
                            background: '#FFB74D',
                            border: '#FF9800'
                        }
                    }
                },
                appliance: {
                    color: {
                        background: '#9C27B0',
                        border: '#7B1FA2',
                        highlight: {
                            background: '#BA68C8',
                            border: '#9C27B0'
                        }
                    }
                },
                client: {
                    color: {
                        background: '#2196F3',
                        border: '#1976D2',
                        highlight: {
                            background: '#64B5F6',
                            border: '#2196F3'
                        }
                    }
                },
                unknown: {
                    color: {
                        background: '#9E9E9E',
                        border: '#616161',
                        highlight: {
                            background: '#BDBDBD',
                            border: '#9E9E9E'
                        }
                    }
                }
            }
        };
        
        // Initialize the network
        var network = new vis.Network(container, data, options);
        
        // Add event listeners
        network.on("stabilizationProgress", function(params) {
            // Update loading bar
            console.log("Stabilization progress:", params.iterations, "/", params.total);
        });
        
        network.on("stabilizationIterationsDone", function() {
            console.log("Stabilization complete");
        });
        
        // Control functions
        function fitNetwork() {
            network.fit({
                animation: {
                    duration: 1000,
                    easingFunction: "easeInOutQuad"
                }
            });
        }
        
        var physicsEnabled = true;
        function togglePhysics() {
            physicsEnabled = !physicsEnabled;
            network.setOptions({physics: {enabled: physicsEnabled}});
        }
        
        var edgeLabelsVisible = true;
        function toggleEdgeLabels() {
            edgeLabelsVisible = !edgeLabelsVisible;
            edges.forEach(function(edge) {
                if (edgeLabelsVisible) {
                    if (edge._originalLabel) {
                        edges.update({id: edge.id, label: edge._originalLabel});
                    }
                } else {
                    if (edge.label) {
                        edge._originalLabel = edge.label;
                        edges.update({id: edge.id, label: ""});
                    }
                }
            });
        }
        
        var nodeLabelsVisible = true;
        function toggleNodeLabels() {
            nodeLabelsVisible = !nodeLabelsVisible;
            nodes.forEach(function(node) {
                if (nodeLabelsVisible) {
                    if (node._originalLabel) {
                        nodes.update({id: node.id, label: node._originalLabel});
                    }
                } else {
                    if (node.label) {
                        node._originalLabel = node.label;
                        nodes.update({id: node.id, label: ""});
                    }
                }
            });
        }
        
        // Initial fit
        setTimeout(fitNetwork, 1000);
    </script>
</body>
</html>
"""
    
    # Write HTML to file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logging.info(f"Network topology visualization saved to {output_path}")
    return str(output_path)

def open_topology_visualization(html_path):
    """
    Open the topology visualization in the default web browser
    
    Args:
        html_path (str): Path to the HTML file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        webbrowser.open(f"file://{html_path}")
        return True
    except Exception as e:
        logging.error(f"Error opening topology visualization: {str(e)}")
        return False

def visualize_network_topology(topology_data, network_name=None):
    """
    Generate and open a network topology visualization
    
    Args:
        topology_data (dict): Network topology data with nodes and links
        network_name (str, optional): Name of the network. If None, will use from topology_data.
        
    Returns:
        str: Path to the generated HTML file or None if failed
    """
    try:
        html_path = generate_topology_html(topology_data, network_name)
        open_topology_visualization(html_path)
        return html_path
    except Exception as e:
        logging.error(f"Error visualizing network topology: {str(e)}")
        return None

def build_topology_from_api_data(devices, clients, links=None):
    """
    Build a network topology from Meraki API data
    
    Args:
        devices (list): List of network devices
        clients (list): List of network clients
        links (list, optional): List of topology links. If None, will build manually.
        
    Returns:
        dict: Network topology data with nodes and links
    """
    topology = {
        'nodes': [],
        'links': []
    }
    
    # Process devices
    device_map = {}
    for device in devices:
        device_id = device.get('serial', device.get('mac', str(uuid.uuid4())))
        device_map[device_id] = device
        
        # Create node for device
        node = {
            'id': device_id,
            'label': device.get('name', device.get('mac', 'Unknown')),
            'type': device.get('type', 'unknown'),
            'model': device.get('model', 'Unknown'),
            'ip': device.get('lanIp', device.get('ip', 'Unknown')),
            'mac': device.get('mac', 'Unknown'),
            'status': device.get('status', 'Unknown'),
            'network_id': device.get('networkId', 'Unknown')
        }
        
        # Add ports information if available
        if device.get('ports'):
            node['ports'] = device['ports']
        
        topology['nodes'].append(node)
    
    # Process clients
    client_map = {}
    for client in clients:
        client_id = client.get('id', client.get('mac', str(uuid.uuid4())))
        client_map[client_id] = client
        
        # Create node for client
        node = {
            'id': client_id,
            'label': client.get('description', client.get('dhcpHostname', client.get('hostname', client.get('mac', 'Unknown')))),
            'type': 'client',
            'client_type': client.get('deviceType', 'unknown'),
            'ip': client.get('ip', 'Unknown'),
            'mac': client.get('mac', 'Unknown'),
            'vlan': client.get('vlan', 'Unknown'),
            'status': client.get('status', 'Unknown'),
            'last_seen': client.get('lastSeen', 'Unknown'),
            'connected_device': client.get('recentDeviceName', client.get('deviceName', 'Unknown')),
            'switchport': client.get('switchport', 'Unknown'),
            'switchportDesc': client.get('switchportDesc', '')
        }
        
        topology['nodes'].append(node)
        
        # Create link to connected device if available
        if client.get('recentDeviceSerial'):
            device_id = client.get('recentDeviceSerial')
            if device_id in device_map:
                # Determine connection type
                connection_type = 'wired'
                if client.get('ssid'):
                    connection_type = 'wireless'
                
                # Create a descriptive interface label
                interface_label = 'Unknown'
                if client.get('switchport'):
                    port_info = f"Port {client.get('switchport')}"
                    if client.get('switchportDesc'):
                        port_info += f" ({client.get('switchportDesc')})"
                    interface_label = port_info
                elif client.get('vlan'):
                    interface_label = f"VLAN {client.get('vlan')}"
                
                link = {
                    'source': client_id,
                    'target': device_id,
                    'type': connection_type,
                    'interface': interface_label
                }
                topology['links'].append(link)
    
    # Process API-provided links if available
    if links:
        for link in links:
            source = link.get('source', link.get('sourceSerial', link.get('sourceMac')))
            target = link.get('target', link.get('targetSerial', link.get('targetMac')))
            
            # Skip if source or target is not in our device map
            if not (source in device_map or source in client_map) or not (target in device_map or target in client_map):
                continue
            
            link_type = 'unknown'
            if 'linkType' in link:
                link_type = link['linkType'].lower()
            
            interface_label = 'Unknown'
            if 'sourcePort' in link:
                interface_label = f"Port {link['sourcePort']}"
            
            topology_link = {
                'source': source,
                'target': target,
                'type': link_type,
                'interface': interface_label
            }
            topology['links'].append(topology_link)
    
    # If no links were provided, try to infer connections between devices
    elif not topology['links']:
        # Create connections between switches based on MAC address tables
        for device_id, device in device_map.items():
            if device.get('type') == 'switch' and 'ports' in device:
                for port_number, port_data in device.get('ports', {}).items():
                    if 'cdp' in port_data and port_data['cdp'].get('deviceId'):
                        # Find target device by name
                        target_name = port_data['cdp'].get('deviceId')
                        target_id = None
                        for d_id, d in device_map.items():
                            if d.get('name') == target_name:
                                target_id = d_id
                                break
                        
                        if target_id:
                            link = {
                                'source': device_id,
                                'target': target_id,
                                'type': 'switch',
                                'interface': f"Port {port_number}"
                            }
                            topology['links'].append(link)
    
    return topology

def create_vis_network_data(topology_data):
    """
    Create visualization data for network topology
    
    Args:
        topology_data (dict): Network topology data with nodes and links
        
    Returns:
        dict: Visualization data for network topology
    """
    vis_nodes = []
    vis_edges = []
    
    # Process nodes
    for node in topology_data.get('nodes', []):
        node_type = node.get('type', 'unknown')
        
        # Determine icon, shape, and size based on node type
        icon = DEVICE_ICONS.get(node_type, 'device_unknown')
        shape = 'circularImage'
        size = 30
        font_size = 14
        
        # For client devices, use client type icon if available
        if node_type == 'client':
            client_type = node.get('client_type', 'unknown')
            if client_type in DEVICE_ICONS:
                icon = DEVICE_ICONS[client_type]
            size = 20
            font_size = 12
        
        # Create detailed title content for hover tooltip
        if node_type == 'client':
            title_content = f"""<b>{node.get('label', 'Unknown')}</b><br>
<b>Type:</b> {node.get('client_type', 'Unknown')}<br>
<b>IP:</b> {node.get('ip', 'Unknown')}<br>
<b>MAC:</b> {node.get('mac', 'Unknown')}<br>
<b>VLAN:</b> {node.get('vlan', 'Unknown')}<br>
<b>Status:</b> {node.get('status', 'Unknown')}<br>
<b>Connected to:</b> {node.get('connected_device', 'Unknown')}"""
            
            # Add switchport information if available
            if node.get('switchport'):
                port_info = f"{node.get('switchport', 'Unknown')}"
                if node.get('switchportDesc'):
                    port_info += f" ({node.get('switchportDesc')})"
                title_content += f"""<br>
<b>Switchport:</b> {port_info}"""
            
            # Add last seen information
            if node.get('last_seen'):
                title_content += f"<br><b>Last Seen:</b> {node.get('last_seen', 'Unknown')}"
        else:
            title_content = f"""<b>{node.get('label', 'Unknown')}</b><br>
<b>Model:</b> {node.get('model', 'Unknown')}<br>
<b>Type:</b> {node_type}<br>
<b>IP:</b> {node.get('ip', 'Unknown')}<br>
<b>MAC:</b> {node.get('mac', 'Unknown')}<br>
<b>Status:</b> {node.get('status', 'Unknown')}"""
        
        vis_node = {
            'id': node['id'],
            'label': node.get('label', node['id']),
            'title': title_content,
            'shape': shape,
            'image': f"https://img.icons8.com/material/48/{icon}.png",
            'group': node_type,
            'size': size,
            'font': {
                'size': font_size
            }
        }
        vis_nodes.append(vis_node)
    
    # Process links
    connection_types = set()
    for link in topology_data.get('links', []):
        link_type = link.get('type', 'unknown')
        connection_types.add(link_type)
        style = CONNECTION_STYLES.get(link_type, CONNECTION_STYLES['unknown'])
        
        # Create a descriptive label based on the connection type
        label = ""
        if link_type == "uplink":
            label = "Internet Connection"
        elif link_type == "switch":
            label = f"{link.get('interface', 'unknown')}"
        elif link_type == "wireless":
            label = "Wireless Connection"
        elif link_type == "wired":
            # For wired connections, show port and VLAN if available
            interface_info = link.get('interface', 'unknown')
            label = interface_info
        
        vis_edge = {
            'from': link['source'],
            'to': link['target'],
            'label': label,
            'title': label,
            'color': {
                'color': style['color'],
                'highlight': style['highlight']
            },
            'width': style['width'],
            'dashes': style['dashes'],
            'arrows': {
                'to': {
                    'enabled': style['arrow']
                }
            },
            'font': {
                'size': 10,
                'align': 'middle'
            }
        }
        vis_edges.append(vis_edge)
    
    return {
        'nodes': vis_nodes,
        'edges': vis_edges,
        'connection_types': connection_types
    }
