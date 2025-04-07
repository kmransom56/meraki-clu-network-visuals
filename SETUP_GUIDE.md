# Cisco Meraki CLU - Setup Guide

## Overview

The Cisco Meraki Command Line Utility (CLU) is a powerful tool for managing and visualizing Meraki networks. This guide will help you set up and use the application.

## Prerequisites

- **Python**: Version 3.6 or higher
- **Meraki Dashboard API Key**: You'll need API access to your Meraki dashboard
- **Network Access**: Ability to reach api.meraki.com (works through corporate proxies)

## Installation

### Option 1: Automated Setup (Recommended)

1. Extract the zip file to a location on your computer
2. Run the `setup.bat` file by double-clicking it
3. Follow the on-screen instructions

### Option 2: Manual Setup

1. Extract the zip file to a location on your computer
2. Open a command prompt in the extracted directory
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

After installation, you can run the application using one of these methods:

1. **Double-click** the `start_meraki_clu.bat` file created during setup
2. **Command line**: Run `python main.py` from the application directory

## First-Time Setup

When you run the application for the first time:

1. You'll be prompted to enter your Meraki Dashboard API key
2. The key will be securely stored using Fernet encryption in your user directory
3. You may be asked to create a database password for securing sensitive information
4. The application will create a local database file (`cisco_meraki_clu_db.db`) to store configuration data
5. You won't need to enter the API key again on subsequent runs

### Database Information

The application uses a SQLite database (`cisco_meraki_clu_db.db`) to store:
- Configuration settings
- IPinfo access tokens (if used)
- Other non-sensitive application data

This database is encrypted with a password you create during first-time setup. The password is used to protect any sensitive information stored in the database.

### Getting a Meraki API Key

1. Log in to the [Meraki Dashboard](https://dashboard.meraki.com/)
2. Go to your profile (top-right corner)
3. Navigate to "My Profile" → "API access"
4. Generate an API key if you don't already have one

## Features

The application includes several powerful features:

- **Organization and Network Management**: Browse and manage your Meraki organizations and networks
- **Device Management**: View and configure switches, access points, and other devices
- **Network Topology Visualization**: Generate interactive network diagrams showing:
  - Device-to-device connections
  - Client devices with IP addresses and connection details
  - Different connection types with appropriate styling
- **Network Health Monitoring**: Check the status of your networks and devices
- **Firewall Rules Management**: View and analyze firewall configurations

## Troubleshooting

### SSL Certificate Issues

The application includes robust SSL certificate handling that works in corporate environments with proxies like Zscaler. If you encounter SSL-related errors:

1. Ensure you have network connectivity to api.meraki.com
2. Check if your corporate firewall allows access to the Meraki API
3. The application will automatically try alternative verification methods if needed

### API Key Issues

If you encounter authentication issues:

1. Verify your API key is valid in the Meraki Dashboard
2. Check that your API key has the necessary permissions
3. You can reset your stored API key by deleting the key file in your user directory

### Database Issues

If you encounter database-related issues:

1. If you forget your database password, you may need to delete the database file and create a new one
2. The database file is located at `db/cisco_meraki_clu_db.db` in the application directory
3. Deleting this file will reset all stored settings, but will not affect your API key storage

## Security Notes

This application implements several security measures:

1. **API Key Security**: Your API key is stored using Fernet encryption
2. **Database Security**: Sensitive information in the database is protected with a password
3. **SSL Certificate Verification**: Uses a two-step verification strategy with fallbacks
4. **Error Handling**: Comprehensive error handling and logging

## Support

If you encounter any issues, please contact [Your Name/Team] for assistance.

---

 2024 [Your Company]
