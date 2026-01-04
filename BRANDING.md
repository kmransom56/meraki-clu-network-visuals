# Branding Guide - Outset Solutions

This document outlines the branding standards for the Outset Solutions - Meraki Management Utility.

## Company Information

- **Company Name:** Outset Solutions
- **Website:** https://www.outsetsolutions.com
- **Application Name:** Meraki Management Utility
- **Full Application Name:** Outset Solutions - Meraki Management Utility
- **Version:** 2.0

## Branding Configuration

All branding information is centralized in `settings/branding.py`. This makes it easy to update company information across the entire application.

### Usage

```python
from settings import branding

# Get company name
company = branding.COMPANY_NAME  # "Outset Solutions"

# Get full app name
app_name = branding.APP_FULL_NAME  # "Outset Solutions - Meraki Management Utility"

# Get welcome message
welcome = branding.WELCOME_MESSAGE

# Get footer
footer = branding.get_footer()
```

## Branding Elements

### Application Title
- **Display Name:** Outset Solutions - Meraki Management Utility
- **Short Name:** Meraki Management Utility
- **Used in:** CLI headers, welcome messages, documentation

### Welcome Messages
- **Welcome:** "Welcome to Outset Solutions - Meraki Management Utility!"
- **Thank You:** "Thank you for using Outset Solutions - Meraki Management Utility!"

### Footer
- **Format:** Company name, year, website
- **Example:** 
  ```
  OUTSET SOLUTIONS
  2024 Outset Solutions
  https://www.outsetsolutions.com
  ```

## Files with Branding

### Main Application Files
- `main.py` - Main application entry point
- `settings/branding.py` - Branding configuration
- `README.md` - Project documentation

### Documentation Files
- `README.md` - Main readme with company information
- `BRANDING.md` - This file
- `AGENTS.md` - AI agent instructions

## Updating Branding

To update branding information:

1. **Edit `settings/branding.py`** - Update company information
2. **Update README.md** - Update company section
3. **Test changes** - Run the application to verify branding appears correctly

### Example: Changing Company Name

```python
# In settings/branding.py
COMPANY_NAME = "Your Company Name"
COMPANY_URL = "https://www.yourcompany.com"
```

All references throughout the application will automatically use the new branding.

## Branding Standards

### Consistency
- Always use the full application name in user-facing messages
- Use consistent capitalization: "Outset Solutions" (not "OUTSET SOLUTIONS" unless in headers)
- Include company name in all major user interactions

### Professional Tone
- Use professional, clear language
- Maintain a helpful, supportive tone
- Include company information where appropriate

### Visual Elements
- Company name in headers and footers
- Consistent formatting across all messages
- Professional appearance in CLI output

## Copyright and Attribution

### Original Authors
- Matia Zanella (Original author)
- Keith Ransom (Contributor)

### Current Maintainer
- **Outset Solutions** - Current maintainer and enhancer

### License
GNU General Public License v2

## Contact

For branding questions or updates:
- Website: https://www.outsetsolutions.com
- Update the `COMPANY_EMAIL` in `settings/branding.py` with actual contact email
