  #!/usr/bin/env python3
"""
Moving Box Tracker - Testing Framework
======================================

Provides automated testing for the Moving Box Tracker application.
Includes unit tests, integration tests, and API tests.

Target Platform: Raspberry Pi 4
Python Version: Python 3.9+
Code Version: 1.0
"""

import os
import sys
import unittest
import tempfile
import json
import sqlite3
from datetime import datetime
import shutil

# Add the current directory to the path so we can import the application
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the application
import simplified_app as app
import logger
import export
import backup

# Disable logging during tests
logger.configure(level=100)  # Set to a high level to disable logging

class TestDatabaseFunctions(unittest.TestCase):
    """Test database helper functions"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database file
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        
        # Initialize the database
        with app.app.app_context():
            app.init_db()
    
    def tearDown(self):
        """Clean up test environment"""
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])
    
    def test_get_db(self):
        """Test database connection"""
        with app.app.app_context():
            db = app.get_db()
            self.assertIsNotNone(db)
            
            # Test that we can execute a query
            cursor = db.execute('SELECT 1')
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
    
    def test_query_db(self):
        """Test query_db function"""
        with app.app.app_context():
            # Insert a test box
            db = app.get_db()
            now = datetime.now()
            db.execute(
                'INSERT INTO boxes (box_number, priority, category, box_size, description, created_at, last_modified, is_deleted) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (1, 'Priority 1', 'Kitchen', 'Medium', 'Test box', now, now, False)
            )
            db.commit()
            
            # Test query_db with one=True
            result = app.query_db('SELECT * FROM boxes WHERE box_number = ?', [1], one=True)
            self.assertIsNotNone(result)
            self.assertEqual(result['box_number'], 1)
            self.assertEqual(result['priority'], 'Priority 1')
            
            # Test query_db with one=False
            results = app.query_db('SELECT * FROM boxes WHERE box_number = ?', [1])
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['box_number'], 1)
            
            # Test query_db with no results
            result = app.query_db('SELECT * FROM boxes WHERE box_number = ?', [999], one=True)
            self.assertIsNone(result)
            
            results = app.query_db('SELECT * FROM boxes WHERE box_number = ?', [999])
            self.assertEqual(len(results), 0)

class TestBoxFunctions(unittest.TestCase):
    """Test box management functions"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database file
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        
        # Initialize the database
        with app.app.app_context():
            app.init_db()
    
    def tearDown(self):
        """Clean up test environment"""
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])
    
    def test_create_box(self):
        """Test creating a box"""
        with app.app.app_context():
            # Create a box
            box_id = app.create_box(
                priority='Priority 1',
                category='Kitchen',
                box_size='Medium',
                description='Test box',
                editor='test_user'
            )
            
            # Verify the box was created
            self.assertIsNotNone(box_id)
            
            # Get the box and verify its properties
            box = app.get_box(box_id)
            self.assertIsNotNone(box)
            self.assertEqual(box['box_number'], 1)
            self.assertEqual(box['priority'], 'Priority 1')
            self.assertEqual(box['category'], 'Kitchen')
            self.assertEqual(box['box_size'], 'Medium')
            self.assertEqual(box['description'], 'Test box')
            self.assertFalse(box['is_deleted'])
            
            # Verify history record was created
            history = app.get_box_history(box_id)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]['action'], 'create')
            self.assertEqual(history[0]['editor'], 'test_user')
    
    def test_update_box(self):
        """Test updating a box"""
        with app.app.app_context():
            # Create a box
            box_id = app.create_box(
                priority='Priority 1',
                category='Kitchen',
                box_size='Medium',
                description='Test box',
                editor='test_user'
            )
            
            # Update the box
            app.update_box(
                box_id=box_id,
                priority='Priority 2',
                category='Living Room',
                box_size='Large',
                description='Updated test box',
                editor='test_user'
            )
            
            # Get the updated box and verify its properties
            box = app.get_box(box_id)
            self.assertIsNotNone(box)
            self.assertEqual(box['priority'], 'Priority 2')
            self.assertEqual(box['category'], 'Living Room')
            self.assertEqual(box['box_size'], 'Large')
            self.assertEqual(box['description'], 'Updated test box')
            
            # Verify history records
            history = app.get_box_history(box_id)
            self.assertEqual(len(history), 2)  # Create + Update
            self.assertEqual(history[0]['action'], 'update')  # Most recent first
    
    def test_delete_box(self):
        """Test deleting a box"""
        with app.app.app_context():
            # Create a box
            box_id = app.create_box(
                priority='Priority 1',
                category='Kitchen',
                box_size='Medium',
                description='Test box',
                editor='test_user'
            )
            
            # Delete the box
            result = app.delete_box(box_id, 'test_user')
            self.assertTrue(result)
            
            # Verify the box is marked as deleted
            box = app.query_db('SELECT * FROM boxes WHERE id = ?', [box_id], one=True)
            self.assertIsNotNone(box)
            self.assertTrue(box['is_deleted'])
            
            # Verify get_box doesn't return deleted boxes
            box = app.get_box(box_id)
            self.assertIsNone(box)
            
            # Verify history records
            history = app.get_box_history(box_id)
            self.assertEqual(len(history), 2)  # Create + Delete
            self.assertEqual(history[0]['action'], 'delete')  # Most recent first
    
    def test_get_next_box_number(self):
        """Test getting the next box number"""
        with app.app.app_context():
            # Initially should be 1
            self.assertEqual(app.get_next_box_number(), 1)
            
            # Create a box
            box_id = app.create_box(
                priority='Priority 1',
                category='Kitchen',
                box_size='Medium',
                description='Test box',
                editor='test_user'
            )
            
            # Next should be 2
            self.assertEqual(app.get_next_box_number(), 2)
            
            # Create another box
            box_id2 = app.create_box(
                priority='Priority 1',
                category='Kitchen',
                box_size='Medium',
                description='Test box 2',
                editor='test_user'
            )
            
            # Next should be 3
            self.assertEqual(app.get_next_box_number(), 3)
            
            # Delete the first box
            app.delete_box(box_id, 'test_user')
            
            # Next should still be 3 (we don't reuse deleted box numbers)
            self.assertEqual(app.get_next_box_number(), 3)

