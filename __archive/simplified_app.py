#!/usr/bin/env python3
"""
Moving Box Tracker - Version 1.0
================================

A simplified, single-file implementation of the Moving Box Tracker application
using Flask and SQLite (without async) for better reliability in conda environments.

Python Version: 3.11
Created: March 2025
Author: Scott

Features:
- Create new boxes with auto-incremented box numbers
- Edit existing box details
- List all boxes with filtering options
- Search boxes by various criteria
- Export box data to CSV, JSON, and PDF formats
- Print box labels
- Automated backups and restoration
- Structured logging
"""

import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, g, jsonify, send_file, flash, send_from_directory, make_response
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
SCHEMA_VERSION = 1 # Define current schema version

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
app.config['TEMPLATES_AUTO_RELOAD'] = True # Explicitly enable template auto-reloading
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # Disable caching for development

# Initialize logger
logger.info("Starting Moving Box Tracker application")

# Database helper functions
def get_db():
    """Connect to the database and return connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        
        # Set SQLite to return unlimited rows and optimize performance
        db.execute('PRAGMA max_page_count = 2147483646')
        db.execute('PRAGMA page_size = 4096')
        db.execute('PRAGMA cache_size = -2000')  # Use 2MB of memory for page cache
        db.execute('PRAGMA temp_store = MEMORY')  # Store temp tables and indices in memory
        db.execute('PRAGMA journal_mode = WAL')  # Use WAL mode for better concurrency
        db.execute('PRAGMA synchronous = NORMAL')  # Fsync only at critical moments
        db.execute('PRAGMA mmap_size = 268435456')  # Use memory mapping for reading, up to 256MB
        
        logger.debug(f"Connected to database: {app.config['DATABASE']}")
        logger.debug("SQLite pragmas set for optimal performance")
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection when app context ends"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        logger.debug("Database connection closed")

def get_db_version(db):
    """Get the current schema version from the database."""
    cursor = db.cursor()
    cursor.execute("PRAGMA user_version")
    return cursor.fetchone()[0]

def update_db_version(db, version):
    """Update the schema version in the database."""
    cursor = db.cursor()
    cursor.execute(f"PRAGMA user_version = {version}")
    db.commit()

def init_db():
    """Initialize the database tables and apply migrations"""
    db = get_db()
    current_db_version = get_db_version(db)
    
    if current_db_version < SCHEMA_VERSION:
        logger.info(f"Database schema out of date. Current version: {current_db_version}, Target version: {SCHEMA_VERSION}")
        
        if current_db_version < 1:
            logger.info("Applying schema migration to version 1...")
            db.execute('''
                CREATE TABLE IF NOT EXISTS boxes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    box_number INTEGER UNIQUE NOT NULL,
                    priority TEXT NOT NULL,
                    category_id INTEGER,
                    category TEXT NOT NULL,
                    box_size TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    last_modified TIMESTAMP NOT NULL,
                    is_deleted BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
            
            db.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')

            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO categories (name) VALUES (?)", ("General",))
                logger.info("Inserted default category: 'General'")

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
            update_db_version(db, 1)
            logger.info("Schema migrated to version 1.")
        
        # Add more migration steps here if SCHEMA_VERSION increases
        # if current_db_version < 2:
        #    logger.info("Applying schema migration to version 2...")
        #    db.execute("ALTER TABLE some_table ADD COLUMN new_column TEXT")
        #    update_db_version(db, 2)
        #    logger.info("Schema migrated to version 2.")
            
    db.commit()

def query_db(query, args=(), one=False):
    """Query the database and return results"""
    import time
    start_time = time.time()
    
    logger.debug(f"[QUERY] Starting execution of: {query}")
    logger.debug(f"[QUERY] Arguments: {args}")
    
    try:
        db = get_db()
        logger.debug(f"[QUERY] Got database connection in {(time.time() - start_time)*1000:.2f}ms")
        
        # Get current row count in boxes table for comparison
        if 'boxes' in query.lower():
            cur = db.execute('SELECT COUNT(*) FROM boxes')
            total_boxes = cur.fetchone()[0]
            logger.debug(f"[QUERY] Total boxes in database before query: {total_boxes}")
        
        # Execute the query
        cur = db.execute(query, args)
        logger.debug(f"[QUERY] Query executed in {(time.time() - start_time)*1000:.2f}ms")
        
        # Fetch results
        rv = cur.fetchall()
        fetch_time = time.time()
        logger.debug(f"[QUERY] Results fetched in {(fetch_time - start_time)*1000:.2f}ms")
        
        # Analyze results
        row_count = len(rv)
        logger.debug(f"[QUERY] Query returned {row_count} rows")
        
        if row_count > 0:
            logger.debug(f"[QUERY] First row: {dict(rv[0])}")
            logger.debug(f"[QUERY] Last row: {dict(rv[-1])}")
            if 'boxes' in query.lower():
                box_numbers = [r['box_number'] for r in rv if 'box_number' in r]
                if box_numbers:
                    logger.debug(f"[QUERY] Box numbers returned: {sorted(box_numbers)}")
        
        cur.close()
        logger.debug(f"[QUERY] Total execution time: {(time.time() - start_time)*1000:.2f}ms")
        
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        logger.error(f"[QUERY] Database error: {str(e)}")
        logger.error(f"[QUERY] Failed query: {query}")
        logger.error(f"[QUERY] Failed args: {args}")
        raise

def get_box(box_id):
    """Get a box by ID"""
    return query_db('SELECT * FROM boxes WHERE id = ?', [box_id], one=True)

def get_boxes(box_number=None, priority=None, category=None, box_size=None, description=None, limit=None, skip=None):
    """Get boxes with optional filtering and pagination"""
    logger.debug(f"[GET_BOXES] Called with params: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}, limit={limit}, skip={skip}")
    
    # CRITICAL DEBUG - Print to console
    print(f"GET_BOXES CALLED: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}, limit={limit}, skip={skip}")
    
    query = '''
    SELECT b.*, c.name as category
    FROM boxes b
    LEFT JOIN categories c ON b.category_id = c.id
    WHERE 1=1
    '''
    params = []
    
    # Add filters
    if box_number:
        query += ' AND b.box_number = ?'
        params.append(box_number)
    
    if priority:
        query += ' AND b.priority = ?'
        params.append(priority)
    
    if category:
        # Handle both category ID (numeric) and category name (string)
        if str(category).isdigit():
            query += ' AND b.category_id = ?'
            params.append(int(category))
        else:
            query += ' AND c.name = ?'
            params.append(category)
    
    if box_size:
        query += ' AND b.box_size = ?'
        params.append(box_size)
    
    if description:
        query += ' AND b.description LIKE ?'
        params.append(f'%{description}%')
    
    # Add ordering
    query += ' ORDER BY b.box_number'
    
    # Add pagination if specified
    if limit is not None:
        query += ' LIMIT ?'
        params.append(limit)
        if skip is not None:
            query += ' OFFSET ?'
            params.append(skip)
    
    logger.debug(f"[GET_BOXES] Final query: {query}")
    logger.debug(f"[GET_BOXES] Final parameters: {params}")
    
    # CRITICAL DEBUG - Print query details
    print(f"GET_BOXES QUERY: {query}")
    print(f"GET_BOXES PARAMS: {params}")
    
    result = query_db(query, params)
    boxes = [dict(row) for row in result]
    logger.debug(f"[GET_BOXES] Found {len(boxes)} boxes")
    
    # CRITICAL DEBUG - Print result count
    print(f"GET_BOXES RESULT: {len(boxes)} boxes found")
    
    return boxes

def count_boxes(box_number=None, priority=None, category=None, box_size=None, description=None):
    """Count boxes with optional filtering"""
    logger.debug(f"[COUNT_BOXES] Called with params: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}")
    
    # CRITICAL DEBUG - Print to console
    print(f"COUNT_BOXES CALLED: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}")
    
    query = '''
    SELECT COUNT(*) as count
    FROM boxes b
    LEFT JOIN categories c ON b.category_id = c.id
    WHERE 1=1
    '''
    params = []
    
    # Add filters (same as get_boxes)
    if box_number:
        query += ' AND b.box_number = ?'
        params.append(box_number)
    
    if priority:
        query += ' AND b.priority = ?'
        params.append(priority)
    
    if category:
        # Handle both category ID (numeric) and category name (string)
        if str(category).isdigit():
            query += ' AND b.category_id = ?'
            params.append(int(category))
        else:
            query += ' AND c.name = ?'
            params.append(category)
    
    if box_size:
        query += ' AND b.box_size = ?'
        params.append(box_size)
    
    if description:
        query += ' AND b.description LIKE ?'
        params.append(f'%{description}%')
    
    logger.debug(f"[COUNT_BOXES] Final query: {query}")
    logger.debug(f"[COUNT_BOXES] Final parameters: {params}")
    
    # CRITICAL DEBUG - Print query details
    print(f"COUNT_BOXES QUERY: {query}")
    print(f"COUNT_BOXES PARAMS: {params}")
    
    result = query_db(query, params, one=True)
    count = result['count'] if result else 0
    logger.debug(f"[COUNT_BOXES] Found {count} boxes")
    
    # CRITICAL DEBUG - Print result count
    print(f"COUNT_BOXES RESULT: {count} boxes found")
    
    return count


def count_boxes_using_category(category_id):
    """Count how many boxes use a specific category"""
    result = query_db('SELECT COUNT(*) FROM boxes WHERE category_id = ?', [category_id], one=True)
    return result[0] if result else 0


def edit_category(category_id, new_name):
    """Edit category name and update all boxes using it"""
    if not new_name or not new_name.strip():
        return False, "Category name cannot be empty"
    
    new_name = new_name.strip()
    
    try:
        db = get_db()
        
        # Check if another category with this name already exists
        existing = query_db('SELECT id FROM categories WHERE name COLLATE NOCASE = ? AND id != ?',
                           [new_name, category_id], one=True)
        if existing:
            return False, f"Another category with name '{new_name}' already exists"
        
        # Get old name for logging
        old_category = query_db('SELECT name FROM categories WHERE id = ?', 
                               [category_id], one=True)
        if not old_category:
            return False, f"Category with ID {category_id} not found"
        
        old_name = old_category['name']
        
        # Update the category name
        db.execute('UPDATE categories SET name = ? WHERE id = ?', 
                  [new_name, category_id])
        
        # Update all boxes using this category
        db.execute('UPDATE boxes SET category = ? WHERE category_id = ?', 
                  [new_name, category_id])
        
        # Get count of updated boxes
        box_count = count_boxes_using_category(category_id)
        
        db.commit()
        logger.info(f"Updated category ID {category_id} from '{old_name}' to '{new_name}' and updated {box_count} boxes")
        
        return True, f"Category updated successfully. {box_count} boxes were also updated."
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}")
        return False, f"Error updating category: {e}"


def delete_category(category_id):
    """Delete a category if it's not in use"""
    box_count = count_boxes_using_category(category_id)
    if box_count > 0:
        return False, f"Cannot delete category - {box_count} boxes are using it"
    
    try:
        db = get_db()
        db.execute('DELETE FROM categories WHERE id = ?', [category_id])
        db.commit()
        logger.info(f"Deleted category ID: {category_id}")
        return True, "Category deleted successfully"
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}")
        return False, f"Error deleting category: {e}"

