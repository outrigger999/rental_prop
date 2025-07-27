# Permission Fixes in Sync Script

## Overview

This document details the comprehensive permission fixes implemented in the sync script (`sync_to_pi.sh`) for the Moving Box Tracker application. The improvements ensure that both static and template files have the correct permissions to be served by Nginx without 403 Forbidden errors.

## Background

The application was experiencing recurring 403 Forbidden errors when accessing static files (CSS/JS) and templates through the Nginx domain (`moving.box`), while direct access via IP address (`192.168.10.10:5001`) worked fine. This indicated permission issues with how files were being served by Nginx.

## Root Causes Identified

1. **Restrictive File Permissions**: Static files had overly restrictive permissions (700) preventing the Nginx user (`www-data`) from reading them.

2. **Template Directory Permissions**: Similar permission issues affected the templates directory.

3. **Parent Directory Traversal**: Parent directories needed execute+read permissions for Nginx to traverse them.

4. **Git Sync Limitations**: Git does not preserve full Unix permissions, only the executable bit, causing permissions to be lost during deployments.

## Solution Implemented

### Sync Script Version 2.6 Changes

1. **Extended Permission Fixes**:
   ```bash
   # Fix directory permissions (755 = rwxr-xr-x) for both static and templates
   find static templates -type d -exec chmod 755 {} \;
   
   # Fix file permissions (644 = rw-r--r--) for both static and templates
   find static templates -type f -exec chmod 644 {} \;
   
   # Fix ownership for both static and templates
   sudo chown -R smashimo:www-data ~/moving_box_tracker/static/ ~/moving_box_tracker/templates/
   sudo chmod -R g+r ~/moving_box_tracker/static/ ~/moving_box_tracker/templates/
   ```

2. **Parent Directory Permissions**:
   ```bash
   # Fix parent directory permissions
   chmod o+rx ~ ~/moving_box_tracker
   ```

3. **Comprehensive Verification**:
   ```bash
   # Verify static directory permissions
   STATIC_DIR_PERMS=$(ls -ld ~/moving_box_tracker/static | awk '{print $1}')
   if [[ "$STATIC_DIR_PERMS" != "drwxr-xr-x"* ]]; then
       echo -e "${RED}[ERROR]${NC} Static directory permissions verification failed!"
       exit 1
   fi
   
   # Check templates directory permissions
   TEMPLATES_DIR_PERMS=$(ls -ld ~/moving_box_tracker/templates | awk '{print $1}')
   if [[ "$TEMPLATES_DIR_PERMS" != "drwxr-xr-x"* ]]; then
       echo -e "${RED}[ERROR]${NC} Templates directory permissions verification failed!"
       exit 1
   fi
   ```

## Key Benefits

1. **Permanent Solution**: Permissions are fixed automatically with every deployment.

2. **Comprehensive Coverage**: Both static and template files are properly handled.

3. **Verification**: Thorough checks ensure permissions are correctly set.

4. **Error Reporting**: Detailed error messages if permission issues are detected.

## Permission Requirements Summary

| Item | Required Permission | Ownership | Purpose |
|------|---------------------|-----------|--------|
| Directories | 755 (rwxr-xr-x) | smashimo:www-data | Allow Nginx to traverse directories |
| Files | 644 (rw-r--r--) | smashimo:www-data | Allow Nginx to read files |
| Parent Dirs | o+rx | smashimo:smashimo | Allow Nginx to traverse to target directories |

## Best Practices

1. **Always Use the Sync Script**: The sync script now handles all permission issues automatically.

2. **Avoid Manual Permission Changes**: Let the script handle permissions to ensure consistency.

3. **Check Logs**: If 403 errors occur, check the sync script logs for permission verification failures.

## Conclusion

The permission fixes in sync script version 2.6 provide a robust, permanent solution to the 403 Forbidden errors that were occurring with static and template files. By automatically setting the correct permissions during each deployment, the application now works reliably through both direct IP access and the Nginx domain.
