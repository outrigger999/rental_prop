# Codebase Summary - Rental Property Tracker

## Project Structure

### Key Components and Their Interactions

#### Core Application Files
- **`app.py`** - Main Flask application with routes and database operations, including search and export functionality
- **`rental_properties.db`** - SQLite database storing property information
- **`requirements.txt`** - Python dependencies (Flask, gunicorn, Werkzeug)
- **`sync_to_pi.sh`** - Working Git-based deployment script

#### Configuration Files
- **`rental_prop.service`** - Systemd service configuration for Pi deployment
- **`nginx.conf`** - Web server configuration (if using nginx proxy)
- **`.env`** - Environment variables and configuration

#### Templates and Static Files
- **`templates/`** - Jinja2 HTML templates for web interface
  - **`index.html`** - Main page with property listings and search functionality
  - **`add_property.html`** - Form for adding new rental properties
  - **`export.html`** - Data export and backup options
- **`static/`** - CSS, JavaScript, and uploaded images
  - **`css/style.css`** - Styling for all pages, including search and export features
- **`static/uploads/`** - User-uploaded property images

#### User Instructions
- **`userInstructions/`** - Documentation for users
  - **`git_workflow_and_deployment.md`** - Git and deployment workflow
  - **`feature_guide.md`** - Guide to using all application features

#### Documentation and Context
- **`windsurf_docs/`** - Project documentation (this directory)
- **JSON Context Files** - 7 files containing comprehensive project context
- **`__archive/`** - Previous project files including working sync script

## Data Flow

### Property Management Flow
1. User accesses web interface via Flask routes
2. Property data entered through HTML forms
3. Flask processes form data and validates input
4. Data stored in SQLite database via parameterized queries
5. Property listings retrieved and displayed via Jinja2 templates

### Search Flow
1. User enters search criteria in the search form on the index page
2. Form submitted via GET request to the /search route
3. Flask builds a dynamic SQL query based on search parameters
4. Filtered results retrieved from database and displayed
5. Search parameters preserved in form fields for refinement

### Export Flow
1. User accesses export page via "Export Data" button
2. User selects desired export format (CSV or JSON)
3. Flask retrieves all property data from database
4. Data formatted according to selected format
5. File generated with timestamp and sent as downloadable attachment

### Deployment Flow
1. Code changes committed to Git repository
2. Sync script pulls latest changes to Raspberry Pi
3. Service restarted to apply changes
4. Database and uploads synchronized bidirectionally

## External Dependencies

### Python Packages
- **Flask** - Web framework for routes and templating
- **sqlite3** - Database operations (built into Python)
- **os** - File system operations for uploads
- **csv** - CSV file generation for data export
- **json** - JSON data formatting for export
- **io** - In-memory file operations for exports
- **datetime** - Timestamp generation for export filenames
- **gunicorn** - WSGI HTTP server for production deployment

### System Dependencies
- **Git** - Version control and deployment mechanism
- **SSH** - Remote access to Raspberry Pi
- **rsync** - File synchronization for database/uploads
- **systemd** - Service management on Pi

### Planned Integrations
- **Google Maps API** - Route visualization and commute analysis (Phase 2)

## Recent Significant Changes

### Issues Resolved
1. **Sync Script Problems** - Replaced broken script with working version based on archive

### Phase 2 Feature Implementation (Completed) 
- **Enhanced Add Property Page**: Image upload functionality with property and map image support
- **Advanced Search System**: Comprehensive filtering with multiple criteria
- **Data Export Features**: CSV and JSON export capabilities with backup functionality
- **UI/UX Improvements**: Enhanced styling and user experience across all pages
- **Database Schema Updates**: Added image path columns and source URL tracking
- **File Upload Management**: Organized uploads into categorized subfolders

### Deployment and Infrastructure (Bulletproof) 
- **Git-Based Deployment**: Established proper version control workflow with mandatory commit-first process
- **Sync Script Enhancement**: Updated `sync_to_pi_working.sh` for reliable Pi deployment
- **Permission Management**: Automated static file permission handling (prevents 403 errors)
- **Service Configuration**: Proper systemd service setup for production
- **SSH Configuration**: Documented and implemented proper SSH host alias setup

### Comprehensive Documentation (Complete) 
- **Project Template Guide**: Complete guide to clone projects without deployment issues
- **Sync Strategies**: Git-first workflow documentation with troubleshooting
- **User Instructions**: Comprehensive feature guides created
- **Technical Documentation**: Complete windsurf_docs structure established
- **Troubleshooting Guides**: Solutions for all encountered deployment issues

## User Feedback Integration and Development Impact

### Current Development Focus
Based on user requirements and project analysis:
- **Priority 1:** User testing of search and export features
- **Priority 2:** Refinement based on user feedback
- **Priority 3:** Planning for Phase 3 features
- **Priority 4:** Performance optimization for Raspberry Pi environment

### Development Workflow Requirements
- All changes must be committed to Git
- Use feature branches for any modifications
- Deploy via Git pull on Pi (no direct file transfers)
- Maintain regular memory updates for project context

## Database Schema

### Properties Table
```sql
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_type TEXT NOT NULL,
    address TEXT NOT NULL,
    price REAL NOT NULL,
    sq_ft INTEGER,
    cat_friendly INTEGER,
    num_bedrooms INTEGER,
    air_conditioning INTEGER,
    parking_type TEXT,
    commute_morning TEXT,
    commute_midday TEXT,
    commute_evening TEXT
);
```

## Critical Next Steps
1. Fix Flask app host binding in `app.py`
2. Rewrite `sync_to_pi.sh` based on working archive version
3. Test complete deployment workflow
4. Verify browser accessibility from network devices
5. Document user instructions for ongoing development
