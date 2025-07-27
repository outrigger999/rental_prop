#!/usr/bin/env python3
"""
Moving Box Tracker - Version 1.1 - Fixed for Categories Schema
================================

Updated to work with the migrated database schema that uses:
- categories table for category management  
- category_id foreign key in boxes table
- category_old for backward compatibility

Features:
- Dynamic category management
- Mobile-friendly category addition
- Safe category deletion with usage protection
- All existing functionality preserved
"""

import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, g, jsonify, send_file, flash, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
import shutil
import atexit
import csv
import json

# Import custom modules
import logger
import export

# Configuration
DATABASE = 'moving_boxes.db'
DEBUG = True
SECRET_KEY = os.urandom(24)

# Constants
DATA_FILE = Path('data/box_data.json')
BACKUP_CONFIG_FILE = Path('backup_config.json')

# Load backup configuration
def load_backup_config():
    """Load backup configuration from backup_config.json"""
    try:
        if BACKUP_CONFIG_FILE.exists():
            with open(BACKUP_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        else:
            # Default configuration if file doesn't exist
            config = {
                "backup_directory": "backups",
                "max_backups": 20,
                "database_path": DATABASE,
                "auto_backup": True,
                "backup_interval": 86400,  # 1 day in seconds
                "last_backup": datetime.now().isoformat()
            }
            # Save default config
            with open(BACKUP_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            return config
    except Exception as e:
        app.logger.error(f"Error loading backup configuration: {e}")
        # Fallback to defaults
        return {
            "backup_directory": "backups",
            "max_backups": 20,
            "database_path": DATABASE,
            "auto_backup": True,
            "backup_interval": 86400,
            "last_backup": datetime.now().isoformat()
        }

def update_backup_timestamp():
    """Update the last_backup timestamp in the configuration file"""
    try:
        config = load_backup_config()
        config["last_backup"] = datetime.now().isoformat()
        with open(BACKUP_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error updating backup timestamp: {e}")

# Ensure data directory exists
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

# Ensure backup directory exists
config = load_backup_config()
BACKUP_DIR = Path(config["backup_directory"])
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(__name__)
app.secret_key = SECRET_KEY  # Ensure secret key is set for flash messages

# Initialize logger
logger.info("Starting Moving Box Tracker application")

# Database helper functions
def get_db():
    """Connect to the database and return connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        logger.debug(f"Connected to database: {app.config['DATABASE']}")
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection when app context ends"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        logger.debug("Database connection closed")

def init_db():
    """Initialize the database tables - Updated for migrated schema"""
    db = get_db()
    
    # Create categories table if it doesn't exist
    db.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # The boxes table should already exist with the migrated schema
    # Just ensure box_history exists
    db.execute('''
        CREATE TABLE IF NOT EXISTS box_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            box_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            changes TEXT NOT NULL,
            editor TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            FOREIGN KEY (box_id) REFERENCES boxes (id)
        )
    ''')
    db.commit()

def query_db(query, args=(), one=False):
    """Query the database and return results"""
    logger.debug(f"Executing query: {query} with args: {args}")
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Category management functions
def get_categories():
    """Get all active categories"""
    return query_db('SELECT * FROM categories WHERE is_active = 1 ORDER BY name')

def get_category_by_id(category_id):
    """Get category by ID"""
    return query_db('SELECT * FROM categories WHERE id = ?', [category_id], one=True)

def get_category_by_name(name):
    """Get category by name"""
    return query_db('SELECT * FROM categories WHERE name = ? AND is_active = 1', [name], one=True)

def create_category(name):
    """Create a new category"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO categories (name, created_at) VALUES (?, ?)',
            (name, datetime.now())
        )
        category_id = cursor.lastrowid
        db.commit()
        logger.info(f"Created new category: {name} (ID: {category_id})")
        return category_id
    except sqlite3.IntegrityError:
        logger.warning(f"Category '{name}' already exists")
        return None
    except Exception as e:
        logger.error(f"Error creating category '{name}': {e}")
        return None

def count_boxes_using_category(category_id):
    """Count how many boxes use a specific category"""
    result = query_db('SELECT COUNT(*) FROM boxes WHERE category_id = ? AND is_deleted = 0', [category_id], one=True)
    return result[0] if result else 0

def delete_category(category_id):
    """Delete a category if it's not in use"""
    box_count = count_boxes_using_category(category_id)
    if box_count > 0:
        return False, f"Cannot delete category - {box_count} boxes are using it"
    
    try:
        db = get_db()
        db.execute('UPDATE categories SET is_active = 0 WHERE id = ?', [category_id])
        db.commit()
        logger.info(f"Deactivated category ID: {category_id}")
        return True, "Category deleted successfully"
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}")
        return False, f"Error deleting category: {e}"

def get_box(box_id):
    """Get a single box by ID with category name"""
    return query_db('''
        SELECT b.*, c.name as category_name 
        FROM boxes b 
        LEFT JOIN categories c ON b.category_id = c.id 
        WHERE b.id = ? AND NOT b.is_deleted
    ''', [box_id], one=True)

def get_boxes(skip=0, limit=20, box_number=None, priority=None, category=None, box_size=None, description=None):
    """Get boxes with optional filtering - Updated for new schema"""
    query = '''
        SELECT b.*, c.name as category_name 
        FROM boxes b 
        LEFT JOIN categories c ON b.category_id = c.id 
        WHERE NOT b.is_deleted
    '''
    params = []
    
    if box_number:
        query += ' AND b.box_number = ?'
        params.append(box_number)
    
    if priority:
        query += ' AND b.priority = ?'
        params.append(priority)
    
    if category:
        query += ' AND c.name = ?'
        params.append(category)
        
    if box_size:
        query += ' AND b.box_size = ?'
        params.append(box_size)
        
    if description:
        query += ' AND b.description LIKE ?'
        params.append(f'%{description}%')
    
    query += ' ORDER BY b.box_number LIMIT ? OFFSET ?'
    params.extend([limit, skip])
    
    logger.debug(f"Getting boxes with filters: {params}")
    return query_db(query, params)

def count_boxes(box_number=None, priority=None, category=None, box_size=None, description=None):
    """Count boxes with optional filtering - Updated for new schema"""
    query = '''
        SELECT COUNT(*) 
        FROM boxes b 
        LEFT JOIN categories c ON b.category_id = c.id 
        WHERE NOT b.is_deleted
    '''
    params = []
    
    if box_number:
        query += ' AND b.box_number = ?'
        params.append(box_number)
    
    if priority:
        query += ' AND b.priority = ?'
        params.append(priority)
    
    if category:
        query += ' AND c.name = ?'
        params.append(category)
        
    if box_size:
        query += ' AND b.box_size = ?'
        params.append(box_size)
        
    if description:
        query += ' AND b.description LIKE ?'
        params.append(f'%{description}%')
    
    result = query_db(query, params, one=True)
    return result[0] if result else 0

def get_next_box_number():
    """Get the next available box number"""
    db = get_db()
    with db:  # Start a transaction
        try:
            # Get the highest box number currently in use
            result = query_db('SELECT MAX(box_number) as max_num FROM boxes WHERE is_deleted = 0', one=True)
            current_max = result['max_num'] if result['max_num'] is not None else 0
            
            # Get all box numbers in use
            used_numbers = set(row['box_number'] for row in query_db('SELECT box_number FROM boxes WHERE is_deleted = 0'))
            
            # Debug information
            logger.info(f"Next box number calculation - Current max: {current_max}, Used numbers: {used_numbers}")
            
            # Find the first gap in the sequence
            next_number = 1
            while next_number in used_numbers:
                next_number += 1
            
            logger.info(f"Next box number selected: {next_number}")
            return next_number
            
        except Exception as e:
            logger.error(f"Error getting next box number: {str(e)}")
            raise

def create_box(priority, category_name, box_size, description, editor):
    """Create a new box - Updated for new schema"""
    db = get_db()
    with db:  # Start a transaction
        try:
            box_number = get_next_box_number()
            cursor = db.cursor()
            
            # Get or create category
            category = get_category_by_name(category_name)
            if not category:
                category_id = create_category(category_name)
                if not category_id:
                    raise ValueError(f"Could not create category: {category_name}")
            else:
                category_id = category['id']
            
            # Debug: log all boxes in the database
            all_boxes = query_db('SELECT id, box_number, is_deleted FROM boxes', [])
            logger.info(f"All boxes in database before creating new box: {[dict(row) for row in all_boxes]}")
            
            # Double-check the box number isn't in use
            existing = cursor.execute('SELECT 1 FROM boxes WHERE box_number = ? AND is_deleted = 0', [box_number]).fetchone()
            if existing:
                raise ValueError(f"Box number {box_number} is already in use")
            
            cursor.execute(
                '''INSERT INTO boxes (box_number, priority, category_id, box_size, description, created_at, last_modified, is_deleted) 
                   VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'), 0)''',
                (box_number, priority, category_id, box_size, description)
            )
            box_id = cursor.lastrowid
            
            # Add history record
            changes = f"Created box #{box_number}"
            cursor.execute(
                'INSERT INTO box_history (box_id, action, changes, editor, timestamp) VALUES (?, ?, ?, ?, datetime("now"))',
                (box_id, 'create', changes, editor)
            )
            
            logger.info(f"Box #{box_number} created successfully with ID: {box_id}")
            return box_id
            
        except Exception as e:
            logger.error(f"Error creating box: {str(e)}")
            raise

def update_box(box_id, priority, category_name, box_size, description, editor):
    """Update an existing box - Updated for new schema"""
    box = get_box(box_id)
    if not box:
        logger.warning(f"Attempted to update non-existent box with ID: {box_id}")
        return None
    
    logger.info(f"Updating box #{box['box_number']} (ID: {box_id})")
    
    # Get or create category
    category = get_category_by_name(category_name)
    if not category:
        category_id = create_category(category_name)
        if not category_id:
            raise ValueError(f"Could not create category: {category_name}")
    else:
        category_id = category['id']
    
    changes = []
    if box['priority'] != priority:
        changes.append(f"Priority: {box['priority']} -> {priority}")
    if box['category_name'] != category_name:
        changes.append(f"Category: {box['category_name']} -> {category_name}")
    if box['box_size'] != box_size:
        changes.append(f"Size: {box['box_size']} -> {box_size}")
    if box['description'] != description:
        changes.append(f"Description updated")
    
    now = datetime.now()
    
    db = get_db()
    
    # Update box
    db.execute(
        'UPDATE boxes SET priority = ?, category_id = ?, box_size = ?, description = ?, last_modified = ? WHERE id = ?',
        (priority, category_id, box_size, description, now, box_id)
    )
    
    # Add history record if there were changes
    if changes:
        db.execute(
            'INSERT INTO box_history (box_id, action, changes, editor, timestamp) VALUES (?, ?, ?, ?, ?)',
            (box_id, 'update', '\n'.join(changes), editor, now)
        )
        logger.info(f"Box #{box['box_number']} updated with changes: {changes}")
    else:
        logger.info(f"Box #{box['box_number']} updated (no changes detected)")
    
    db.commit()
    return box_id

def delete_box(box_id, editor):
    """Soft delete a box"""
    box = get_box(box_id)
    if not box:
        logger.warning(f"Attempted to delete non-existent box with ID: {box_id}")
        return False
    
    logger.info(f"Deleting box #{box['box_number']} (ID: {box_id})")
    
    now = datetime.now()
    db = get_db()
    
    # Soft delete the box
    db.execute('UPDATE boxes SET is_deleted = ?, last_modified = ? WHERE id = ?', (True, now, box_id))
    
    # Add history record
    db.execute(
        'INSERT INTO box_history (box_id, action, changes, editor, timestamp) VALUES (?, ?, ?, ?, ?)',
        (box_id, 'delete', f"Deleted box #{box['box_number']}", editor, now)
    )
    
    db.commit()
    logger.info(f"Box #{box['box_number']} deleted successfully")
    return True

def get_box_history(box_id):
    """Get history for a box"""
    logger.debug(f"Getting history for box ID: {box_id}")
    return query_db('SELECT * FROM box_history WHERE box_id = ? ORDER BY timestamp DESC', [box_id])

def get_priority_color(priority):
    """Return Bootstrap color class based on priority"""
    priority_colors = {
        "Priority 1": "danger",
        "Priority 2": "warning",
        "Important": "primary",
        "Store": "success"
    }
    return priority_colors.get(priority, "secondary")

def get_recent_boxes(limit=5):
    """Get recently created boxes - Updated for new schema"""
    return query_db('''
        SELECT b.*, c.name as category_name 
        FROM boxes b 
        LEFT JOIN categories c ON b.category_id = c.id 
        WHERE b.is_deleted = 0 
        ORDER BY b.created_at DESC 
        LIMIT ?
    ''', [limit])

# Ensure the database is initialized
with app.app_context():
    init_db()

# Backup functions (unchanged)
def get_last_backup_time():
    """Gets the timestamp of the last successful backup from config."""
    try:
        config = load_backup_config()
        last_backup_str = config.get("last_backup")
        if last_backup_str:
            return datetime.fromisoformat(last_backup_str)
        return None
    except Exception as e:
        app.logger.error(f"Error reading last backup time: {e}")
        return None

def run_simple_backup(manual_trigger=False):
    """Performs a simple backup of the database file based on config."""
    with app.app_context():
        config = load_backup_config()
        db_path = config["database_path"]
        db_file = Path(db_path)
        backup_dir = Path(config["backup_directory"])
        max_backups = config["max_backups"]
        
        if not db_file.exists():
            app.logger.warning(f"Database file {db_file} does not exist. Skipping backup.")
            if manual_trigger:
                flash(f"Database file {db_file} does not exist, backup skipped.", "warning")
            return False

        app.logger.info("Starting database backup...")
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            backup_filename = f"database_backup_{timestamp}.db"
            destination_path = backup_dir / backup_filename
            
            # Copy the file, preserving metadata like modification time
            shutil.copy2(db_file, destination_path)
            
            app.logger.info(f"Successfully backed up database to {destination_path}")
            update_backup_timestamp()  # Update timestamp in config
            
            # --- Pruning Logic ---
            # Keep the last N backups
            all_backups = sorted(
                [f for f in backup_dir.glob('database_backup_*.db') if f.is_file()],
                key=os.path.getmtime,
                reverse=True  # Newest first
            )
            
            if len(all_backups) > max_backups:
                backups_to_delete = all_backups[max_backups:]
                app.logger.info(f"Pruning {len(backups_to_delete)} old backup(s)...")
                for old_backup in backups_to_delete:
                    try:
                        old_backup.unlink()
                        app.logger.info(f"Deleted old backup: {old_backup.name}")
                    except OSError as e:
                        app.logger.error(f"Error deleting old backup {old_backup.name}: {e}")
            # --- End Pruning Logic ---

            if manual_trigger:
                 flash(f"Backup created successfully: {backup_filename}", "success")
            return True  # Indicate success

        except Exception as e:
            app.logger.error(f"An unexpected error occurred during backup: {e}")
            if manual_trigger:
                 flash(f"An unexpected error occurred during backup: {e}", "danger")
            return False  # Indicate failure

# Schedule the backup job (runs daily at midnight)
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(run_simple_backup, 'cron', hour=0, minute=0, id='daily_database_backup')
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Check for automatic backup 
def check_auto_backup():
    """Check if a backup is needed based on config settings and last backup time."""
    config = load_backup_config()
    
    # Skip if auto backup is disabled
    if not config.get("auto_backup", True):
        app.logger.info("Automatic backup is disabled in configuration.")
        return
        
    last_backup = get_last_backup_time()
    now = datetime.now()
    backup_needed = False
    
    if last_backup is None:
        app.logger.info("No previous backup timestamp found. Running initial backup.")
        backup_needed = True
    else:
        # Convert backup_interval from seconds to timedelta
        interval = timedelta(seconds=config.get("backup_interval", 86400))
        time_since_backup = now - last_backup
        
        if time_since_backup > interval:
            app.logger.info(f"Last backup was at {last_backup}. More than {interval} ago. Running catch-up backup.")
            backup_needed = True
    
    if backup_needed:
        # Run the backup silently on startup
        run_simple_backup(manual_trigger=False)

# Run the auto-backup check
check_auto_backup()

# Routes
@app.route('/')
def root():
    """Redirect to create box page"""
    logger.log_request(request, '/')
    return redirect(url_for('create_box_form'))

@app.route('/create', methods=['GET', 'POST'])
def create_box_form():
    """Show create box form and handle submission"""
    logger.log_request(request, '/create')
    
    if request.method == 'POST':
        try:
            # Print form data for debugging
            print("Form data:", request.form)
            
            # Get the submitted box number
            submitted_box_number = int(request.form.get('box_number', 0))
            
            # Always recalculate the next available box number at submission time
            # This prevents race conditions where someone else created a box with this number
            # while the form was open
            next_available = get_next_box_number()
            
            # If submitted box number is not available (someone else took it)
            # use the next available one instead
            box_number_to_use = submitted_box_number
            if submitted_box_number != next_available and submitted_box_number < next_available:
                # The submitted number is no longer available, use the new next available
                box_number_to_use = next_available
                flash(f"Box #{submitted_box_number} was already taken by someone else. Using box #{next_available} instead.", "warning")
            
            # Create the box
            create_box(
                priority=request.form['priority'],
                category_name=request.form['category'],
                box_size=request.form['box_size'],
                description=request.form['description'],
                editor='user'
            )
                
            logger.log_response(200, '/create')
            return redirect(url_for('list_boxes'))
        except Exception as e:
            logger.exception(f"Error creating box: {str(e)}")
            return render_template(
                'create.html',
                box=None,
                next_box_number=get_next_box_number(),
                categories=get_categories(),
                error=f"Error creating box: {str(e)}"
            )
    
    logger.log_response(200, '/create')
    return render_template(
        'create.html',
        box=None,
        next_box_number=get_next_box_number(),
        categories=get_categories()
    )

@app.route('/edit/<int:box_id>', methods=['GET', 'POST'])
def edit_box_form(box_id):
    """Show edit box form and handle submission"""
    logger.log_request(request, f'/edit/{box_id}')
    
    box = get_box(box_id)
    if not box:
        logger.warning(f"Box not found: {box_id}")
        logger.log_response(404, f'/edit/{box_id}')
        return "Box not found", 404
    
    if request.method == 'POST':
        try:
            update_box(
                box_id=box_id,
                priority=request.form['priority'],
                category_name=request.form['category'],
                box_size=request.form['box_size'],
                description=request.form['description'],
                editor='user'
            )
            logger.log_response(200, f'/edit/{box_id}')
            return redirect(url_for('list_boxes'))
        except Exception as e:
            logger.exception(f"Error updating box: {str(e)}")
            return render_template(
                'create.html',
                box=dict(box),
                categories=get_categories(),
                error=f"Error updating box: {str(e)}"
            )
    
    logger.log_response(200, f'/edit/{box_id}')
    return render_template(
        'create.html',
        box=dict(box),
        categories=get_categories()
    )

@app.route('/categories')
def manage_categories():
    """Category management page"""
    logger.log_request(request, '/categories')
    
    categories = get_categories()
    categories_with_usage = []
    
    for category in categories:
        usage_count = count_boxes_using_category(category['id'])
        categories_with_usage.append({
            'id': category['id'],
            'name': category['name'],
            'created_at': category['created_at'],
            'usage_count': usage_count,
            'can_delete': usage_count == 0
        })
    
    logger.log_response(200, '/categories')
    return render_template('categories.html', categories=categories_with_usage)

@app.route('/api/categories', methods=['GET', 'POST'])
def api_categories():
    """API for category management"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            return jsonify({"success": False, "error": "Category name is required"}), 400
        
        category_id = create_category(name)
        if category_id:
            return jsonify({"success": True, "id": category_id, "name": name})
        else:
            return jsonify({"success": False, "error": "Category already exists"}), 400
    
    # GET request
    categories = get_categories()
    return jsonify([dict(cat) for cat in categories])

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id):
    """Delete a category via API"""
    success, message = delete_category(category_id)
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 400

@app.route('/list')
def list_boxes():
    """Show box list with optional filtering"""
    logger.log_request(request, '/list')
    
    page = request.args.get('page', 1, type=int)
    per_page = 30  # Increased from 20 to 30
    show_all = request.args.get('show_all', 'false').lower() == 'true'
    
    # Get filter parameters
    box_number = request.args.get('box_number', type=int)
    priority = request.args.get('priority')
    category = request.args.get('category')
    box_size = request.args.get('box_size')
    description = request.args.get('description')
    
    # Get recent boxes first
    recent_boxes = get_recent_boxes(5)
    
    # Get total count for pagination
    total = count_boxes(
        box_number=box_number,
        priority=priority,
        category=category,
        box_size=box_size,
        description=description
    )
    
    # If show_all is requested, get all boxes without pagination
    if show_all:
        boxes_data = get_boxes(
            skip=0,
            limit=total,  # Get all boxes
            box_number=box_number,
            priority=priority,
            category=category,
            box_size=box_size,
            description=description
        )
        total_pages = 1
        page = 1
    else:
        # Get boxes with filters and pagination
        boxes_data = get_boxes(
            skip=(page - 1) * per_page,
            limit=per_page,
            box_number=box_number,
            priority=priority,
            category=category,
            box_size=box_size,
            description=description
        )
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    logger.log_response(200, '/list')
    return render_template(
        'list.html',
        boxes=[dict(box) for box in boxes_data],
        recent_boxes=recent_boxes,
        page=page,
        total_pages=total_pages,
        total_boxes=total,
        show_all=show_all,
        get_priority_color=get_priority_color,
        current_filters={
            'box_number': box_number,
            'priority': priority,
            'category': category,
            'box_size': box_size,
            'description': description
        }
    )

# Additional routes continue with existing backup, export, and API functionality...
# (Rest of routes unchanged from original file)

@app.route('/search')
def search_boxes():
    """Show search page"""
    logger.log_request(request, '/search')
    logger.log_response(200, '/search')
    return render_template('search.html')

@app.route('/export')
def export_page():
    """Renders the page with export options."""
    return render_template('export.html')

# Export Routes
@app.route('/export/csv')
def export_csv():
    """Route to export box data as CSV."""
    try:
        # Get filter parameters from query string
        search_term = request.args.get('search', None)
        category = request.args.get('category', None)
        priority = request.args.get('priority', None)
        
        # Call the export function
        success, result = export.export_to_csv(
            get_db(),
            search_term=search_term,
            category=category,
            priority=priority
        )
        
        if success:
            # Send the file for download - using correct parameters
            logger.info(f"Sending CSV file for download: {result}")
            return send_file(
                path_or_file=result,
                mimetype='text/csv',
                as_attachment=True,
                download_name=os.path.basename(result)
            )
        else:
            # Return an error message
            flash(f"Export failed: {result}", "danger")
            return redirect(url_for('export_page'))
            
    except Exception as e:
        logger.error(f"Error in export_csv route: {str(e)}")
        flash(f"Export failed: {str(e)}", "danger")
        return redirect(url_for('export_page'))

@app.route('/export/json')
def export_json():
    """Route to export box data as JSON."""
    try:
        # Get filter parameters from query string
        search_term = request.args.get('search', None)
        category = request.args.get('category', None)
        priority = request.args.get('priority', None)
        
        # Call the export function
        success, result = export.export_to_json(
            get_db(),
            search_term=search_term,
            category=category,
            priority=priority
        )
        
        if success:
            # Send the file for download - using correct parameters
            logger.info(f"Sending JSON file for download: {result}")
            return send_file(
                path_or_file=result,
                mimetype='application/json',
                as_attachment=True,
                download_name=os.path.basename(result)
            )
        else:
            # Return an error message
            flash(f"Export failed: {result}", "danger")
            return redirect(url_for('export_page'))
            
    except Exception as e:
        logger.error(f"Error in export_json route: {str(e)}")
        flash(f"Export failed: {str(e)}", "danger")
        return redirect(url_for('export_page'))

@app.route('/backup')
def backup_page():
    """Displays the backup status page."""
    config = load_backup_config()
    backup_dir = Path(config["backup_directory"])
    max_backups = config["max_backups"]
    
    # List backup files
    backup_files = []
    if backup_dir.exists():
        try:
            # Sort by modification time, newest first
            backup_files = sorted(
                [f for f in backup_dir.glob('database_backup_*.db') if f.is_file()],
                key=os.path.getmtime,
                reverse=True  # Newest first
            )
            # Get just the filenames
            backup_files = [f.name for f in backup_files]
        except Exception as e:
            app.logger.error(f"Error listing backup files: {e}")
            flash(f"Error listing backup files: {e}", "danger")
    else:
        flash(f"Backup directory '{backup_dir}' does not exist.", "warning")

    return render_template('backup.html', 
                           archives=backup_files,
                           last_backup_time=get_last_backup_time(),
                           backup_config=config)

@app.route('/backup/run', methods=['POST'])
def trigger_backup():
    """Manually triggers a backup."""
    success = run_simple_backup(manual_trigger=True)
    # Redirect back to the backup page to show status/flash message
    return redirect(url_for('backup_page'))

@app.route('/backup/delete', methods=['POST'])
def delete_backups():
    """Delete selected backup files."""
    config = load_backup_config()
    backup_dir = Path(config["backup_directory"])
    
    # Get list of selected backups from form
    selected_backups = request.form.getlist('selected_backups')
    
    if not selected_backups:
        flash("No backup files were selected for deletion.", "warning")
        return redirect(url_for('backup_page'))
    
    deleted_count = 0
    error_count = 0
    
    for filename in selected_backups:
        # Security validation: ensure filename has the correct format and doesn't contain path traversal
        if not filename.startswith('database_backup_') or '..' in filename or '/' in filename:
            flash(f"Invalid backup filename: {filename}", "danger")
            error_count += 1
            continue
        
        file_path = backup_dir / filename
        
        try:
            if file_path.exists():
                file_path.unlink()  # Delete the file
                app.logger.info(f"Deleted backup file: {filename}")
                deleted_count += 1
            else:
                flash(f"Backup file not found: {filename}", "warning")
                error_count += 1
        except Exception as e:
            app.logger.error(f"Error deleting backup file {filename}: {e}")
            flash(f"Error deleting {filename}: {str(e)}", "danger")
            error_count += 1
    
    if deleted_count > 0:
        if error_count > 0:
            flash(f"Deleted {deleted_count} backup files. Failed to delete {error_count} files.", "info")
        else:
            flash(f"Successfully deleted {deleted_count} backup files.", "success")
    else:
        flash("No backup files were deleted.", "warning")
    
    return redirect(url_for('backup_page'))

# Add route to download a specific backup file
@app.route('/backup/download/<filename>')
def download_backup(filename):
    """Allows downloading a specific backup file."""
    config = load_backup_config()
    backup_dir = Path(config["backup_directory"])
    
    try:
        # Basic security check: ensure filename looks like our pattern
        # and doesn't contain path traversal characters
        if not filename.startswith('database_backup_') or '..' in filename or '/' in filename:
            flash("Invalid backup filename.", "danger")
            return redirect(url_for('backup_page'))
            
        # send_from_directory is safer for preventing path traversal
        return send_from_directory(backup_dir, filename, as_attachment=True)
    except FileNotFoundError:
        flash(f"Backup file '{filename}' not found.", "danger")
        return redirect(url_for('backup_page'))
    except Exception as e:
        app.logger.error(f"Error downloading backup file {filename}: {e}")
        flash(f"Error downloading backup: {e}", "danger")
        return redirect(url_for('backup_page'))

@app.route('/api/boxes')
def api_list_boxes():
    """API endpoint for box listing"""
    logger.log_request(request, '/api/boxes')
    
    # Get filter parameters
    box_number = request.args.get('box_number', None, type=int)
    priority = request.args.get('priority')
    category = request.args.get('category')
    box_size = request.args.get('box_size')
    description = request.args.get('description')
    
    # Get boxes with filters
    boxes_data = get_boxes(
        box_number=box_number,
        priority=priority,
        category=category,
        box_size=box_size,
        description=description
    )
    
    # Convert to list of dicts for JSON response
    boxes = []
    for box in boxes_data:
        box_dict = dict(box)
        # Convert datetime objects to ISO format strings
        if isinstance(box_dict['created_at'], datetime):
            box_dict['created_at'] = box_dict['created_at'].isoformat()
        elif not isinstance(box_dict['created_at'], str):
            box_dict['created_at'] = str(box_dict['created_at'])
            
        if isinstance(box_dict['last_modified'], datetime):
            box_dict['last_modified'] = box_dict['last_modified'].isoformat()
        elif not isinstance(box_dict['last_modified'], str):
            box_dict['last_modified'] = str(box_dict['last_modified'])
        boxes.append(box_dict)
    
    logger.log_response(200, '/api/boxes')
    return jsonify(boxes)

@app.route('/api/boxes/<int:box_id>', methods=['DELETE'])
def api_delete_box(box_id):
    """API endpoint for box deletion"""
    logger.log_request(request, f'/api/boxes/{box_id}')
    
    editor = request.args.get('editor', 'user')
    
    if delete_box(box_id, editor):
        logger.log_response(200, f'/api/boxes/{box_id}')
        return jsonify({"success": True})
    
    logger.log_response(404, f'/api/boxes/{box_id}')
    return jsonify({"success": False, "error": "Box not found"}), 404

@app.route('/delete/<int:box_id>', methods=['POST'])
def delete_box_form(box_id):
    """Handle box deletion from web form"""
    logger.log_request(request, f'/delete/{box_id}')
    
    delete_box(box_id, 'user')
    
    logger.log_response(302, f'/delete/{box_id}')
    return redirect(url_for('list_boxes'))

@app.route('/api/clear-database', methods=['POST'])
def clear_database():
    """API endpoint to clear all boxes from the database (for testing only)"""
    logger.log_request(request, '/api/clear-database')
    
    try:
        db = get_db()
        
        # Log database contents before clearing
        all_boxes_before = query_db('SELECT id, box_number, is_deleted FROM boxes', [])
        logger.info(f"Database contents before clearing: {[dict(row) for row in all_boxes_before]}")
        
        with db:
            # Delete all boxes and their history
            cursor = db.cursor()
            
            # First delete all box history records to maintain foreign key integrity
            cursor.execute('DELETE FROM box_history')
            history_count = cursor.rowcount
            
            # Then delete all boxes
            cursor.execute('DELETE FROM boxes')
            box_count = cursor.rowcount
            
            db.commit()
        
        # Verify database is empty after clearing
        all_boxes_after = query_db('SELECT id, box_number, is_deleted FROM boxes', [])
        logger.info(f"Database contents after clearing: {[dict(row) for row in all_boxes_after]}")
            
        logger.info(f"Cleared database: deleted {box_count} boxes and {history_count} history records")
        logger.log_response(200, '/api/clear-database')
        return jsonify({"success": True, "message": f"Successfully deleted {box_count} boxes from database"})
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        logger.log_response(500, '/api/clear-database')
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/purge-deleted', methods=['POST'])
def purge_deleted_data():
    """Permanently remove all soft-deleted boxes from the database"""
    logger.log_request(request, '/api/purge-deleted')
    
    try:
        db = get_db()
        with db:
            cursor = db.cursor()
            
            # Get the IDs of all deleted boxes
            deleted_box_ids = [row['id'] for row in 
                              query_db('SELECT id FROM boxes WHERE is_deleted = 1')]
            
            # Delete history for all these boxes
            for box_id in deleted_box_ids:
                cursor.execute('DELETE FROM box_history WHERE box_id = ?', (box_id,))
            history_count = len(deleted_box_ids)
            
            # Then delete the boxes themselves
            cursor.execute('DELETE FROM boxes WHERE is_deleted = 1')
            box_count = cursor.rowcount
            
            db.commit()
            
        logger.info(f"Purged soft-deleted data: removed {box_count} boxes and their history")
        flash(f"Successfully purged {box_count} soft-deleted boxes from database", "success")
        logger.log_response(200, '/api/purge-deleted')
        return redirect(url_for('backup_page'))
    except Exception as e:
        logger.error(f"Error purging deleted data: {str(e)}")
        flash(f"Error purging deleted data: {str(e)}", "danger")
        logger.log_response(500, '/api/purge-deleted')
        return redirect(url_for('backup_page'))

@app.route('/clear-database', methods=['POST', 'GET'])
def clear_database_form():
    """Web form endpoint to clear the database with a page refresh"""
    logger.log_request(request, '/clear-database')
    
    try:
        db = get_db()
        
        # Log database contents before clearing
        all_boxes_before = query_db('SELECT id, box_number, is_deleted FROM boxes', [])
        logger.info(f"Database contents before clearing: {[dict(row) for row in all_boxes_before]}")
        
        with db:
            # Delete all boxes and their history
            cursor = db.cursor()
            
            # First delete all box history records to maintain foreign key integrity
            cursor.execute('DELETE FROM box_history')
            history_count = cursor.rowcount
            
            # Then delete all boxes
            cursor.execute('DELETE FROM boxes')
            box_count = cursor.rowcount
            
            # Make sure changes are committed
            db.commit()
        
        # Verify database is empty after clearing
        all_boxes_after = query_db('SELECT id, box_number, is_deleted FROM boxes', [])
        logger.info(f"Database contents after clearing: {[dict(row) for row in all_boxes_after]}")
            
        logger.info(f"Cleared database: deleted {box_count} boxes and {history_count} history records")
        flash(f"Successfully deleted {box_count} boxes and {history_count} history records from database", "success")
        
        logger.log_response(302, '/clear-database')
        # Redirect to create box page to start with a clean state
        return redirect(url_for('create_box_form'))
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        flash(f"Error clearing database: {str(e)}", "danger")
        logger.log_response(500, '/clear-database')
        return redirect(url_for('create_box_form'))

@app.route('/update-backup-config', methods=['POST'])
def update_backup_config():
    """Update the backup configuration settings."""
    logger.log_request(request, '/update-backup-config')
    
    try:
        # Get the current configuration
        config = load_backup_config()
        
        # Get the max_backups setting from the form
        max_backups = request.form.get('max_backups', type=int)
        
        # Validate the input
        if max_backups is not None:
            # Ensure it's within valid range (1-50)
            if max_backups < 1:
                max_backups = 1
                flash("Minimum number of backups set to 1.", "warning")
            elif max_backups > 50:
                max_backups = 50
                flash("Maximum number of backups limited to 50.", "warning")
            
            # Only update if the value has changed
            if max_backups != config["max_backups"]:
                # Update the configuration
                old_value = config["max_backups"]
                config["max_backups"] = max_backups
                
                # Save the updated configuration
                with open(BACKUP_CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                
                logger.info(f"Updated max_backups setting from {old_value} to {max_backups}")
                flash(f"Updated maximum number of backups from {old_value} to {max_backups}.", "success")
        
        logger.log_response(302, '/update-backup-config')
        return redirect(url_for('backup_page'))
    except Exception as e:
        logger.error(f"Error updating backup configuration: {str(e)}")
        flash(f"Error updating backup configuration: {str(e)}", "danger")
        logger.log_response(302, '/update-backup-config')
        return redirect(url_for('backup_page'))

# Add this at the bottom for running the app directly 
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
