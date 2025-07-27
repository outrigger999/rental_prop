#!/usr/bin/env python3
"""
Moving Box Tracker - Automated Backup System
===========================================

Provides functionality to create automated backups of the database.
Supports scheduled backups and rotation.

Target Platform: Raspberry Pi 4
Python Version: Python 3.9+
Code Version: 1.1 (Simplified Backup)
"""

import os
import json
import logging
import datetime
import time
import shutil
import uuid
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration file path
BACKUP_CONFIG_FILE = 'backup_config.json'
DATABASE_PATH = 'moving_boxes.db' # Assuming relative path to Flask app root
PROJECT_ROOT = Path(__file__).resolve().parent # Assuming backup.py is in project root

# Default configuration (used if config file is missing or invalid)
DEFAULT_CONFIG = {
    "backup_directory": "backups",
    "db_path": DATABASE_PATH,
    "auto_backup_interval_seconds": 86400, # 24 hours
    "max_backups": 10, # Keep the last 10 backups
    "last_backup_check": None
}

# Dictionary to track backup tasks and their status
backup_tasks = {}

# --- Configuration Management ---

def load_config():
    """Load backup configuration from file."""
    config = DEFAULT_CONFIG.copy() # Start with defaults
    if os.path.exists(BACKUP_CONFIG_FILE):
        try:
            with open(BACKUP_CONFIG_FILE, 'r') as f:
                user_config = json.load(f)
                config.update(user_config) # Override defaults with user settings
            logger.info(f"Loaded configuration from {BACKUP_CONFIG_FILE}")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {BACKUP_CONFIG_FILE}. Using default configuration.", exc_info=True)
            config = DEFAULT_CONFIG.copy() # Revert to defaults on error
        except Exception as e:
            logger.error(f"Error loading configuration from {BACKUP_CONFIG_FILE}: {e}. Using default configuration.", exc_info=True)
            config = DEFAULT_CONFIG.copy() # Revert to defaults on error
    else:
        logger.info(f"{BACKUP_CONFIG_FILE} not found. Using default configuration and creating the file.")
        save_config(config) # Create the file with defaults

    # Ensure essential paths are absolute relative to project root if they aren't already
    config['db_path'] = str(PROJECT_ROOT / config['db_path'])
    config['backup_directory'] = str(PROJECT_ROOT / config['backup_directory'])

    # Ensure backup directory exists
    try:
        os.makedirs(config['backup_directory'], exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create backup directory {config['backup_directory']}: {e}", exc_info=True)
        # If the dir can't be created, backups will fail later, but let load_config succeed for now.

    # Convert last_backup_check from string if necessary (occurs after first save/load)
    if isinstance(config.get('last_backup_check'), str):
        try:
            # Attempt to parse ISO format string back to timestamp
             dt_obj = datetime.datetime.fromisoformat(config['last_backup_check'])
             config['last_backup_check'] = dt_obj.timestamp()
        except (ValueError, TypeError):
             logger.warning(f"Could not parse last_backup_check timestamp string: {config['last_backup_check']}. Resetting.")
             config['last_backup_check'] = None


    return config

def save_config(config):
    """Save backup configuration to file"""
    try:
        # Store timestamp as ISO string for readability in JSON
        config_to_save = config.copy()
        if config_to_save.get('last_backup_check') is not None:
             config_to_save['last_backup_check'] = datetime.datetime.fromtimestamp(config_to_save['last_backup_check']).isoformat()

        # Store relative paths if possible
        try:
            config_to_save['db_path'] = str(Path(config['db_path']).relative_to(PROJECT_ROOT))
        except ValueError:
             pass # Keep absolute path if not relative to project root
        try:
             config_to_save['backup_directory'] = str(Path(config['backup_directory']).relative_to(PROJECT_ROOT))
        except ValueError:
             pass # Keep absolute path if not relative to project root


        with open(BACKUP_CONFIG_FILE, 'w') as f:
            json.dump(config_to_save, f, indent=4)
        logger.info(f"Saved configuration to {BACKUP_CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Failed to save configuration to {BACKUP_CONFIG_FILE}: {e}", exc_info=True)

# --- Core Backup Functions ---

def create_backup(custom_name=None):
    """
    Creates a timestamped backup of the database file.
    
    Args:
        custom_name (str, optional): Custom prefix for the backup filename.
        
    Returns:
        str: Task ID for tracking the backup progress
    """
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Store the task with initial status
    backup_tasks[task_id] = {
        'status': 'running',
        'start_time': time.time(),
        'message': 'Backup started',
        'result': None
    }
    
    # Run the actual backup process
    try:
        config = load_config()
        db_path = config['db_path']
        backup_dir = config['backup_directory']
        
        # Validate source database exists
        if not os.path.exists(db_path):
            backup_tasks[task_id]['status'] = 'failed'
            backup_tasks[task_id]['message'] = f"Database file not found: {db_path}"
            logger.error(f"Database file not found: {db_path}")
            return task_id
        
        # Create timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Construct backup filename with optional custom prefix
        if custom_name:
            # Sanitize custom name (remove special chars, spaces->underscores)
            custom_prefix = ''.join(c if c.isalnum() else '_' for c in custom_name)
            backup_filename = f"{custom_prefix}_{timestamp}.db"
        else:
            backup_filename = f"backup_{timestamp}.db"
        
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the file
        shutil.copy2(db_path, backup_path)
        
        # Rotate old backups if needed
        rotate_backups()
        
        # Update task status to completed
        backup_tasks[task_id]['status'] = 'completed'
        backup_tasks[task_id]['message'] = f"Backup completed: {backup_filename}"
        backup_tasks[task_id]['result'] = {
            'name': backup_filename,
            'path': backup_path,
            'size': os.path.getsize(backup_path),
            'timestamp': os.path.getmtime(backup_path)
        }
        
        logger.info(f"Backup created successfully: {backup_path}")
        return task_id
    except Exception as e:
        # Update task status to failed
        backup_tasks[task_id]['status'] = 'failed'
        backup_tasks[task_id]['message'] = f"Backup failed: {str(e)}"
        
        logger.error(f"Backup creation failed: {e}", exc_info=True)
        return task_id

def get_backup_status(task_id):
    """
    Get the status of a backup task
    
    Args:
        task_id (str): The ID of the backup task to check
        
    Returns:
        dict: Task status information or None if not found
    """
    if task_id in backup_tasks:
        return backup_tasks[task_id]
    return None

def list_backups():
    """List available backup files, sorted newest first."""
    config = load_config()
    backup_dir = config['backup_directory']
    backups = []
    try:
        if not os.path.isdir(backup_dir):
             logger.warning(f"Backup directory {backup_dir} does not exist.")
             return []
             
        for filename in os.listdir(backup_dir):
            if filename.endswith(".db"): # Simple filter, adjust if needed
                 filepath = os.path.join(backup_dir, filename)
                 if os.path.isfile(filepath):
                      try:
                           mtime = os.path.getmtime(filepath)
                           backups.append({
                                "name": filename,
                                "path": filepath,
                                "timestamp": mtime,
                                "size": os.path.getsize(filepath)
                           })
                      except OSError:
                           logger.warning(f"Could not get stats for file: {filepath}")

        # Sort by modification time, newest first
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    except Exception as e:
        logger.error(f"Error listing backups in {backup_dir}: {e}", exc_info=True)
        return []


def rotate_backups():
    """Remove oldest backups if the count exceeds max_backups."""
    config = load_config()
    backup_dir = config['backup_directory']
    max_backups = config.get('max_backups', DEFAULT_CONFIG['max_backups']) # Default if missing

    if not max_backups or max_backups <= 0:
        logger.info("Backup rotation is disabled (max_backups <= 0).")
        return

    try:
        # Get backups sorted oldest first for deletion
        all_backups = list_backups()
        # Need to sort by timestamp ascending to delete oldest
        all_backups.sort(key=lambda x: x['timestamp']) 

        num_backups = len(all_backups)
        if num_backups > max_backups:
            num_to_delete = num_backups - max_backups
            logger.info(f"Rotating backups: Found {num_backups}, max allowed {max_backups}. Deleting {num_to_delete} oldest backups.")
            
            deleted_count = 0
            for i in range(num_to_delete):
                backup_to_delete = all_backups[i]
                try:
                    os.remove(backup_to_delete['path'])
                    logger.info(f"Deleted old backup: {backup_to_delete['name']}")
                    deleted_count += 1
                except OSError as e:
                    logger.error(f"Failed to delete old backup {backup_to_delete['path']}: {e}")
            
            logger.info(f"Rotation complete. Deleted {deleted_count} backups.")
        else:
            logger.debug(f"Rotation check: Found {num_backups} backups, limit is {max_backups}. No deletion needed.")

    except Exception as e:
        logger.error(f"Error during backup rotation: {e}", exc_info=True)


def delete_backup_archive(archive_name):
    """
    Delete a specific backup file by name.
    
    Args:
        archive_name (str): Name of the backup file to delete
        
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    config = load_config()
    backup_dir = config['backup_directory']
    
    try:
        # Find the backup with the specified name
        all_backups = list_backups()
        backup_to_delete = None
        
        for backup in all_backups:
            if backup['name'] == archive_name:
                backup_to_delete = backup
                break
        
        if not backup_to_delete:
            return False, f"Backup '{archive_name}' not found"
        
        # Delete the backup file
        os.remove(backup_to_delete['path'])
        logger.info(f"Deleted backup: {archive_name}")
        return True, f"Backup '{archive_name}' deleted successfully"
        
    except OSError as e:
        error_msg = f"Failed to delete backup '{archive_name}': {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error deleting backup '{archive_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg


# --- Auto Backup Check ---
def check_auto_backup():
    """Check if an automatic backup is due and run it."""
    config = load_config()
    interval = config.get('auto_backup_interval_seconds')
    last_check = config.get('last_backup_check') # This is a float timestamp or None

    if not interval or interval <= 0:
        logger.info("Auto backup interval not set or invalid, skipping check.")
        return

    now_ts = time.time()
    run_backup = False
    if last_check is None:
        logger.info("First run detected, scheduling initial auto backup.")
        run_backup = True
    else:
        if now_ts - last_check >= interval:
            logger.info("Auto backup interval reached.")
            run_backup = True
        else:
            logger.debug("Auto backup interval not yet reached.")

    if run_backup:
        logger.info("Triggering automatic backup...")
        try:
            task_id = create_backup(custom_name="auto") # Pass "auto" as custom name
            # Check task status instead of using the boolean success value
            task_status = get_backup_status(task_id)
            if task_status and task_status['status'] == 'completed':
                logger.info(f"Automatic backup completed successfully (Task ID: {task_id}).")
                config['last_backup_check'] = now_ts # Update timestamp only on success
                save_config(config) # Save the updated timestamp
            else:
                logger.error(f"Automatic backup failed or still running (Task ID: {task_id}).")
                # Do not update last_backup_check on failure, try again next time
        except Exception as e:
            logger.error(f"Failed to trigger automatic backup: {e}", exc_info=True)


# --- Command Line Interface (Example usage) ---
# if __name__ == '__main__':
#     print("Running manual backup...")
#     if create_backup(custom_name="manual"):
#          print("Manual backup successful.")
#     else:
#          print("Manual backup failed.")
#     
#     print("Checking auto backup...")
#     check_auto_backup()
#     
#     print("Listing current backups:")
#     backups = list_backups()
#     if backups:
#          for backup in backups:
#               ts_str = datetime.datetime.fromtimestamp(backup['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
#               print(f" - {backup['name']} (Created: {ts_str}, Size: {backup['size']} bytes)")
#     else:
#          print("No backups found.")


# Initial config load when module is imported
load_config()