def get_next_box_number():
    """Get the next available box number"""
    db = get_db()
    with db:  # Start a transaction
        try:
            # Get the highest box number currently in use
            result = query_db('SELECT MAX(box_number) as max_num FROM boxes', one=True)
            current_max = result['max_num'] if result['max_num'] is not None else 0
            
            # Get all box numbers in use
            used_numbers = set(row['box_number'] for row in query_db('SELECT box_number FROM boxes'))
            
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

def create_box(priority, category_id, box_size, description, editor, box_number=None):
    """Create a new box"""
    db = get_db()
    with db:  # Start a transaction
        try:
            if box_number is None:
                box_number = get_next_box_number()
            cursor = db.cursor()
            
            # Debug: log all boxes in the database
            all_boxes = query_db('SELECT id, box_number FROM boxes', [])
            logger.info(f"All boxes in database before creating new box: {[dict(row) for row in all_boxes]}")
            
            # Double-check the box number isn't in use
            existing = cursor.execute('SELECT 1 FROM boxes WHERE box_number = ?', [box_number]).fetchone()
            if existing:
                raise ValueError(f"Box number {box_number} is already in use")
            
            # Get category name
            category = query_db('SELECT name FROM categories WHERE id = ?', [category_id], one=True)
            if not category:
                raise ValueError(f"Invalid category ID: {category_id}")
            category_name = category['name']
            
            now = datetime.now() # Get current datetime once
            cursor.execute(
                '''INSERT INTO boxes (box_number, priority, category_id, category, box_size, description, created_at, last_modified) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (box_number, priority, category_id, category_name, box_size, description, now, now)
            )
            box_id = cursor.lastrowid
            
            # Add history record
            changes = f"Created box #{box_number}"
            cursor.execute(
                'INSERT INTO box_history (box_id, action, changes, editor, timestamp) VALUES (?, ?, ?, ?, ?)',
                (box_id, 'create', changes, editor, now) # Pass 'now' datetime object
            )
            
            logger.info(f"Box #{box_number} created successfully with ID: {box_id}")
            return box_id
            
        except Exception as e:
            logger.error(f"Error creating box: {str(e)}")
            db.rollback()  # Rollback the transaction in case of error
            raise

def update_box(box_id, priority, category_id, category, box_size, description, editor):
    """Update an existing box"""
    box = get_box(box_id)
    if not box:
        logger.warning(f"Attempted to update non-existent box with ID: {box_id}")
        return None
    
    logger.info(f"Updating box #{box['box_number']} (ID: {box_id})")
    
    changes = []
    if box['priority'] != priority:
        changes.append(f"Priority: {box['priority']} -> {priority}")
    if box['category_id'] != category_id:
        changes.append(f"Category: {box['category']} -> {category}")
    if box['box_size'] != box_size:
        changes.append(f"Size: {box['box_size']} -> {box_size}")
    if box['description'] != description:
        changes.append(f"Description updated")
    
    now = datetime.now()
    
    db = get_db()
    
    # Update box
    db.execute(
        'UPDATE boxes SET priority = ?, category_id = ?, category = ?, box_size = ?, description = ?, last_modified = ? WHERE id = ?',
        (priority, category_id, category, box_size, description, now, box_id)
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
    """Hard delete a box and its history"""
    box = get_box(box_id)
    if not box:
        logger.warning(f"Attempted to delete non-existent box with ID: {box_id}")
        return False
    
    logger.info(f"Permanently deleting box #{box['box_number']} (ID: {box_id})")
    
    db = get_db()
    with db:  # Use transaction
        try:
            # Delete box history first (due to foreign key)
            db.execute('DELETE FROM box_history WHERE box_id = ?', [box_id])
            
            # Delete the box
            db.execute('DELETE FROM boxes WHERE id = ?', [box_id])
            
            db.commit()
            logger.info(f"Box #{box['box_number']} permanently deleted")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting box: {str(e)}")
            raise

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
    """Get recently created boxes"""
    return query_db('''
        SELECT * FROM boxes 
        WHERE 1=1 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', [limit])

# Ensure the database is initialized
with app.app_context():
    init_db()

# Get the start time
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

def get_categories():
    """Get all categories from the database"""
    return query_db('SELECT id, name FROM categories ORDER BY name')

# Basic routes
@app.route('/create', methods=['GET', 'POST'])
def create_box_form():
    """Show create box form and handle submission"""
    logger.log_request(request, '/create')
    
    categories = get_categories()
    logger.info(f"Available categories: {categories}")
    
    if request.method == 'POST':
        try:
            # Log form data for debugging
            logger.info(f"Received form data: {request.form}")
            
            # Get the submitted box number
            submitted_box_number = int(request.form.get('box_number', 0))
            logger.info(f"Submitted box number: {submitted_box_number}")
            
            # Always recalculate the next available box number at submission time
            next_available = get_next_box_number()
            logger.info(f"Next available box number: {next_available}")
            
            # If submitted box number is not available, use the next available one
            box_number_to_use = submitted_box_number
            if submitted_box_number != next_available and submitted_box_number < next_available:
                box_number_to_use = next_available
                flash(f"Box #{submitted_box_number} was already taken. Using box #{next_available} instead.", "warning")
            logger.info(f"Box number to use: {box_number_to_use}")
            
            # Get the category name from the category ID
            category_id = int(request.form.get('category')) # Use .get() for safety
            category_name = next((cat['name'] for cat in categories if cat['id'] == category_id), None)
            
            if category_name is None:
                raise ValueError(f"Invalid category ID: {category_id}")

            # Get box_size and validate it
            box_size = request.form.get('box_size')
            if not box_size:
                raise ValueError("Box size is required.")
            
            logger.info(f"Creating box with: Priority: {request.form.get('priority')}, Category ID: {category_id}, Category Name: {category_name}, Size: {box_size}, Description: {request.form.get('description')}")
            
            # Create the box with the appropriate number
            box_id = create_box(
                priority=request.form.get('priority'),
                category_id=category_id,
                box_size=box_size, # Pass the validated box_size
                description=request.form.get('description'),
                editor='user',
                box_number=box_number_to_use  # Pass the box number we calculated
            )
            
            logger.info(f"Box #{box_number_to_use} created successfully with ID: {box_id}")
            flash(f"Box #{box_number_to_use} created successfully!", "success")
            
            logger.log_response(200, '/create')
            return redirect(url_for('list_boxes'))
        except Exception as e:
            logger.exception(f"Error creating box: {str(e)}")
            flash(f"Error creating box: {str(e)}", "danger")
            return render_template(
                'create.html',
                box=None,
                next_box_number=get_next_box_number(),
                categories=categories,
                error=f"Error creating box: {str(e)}"
            )
    else:
        logger.info("GET request received for create_box_form")
    
    next_box_number = get_next_box_number()
    logger.info(f"Next box number for GET request: {next_box_number}")
    logger.log_response(200, '/create')
    print("DEBUG: Attempting to render create.html template. Cache disabled. (New Test Message)") # Diagnostic print
    return render_template(
        'create.html',
        box=None,
        next_box_number=next_box_number,
        categories=categories
    )

@app.route('/categories/add', methods=['POST'])
def add_category():
    """Add a new category from a web form submission"""
    name = request.form.get('name', '').strip()
    if not name:
        flash('Category name cannot be empty', 'error')
        return redirect(url_for('manage_categories'))

    db = get_db()
    try:
        cursor = db.cursor()
        # Check for duplicate (case insensitive)
        cursor.execute('SELECT id FROM categories WHERE name COLLATE NOCASE = ?', (name,))
        existing = cursor.fetchone()
        if existing:
            flash(f"Category '{name}' already exists (case-insensitive match)", 'error')
            return redirect(url_for('manage_categories'))

        cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        db.commit()
        flash('Category added successfully', 'success')
    except Exception as e:
        logger.error(f"Error adding category: {e}")
        flash(f'Error adding category: {e}', 'error')
    return redirect(url_for('manage_categories'))

@app.route('/edit/<int:box_id>', methods=['GET', 'POST'])
def edit_box_form(box_id):
    """Show edit box form and handle submission"""
    logger.log_request(request, f'/edit/{box_id}')
    
    box = get_box(box_id)
    if not box:
        logger.warning(f"Box not found: {box_id}")
        logger.log_response(404, f'/edit/{box_id}')
        return "Box not found", 404
    
    categories = get_categories()
    
    if request.method == 'POST':
        try:
            category_id = int(request.form['category'])
            category_name = next((cat['name'] for cat in categories if cat['id'] == category_id), None)
            
            if category_name is None:
                raise ValueError(f"Invalid category ID: {category_id}")
            
            update_box(
                box_id=box_id,
                priority=request.form['priority'],
                category_id=category_id,
                category=category_name,
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
                categories=categories,
                error=f"Error updating box: {str(e)}"
            )
    
    logger.log_response(200, f'/edit/{box_id}')
    return render_template(
        'create.html',
        box=dict(box),
        categories=categories
    )

@app.route('/categories')
def manage_categories():
    """Category management page"""
    logger.log_request(request, '/categories')
    
    # Get categories with created_at field (or current timestamp if missing)
    db = get_db()
    categories = db.execute('SELECT id, name, COALESCE(created_at, CURRENT_TIMESTAMP) as created_at FROM categories').fetchall()
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
    logger.debug(f"[LIST] Rendering template with {len(categories_with_usage)} categories")
    return render_template('categories.html', categories=categories_with_usage)

@app.route('/boxes')
@app.route('/list')
def list_boxes():
    """Show box list with optional filtering"""
    logger.log_request(request, '/boxes')
    
    # CRITICAL DEBUG - Print to console
    print("=" * 50)
    print("LIST_BOXES ROUTE CALLED")
    print(f"Request args: {dict(request.args)}")
    print("=" * 50)
    
    # Get filter parameters
    box_number = request.args.get('box_number')
    priority = request.args.get('priority')
    category = request.args.get('category')
    box_size = request.args.get('box_size')
    description = request.args.get('description')
    
    logger.debug(f"[LIST] Request args: {dict(request.args)}")
    logger.debug(f"[LIST] Request headers: {dict(request.headers)}")
    logger.debug(f"Filters: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}")
    
    # CRITICAL DEBUG - Print filters
    print(f"FILTERS: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}")
    
    # Get total count with filters
    logger.debug(f"[LIST] Calling count_boxes with params: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}")
    total = count_boxes(
        box_number=box_number,
        priority=priority,
        category=category,
        box_size=box_size,
        description=description
    )
    logger.debug(f"[LIST] count_boxes returned total_boxes={total}")
    
    # CRITICAL DEBUG - Print count
    print(f"COUNT_BOXES RETURNED: {total}")
    
    # Get all boxes with filters (no limit)
    logger.debug(f"[LIST] Calling get_boxes with params: box_number={box_number}, priority={priority}, category={category}, box_size={box_size}, description={description}, limit=None, skip=None")
    boxes_data = get_boxes(
        box_number=box_number,
        priority=priority,
        category=category,
        box_size=box_size,
        description=description,
        limit=None,
        skip=None
    )
    logger.debug(f"[LIST] get_boxes returned {len(boxes_data)} boxes")
    logger.debug(f"[LIST] First 5 box numbers: {[box['box_number'] for box in boxes_data[:5]]}")
    
    # CRITICAL DEBUG - Print actual boxes returned
    print(f"GET_BOXES RETURNED: {len(boxes_data)} boxes")
    if boxes_data:
        box_numbers = [box['box_number'] for box in boxes_data]
        print(f"BOX NUMBERS: {sorted(box_numbers)}")
    print("=" * 50)
    
    # Debug logging
    logger.debug(f"Total boxes from count: {total}")
    logger.debug(f"Actual boxes returned: {len(boxes_data)}")
    
    # Get all categories for the filter dropdown
    categories = get_categories()
    
    logger.log_response(200, '/boxes')
    response = make_response(render_template(
        'list.html',
        boxes=[dict(box) for box in boxes_data],
        total_boxes=total,
        get_priority_color=get_priority_color,
        current_filters={
            'box_number': box_number,
            'priority': priority,
            'category': category,
            'box_size': box_size,
            'description': description
        },
        categories=categories
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

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

# Removed purge_deleted_data function since we now use hard deletes

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
    except Exception as e:
        logger.error(f"Error updating backup configuration: {str(e)}")
        flash(f"Error updating backup configuration: {str(e)}", "danger")
        logger.log_response(302, '/update-backup-config')
        return redirect(url_for('backup_page'))

# API Routes - Must be defined before the main block
@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def api_edit_category(category_id):
    """Edit a category via API"""
    # Handle both JSON and form-encoded data
    if request.is_json:
        data = request.get_json()
        new_name = (data.get('name') or '').strip()
    else:
        new_name = (request.form.get('name') or '').strip()
        
    if not new_name:
        return jsonify({"success": False, "error": "Category name is required"}), 400
        
    success, message = edit_category(category_id, new_name)
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 400

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id):
    """Delete a category via API"""
    success, message = delete_category(category_id)
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 400

@app.route('/api/categories', methods=['GET', 'POST'])
def api_categories():
    """API for category management (list/add categories)"""
    # GET request - return all categories
    if request.method == 'GET':
        categories = get_categories()
        return jsonify([dict(cat) for cat in categories])
    
    # POST request - add a new category
    # Handle both JSON and form-encoded data
    if request.is_json:
        data = request.get_json()
        name = (data.get('name') or '').strip()
    else:
        name = (request.form.get('name') or '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': 'Category name is required'}), 400
    
    # Check for duplicate (case insensitive)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM categories WHERE name COLLATE NOCASE = ?', (name,))
    existing = cur.fetchone()
    if existing:
        return jsonify({'success': False, 'error': 'Category already exists'}), 400
    
    # Insert new category
    cur.execute('INSERT INTO categories (name) VALUES (?)', (name,))
    conn.commit()
    new_id = cur.lastrowid
    return jsonify({'success': True, 'id': new_id, 'name': name}), 200

# Add this at the bottom for running the app directly 
@app.route('/')
def root():
    """Redirect to create box page"""
    logger.log_request(request, '/')
    return redirect(url_for('create_box_form'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
