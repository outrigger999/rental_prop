# Duplicate Categories Prevention

## Issue
The system was allowing duplicate categories to be added with the same name. For example, there were two instances of "Scott's Office" category in the database. One was associated with 4 boxes and the other with 1 box. This created confusion and made it impossible to delete one of the duplicates since it was marked as being used by boxes.

## Solution
We implemented a two-part solution to address this issue:

### 1. Database Restoration
- Created a backup of the problematic database (`moving_boxes.db.dupe_categories_backup`)
- Restored a database from May 28th that was free of duplicate categories

### 2. Duplicate Prevention Implementation
- **Server-side validation**: Enhanced the `api_add_category` function in `simplified_app.py` to use **case-insensitive** comparison when checking for duplicate categories
- **Client-side validation**: Updated the JavaScript in `main.js` to check for existing categories before adding new ones
- **Cleanup script**: Created `fix_duplicate_categories.py` as a utility to detect and merge duplicate categories if they appear in the future

## Technical Details

### Server-side Implementation
The category name check now uses SQLite's `COLLATE NOCASE` to ensure case-insensitive comparison:

```python
# Check for duplicate (case insensitive)
cur.execute('SELECT id, name FROM categories WHERE name COLLATE NOCASE = ?', (name,))
```

### Client-side Implementation
When adding a new category via the Quick Add button, the JavaScript now:
1. Checks all existing categories in the dropdown
2. Performs a case-insensitive comparison
3. If a match is found, selects the existing category instead of adding a duplicate
4. Alerts the user that the category already exists

### Cleanup Script
The `fix_duplicate_categories.py` script:
- Identifies categories with identical names (case-insensitive)
- Keeps the category with the lowest ID
- Updates all boxes using duplicate categories to reference the kept category
- Removes the redundant categories

## Testing
The solution was tested by:
1. Restoring a clean database backup
2. Attempting to add a duplicate category both through the UI and API
3. Verifying that duplicates were properly rejected

## Branch Information
- **Branch**: fix/duplicate-categories
- **Created From**: stable/2025-05-28
- **Files Modified**: 
  - simplified_app.py
  - static/js/main.js
- **Files Added**:
  - fix_duplicate_categories.py
  - windsurf_docs/duplicate-categories-prevention.md

## Future Considerations
- Consider adding a database constraint or trigger to further prevent duplicates
- Add validation when importing categories from external sources
- Implement a periodic database integrity check to detect and fix issues
