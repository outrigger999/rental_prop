from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

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

@app.route('/')
def index():
    conn = get_db_connection()
    properties = conn.execute('SELECT * FROM properties').fetchall()
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

if __name__ == '__main__':
    app.run(debug=True)
