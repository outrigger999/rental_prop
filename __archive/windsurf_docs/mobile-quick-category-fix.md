# Mobile Quick Category Button Fix and Permission Handling

## Overview
This document describes the fix for the quick category button on mobile devices and improvements to permission handling for static files in the Moving Box Tracker application.

## Issues Fixed
1. **Mobile Quick Category Button**: The quick category button was not working properly on mobile devices while working fine on desktop browsers
2. **Recurring 403 Forbidden Errors**: Static files (CSS/JS) were periodically experiencing 403 Forbidden errors

## Root Causes

### Mobile Button Issue
The button target area was too small for reliable touch input on mobile devices. Mobile browsers have different touch handling behaviors compared to desktop click events, requiring larger touch targets.

### Permission Issues
Git does not preserve full Unix permissions during syncing, only the executable bit. This means that when files are updated through Git operations, their permissions may revert to restrictive defaults (700) which Nginx cannot read.

## Solutions Implemented

### Quick Category Button Fix
Enhanced mobile support in `static/js/main.js`:
```javascript
// Make the button easier to tap on mobile
if (window.innerWidth <= 768) { // Mobile view
    quickAddCategoryBtn.style.height = '38px';
    quickAddCategoryBtn.style.padding = '6px 12px';
}
```

This approach:
- Only applies on mobile screen sizes (≤768px width)
- Increases button height and padding for better touch targets
- Preserves the original button behavior on desktop

### Permission Handling Improvements
1. **Separated Concerns**: Removed permission handling from sync_to_pi.sh (v2.1)
2. **Created Dedicated Scripts**:
   - `fix_pi_permissions.sh`: Run from Mac to fix permissions on Pi
   - `fix_pi_permissions_local.sh`: Run directly on Pi to fix permissions locally

The permission scripts ensure:
- Static directories have 755 permissions
- Static files have 644 permissions
- Proper ownership (user:www-data) for Nginx access
- Parent directories have execute+read permissions (o+rx)

## New Deployment Workflow
1. Use `sync_to_pi.sh` to deploy code changes
2. If 403 Forbidden errors occur, run `fix_pi_permissions.sh` to reset permissions

## Technical Notes
- Permission requirements for Nginx:
  - Static files: 644 (rw-r--r--)
  - Directories: 755 (rwxr-xr-x)
  - Parent directories: At least o+rx (--x--x--x)
  
- Git only preserves the executable bit, not full Unix permissions
- The Mac OS extended attributes (@) can sometimes interfere with permission handling

## Branch Information
This fix was implemented in the `fix/quick-category-mobile` branch.
