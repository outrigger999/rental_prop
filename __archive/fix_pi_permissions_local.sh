#!/bin/bash

# Fix Pi Permissions Script - Local Version
# Version 1.0
#
# This script fixes permissions for the Moving Box Tracker application
# when run directly on the Raspberry Pi.

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[INFO]${NC} Setting correct permissions for static files..."

# Change to project directory
cd ~/moving_box_tracker || { echo -e "${RED}[ERROR]${NC} Failed to change to project directory!"; exit 1; }

# Ensure static directory and subdirectories have correct permissions (755)
find static -type d -exec chmod 755 {} \; || { echo -e "${RED}[ERROR]${NC} Failed to set directory permissions!"; exit 1; }

# Ensure static files have correct permissions (644)
find static -type f -exec chmod 644 {} \; || { echo -e "${RED}[ERROR]${NC} Failed to set file permissions!"; exit 1; }

echo -e "${GREEN}[INFO]${NC} Setting correct ownership for static files..."
# Make sure nginx user (www-data) can read the files
sudo chown -R ${USER}:www-data ~/moving_box_tracker/static/ || { echo -e "${RED}[ERROR]${NC} Failed to set ownership!"; exit 1; }
sudo chmod -R g+r ~/moving_box_tracker/static/ || { echo -e "${RED}[ERROR]${NC} Failed to set group read permissions!"; exit 1; }

echo -e "${GREEN}[SUCCESS]${NC} Static file permissions and ownership updated."

# Also ensure parent directories have at least execute+read permissions
echo -e "${GREEN}[INFO]${NC} Checking parent directory permissions..."
sudo chmod o+rx ~ || { echo -e "${RED}[ERROR]${NC} Failed to set home directory permissions!"; exit 1; }
sudo chmod o+rx ~/moving_box_tracker || { echo -e "${RED}[ERROR]${NC} Failed to set project directory permissions!"; exit 1; }

echo -e "${GREEN}[SUCCESS]${NC} Parent directory permissions updated."
echo -e "${GREEN}[INFO]${NC} All permissions have been fixed successfully."
echo -e "${GREEN}[INFO]${NC} If you were experiencing 403 Forbidden errors, they should now be resolved."
