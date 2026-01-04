"""
Branding Configuration for Outset Solutions - Meraki Management Utility

This module contains branding information that can be used throughout the application.
"""

# Company Information
COMPANY_NAME = "Outset Solutions"
COMPANY_URL = "https://www.outsetsolutions.com"
COMPANY_EMAIL = "info@outsetsolutions.com"  # Update with actual email if available

# Application Information
APP_NAME = "Meraki Management Utility"
APP_FULL_NAME = f"{COMPANY_NAME} - {APP_NAME}"
APP_VERSION = "2.0"
APP_DESCRIPTION = "A professional network management tool for Cisco Meraki"

# Branding Messages
WELCOME_MESSAGE = f"Welcome to {APP_FULL_NAME}!"
THANK_YOU_MESSAGE = f"Thank you for using {APP_FULL_NAME}!"

# Footer Information
FOOTER_TEMPLATE = "{company_name}\n{year} {company_name}\n{company_url}"

def get_footer(year=None):
    """Get formatted footer text"""
    from datetime import datetime
    if year is None:
        year = datetime.now().year
    return FOOTER_TEMPLATE.format(
        company_name=COMPANY_NAME,
        year=year,
        company_url=COMPANY_URL
    )

def get_app_title():
    """Get the full application title"""
    return APP_FULL_NAME

def get_branded_message(message_type="welcome"):
    """Get branded messages"""
    messages = {
        "welcome": WELCOME_MESSAGE,
        "thank_you": THANK_YOU_MESSAGE,
    }
    return messages.get(message_type, "")
