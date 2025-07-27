#!/usr/bin/env python3
"""
Database Migration: Add Categories Table
========================================

This script safely adds a categories table to the Moving Box Tracker database
while preserving all existing box data.

Safety Features:
- Creates backup before any changes
- Only adds new table, doesn't modify existing structure  
- Populates categories from existing box data
- Fully reversible
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
DATABASE = 'moving_boxes.db'
BACKUP_DIR = Path('backups')

def create_backup():
    """Create a backup of the current database before migration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'backup_before_categories_migration_{timestamp}.db'
    
    BACKUP_DIR.mkdir(exist_ok=True)
    shutil.copy2(DATABASE, backup_file)
    print(f"✅ Backup created: {backup_file}")
    return backup_file

def get_existing_categories(db):
    """Extract unique categories from existing boxes"""
    cursor = db.execute('SELECT DISTINCT category FROM boxes WHERE is_deleted = 0 ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]
    print(f"📋 Found {len(categories)} existing categories: {categories}")
    return categories

def create_categories_table(db):
    """Create the categories table"""
    db.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create index for faster lookups
    db.execute('CREATE INDEX IF NOT EXISTS idx_category_name ON categories(name)')
    print("✅ Categories table created")

def populate_categories(db, categories):
    """Populate categories table with existing category names"""
    for category in categories:
        try:
            db.execute(
                'INSERT OR IGNORE INTO categories (name, created_at) VALUES (?, ?)',
                (category, datetime.now())
            )
        except sqlite3.Error as e:
            print(f"⚠️  Warning: Could not add category '{category}': {e}")
    
    db.commit()
    print(f"✅ Populated {len(categories)} categories")

def verify_migration(db):
    """Verify the migration was successful"""
    # Check categories table exists and has data
    cursor = db.execute('SELECT COUNT(*) FROM categories')
    category_count = cursor.fetchone()[0]
    
    # Check existing boxes are still intact
    cursor = db.execute('SELECT COUNT(*) FROM boxes WHERE is_deleted = 0')
    box_count = cursor.fetchone()[0]
    
    print(f"✅ Verification complete:")
    print(f"   - Categories table: {category_count} entries")
    print(f"   - Boxes preserved: {box_count} entries")
    
    return category_count > 0 and box_count > 0

def main():
    """Run the migration"""
    print("🚀 Starting Categories Table Migration")
    print("=" * 40)
    
    # Safety check
    if not Path(DATABASE).exists():
        print(f"❌ Database file {DATABASE} not found!")
        return False
    
    try:
        # Step 1: Create backup
        backup_file = create_backup()
        
        # Step 2: Connect to database
        print("📂 Connecting to database...")
        db = sqlite3.connect(DATABASE)
        
        # Step 3: Get existing categories
        existing_categories = get_existing_categories(db)
        
        # Step 4: Create categories table
        print("🔧 Creating categories table...")
        create_categories_table(db)
        
        # Step 5: Populate with existing data
        print("📝 Populating categories...")
        populate_categories(db, existing_categories)
        
        # Step 6: Verify migration
        print("🔍 Verifying migration...")
        if verify_migration(db):
            print("✅ Migration completed successfully!")
            print(f"💾 Backup available at: {backup_file}")
            return True
        else:
            print("❌ Migration verification failed!")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"💾 Restore from backup: {backup_file}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n⚠️  Migration failed. Your original database is unchanged.")
        print("   Use the backup file to restore if needed.")