class TestRoutes(unittest.TestCase):
    """Test Flask routes"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database file
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        
        # Initialize the database
        with app.app.app_context():
            app.init_db()
    
    def tearDown(self):
        """Clean up test environment"""
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])
    
    def test_root_route(self):
        """Test root route redirects to create box form"""
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Box', response.data)
    
    def test_create_box_route(self):
        """Test create box route"""
        # Test GET request
        response = self.app.get('/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Box', response.data)
        
        # Test POST request
        response = self.app.post('/create', data={
            'priority': 'Priority 1',
            'category': 'Kitchen',
            'box_size': 'Medium',
            'description': 'Test box'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Box List', response.data)
        
        # Verify the box was created
        with app.app.app_context():
            box = app.query_db('SELECT * FROM boxes WHERE box_number = ?', [1], one=True)
            self.assertIsNotNone(box)
            self.assertEqual(box['priority'], 'Priority 1')
    
    def test_list_boxes_route(self):
        """Test list boxes route"""
        # Create some boxes
        with app.app.app_context():
            app.create_box(
                priority='Priority 1',
                category='Kitchen',
                box_size='Medium',
                description='Test box 1',
                editor='test_user'
            )
            app.create_box(
                priority='Priority 2',
                category='Living Room',
                box_size='Large',
                description='Test box 2',
                editor='test_user'
            )
        
        # Test list route
        response = self.app.get('/list')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Box List', response.data)
        self.assertIn(b'Test box 1', response.data)
        self.assertIn(b'Test box 2', response.data)
        
        # Test filtering
        response = self.app.get('/list?priority=Priority+1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test box 1', response.data)
        self.assertNotIn(b'Test box 2', response.data)
    
    def test_api_list_boxes(self):
        """Test API list boxes endpoint"""
        # Create some boxes
        with app.app.app_context():
            app.create_box(
                priority='Priority 1',
                category='Kitchen',
                box_size='Medium',
                description='Test box 1',
                editor='test_user'
            )
            app.create_box(
                priority='Priority 2',
                category='Living Room',
                box_size='Large',
                description='Test box 2',
                editor='test_user'
            )
        
        # Test API endpoint
        response = self.app.get('/api/boxes')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['box_number'], 1)
        self.assertEqual(data[1]['box_number'], 2)
        
        # Test filtering
        response = self.app.get('/api/boxes?priority=Priority+1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['box_number'], 1)

class TestExportModule(unittest.TestCase):
    """Test export module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Set export directory to a temporary directory
        self.export_dir = tempfile.mkdtemp()
        export.EXPORT_DIRECTORY = self.export_dir
        
        # Create a test database
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Create tables
        conn.executescript('''
            CREATE TABLE boxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                box_number INTEGER NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                box_size TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN NOT NULL DEFAULT 0
            );
            
            CREATE TABLE box_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                box_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                editor TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (box_id) REFERENCES boxes (id)
            );
        ''')
        
        # Insert test data
        now = datetime.now().isoformat()
        conn.execute(
            'INSERT INTO boxes (box_number, priority, category, box_size, description, created_at, last_modified, is_deleted) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (1, 'Priority 1', 'Kitchen', 'Medium', 'Test box 1', now, now, False)
        )
        conn.execute(
            'INSERT INTO boxes (box_number, priority, category, box_size, description, created_at, last_modified, is_deleted) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (2, 'Priority 2', 'Living Room', 'Large', 'Test box 2', now, now, False)
        )
        conn.commit()
        conn.close()
        
        # Set the database path for the export module
        export.DATABASE_PATH = self.db_path
    
    def tearDown(self):
        """Clean up test environment"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
        shutil.rmtree(self.export_dir)
    
    def test_export_to_csv(self):
        """Test exporting to CSV"""
        # Export to CSV
        filename = 'test_export.csv'
        filepath = export.export_to_csv(filename=filename)
        
        # Verify the file was created
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        
        # Verify the file contains the expected data
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('box_number', content)
            self.assertIn('Test box 1', content)
            self.assertIn('Test box 2', content)
    
    def test_export_to_json(self):
        """Test exporting to JSON"""
        # Export to JSON
        filename = 'test_export.json'
        filepath = export.export_to_json(filename=filename)
        
        # Verify the file was created
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        
        # Verify the file contains the expected data
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['box_number'], 1)
            self.assertEqual(data[1]['box_number'], 2)
            self.assertEqual(data[0]['description'], 'Test box 1')
            self.assertEqual(data[1]['description'], 'Test box 2')

class TestBackupModule(unittest.TestCase):
    """Test backup module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Set backup directory to a temporary directory
        self.backup_dir = tempfile.mkdtemp()
        backup.BACKUP_DIRECTORY = self.backup_dir
        
        # Create a test database
        conn = sqlite3.connect(self.db_path)
        
        # Create tables
        conn.executescript('''
            CREATE TABLE boxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                box_number INTEGER NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                box_size TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN NOT NULL DEFAULT 0
            );
        ''')
        
        # Insert test data
        conn.execute(
            'INSERT INTO boxes (box_number, priority, category, box_size, description) '
            'VALUES (?, ?, ?, ?, ?)',
            (1, 'Priority 1', 'Kitchen', 'Medium', 'Test box 1')
        )
        conn.commit()
        conn.close()
        
        # Set the database path for the backup module
        backup.DATABASE_PATH = self.db_path
    
    def tearDown(self):
        """Clean up test environment"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
        shutil.rmtree(self.backup_dir)
    
    def test_create_backup(self):
        """Test creating a backup"""
        # Create a backup
        backup_path = backup.create_backup()
        
        # Verify the backup was created
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify the backup is a valid SQLite database
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        self.assertIn(('boxes',), tables)
        
        # Verify the backup contains the expected data
        cursor.execute('SELECT * FROM boxes')
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 1)  # box_number
        self.assertEqual(rows[0][2], 'Priority 1')  # priority
        conn.close()
    
    def test_list_backups(self):
        """Test listing backups"""
        # Create some backups
        backup.create_backup()
        backup.create_backup()
        
        # List backups
        backups = backup.list_backups()
        
        # Verify the backups were listed
        self.assertEqual(len(backups), 2)
        self.assertTrue('filename' in backups[0])
        self.assertTrue('path' in backups[0])
        self.assertTrue('size_bytes' in backups[0])
        self.assertTrue('date' in backups[0])
    
    def test_restore_backup(self):
        """Test restoring a backup"""
        # Create a backup
        backup_path = backup.create_backup()
        
        # Modify the original database
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM boxes')
        conn.commit()
        conn.close()
        
        # Verify the original database is empty
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM boxes')
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0)
        conn.close()
        
        # Restore the backup
        result = backup.restore_backup(backup_path)
        self.assertTrue(result)
        
        # Verify the database was restored
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM boxes')
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        conn.close()

if __name__ == '__main__':
    unittest.main()
