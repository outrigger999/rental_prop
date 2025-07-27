# Codebase Summary

## Key Components and Their Interactions
### Sync Scripts
- `sync_to_pi.sh`: Handles file synchronization from Mac to Raspberry Pi
- `sync_from_pi_periodic.py`: Handles periodic sync from Pi to Mac

### Data Processing
- Python scripts for migration, export, and backup (e.g., `migrate_categories.py`, `export.py`, `simplified_app.py`)
- Database management scripts (e.g., `fix_box_categories.py`, `fix_duplicate_categories.py`)

### Web Application
- Main application: `simplified_app.py` - Flask web application with API endpoints and database functions
- Static files in `static/` (CSS, JS)
- HTML templates in `templates/` (e.g., `categories.html`, `list_boxes.html`)

## Data Flow
- Project files are maintained on Mac and synchronized to Raspberry Pi using shell and Python scripts.
- Data is processed and exported using Python scripts, with outputs stored in `exports/` or `data/`.

## External Dependencies
- **rsync**: Used in shell scripts for efficient file transfer
- **Python 3.x**: Required for all Python scripts
- **Git**: For version control

## Recent Significant Changes
- **2025-05-30**: Fixed category management issues in the moving box tracker application:
  - Updated frontend code to properly handle error messages for duplicate categories
  - Created testing instructions in `userInstructions/sync_and_test_category_fixes.md`
- Documentation system (`roocode_docs`) initialized for project context and workflow management

## User Feedback Integration and Its Impact on Development
- User feedback led to correction of sync paths and improved documentation practices
- User feedback about category management issues led to improvements in error handling and user experience
- Ongoing: Documentation and workflow will be updated as new feedback is received

## Additional Reference Documents
- None yet. Future documents (e.g., styleAesthetic.md, wireframes.md) will be listed here.
