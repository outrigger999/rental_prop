#!/usr/bin/env python3
"""
Moving Box Tracker - Logging System
==================================

A structured logging system for the Moving Box Tracker application.
Provides consistent logging across the application with different log levels,
file and console output, and rotation capabilities.

Target Platform: Raspberry Pi 4
Python Version: Python 3.9+
Code Version: 1.0
"""

import os
import logging
import logging.handlers
from datetime import datetime

# Configuration
LOG_DIRECTORY = 'logs'
LOG_FILENAME = 'moving_box_tracker.log'
LOG_LEVEL = logging.DEBUG  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 5  # Number of backup logs to keep

# Ensure log directory exists
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create logger
logger = logging.getLogger('moving_box_tracker')
logger.setLevel(LOG_LEVEL)

# Create formatters
file_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
)
console_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

# Create file handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIRECTORY, LOG_FILENAME),
    maxBytes=MAX_LOG_SIZE,
    backupCount=BACKUP_COUNT
)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(file_formatter)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Show all messages in console
console_handler.setFormatter(console_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Convenience functions
def debug(message, *args, **kwargs):
    """Log a debug message"""
    logger.debug(message, *args, **kwargs)

def info(message, *args, **kwargs):
    """Log an info message"""
    logger.info(message, *args, **kwargs)

def warning(message, *args, **kwargs):
    """Log a warning message"""
    logger.warning(message, *args, **kwargs)

def error(message, *args, **kwargs):
    """Log an error message"""
    logger.error(message, *args, **kwargs)

def critical(message, *args, **kwargs):
    """Log a critical message"""
    logger.critical(message, *args, **kwargs)

def exception(message, *args, **kwargs):
    """Log an exception message with traceback"""
    logger.exception(message, *args, **kwargs)

def log_request(request, route):
    """Log an HTTP request"""
    info(f"Request: {request.method} {route} - IP: {request.remote_addr}")

def log_response(status_code, route):
    """Log an HTTP response"""
    if status_code >= 400:
        warning(f"Response: {status_code} for {route}")
    else:
        info(f"Response: {status_code} for {route}")

def log_database_operation(operation, table, record_id=None):
    """Log a database operation"""
    if record_id:
        info(f"Database: {operation} on {table} (ID: {record_id})")
    else:
        info(f"Database: {operation} on {table}")

def log_error(error, context=None):
    """Log an error with context"""
    if context:
        error(f"Error: {str(error)} - Context: {context}")
    else:
        error(f"Error: {str(error)}")

def configure(level=None, log_file=None):
    """Reconfigure the logger with new settings"""
    if level:
        logger.setLevel(level)
        file_handler.setLevel(level)
    
    if log_file:
        file_handler.baseFilename = os.path.join(LOG_DIRECTORY, log_file)

# Log startup
info(f"=== Moving Box Tracker Started at {datetime.now().isoformat()} ===")