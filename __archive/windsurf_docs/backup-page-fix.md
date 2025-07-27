# Backup Page Fix

## Problem

The backup page in the Moving Box Tracker application was returning a 500 Internal Server Error when accessed. This was preventing users from managing database backups, which is an important maintenance feature.

## Root Cause

After investigating the code, we identified that the backup page was referencing a non-existent function called `purge_deleted_data`. This function had been intentionally removed from the application, as indicated by a comment in the code:

```python
# Removed purge_deleted_data function since we now use hard deletes
```

However, the template still contained:
1. A form that attempted to submit to this non-existent route
2. JavaScript code that tried to manipulate a hidden UI element for this feature
3. Event handlers that attempted to show/hide the purge button based on Alt/Option key presses

When the page tried to render, it couldn't find the `purge_deleted_data` route, causing the internal server error.

## Solution

We fixed the issue by:

1. **Removing the Purge Form**: Removed the HTML form that was trying to submit to the non-existent route, replacing it with a comment explaining that the functionality has been removed.

```html
<!-- Purge deleted data functionality removed as the app now uses hard deletes -->
```

2. **Removing Related JavaScript**: Eliminated all JavaScript code related to the purge functionality:
   - Removed the `confirmPurge()` function that was used for confirmation dialogs
   - Removed event listeners for Alt/Option key that would show/hide the purge button
   - Removed references to the non-existent DOM element

3. **Maintaining Template Structure**: Ensured that other JavaScript functionality in the template continues to work correctly by fixing the DOMContentLoaded event handler structure.

## Testing Performed

The fix was tested by:
1. Accessing the backup page via the web interface
2. Verifying that the page loads without errors
3. Confirming that the remaining backup functionality works correctly:
   - Viewing existing backups
   - Running manual backups
   - Updating the max backups setting

## Technical Approach

This fix followed the principle of removing dead code rather than trying to reimplement missing functionality. Since the application had intentionally moved from soft deletes to hard deletes, the purge functionality was no longer needed.

## Implementation Details

### Changes to backup.html

1. **Removed HTML form**: 
```html
<div id="purgeButtonContainer" style="display: none;">
    <form action="{{ url_for('purge_deleted_data') }}" method="POST" onsubmit="return confirmPurge()">
        <button type="submit" id="purgeDataBtn" class="btn btn-warning">Purge Soft-Deleted Data</button>
    </form>
</div>
```

2. **Removed JavaScript functions and event handlers**:
```javascript
function confirmPurge() {
    return confirm('WARNING: This will permanently delete all soft-deleted boxes and their history from the database. This action cannot be undone. Are you sure you want to continue?');
}

// Option key handling for purge button
document.addEventListener('DOMContentLoaded', function() {
    const purgeButtonContainer = document.getElementById('purgeButtonContainer');
    
    document.addEventListener('keydown', function(event) {
        // The Option key on Mac is detected as 'Alt' in JavaScript
        if (event.altKey) {
            if (purgeButtonContainer) purgeButtonContainer.style.display = 'block';
        }
    });
    
    document.addEventListener('keyup', function(event) {
        // Check if Alt key is not pressed
        if (!event.altKey) {
            if (purgeButtonContainer) purgeButtonContainer.style.display = 'none';
        }
    });
});
```

3. **Fixed JavaScript structure**: Ensured the remaining event handlers work correctly.

## Future Considerations

1. **Documentation Update**: Consider updating user documentation to reflect that the application now uses hard deletes exclusively.
2. **Code Cleanup**: A more thorough code review might reveal other references to removed functionality that should be cleaned up.

## Branch Information

This fix was implemented in the `fix/backup-page-error` branch, based on the stable `stable/2025-05-28` branch.
