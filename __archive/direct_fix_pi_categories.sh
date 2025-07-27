#!/bin/bash
# Non-interactive script to directly fix duplicate categories on the Pi

# Define SSH connection
REMOTE_HOST="movingdb"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[INFO]${NC} Connecting to Pi to fix categories..."

# Run non-interactive SQL commands directly on the Pi database
ssh -i ~/.ssh/id_rsa $REMOTE_HOST << 'EOF'
    cd ~/moving_box_tracker
    echo "=== Categories with 'Scott' in the name ==="
    sqlite3 moving_boxes.db "SELECT id, name FROM categories WHERE name LIKE '%Scott%' ORDER BY id;"
    
    echo -e "\n=== Direct SQL Fix for Duplicate Scott's Office ==="
    # Direct fix for Scott's Office - assuming ID 1 is the one to keep
    # First, identify all Scott's Office categories
    SCOTT_CATS=$(sqlite3 moving_boxes.db "SELECT id FROM categories WHERE name LIKE 'Scott''s Office' ORDER BY id;")
    
    if [ -z "$SCOTT_CATS" ]; then
        echo "No 'Scott's Office' categories found."
    else
        # Get the first ID to keep
        read -r keep_id rest_ids <<< "$SCOTT_CATS"
        echo "Found 'Scott's Office' categories. Keeping ID $keep_id."
        
        # Process each remaining ID
        for id in $rest_ids; do
            echo "Updating boxes using category ID $id to use ID $keep_id"
            sqlite3 moving_boxes.db "UPDATE boxes SET category_id = $keep_id WHERE category_id = $id;"
            echo "Deleting duplicate category ID $id"
            sqlite3 moving_boxes.db "DELETE FROM categories WHERE id = $id;"
        done
    fi
    
    echo -e "\n=== Checking for other duplicate categories ==="
    DUPE_CATS=$(sqlite3 moving_boxes.db "SELECT name, GROUP_CONCAT(id) FROM categories GROUP BY name HAVING COUNT(*) > 1;")
    
    if [ -z "$DUPE_CATS" ]; then
        echo "No other duplicate categories found."
    else
        echo "$DUPE_CATS" | while IFS="|" read -r name ids; do
            echo "Found duplicate for: $name with IDs: $ids"
            # Get the first ID (lowest) to keep
            keep_id=$(echo $ids | cut -d, -f1)
            # Get the rest of the IDs to delete
            remove_ids=$(echo $ids | cut -d, -f2-)
            
            echo "Keeping ID $keep_id and removing IDs: $remove_ids"
            
            # Update each ID that needs to be removed
            for remove_id in $(echo $remove_ids | tr ',' ' '); do
                echo "Updating boxes with category_id=$remove_id to use category_id=$keep_id"
                sqlite3 moving_boxes.db "UPDATE boxes SET category_id = $keep_id WHERE category_id = $remove_id;"
                echo "Deleting category with ID $remove_id"
                sqlite3 moving_boxes.db "DELETE FROM categories WHERE id = $remove_id;"
            done
        done
    fi
    
    echo -e "\n=== Verification after fix ==="
    sqlite3 moving_boxes.db "SELECT id, name FROM categories WHERE name LIKE '%Scott%' ORDER BY id;"
    echo
    sqlite3 moving_boxes.db "SELECT name, COUNT(*) FROM categories GROUP BY name HAVING COUNT(*) > 1;"
    
    echo -e "\n=== Restarting service ==="
    sudo systemctl restart moving_boxes.service
    
    echo "Fix completed! Please check the web interface."
EOF

echo -e "${GREEN}[INFO]${NC} Script completed!"
