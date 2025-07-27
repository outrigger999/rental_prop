# Codebase Summary - Rental Property Tracker

## Project Structure

### Key Components and Their Interactions

#### Core Application Files
- **`app.py`** - Main Flask application with routes and database operations
- **`rental_properties.db`** - SQLite database storing property information
- **`requirements.txt`** - Python dependencies (Flask, basic requirements)
- **`sync_to_pi.sh`** - Deployment script (currently has syntax errors)

#### Configuration Files
- **`rental_prop.service`** - Systemd service configuration for Pi deployment
- **`nginx.conf`** - Web server configuration (if using nginx proxy)
- **`.env`** - Environment variables and configuration

#### Templates and Static Files
- **`templates/`** - Jinja2 HTML templates for web interface
- **`static/`** - CSS, JavaScript, and uploaded images
- **`static/uploads/`** - User-uploaded property images

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

### System Dependencies
- **Git** - Version control and deployment mechanism
- **SSH** - Remote access to Raspberry Pi
- **rsync** - File synchronization for database/uploads
- **systemd** - Service management on Pi

### Planned Integrations
- **Google Maps API** - Route visualization and commute analysis (Phase 2)

## Recent Significant Changes

### Issues Identified
1. **Sync Script Problems** - Current `sync_to_pi.sh` has syntax errors preventing deployment
2. **Browser Access Issue** - Flask app not accessible from network (host binding problem)
3. **Git Workflow** - Need to establish proper branching and deployment via Git

### Documentation Creation
- Established `windsurf_docs/` structure per custom instructions
- Created comprehensive project context documentation
- Identified working sync script in `__archive/` for reference

## User Feedback Integration and Development Impact

### Current Development Focus
Based on user requirements and project analysis:
- **Priority 1:** Fix browser accessibility (Flask host binding)
- **Priority 2:** Create working sync script based on archive version
- **Priority 3:** Establish Git-based deployment workflow
- **Priority 4:** Complete MVP functionality testing

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
