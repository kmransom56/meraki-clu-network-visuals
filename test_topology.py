#!/usr/bin/env python3
"""
Test script for the network topology functionality in the Meraki API module.
"""
import os
import logging
from dotenv import load_dotenv
from modules.meraki.meraki_api import initialize_api_key, get_organizations, get_organization_networks, get_network_topology

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

def test_network_topology():
    """Test the network topology functionality with improved error handling."""
    try:
        # Initialize API key
        api_key = initialize_api_key()
        if not api_key:
            logging.error("Failed to initialize API key")
            return
        
        # Get organizations
        logging.info("Fetching organizations...")
        organizations = get_organizations(api_key)
        if not organizations:
            logging.error("No organizations found")
            return
        
        # Use the first organization
        org_id = organizations[0]['id']
        org_name = organizations[0]['name']
        logging.info(f"Using organization: {org_name} (ID: {org_id})")
        
        # Get networks for the organization
        logging.info(f"Fetching networks for organization {org_id}...")
        networks = get_organization_networks(api_key, org_id)
        if not networks:
            logging.error(f"No networks found for organization {org_id}")
            return
        
        # Test network topology for each network
        for network in networks:
            network_id = network['id']
            network_name = network['name']
            logging.info(f"Testing network topology for: {network_name} (ID: {network_id})")
            
            topology = get_network_topology(api_key, network_id)
            if topology:
                logging.info(f"Successfully retrieved topology for network {network_name}")
                logging.info(f"Nodes: {len(topology['nodes'])}")
                logging.info(f"Links: {len(topology['links'])}")
                
                # Print some node details
                if topology['nodes']:
                    logging.info("Sample nodes:")
                    for node in topology['nodes'][:3]:  # Show up to 3 nodes
                        logging.info(f"  - {node['name']} ({node['model']})")
            else:
                logging.warning(f"No topology data for network {network_name}")
        
        logging.info("Network topology testing completed successfully")
        
    except Exception as e:
        logging.error(f"Error testing network topology: {str(e)}")

if __name__ == "__main__":
    test_network_topology()
