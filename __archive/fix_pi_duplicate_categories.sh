#!/bin/bash
# Script to fix duplicate categories on the Raspberry Pi
# Created as part of fix/duplicate-categories branch

echo "Connecting to Pi to fix duplicate categories..."

# Define SSH connection
REMOTE_HOST="movingdb"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# First, upload our fix script to the Pi (in case sync hasn't run yet)
echo -e "${GREEN}[INFO]${NC} Uploading fix_duplicate_categories.py to Pi..."
scp fix_duplicate_categories.py $REMOTE_HOST:~/moving_box_tracker/

# Now run the script on the Pi
echo -e "${GREEN}[INFO]${NC} Running fix script on Pi..."
ssh -i ~/.ssh/id_rsa $REMOTE_HOST << 'EOF'
    cd ~/moving_box_tracker
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate movingbox
    python fix_duplicate_categories.py
    
    # Restart the service to apply changes
    echo "Restarting service..."
    sudo systemctl restart moving_boxes.service
    
    # Check service status
    echo "Service status:"
    sudo systemctl status moving_boxes.service --no-pager
EOF

echo -e "${GREEN}[INFO]${NC} Fix completed! Please verify the categories in the web interface."
