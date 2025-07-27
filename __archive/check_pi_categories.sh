#!/bin/bash
# Script to check and fix duplicate categories directly on the Pi database

# Define SSH connection
REMOTE_HOST="movingdb"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[INFO]${NC} Connecting to Pi to check categories..."

# Run SQL commands directly on the Pi database
ssh -i ~/.ssh/id_rsa $REMOTE_HOST << 'EOF'
    cd ~/moving_box_tracker
    echo "=== Categories in database ==="
    sqlite3 moving_boxes.db "SELECT id, name FROM categories WHERE name LIKE '%Scott%Office%' ORDER BY id;"
    
    echo -e "\n=== Checking for duplicate categories ==="
    sqlite3 moving_boxes.db "SELECT name, COUNT(*) as count, GROUP_CONCAT(id) as ids FROM categories GROUP BY name HAVING count > 1;"
    
    echo -e "\n=== Do you want to fix duplicates? (y/n) ==="
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Fixing duplicates..."
        # Find duplicates and fix them directly with SQL
        DUPE_CATS=$(sqlite3 moving_boxes.db "SELECT name, GROUP_CONCAT(id) FROM categories GROUP BY name HAVING COUNT(*) > 1;")
        
        if [ -z "$DUPE_CATS" ]; then
            echo "No duplicate categories found in SQL query result."
            exit 0
        fi
        
        echo "$DUPE_CATS" | while IFS="|" read -r name ids; do
            echo "Found duplicate for: $name with IDs: $ids"
            # Get the first ID (lowest) to keep
            keep_id=$(echo $ids | cut -d, -f1)
            # Get the rest of the IDs to delete
            remove_ids=$(echo $ids | sed "s/$keep_id,//g" | sed "s/,$keep_id//g" | sed "s/$keep_id//g")
            
            if [ -z "$remove_ids" ]; then
                echo "No duplicate IDs to remove for $name"
                continue
            fi
            
            echo "Keeping ID $keep_id and removing IDs: $remove_ids"
            
            # Update each ID that needs to be removed
            for remove_id in $(echo $remove_ids | tr ',' ' '); do
                echo "Updating boxes with category_id=$remove_id to use category_id=$keep_id"
                sqlite3 moving_boxes.db "UPDATE boxes SET category_id = $keep_id WHERE category_id = $remove_id;"
                echo "Deleting category with ID $remove_id"
                sqlite3 moving_boxes.db "DELETE FROM categories WHERE id = $remove_id;"
            done
        done
        
        echo "Restarting service..."
        sudo systemctl restart moving_boxes.service
        
        echo "Fix completed! Duplicate categories have been removed."
    else
        echo "No changes made."
    fi
EOF

echo -e "${GREEN}[INFO]${NC} Script completed!"
