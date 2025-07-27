#!/bin/bash

# Nginx Diagnostic Script for Moving Box Tracker
# This script checks common Nginx configuration issues

echo "Running Nginx Diagnostic Script"
echo "------------------------------"

# SSH into the Pi and run diagnostics
ssh movingdb << 'EOF'
    echo "1. Checking Nginx configuration..."
    sudo nginx -t

    echo -e "\n2. Checking permissions for static files..."
    ls -la ~/moving_box_tracker/static/
    ls -la ~/moving_box_tracker/static/css/
    ls -la ~/moving_box_tracker/static/js/

    echo -e "\n3. Checking Nginx user..."
    ps aux | grep nginx | grep -v grep

    echo -e "\n4. Checking if Nginx can access the files..."
    sudo -u www-data ls -la ~/moving_box_tracker/static/css/
    sudo -u www-data ls -la ~/moving_box_tracker/static/js/

    echo -e "\n5. Checking parent directory permissions..."
    ls -la ~/moving_box_tracker/
    ls -la ~/

    echo -e "\n6. Creating a test file accessible by www-data..."
    echo "This is a test file" > ~/moving_box_tracker/static/test.txt
    chmod 644 ~/moving_box_tracker/static/test.txt
    sudo chown www-data:www-data ~/moving_box_tracker/static/test.txt
    
    echo -e "\n7. Ensure all parent directories are executable..."
    chmod +x ~
    chmod +x ~/moving_box_tracker
    
    echo -e "\n8. Apply stronger fix - make parent directories readable by others..."
    chmod o+rx ~
    chmod o+rx ~/moving_box_tracker
    
    echo -e "\n9. Final permissions check..."
    ls -la ~/
    ls -la ~/moving_box_tracker/
EOF

echo "------------------------------"
echo "Diagnostic script completed. Try accessing moving.box in your browser now."
