# Stable Release 2025-07-02

## Overview

This document details the stable release of the Moving Box Tracker application dated July 2, 2025. This release includes significant improvements to the category search filter user experience and comprehensive permission fixes for static and template files.

## Release Information

- **Branch Name**: `stable/2025-07-02`
- **Based On**: `stable/2025-06-17`
- **Merged Features**: `fix/category-modal-and-dropdown-ux`

## Key Features and Improvements

### 1. Enhanced Category Search Filter

The category dropdown search filter has been completely redesigned to improve usability, especially when creating multiple boxes in the same category:

- **Persistent Filtering**: Filter remains active until explicitly cleared
- **Clear Button**: Added a dedicated button to reset the filter
- **Visual Feedback**: Shows the number of matching categories
- **Hidden Non-Matches**: Non-matching categories are completely hidden
- **User Instructions**: Added clear instructions explaining how to use the filter

See [Category Search Filter Implementation](./category-search-filter-implementation.md) for detailed documentation.

### 2. Comprehensive Permission Fixes

The sync script has been upgraded to version 2.6 with significant improvements to file permission handling:

- **Extended Coverage**: Now fixes permissions for both static AND templates directories
- **Correct Permissions**: Sets directory permissions to 755 and file permissions to 644
- **Ownership Management**: Applies correct ownership (smashimo:www-data)
- **Verification**: Added thorough checks for directory and file permissions
- **Error Reporting**: Provides detailed error messages if permission issues are detected

See [Permission Fixes in Sync Script](./permission-fixes-sync-script.md) for detailed documentation.

## Testing Performed

1. **Category Search Filter**:
   - Tested on both desktop and mobile devices
   - Verified filter persistence between box submissions
   - Confirmed clear button functionality
   - Validated visual feedback and instructions

2. **Permission Fixes**:
   - Deployed to Raspberry Pi using sync script
   - Verified permissions on static and template files
   - Confirmed access through both direct IP and Nginx domain
   - Validated that 403 Forbidden errors no longer occur

## Known Issues

No known issues in this release.

## Deployment Instructions

1. Switch to the stable branch:
   ```bash
   git checkout stable/2025-07-02
   ```

2. Deploy to Raspberry Pi using the sync script:
   ```bash
   ./sync_to_pi.sh
   ```

3. Verify the application is accessible at:
   - Direct IP: http://192.168.10.10:5001
   - Nginx domain: http://moving.box

## Future Improvements

1. **Category Search Filter**:
   - Add keyboard navigation for the dropdown
   - Implement fuzzy search for more forgiving matching
   - Remember recent filters for quick access

2. **Permission Management**:
   - Add a dedicated permission verification command
   - Implement automatic permission recovery if issues are detected

## Contributors

- Scott (User)
- Windsurf (AI Assistant)
