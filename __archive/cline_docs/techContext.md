# Technical Context

## Technology Stack
1. **Backend**
   - Python 3.11
   - Flask web framework
   - SQLite database
   - APScheduler for automated tasks

2. **Frontend**
   - HTML5
   - Bootstrap 5.3 CSS framework
   - JavaScript (vanilla)
   - Mobile-responsive design

3. **Deployment**
   - Raspberry Pi 4
   - Nginx reverse proxy
   - Systemd service management
   - Conda environment

## Development Setup
1. **Environment**
   - Conda environment: `movingbox`
   - Python packages managed via requirements.txt
   - VSCode as primary editor
   - Git for version control

2. **Project Structure**
   ```
   moving-db/
   ├── simplified_app.py      # Main application
   ├── schema.sql            # Database schema
   ├── db_migration.py       # Schema migration
   ├── backup.py             # Backup management
   ├── logger.py             # Logging system
   ├── export.py            # Data export
   ├── static/              # Static assets
   │   ├── css/
   │   └── js/
   ├── templates/           # HTML templates
   ├── backups/            # Database backups
   └── logs/               # Application logs
   ```

3. **Database Schema**
   - boxes table (main data)
   - box_history table (change tracking)
   - categories table (box categorization)
   - alembic_version table (migration tracking)

## Technical Constraints
1. **Hardware**
   - Must run on Raspberry Pi 4
   - Limited memory and CPU
   - Network accessible at 192.168.10.10

2. **Software**
   - Python 3.9+ requirement
   - SQLite limitations (single-writer)
   - Conda environment dependencies
   - Nginx configuration

3. **Development**
   - Local to Pi synchronization required
   - Manual service management
   - Database backup coordination
   - Schema migration handling

## Dependencies
1. **Python Packages**
   - Flask: Web framework
   - APScheduler: Task scheduling
   - SQLite3: Database
   - ReportLab: PDF generation
   - Additional packages in requirements.txt

2. **System Requirements**
   - Nginx
   - Systemd
   - Conda
   - SQLite3

3. **Development Tools**
   - sync_to_pi.sh: Deployment script
   - sync_from_pi.sh: Backup script
   - setup_raspberry_pi.sh: Setup script
   - insert-variables.sh: Config tool

## Tool Usage Patterns
1. **Development Workflow**
   ```bash
   # Make changes locally
   # Test changes
   ./sync_to_pi.sh  # Deploy to Pi
   # Verify on Pi
   ./sync_from_pi.sh  # Backup if needed
   ```

2. **Database Management**
   ```python
   # Backup database
   python backup.py backup
   
   # Restore database
   python backup.py restore
   
   # List backups
   python backup.py list
   ```

3. **Service Management**
   ```bash
   # Restart service
   sudo systemctl restart moving_boxes.service
   
   # Check status
   sudo systemctl status moving_boxes.service
   
   # View logs
   sudo journalctl -u moving_boxes.service
   ```

## Security Considerations
1. **Data Protection**
   - Daily automated backups
   - Backup rotation (max 20 copies)
   - Transaction-based operations
   - Safe schema migrations

2. **Access Control**
   - Local network only
   - No authentication (yet)
   - Nginx as reverse proxy
   - Limited port exposure

3. **Error Handling**
   - Structured logging
   - Transaction rollbacks
   - Migration safety checks
   - Service auto-restart

## Performance Patterns
1. **Database**
   - Indexed fields:
     - box_number
     - category_id
     - box_history_box_id
   - Pagination (50 items/page)
   - Soft deletes
   - Query optimization

2. **Application**
   - Connection pooling
   - Template caching
   - Static file serving
   - Efficient queries

3. **Frontend**
   - Minimal JavaScript
   - Bootstrap optimization
   - Mobile responsiveness
   - Efficient DOM updates

## Monitoring & Maintenance
1. **Logging**
   - Application events
   - Request/response tracking
   - Error logging
   - Service status

2. **Backup System**
   - Daily automated backups
   - Manual backup option
   - Backup rotation
   - Restore capability

3. **Health Checks**
   - Service monitoring
   - Database integrity
   - Backup verification
   - Schema validation
