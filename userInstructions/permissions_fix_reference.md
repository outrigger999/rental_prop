# Quick Reference: Nginx Static File Permissions Fix

## If You See 403 Forbidden Errors on Static Files

### Quick Diagnosis
```bash
# SSH to the Pi
ssh smashimo@movingdb

# Check if www-data can access your static files
sudo -u www-data cat ~/rental_prop/static/css/style.css
```

If this fails, you need to apply the permissions fix.

### Quick Fix Commands
```bash
# Run these commands on the Pi to fix permissions
sudo chmod 755 ~/rental_prop
sudo chmod 755 ~/rental_prop/static
sudo chmod 755 ~/rental_prop/static/css
sudo chmod 755 ~/rental_prop/static/js
sudo chmod 755 ~/rental_prop/templates

# Fix file permissions
sudo find ~/rental_prop/static -type f -exec chmod 644 {} \;
sudo find ~/rental_prop/templates -type f -exec chmod 644 {} \;

# Fix ownership
sudo chown -R smashimo:www-data ~/rental_prop/static/
sudo chown -R smashimo:www-data ~/rental_prop/templates/

# Reload nginx
sudo systemctl reload nginx
```

### Verify the Fix
```bash
# This should now work without errors
sudo -u www-data cat ~/rental_prop/static/css/style.css
```

### Why This Happens
- Directory permissions get set to 700 (drwx------) instead of 755 (drwxr-xr-x)
- This prevents nginx (www-data user) from traversing directories to reach static files
- File permissions might be correct (644) but directories are inaccessible

### Prevention
- The sync script now includes this fix automatically
- Always run the sync script after manual file operations
- Check permissions if you manually copy files to the Pi

## Emergency Contact
If this fix doesn't work, check the full troubleshooting guide in:
`windsurf_docs/nginx_permissions_troubleshooting.md`
