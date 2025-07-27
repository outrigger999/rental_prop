# Nginx Configuration and File Permissions Fix

This document explains the changes made to fix the Nginx configuration and file permissions for proper domain name access to the Moving Box Tracker application.

## Problem

The application features (Quick Category, Create Box, Delete Box) were working when accessing via direct IP address (`192.168.10.10:5001`), but **not** when accessing via the domain name (`moving.box`).

## Root Causes Identified

1. **Nginx Configuration Issues**:
   - Incorrect server_name (was localhost instead of moving.box)
   - Wrong port configuration (8000 instead of 5001)
   - Incorrect paths for static files
   - Missing API route handling

2. **File Permission Issues**:
   - Static file permissions too restrictive (700)
   - Directory permissions too restrictive
   - Nginx user (www-data) couldn't access static files

## Changes Made

1. **Updated Nginx Configuration**:
   - Set server_name to `moving.box`
   - Set correct port (5001) for the application
   - Updated static file paths to `/home/pi/moving_box_tracker/static/`
   - Added proper API endpoint handling
   - Added security headers and improved caching
   - Added custom error pages

2. **Required Permission Changes on Pi** (These must be applied after sync):

```bash
# Fix directory permissions (755 allows Nginx to read and traverse directories)
sudo chmod -R 755 ~/moving_box_tracker/static
sudo chmod -R 755 ~/moving_box_tracker/templates

# Fix file permissions (644 allows Nginx to read files)
sudo find ~/moving_box_tracker/static -type f -exec chmod 644 {} \;
```

## How to Apply the Fix

1. Run the sync script to deploy the updated Nginx configuration:
   ```bash
   ./sync_to_pi.sh
   ```

2. SSH into the Raspberry Pi and apply the permission fixes:
   ```bash
   ssh movingdb
   
   # Then run the permission commands above
   chmod -R 755 ~/moving_box_tracker/static
   chmod -R 755 ~/moving_box_tracker/templates
   find ~/moving_box_tracker/static -type f -exec chmod 644 {} \;
   
   # Restart Nginx
   sudo systemctl restart nginx
   ```

3. Access the application via `moving.box` in your browser - all features should now work.

## Troubleshooting

If issues persist:

1. Check Nginx error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. Check application logs:
   ```bash
   tail -f ~/moving_box_tracker/logs/app.log
   ```

3. Verify Nginx configuration is valid:
   ```bash
   sudo nginx -t
   ```
