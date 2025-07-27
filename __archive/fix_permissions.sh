#!/bin/bash

# Moving Box Tracker Permissions Fix Script
# This script applies the exact permission fixes that worked previously

echo "Running Permission Fix Script for Moving Box Tracker"
echo "-----------------------------------------------------"

# SSH into the Pi and apply the permission fixes
ssh movingdb << 'EOF'
    echo "Fixing directory permissions..."
    chmod -R 755 ~/moving_box_tracker/static
    chmod -R 755 ~/moving_box_tracker/templates
    
    echo "Fixing file permissions..."
    find ~/moving_box_tracker/static -type f -exec chmod 644 {} \;
    
    echo "Restarting Nginx..."
    sudo systemctl restart nginx
    
    echo "Permissions fix completed."
EOF

echo "-----------------------------------------------------"
echo "Permission fix script completed."
