# Moving Box Tracker

A simple application for tracking moving boxes, their contents, and locations. Designed to be easy to use, mobile-friendly, and deployable on a Raspberry Pi.

## Features

- Create and track boxes with unique numbers
- Assign priority levels and categories to each box
- Search and filter boxes by various criteria
- Responsive design that works on mobile devices
- Simple, lightweight Flask implementation
- Automatic handling of concurrent users creating boxes simultaneously
- Database backup and restoration functionality
- Complete database clearing for testing purposes
- User warning system for box number reservation
- Hidden admin functions for data management

## Technology Stack

- **Backend**: Flask, SQLite
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite (standard library)
- **PDF Export**: ReportLab library

## Project Structure

```
/
├── simplified_app.py     # Main application file with all routes and logic
├── schema.sql            # Database schema for SQLite
├── requirements.txt      # Simple dependency list
├── moving_boxes.db       # SQLite database
├── export.py             # Module for data export functionality
├── logger.py             # Logging utilities
├── backups/              # Directory for database backups
├── static/               # Static assets
│   ├── css/              # CSS stylesheets
│   └── js/               # JavaScript files
└── templates/            # HTML templates
    ├── base.html         # Base template with layout
    ├── create.html       # Form for creating/editing boxes
    ├── list.html         # List of boxes with filters
    ├── search.html       # Advanced search page
    ├── backup.html       # Backup management page
    └── export.html       # Data export options
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/outrigger999/moving-box-tracker.git
   cd moving-box-tracker
   ```

2. Set up Python environment (3.7+):

   **Option A: Using Conda (Recommended)**
   ```bash
   # Create a new conda environment
   conda create -n movingbox python=3.11
   
   # Activate the environment
   conda activate movingbox
   ```

   **Option B: Using pip/venv**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

3. Install dependencies:

   **With Conda environment active:**
   ```bash
   pip install -r requirements.txt
   ```

   **With pip/venv:**
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database (first run only):
   ```bash
   python -c "from simplified_app import app, init_db; init_db()"
   ```

5. Run the application:
   ```bash
   python simplified_app.py
   ```

6. Access the application at http://127.0.0.1:5000

**Note**: Remember to activate your conda environment (`conda activate movingbox`) each time you work on the project.

## Development Workflow

This project uses a branching workflow for safe feature development. See `DEVELOPMENT_WORKFLOW.md` for detailed instructions on:
- Creating feature branches
- Safe development practices  
- Merging changes back to main
- Best practices and examples

## Deployment on Raspberry Pi

For deployment on a Raspberry Pi, consider using:

1. Nginx as a reverse proxy
2. Systemd for process management
3. Gunicorn as a production WSGI server

Example systemd service file is included (`moving_boxes.service`).

## Advanced Features

### Backup and Restoration

The application includes a complete backup system:

1. **Automated Daily Backups**: The system automatically creates database backups daily
2. **Manual Backups**: Users can trigger manual backups from the backup management page
3. **Configurable Backup Retention**: Users can set the number of backups to retain (1-50) directly from the backup page
   - When set to 1: Each new backup replaces the previous one
   - When set to multiple: The system maintains the specified number of most recent backups
4. **Confirmation Dialogs**: Prevents accidental changes to critical backup settings
5. **Restoration**: Easy database restoration by replacing the current database file with a backup

To restore from backup:
1. Download the desired backup file from the backup management page
2. Stop the application
3. Rename the downloaded backup file to `moving_boxes.db`
4. Replace the current database file with the renamed backup
5. Restart the application

### Concurrent User Handling

The application automatically handles race conditions when multiple users are creating boxes simultaneously:

1. If two users attempt to create a box with the same number at the same time, the system automatically assigns the next available number to the second user
2. Users are notified if their box number was changed due to a concurrent creation
3. Form data is preserved, ensuring a smooth user experience
4. Clear UI warnings inform users that box numbers aren't reserved until the "Create Box" button is clicked

### Box Number Reservation System

To prevent mismatched box numbers between physical boxes and database records:

1. **Warning System**: Clear alerts on the create box form explain that box numbers aren't reserved until submission
2. **User Guidance**: Instructions advise users to complete the form before labeling physical boxes
3. **Automatic Reassignment**: If a box number is claimed by another user while a form is open, the system automatically assigns the next available number

### Testing and Administration Utilities

For testing and administration purposes, the application includes:

1. **Database Clearing**: Completely remove all boxes and history records (Option key to access)
2. **Soft-Deleted Data Purging**: Remove any soft-deleted boxes that may be cluttering the database (Option key to access)
3. **Administrative Functions**: Hidden behind keyboard modifiers for security

### Sync Script Features

The application includes a robust sync script for deployment to Raspberry Pi:

1. **Dependency Management**: Automatically checks and installs updated dependencies
2. **Service Management**: Properly stops and starts the service during updates
3. **Process Handling**: Ensures clean process termination during updates
4. **Fallback Mechanism**: Alternative startup method if systemd service fails
5. **Status Reporting**: Clear, color-coded status indicators during sync process

## Potential Future Improvements

Several potential improvements have been identified:

1. **Optimistic Concurrency Control**: Could be implemented for editing operations
2. **Deletion Safeguards**: Additional checks to prevent editing deleted boxes
3. **Transaction Management**: More explicit transaction boundaries for complex operations

## License

MIT License
