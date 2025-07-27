# Manage Categories Functionality Restoration

## Problem

The "Manage Categories" button and functionality were missing from the Moving Box Tracker application due to an earlier code edit that accidentally removed several critical functions and routes.

## Root Causes

1. **Missing Functions & Routes**: A previous code edit to remove a duplicate function in `simplified_app.py` accidentally removed:
   - `count_boxes_using_category` function
   - `delete_category` function
   - `manage_categories` route
   - `api_delete_category` endpoint

2. **API Data Handling Issues**: The API endpoint for adding categories was only set up to handle JSON data, while the form was submitting URL-encoded data.

3. **Missing Category Data Field**: The categories template expected a `created_at` field for each category, but it wasn't being provided by our database query.

## Solutions Implemented

### 1. Restored Missing Functions

Added back the following functions that were accidentally removed:

```python
def count_boxes_using_category(category_id):
    """Count how many boxes use a specific category"""
    result = query_db('SELECT COUNT(*) FROM boxes WHERE category_id = ?', [category_id], one=True)
    return result[0] if result else 0


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
```

### 2. Restored and Fixed the Manage Categories Route

Added back the route with improved query to handle the `created_at` field:

```python
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
    return render_template('categories.html', categories=categories_with_usage)
```

### 3. Restored API Endpoint for Category Deletion

Added back the API endpoint for deleting categories:

```python
@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id):
    """Delete a category via API"""
    success, message = delete_category(category_id)
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 400
```

### 4. Fixed API Data Handling

Modified the API endpoint to handle both JSON and form-encoded data:

```python
@app.route('/api/categories', methods=['POST'])
def api_add_category():
    # Handle both JSON and form-encoded data
    if request.is_json:
        data = request.get_json()
        name = (data.get('name') or '').strip()
    else:
        name = (request.form.get('name') or '').strip()
        
    if not name:
        return jsonify({'success': False, 'error': 'Category name is required'}), 400

    # Check for duplicate
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id FROM categories WHERE name = ?', (name,))
    existing = cur.fetchone()
    if existing:
        return jsonify({'success': False, 'error': 'Category already exists'}), 400

    # Insert new category
    cur.execute('INSERT INTO categories (name, created_at) VALUES (?, CURRENT_TIMESTAMP)', (name,))
    conn.commit()
    new_id = cur.lastrowid
    return jsonify({'success': True, 'id': new_id, 'name': name}), 200
```

### 5. Added Management Button to UI

Added a "Manage Categories" button (gear icon) to the create.html template:

```html
<a href="{{ url_for('manage_categories') }}" class="btn btn-outline-primary" title="Manage all categories">
    <i class="bi bi-gear"></i>
</a>
```

## Testing Performed

The following functionality was tested and confirmed working:

1. **Quick Category Button**: Works correctly - opens modal and allows adding new categories
2. **Create Box Button**: Works correctly - creates new boxes with assigned categories
3. **Delete Box Button**: Works correctly - removes boxes from the database
4. **Manage Categories**: Works correctly - displays all categories with usage counts and allows:
   - Adding new categories
   - Viewing existing categories with their usage
   - Deleting unused categories

## Branch Information

All changes were developed in the `fix/restore-manage-categories-button` branch and merged into the `stable/2025-05-28` branch after successful testing.

## Future Considerations

1. **Backup Functions**: Consider implementing category backup functions to prevent accidental data loss.
2. **UI Improvements**: The category management UI could be enhanced with search functionality for large category lists.
3. **Validation**: More robust form validation could be added to prevent duplicate categories or invalid names.
