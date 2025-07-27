import sqlite3
import os
import sys

# Add the current directory to the Python path to import logger
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logger

DATABASE = 'moving_boxes.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def fix_box_categories():
    logger.info("Starting fix for box categories...")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all categories for easy lookup
        cursor.execute("SELECT id, name FROM categories")
        categories = {row['id']: row['name'] for row in cursor.fetchall()}
        logger.info(f"Loaded {len(categories)} categories.")

        # Select boxes where category_id is not NULL and category text might be incorrect
        # We'll update the category text based on the category_id
        cursor.execute("SELECT id, box_number, category_id, category FROM boxes WHERE category_id IS NOT NULL")
        boxes_to_check = cursor.fetchall()
        logger.info(f"Found {len(boxes_to_check)} boxes with category_id to check.")

        updated_count = 0
        for box in boxes_to_check:
            box_id = box['id']
            box_number = box['box_number']
            category_id = box['category_id']
            current_category_text = box['category']

            if category_id in categories:
                correct_category_name = categories[category_id]
                if current_category_text != correct_category_name:
                    logger.info(f"Box #{box_number} (ID: {box_id}): Updating category text from '{current_category_text}' to '{correct_category_name}' (category_id: {category_id})")
                    cursor.execute("UPDATE boxes SET category = ? WHERE id = ?", (correct_category_name, box_id))
                    updated_count += 1
            else:
                # This case means category_id is not NULL but points to a non-existent category
                # This should ideally not happen if foreign key constraints are enforced,
                # but can happen if categories were deleted without handling dependent boxes.
                logger.warning(f"Box #{box_number} (ID: {box_id}): category_id {category_id} does not exist in categories table. Setting category to NULL.")
                cursor.execute("UPDATE boxes SET category_id = NULL, category = NULL WHERE id = ?", (box_id,))
                updated_count += 1 # Count this as an update as well

        conn.commit()
        logger.info(f"Fix completed. Total {updated_count} boxes updated.")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    fix_box_categories()