#!/bin/bash
# Direct fix script specifically for Scott's Office duplicate

echo "Connecting to Pi to fix Scott's Office duplicate..."

# Execute precise SQL commands to fix the issue
ssh movingdb << 'EOF'
    cd ~/moving_box_tracker
    echo "Before fix:"
    sqlite3 moving_boxes.db "SELECT id, name FROM categories WHERE name = 'Scott''s Office';"
    
    # Update all boxes using category ID 27 to use ID 1 instead
    echo "Updating boxes..."
    sqlite3 moving_boxes.db "UPDATE boxes SET category_id = 1 WHERE category_id = 27;"
    
    # Delete the duplicate category
    echo "Deleting duplicate category..."
    sqlite3 moving_boxes.db "DELETE FROM categories WHERE id = 27;"
    
    echo "After fix:"
    sqlite3 moving_boxes.db "SELECT id, name FROM categories WHERE name = 'Scott''s Office';"
    
    # Restart the service
    echo "Restarting service..."
    sudo systemctl restart moving_boxes.service
EOF

echo "Fix completed! Please check the web interface."
