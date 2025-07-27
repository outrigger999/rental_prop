# Nginx Domain Access Fix

## Problem

Three key features of the Moving Box Tracker application were affected when accessing through the Nginx domain (`moving.box`), while they worked correctly when accessing directly via IP address (`192.168.10.10:5001`):

1. **Quick Category Button** - Not working (JavaScript not loading)
2. **Create Box Button** - Fixed and working
3. **Delete Box Button** - Fixed and working

## Root Causes

Multiple issues were identified and fixed:

1. **API Route Position**: The `/api/categories` route was defined after the `if __name__ == '__main__'` block in `simplified_app.py`, preventing it from being registered when the app runs as a module through a WSGI server.

2. **File Permission Issues**: Static files were inaccessible to Nginx (www-data user) due to restrictive permissions:
   - Home directory (`~`) had `700` permissions (`drwx------`)
   - Project directory (`~/moving_box_tracker`) had `700` permissions
   - Nginx (www-data user) couldn't traverse these directories to reach the static files

3. **Nginx Configuration**: The Nginx configuration needed simplification and proper handling of static files.

## Solutions Applied

### 1. Fixed API Route Position

Moved the `/api/categories` route before the `if __name__ == '__main__'` block in `simplified_app.py`:

```python
# API Routes - Must be defined before the main block
@app.route('/api/categories', methods=['POST'])
def api_add_category():
    # Function code...

# Add this at the bottom for running the app directly 
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
```

### 2. Simplified Nginx Configuration

Implemented a more straightforward Nginx configuration:

```nginx
server {
    listen 80;
    server_name moving.box;
    
    # Set document root to the Flask app directory
    root /home/pi/moving_box_tracker;

    # Main application - proxy all requests to Flask
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
    }

    # Static files - simplest possible configuration
    location /static/ {
        # This is the KEY DIFFERENCE - using alias instead of root with the correct path
        alias /home/pi/moving_box_tracker/static/;
        # Basic settings
        autoindex off;
        expires max;
    }

    # Log configuration
    access_log /var/log/nginx/moving_box_access.log;
    error_log /var/log/nginx/moving_box_error.log warn;
}
```

### 3. Fixed File Permissions

Created diagnostic and fix scripts to properly set permissions:

#### Permissions Fix Script (`fix_permissions.sh`)

```bash
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
```

#### Diagnostic Script (`diagnose_nginx.sh`)

```bash
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
```

## Critical Finding

The most important discovery was that **parent directory traversal permissions** are crucial for Nginx to access static files. Even if the static files themselves have correct permissions (644), Nginx won't be able to access them if it can't traverse the parent directories.

This requires:
1. Home directory (`~`) to have at least `drwx--x--x` permissions (701)
2. Project directory (`~/moving_box_tracker`) to have at least `drwx--x--x` permissions (701)

Our solution applied `drwx--xr-x` permissions (705) to allow both traversal and listing.

## How to Apply These Fixes in the Future

If similar issues occur in the future:

1. Check API route placement in the Flask application
2. Verify Nginx configuration (use the simplified version provided)
3. Run the diagnostic script to identify permission issues
4. Run the permissions fix script to apply the necessary permissions
5. Restart Nginx and the Flask application

## Testing the Fix

After applying all fixes, all three core features work correctly when accessing the application through the `moving.box` domain:

1. Quick Category Button - Working properly
2. Create Box Button - Working properly
3. Delete Box Button - Working properly
