from flask import Flask, render_template, request, redirect, url_for, send_file, Response, flash
import sqlite3
import os
import csv
import json
from datetime import datetime
import io
import time
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rental_prop_secret_key'
DATABASE = 'rental_properties.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload folder and image subfolders exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create subfolders for different image types
PROPERTY_IMAGES = os.path.join(UPLOAD_FOLDER, 'property_images')
MAP_IMAGES = os.path.join(UPLOAD_FOLDER, 'map_images')

for folder in [PROPERTY_IMAGES, MAP_IMAGES]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if source_url column exists
    cursor.execute("PRAGMA table_info(properties)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_type TEXT NOT NULL,
            address TEXT,
            source_url TEXT,
            price REAL NOT NULL,
            sq_ft INTEGER,
            cat_friendly INTEGER,
            num_bedrooms INTEGER,
            air_conditioning INTEGER,
            parking_type TEXT,
            commute_morning TEXT,
            commute_midday TEXT,
            commute_evening TEXT,
            main_image TEXT,
            image_1 TEXT,
            image_2 TEXT,
            image_3 TEXT,
            image_4 TEXT,
            image_5 TEXT,
            map_image TEXT
        )
    ''')
    
    # Add columns if they don't exist in an existing table
    if 'properties' in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        if 'source_url' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN source_url TEXT')
        if 'main_image' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN main_image TEXT')
        if 'image_1' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN image_1 TEXT')
        if 'image_2' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN image_2 TEXT')
        if 'image_3' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN image_3 TEXT')
        if 'image_4' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN image_4 TEXT')
        if 'image_5' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN image_5 TEXT')
        if 'map_image' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN map_image TEXT')
        
        # Make address optional for existing table
        try:
            conn.execute('CREATE TABLE temp_properties AS SELECT * FROM properties')
            conn.execute('DROP TABLE properties')
            conn.execute('''
                CREATE TABLE properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_type TEXT NOT NULL,
                    address TEXT,
                    source_url TEXT,
                    price REAL NOT NULL,
                    sq_ft INTEGER,
                    cat_friendly INTEGER,
                    num_bedrooms INTEGER,
                    air_conditioning INTEGER,
                    parking_type TEXT,
                    commute_morning TEXT,
                    commute_midday TEXT,
                    commute_evening TEXT,
                    main_image TEXT,
                    image_1 TEXT,
                    image_2 TEXT,
                    image_3 TEXT,
                    image_4 TEXT,
                    image_5 TEXT,
                    map_image TEXT
                )
            ''')
            conn.execute('INSERT INTO properties SELECT id, property_type, address, NULL, price, sq_ft, cat_friendly, num_bedrooms, air_conditioning, parking_type, commute_morning, commute_midday, commute_evening, NULL, NULL, NULL, NULL, NULL, NULL, NULL FROM temp_properties')
            conn.execute('DROP TABLE temp_properties')
        except sqlite3.OperationalError:
            # If there's an error, the database might be empty or corrupted
            pass
    
    conn.commit()
    conn.close()

# Initialize the database when the app starts
with app.app_context():
    init_db()
    
# Deployment timestamp functionality
TIMESTAMP_FILE = 'deployment_timestamp.txt'

def get_deployment_timestamp():
    """Read the deployment timestamp from file or return default message"""
    try:
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, 'r') as f:
                timestamp = f.read().strip()
                if timestamp:
                    return timestamp
    except Exception:
        pass
    return "No deployment timestamp available"

@app.route('/')
def index():
    conn = get_db_connection()
    properties = conn.execute('SELECT * FROM properties').fetchall()
    conn.close()
    
    # Get the deployment timestamp
    deployment_timestamp = get_deployment_timestamp()
    
    return render_template('index.html', properties=properties, deployment_timestamp=deployment_timestamp)

@app.route('/search')
def search():
    # Get search parameters from request
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    min_bedrooms = request.args.get('min_bedrooms', '')
    property_type = request.args.get('property_type', '')
    cat_friendly = request.args.get('cat_friendly')
    air_conditioning = request.args.get('air_conditioning')
    
    # Build the query dynamically
    query = 'SELECT * FROM properties WHERE 1=1'
    params = []
    
    if min_price:
        query += ' AND price >= ?'
        params.append(float(min_price))
    
    if max_price:
        query += ' AND price <= ?'
        params.append(float(max_price))
    
    if min_bedrooms:
        query += ' AND num_bedrooms >= ?'
        params.append(int(min_bedrooms))
    
    if property_type:
        query += ' AND property_type = ?'
        params.append(property_type)
    
    if cat_friendly:
        query += ' AND cat_friendly = 1'
    
    if air_conditioning:
        query += ' AND air_conditioning = 1'
    
    # Execute the query
    conn = get_db_connection()
    properties = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('index.html', properties=properties)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder='property_images'):
    """Save uploaded file to specified subfolder and return the path"""
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        original_filename = secure_filename(file.filename)
        filename_parts = original_filename.rsplit('.', 1)
        unique_filename = f"{filename_parts[0]}_{uuid.uuid4().hex}.{filename_parts[1]}"
        
        # Create path relative to static folder
        save_dir = os.path.join(UPLOAD_FOLDER, subfolder)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        file_path = os.path.join(save_dir, unique_filename)
        file.save(file_path)
        
        # Return the path that will be saved in the database (relative to static)
        return os.path.join('uploads', subfolder, unique_filename)
    return None

@app.route('/add', methods=('GET', 'POST'))
def add_property():
    if request.method == 'POST':
        property_type = request.form['property_type']
        address = request.form.get('address')
        source_url = request.form.get('source_url')
        price = request.form['price']
        sq_ft = request.form.get('sq_ft')
        cat_friendly = 1 if request.form.get('cat_friendly') else 0
        num_bedrooms = request.form.get('num_bedrooms')
        air_conditioning = 1 if request.form.get('air_conditioning') else 0
        parking_type = request.form.get('parking_type')
        commute_morning = request.form.get('commute_morning')
        commute_midday = request.form.get('commute_midday')
        commute_evening = request.form.get('commute_evening')
        
        # Process uploaded files
        main_image = None
        image_1 = None
        image_2 = None
        image_3 = None
        image_4 = None
        image_5 = None
        map_image = None
        
        # Handle main property image
        if 'main_image' in request.files:
            main_image_file = request.files['main_image']
            if main_image_file.filename != '':
                main_image = save_uploaded_file(main_image_file, 'property_images')
        
        # Handle gallery images
        for i in range(1, 6):
            file_key = f'gallery_image_{i}'
            if file_key in request.files:
                gallery_file = request.files[file_key]
                if gallery_file.filename != '':
                    image_path = save_uploaded_file(gallery_file, 'property_images')
                    if i == 1:
                        image_1 = image_path
                    elif i == 2:
                        image_2 = image_path
                    elif i == 3:
                        image_3 = image_path
                    elif i == 4:
                        image_4 = image_path
                    elif i == 5:
                        image_5 = image_path
        
        # Handle map image
        if 'map_image' in request.files:
            map_file = request.files['map_image']
            if map_file.filename != '':
                map_image = save_uploaded_file(map_file, 'map_images')

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO properties (property_type, address, source_url, price, sq_ft, cat_friendly, num_bedrooms, '
            'air_conditioning, parking_type, commute_morning, commute_midday, commute_evening, '
            'main_image, image_1, image_2, image_3, image_4, image_5, map_image) VALUES '
            '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (property_type, address, source_url, price, sq_ft, cat_friendly, num_bedrooms, air_conditioning, 
             parking_type, commute_morning, commute_midday, commute_evening, 
             main_image, image_1, image_2, image_3, image_4, image_5, map_image)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_property.html')

@app.route('/export_data')
def export_data():
    return render_template('export.html')

@app.route('/export/<format>')
def export_file(format):
    conn = get_db_connection()
    properties = conn.execute('SELECT * FROM properties').fetchall()
    conn.close()
    
    if format == 'csv':
        # Create a CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['id', 'property_type', 'address', 'source_url', 'price', 'sq_ft', 'cat_friendly', 
                        'num_bedrooms', 'air_conditioning', 'parking_type', 
                        'commute_morning', 'commute_midday', 'commute_evening',
                        'main_image', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'map_image'])
        
        # Write data rows
        for prop in properties:
            writer.writerow([prop['id'], prop['property_type'], prop['address'], prop['source_url'],
                            prop['price'], prop['sq_ft'], prop['cat_friendly'], 
                            prop['num_bedrooms'], prop['air_conditioning'], prop['parking_type'], 
                            prop['commute_morning'], prop['commute_midday'], prop['commute_evening'],
                            prop.get('main_image'), prop.get('image_1'), prop.get('image_2'),
                            prop.get('image_3'), prop.get('image_4'), prop.get('image_5'),
                            prop.get('map_image')])
        
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=rental_properties_{timestamp}.csv"}
        )
    
    elif format == 'json':
        # Convert properties to list of dicts for JSON serialization
        properties_list = []
        for prop in properties:
            properties_list.append({
                'id': prop['id'],
                'property_type': prop['property_type'],
                'address': prop['address'],
                'source_url': prop.get('source_url'),
                'price': prop['price'],
                'sq_ft': prop['sq_ft'],
                'cat_friendly': bool(prop['cat_friendly']),
                'num_bedrooms': prop['num_bedrooms'],
                'air_conditioning': bool(prop['air_conditioning']),
                'parking_type': prop['parking_type'],
                'commute_morning': prop['commute_morning'],
                'commute_midday': prop['commute_midday'],
                'commute_evening': prop['commute_evening'],
                'main_image': prop.get('main_image'),
                'image_1': prop.get('image_1'),
                'image_2': prop.get('image_2'),
                'image_3': prop.get('image_3'),
                'image_4': prop.get('image_4'),
                'image_5': prop.get('image_5'),
                'map_image': prop.get('map_image')
            })
        
        # Create JSON response
        output = json.dumps({'properties': properties_list}, indent=2)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return Response(
            output,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=rental_properties_{timestamp}.json"}
        )
    
    else:
        return "Unsupported format", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
