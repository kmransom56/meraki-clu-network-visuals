# Cisco Meraki CLU - Distribution Package

## Quick Start Guide

Welcome to the Cisco Meraki Command Line Utility (CLU)! This package contains everything you need to get started with managing and visualizing your Meraki networks.

### Installation Steps

1. **Extract** this zip file to a location on your computer
2. **Run** the `setup.bat` file by double-clicking it
3. **Launch** the application using the `start_meraki_clu.bat` file that will be created during setup
4. **Enter** your Meraki Dashboard API key when prompted on first run
5. **Create** a database password when prompted to secure sensitive information

### What's Included

- **Main Application**: Complete codebase for the Meraki CLU
- **Setup Script**: Automated installation of all required dependencies
- **Documentation**: Comprehensive setup guide and usage instructions
- **Launcher**: Easy-to-use batch file for launching the application
- **Database**: Local SQLite database for storing configuration data

### System Requirements

- Windows 7/10/11
- Python 3.6 or higher
- Internet access to api.meraki.com

### Key Features

- **Enhanced Network Visualization**: View detailed network topology with client devices
- **Device Management**: Manage switches, access points, and other Meraki devices
- **Client Information**: See detailed client information including IP addresses and connection types
- **Robust Security**: Works with corporate proxies and implements secure API key storage
- **Configuration Storage**: Securely stores settings and tokens in an encrypted database

For detailed instructions, please refer to the `SETUP_GUIDE.md` file included in this package.

---

## For IT Administrators

This application:
- Uses Fernet encryption for API key storage
- Implements password protection for the local database
- Implements robust SSL certificate handling for corporate environments
- Works with proxy servers like Zscaler without additional configuration
- Includes comprehensive error handling and logging

### Database Information

The application uses a SQLite database (`cisco_meraki_clu_db.db`) to store configuration settings and other non-sensitive data. This database is protected with a password that users create during first-time setup.

---

*Last Updated: April 1, 2025*
