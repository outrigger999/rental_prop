# Nginx Static File Permissions Troubleshooting Guide

## Critical Issue: 403 Forbidden Errors on Static Files

### Root Cause
The primary cause of 403 Forbidden errors for static files in nginx is **directory permissions that prevent the nginx user (www-data) from traversing the directory path** to reach the static files.

### Symptoms
- Browser console shows: `GET /static/css/style.css 403 (Forbidden)`
- Nginx access log shows 403 responses for static file requests
- Main application loads but CSS/JS files fail to load
- File permissions appear correct (644) but directories are inaccessible

### Diagnosis Commands
```bash
# Check directory permissions
ls -ld /home/smashimo/rental_prop
ls -ld /home/smashimo/rental_prop/static
ls -ld /home/smashimo/rental_prop/static/css

# Test if nginx user can access files
sudo -u www-data cat /home/smashimo/rental_prop/static/css/style.css
sudo -u www-data ls /home/smashimo/rental_prop/static/

# Check nginx error logs
sudo tail -n 20 /var/log/nginx/error.log
```

### The Fix (CRITICAL - PRESERVE THIS)

#### 1. Directory Permissions (Most Important)
```bash
# Set directory permissions to 755 (drwxr-xr-x)
# This allows www-data to traverse directories
sudo chmod 755 /home/smashimo/rental_prop
sudo chmod 755 /home/smashimo/rental_prop/static
sudo chmod 755 /home/smashimo/rental_prop/static/css
sudo chmod 755 /home/smashimo/rental_prop/static/js
sudo chmod 755 /home/smashimo/rental_prop/templates
```

#### 2. File Permissions
```bash
# Set file permissions to 644 (-rw-r--r--)
sudo find /home/smashimo/rental_prop/static -type f -exec chmod 644 {} \;
sudo find /home/smashimo/rental_prop/templates -type f -exec chmod 644 {} \;
```

#### 3. Ownership
```bash
# Set correct ownership (user:group)
sudo chown -R smashimo:www-data /home/smashimo/rental_prop/static/
sudo chown -R smashimo:www-data /home/smashimo/rental_prop/templates/
```

#### 4. Verification
```bash
# Verify the fix worked
sudo -u www-data cat /home/smashimo/rental_prop/static/css/style.css
if [ $? -eq 0 ]; then
    echo "SUCCESS: www-data can access static files"
else
    echo "FAILED: Still cannot access static files"
fi
```

### Expected Permissions After Fix
```
/home/smashimo/rental_prop/          drwxr-xr-x (755)
/home/smashimo/rental_prop/static/   drwxr-xr-x (755)
/home/smashimo/rental_prop/static/css/ drwxr-xr-x (755)
/home/smashimo/rental_prop/static/css/style.css -rw-r--r-- (644)
```

### Integration with Sync Script
This fix has been integrated into the `sync_to_pi.sh` script to ensure permissions are correctly set on every deployment.

### Key Learning
**Directory permissions are just as critical as file permissions for nginx static file serving.** All parent directories in the path must be traversable (755) by the nginx user (www-data).

### Troubleshooting Steps
1. Check nginx is running: `sudo systemctl status nginx`
2. Check nginx configuration: `sudo nginx -t`
3. Check directory permissions with `ls -ld`
4. Test www-data access with `sudo -u www-data`
5. Check nginx error logs: `sudo tail /var/log/nginx/error.log`
6. Apply the permissions fix above
7. Reload nginx: `sudo systemctl reload nginx`

### Prevention
- Always ensure sync scripts set directory permissions to 755
- Include permission verification in deployment scripts
- Test www-data access after any file system changes
