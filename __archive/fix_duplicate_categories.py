#!/usr/bin/env python3
import os
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db():
    """Connect to database and return a connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'moving_boxes.db')
    logger.info(f"Opening database at {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fix_duplicate_categories():
    """Find and fix duplicate categories"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Find duplicate category names
        logger.info("Looking for duplicate categories...")
        cursor.execute('''
            SELECT name, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM categories 
            GROUP BY name 
            HAVING count > 1
        ''')
        duplicates = cursor.fetchall()
        
        if not duplicates:
            logger.info("No duplicate categories found.")
            return
        
        for dup in duplicates:
            name = dup['name']
            ids = dup['ids'].split(',')
            logger.info(f"Found duplicate category '{name}' with IDs: {ids}")
            
            # Keep the first ID (lowest ID) and remove others
            keep_id = int(ids[0])
            remove_ids = [int(id) for id in ids[1:]]
            
            logger.info(f"Keeping category ID {keep_id} and removing IDs {remove_ids}")
            
            # Update boxes that use the duplicate categories to use the kept category
            for remove_id in remove_ids:
                logger.info(f"Updating boxes with category_id={remove_id} to use category_id={keep_id}")
                cursor.execute('''
                    UPDATE boxes 
                    SET category_id = ? 
                    WHERE category_id = ?
                ''', (keep_id, remove_id))
                affected = cursor.rowcount
                logger.info(f"Updated {affected} boxes.")
                
                # Now delete the duplicate category
                logger.info(f"Deleting category ID {remove_id}")
                cursor.execute('DELETE FROM categories WHERE id = ?', (remove_id,))
                
        # Commit changes
        conn.commit()
        logger.info("All duplicate categories have been fixed.")
    
    except Exception as e:
        logger.error(f"Error fixing duplicate categories: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_duplicate_categories()
    print("Done! Duplicate categories have been fixed.")
