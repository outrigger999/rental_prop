from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import sqlite3
import os
import csv
import json
from datetime import datetime
import io
import time

app = Flask(__name__)
DATABASE = 'rental_properties.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_type TEXT NOT NULL,
            address TEXT NOT NULL,
            price REAL NOT NULL,
            sq_ft INTEGER,
            cat_friendly INTEGER,
            num_bedrooms INTEGER,
            air_conditioning INTEGER,
            parking_type TEXT,
            commute_morning TEXT,
            commute_midday TEXT,
            commute_evening TEXT
        )
    ''')
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

@app.route('/add', methods=('GET', 'POST'))
def add_property():
    if request.method == 'POST':
        property_type = request.form['property_type']
        address = request.form['address']
        price = request.form['price']
        sq_ft = request.form.get('sq_ft')
        cat_friendly = 1 if request.form.get('cat_friendly') else 0
        num_bedrooms = request.form.get('num_bedrooms')
        air_conditioning = 1 if request.form.get('air_conditioning') else 0
        parking_type = request.form.get('parking_type')
        commute_morning = request.form.get('commute_morning')
        commute_midday = request.form.get('commute_midday')
        commute_evening = request.form.get('commute_evening')

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO properties (property_type, address, price, sq_ft, cat_friendly, num_bedrooms, air_conditioning, parking_type, commute_morning, commute_midday, commute_evening) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (property_type, address, price, sq_ft, cat_friendly, num_bedrooms, air_conditioning, parking_type, commute_morning, commute_midday, commute_evening)
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
        writer.writerow(['id', 'property_type', 'address', 'price', 'sq_ft', 'cat_friendly', 
                        'num_bedrooms', 'air_conditioning', 'parking_type', 
                        'commute_morning', 'commute_midday', 'commute_evening'])
        
        # Write data rows
        for prop in properties:
            writer.writerow([prop['id'], prop['property_type'], prop['address'], 
                            prop['price'], prop['sq_ft'], prop['cat_friendly'], 
                            prop['num_bedrooms'], prop['air_conditioning'], prop['parking_type'], 
                            prop['commute_morning'], prop['commute_midday'], prop['commute_evening']])
        
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
                'price': prop['price'],
                'sq_ft': prop['sq_ft'],
                'cat_friendly': bool(prop['cat_friendly']),
                'num_bedrooms': prop['num_bedrooms'],
                'air_conditioning': bool(prop['air_conditioning']),
                'parking_type': prop['parking_type'],
                'commute_morning': prop['commute_morning'],
                'commute_midday': prop['commute_midday'],
                'commute_evening': prop['commute_evening']
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
