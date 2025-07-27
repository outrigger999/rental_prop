#!/bin/bash

# Fix Local Permissions Script
# This script ensures that all static files have the correct permissions
# to be served by a web server, both locally and when synced to the Pi

echo "Setting correct permissions for static files in local environment..."

# Ensure static directory and subdirectories have correct permissions (755)
find static -type d -exec chmod 755 {} \; || { echo "Failed to set directory permissions!"; exit 1; }

# Ensure static files have correct permissions (644)
find static -type f -exec chmod 644 {} \; || { echo "Failed to set file permissions!"; exit 1; }

# Remove extended attributes that might be causing issues (@)
xattr -c static/css/styles.css
xattr -c static/js/main.js

echo "Local static file permissions updated."
echo "Your files should now work correctly in both local and Pi environments."
