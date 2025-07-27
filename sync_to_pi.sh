#!/bin/bash

# Rental Property Tracker Sync Script
#
# This script syncs the project files to the Raspberry Pi and manages the service.
# It includes a dry-run option, better error handling, conda environment support,
# branch detection, and reverse sync for database and uploads.

# Configuration
LOCAL_DIR="$(pwd)/" # Current working directory
REMOTE_HOST="movingdb"  # Using hostname for SSH authentication
RPI_USER="smashimo"  # Username for SSH connection
REMOTE_USER="smashimo"  # Username for SSH connection
REMOTE_DIR="/home/${REMOTE_USER}/rental_prop/"  # Project directory on Pi
CONDA_ENV="rental_prop_env"
GITHUB_REPO="https://github.com/outrigger999/rental_prop.git"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Constants
VERSION="1.0" # Initial version for Rental Property Tracker

# Function to display messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Display banner function
print_banner() {
    echo -e "\n${GREEN}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  Rental Property Tracker Sync Script v${VERSION}  ${GREEN}║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════╝${NC}\n"
}

# Parse command line arguments
DRY_RUN=false
UPDATE_CONDA=false
TARGET_BRANCH=""

# Get the current branch by default
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --dry-run          Show what would be synced without making changes"
    echo "  --conda            Update conda environment (slower but ensures all dependencies)"
    echo "  --branch=BRANCH    Specify which branch to deploy (default: current branch '$CURRENT_BRANCH')"
    echo "  --help             Show this help message"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --conda)
            UPDATE_CONDA=true
            shift
            ;;
        --branch=*)
            TARGET_BRANCH="${1#*=}"
            print_message "Using branch: $TARGET_BRANCH"
            shift
            ;;
        --help)
            print_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done

# Display the script banner first thing
print_banner

# If no branch was specified, use the current branch
if [ -z "$TARGET_BRANCH" ]; then
    TARGET_BRANCH="$CURRENT_BRANCH"
    print_message "Using current branch: $TARGET_BRANCH"
fi

if [ "$DRY_RUN" = true ]; then
    print_message "Performing a dry run (no changes will be made)"
else
    # Confirm before proceeding
    read -p "This will sync files to $REMOTE_HOST and restart the service. Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_message "Operation cancelled"
        exit 0
    fi
fi

# --- Git Operations (Local) ---
print_message "Pushing local changes to GitHub..."
git add .
git commit -m "Syncing changes to Pi via sync_to_pi.sh" || print_warning "No local changes to commit or commit failed."
git push origin "$TARGET_BRANCH" || { print_error "Failed to push to GitHub!"; exit 1; }
print_message "Local changes pushed to GitHub."

# --- Reverse Sync (FROM Pi to Local) ---
# Sync database and uploads from Pi to local
if [ "$DRY_RUN" = true ]; then
    print_message "DRY RUN: Database and uploads that would be synced FROM Pi:"
    ssh $REMOTE_USER@$REMOTE_HOST "ls -la ${REMOTE_DIR}rental_properties.db 2>/dev/null || echo 'No database file found on Pi'"
    ssh $REMOTE_USER@$REMOTE_HOST "ls -la ${REMOTE_DIR}static/uploads/ 2>/dev/null || echo 'No uploads directory found on Pi'"
else
    print_message "Syncing database and uploads FROM $REMOTE_HOST to local..."
    
    # Sync database file from Pi (if it exists and is newer)
    if ssh $REMOTE_USER@$REMOTE_HOST "test -f ${REMOTE_DIR}rental_properties.db"; then
        print_message "Found database on Pi, syncing to local..."
        rsync -avz --update -e ssh "$REMOTE_USER@$REMOTE_HOST:${REMOTE_DIR}rental_properties.db" "$LOCAL_DIR"
        if [ $? -eq 0 ]; then
            print_message "Database synced successfully from Pi"
        else
            print_warning "Failed to sync database from Pi, but continuing..."
        fi
    else
        print_warning "No database file found on Pi"
    fi
    
    # Sync uploads directory from Pi (if it exists)
    if ssh $REMOTE_USER@$REMOTE_HOST "test -d ${REMOTE_DIR}static/uploads"; then
        print_message "Found uploads directory on Pi, syncing to local..."
        mkdir -p "${LOCAL_DIR}static/uploads" # Create local uploads directory if it doesn't exist
        rsync -avz --update -e ssh "$REMOTE_USER@$REMOTE_HOST:${REMOTE_DIR}static/uploads/" "${LOCAL_DIR}static/uploads/"
        if [ $? -eq 0 ]; then
            print_message "Uploads synced successfully from Pi"
        else
            print_warning "Failed to sync uploads from Pi, but continuing..."
        fi
    else
        print_warning "No uploads directory found on Pi"
    fi
fi

# --- Main Sync (TO Pi) ---
if [ "$DRY_RUN" = true ]; then
    print_message "DRY RUN: Files that would be synced TO Pi:"
    rsync -avzn --delete \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude '*.db' \
        --exclude 'static/uploads/' \
        --exclude '.last_req_checksum' \
        --exclude '.conda/' \
        -e ssh \
        "$LOCAL_DIR" \
        "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
else
    print_message "Syncing files TO $REMOTE_HOST..."
    rsync -avz --delete \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude '*.db' \
        --exclude 'static/uploads/' \
        --exclude '.last_req_checksum' \
        --exclude '.conda/' \
        -e ssh \
        "$LOCAL_DIR" \
        "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
    
    if [ $? -ne 0 ]; then
        print_error "Failed to sync files to $REMOTE_HOST"
        exit 1
    fi
    
    print_message "Executing remote commands on $REMOTE_HOST..."

    ssh $REMOTE_USER@$REMOTE_HOST UPDATE_CONDA=$UPDATE_CONDA TARGET_BRANCH="$TARGET_BRANCH" CONDA_ENV="$CONDA_ENV" REMOTE_DIR="$REMOTE_DIR" << 'EOF'
        # Define colors directly in the SSH session
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        RED='\033[0;31m'
        NC='\033[0m' # No Color
        
        print_message() { echo -e "${GREEN}[INFO]${NC} $1"; }
        print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
        print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

        # Ensure we are in the project directory
        cd "$REMOTE_DIR" || { print_error "Could not cd to project directory!"; exit 1; }

        # --- Conda Environment Management ---
        print_message "Managing Conda environment '$CONDA_ENV'..."
        # Source conda setup script
        source /home/smashimo/miniconda3/etc/profile.d/conda.sh || { print_error "Failed to source miniconda3/etc/profile.d/conda.sh. Is Miniconda installed?"; exit 1; }
        
        # Check if environment exists
        if ! conda env list | grep -q "$CONDA_ENV"; then
            print_message "Conda environment '$CONDA_ENV' not found. Creating it..."
            conda create -n "$CONDA_ENV" python=3.9 -y || { print_error "Failed to create conda environment '$CONDA_ENV'!"; exit 1; }
        fi
        
        conda activate "$CONDA_ENV" || { print_error "Failed to activate conda env '$CONDA_ENV'!"; exit 1; }

        # Generate environment.yml from requirements.txt for robust conda updates
        print_message "Generating environment.yml from requirements.txt..."
        # This is a simplified approach. For complex dependencies, `conda env export` is better.
        # But for simple Flask apps, pip requirements are often sufficient.
        # If you need to manage conda-specific packages, you'd manually create environment.yml
        # or use `conda env export --from-history` on a working local env.
        echo "name: $CONDA_ENV" > environment.yml
        echo "channels:" >> environment.yml
        echo "  - defaults" >> environment.yml
        echo "dependencies:" >> environment.yml
        echo "  - python=3.9" >> environment.yml # Ensure Python version
        while IFS= read -r line; do
            if [[ ! -z "$line" && ! "$line" =~ ^# ]]; then # Ignore empty lines and comments
                echo "  - pip" >> environment.yml
                echo "  - pip:" >> environment.yml
                echo "    - $line" >> environment.yml
            fi
        done < requirements.txt

        if [ "$UPDATE_CONDA" = true ]; then
            print_message "Updating conda environment '$CONDA_ENV' with environment.yml..."
            conda env update -f environment.yml --prune || { print_error "Failed to update conda environment!"; exit 1; }
            print_message "Conda environment updated successfully."
        else
            print_message "Installing/updating pip requirements (use --conda for full conda env update)..."
            pip install -r requirements.txt || { print_error "Failed to install pip requirements!"; exit 1; }
        fi
        print_message "Dependencies installed/updated."

        # --- Git Operations (Remote) ---
        print_message "Resetting local changes on Pi..."
        git reset --hard HEAD
        git clean -fd
        print_message "Pulling latest changes from branch '$TARGET_BRANCH'..."
        git pull origin "$TARGET_BRANCH" || { print_error "Git pull failed for branch '$TARGET_BRANCH'!"; exit 1; }
        print_message "Git pull from branch '$TARGET_BRANCH' successful."

        # --- Permissions Fix ---
        print_message "Fixing static and template file permissions..."
        # Fix directory permissions (755 = rwxr-xr-x) for both static and templates
        print_message "Setting directory permissions to 755..."
        find static templates -type d -exec chmod 755 {} \; || { print_error "Failed to set directory permissions!"; exit 1; }
        
        # Fix file permissions (644 = rw-r--r--) for both static and templates
        print_message "Setting file permissions to 644..."
        find static templates -type f -exec chmod 644 {} \; || { print_error "Failed to set file permissions!"; exit 1; }
        
        # Fix ownership for both static and templates
        print_message "Setting correct ownership..."
        sudo chown -R "$REMOTE_USER":www-data "$REMOTE_DIR"static/ "$REMOTE_DIR"templates/ || { print_error "Failed to set ownership!"; exit 1; }
        sudo chmod -R g+r "$REMOTE_DIR"static/ "$REMOTE_DIR"templates/ || { print_error "Failed to set group read permissions!"; exit 1; }
        
        # Fix parent directory permissions
        print_message "Setting parent directory permissions..."
        sudo chmod o+rx "/home/$REMOTE_USER" || { print_error "Failed to set home directory permissions!"; exit 1; }
        sudo chmod o+rx "$REMOTE_DIR" || { print_error "Failed to set project directory permissions!"; exit 1; }
        
        print_message "Permissions and ownership fixed."

        # --- Database Schema Check ---
        print_message "Checking database schema..."
        if [ ! -f rental_properties.db ]; then
            print_message "Database not found, initializing schema..."
            sqlite3 rental_properties.db < schema.sql || { print_error "Failed to initialize schema!"; exit 1; }
            print_message "Schema initialized successfully."
        fi

        # --- Service Management (Systemd) ---
        # This assumes a systemd service file named rental_prop.service will be created
        SERVICE_NAME="rental_prop.service"
        PROJECT_SERVICE_FILE="${REMOTE_DIR}${SERVICE_NAME}"
        SYSTEMD_SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"
        SERVICE_FILE_UPDATED=false

        if [ -f "$PROJECT_SERVICE_FILE" ]; then
            if sudo test "$PROJECT_SERVICE_FILE" -nt "$SYSTEMD_SERVICE_FILE" 2>/dev/null; then
                print_message "Project service file is newer, updating systemd service file..."
                sudo cp "$PROJECT_SERVICE_FILE" "$SYSTEMD_SERVICE_FILE" || { print_error "Failed to copy service file!"; exit 1; }
                print_message "Systemd service file updated."
                SERVICE_FILE_UPDATED=true
            else
                print_message "Systemd service file is up-to-date."
            fi
        else
            print_warning "Project service file ($PROJECT_SERVICE_FILE) not found. Cannot update systemd service file automatically."
        fi

        if [ "$SERVICE_FILE_UPDATED" = true ]; then
            print_message "Reloading systemd daemon..."
            sudo systemctl daemon-reload || { print_error "Failed to reload systemd daemon!"; exit 1; }
            print_message "Systemd daemon reloaded."
            
            print_message "Enabling service '$SERVICE_NAME'..."
            sudo systemctl enable "$SERVICE_NAME" || { print_error "Failed to enable service!"; exit 1; }
            print_message "Service enabled."
        fi

        print_message "Restarting service '$SERVICE_NAME'..."
        sudo systemctl restart "$SERVICE_NAME" || { print_error "Failed to restart service!"; exit 1; }
        print_message "Service restart command sent."

        # Check service status with retry
        print_message "Waiting for service to become active..."
        RETRY_COUNT=0
        MAX_RETRIES=10 # Try for ~30 seconds
        DELAY=3       # Seconds between retries

        while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
            SERVICE_STATUS=$(systemctl is-active "$SERVICE_NAME")
            if [ "$SERVICE_STATUS" == "active" ]; then
                 print_message "Service is active."
                 break
            fi
            SERVICE_FAILED=$(systemctl is-failed "$SERVICE_NAME")
            if [ "$SERVICE_FAILED" == "failed" ]; then
                 print_error "Service entered failed state."
                 sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager # Show logs on failure
                 exit 1 # Exit SSH sub-shell with error
            fi
            
            print_message "Service status: $SERVICE_STATUS. Retrying in $DELAY seconds..."
            sleep $DELAY
            RETRY_COUNT=$((RETRY_COUNT + 1))
        done

        FINAL_STATUS=$(systemctl is-active "$SERVICE_NAME")
        if [ "$FINAL_STATUS" != "active" ]; then
            print_error "Service failed to become active after $MAX_RETRIES retries."
            print_error "Final status: $FINAL_STATUS"
            sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager # Show logs on timeout
            exit 1 # Exit SSH sub-shell with error
        fi

        # --- Nginx Configuration Update ---
        # This assumes an nginx.conf file will be created in the project root
        print_message "Updating nginx configuration..."
        sudo cp "${REMOTE_DIR}nginx.conf" "/etc/nginx/sites-available/rental_prop" || { print_error "Failed to copy nginx config!"; exit 1; }
        sudo ln -sf "/etc/nginx/sites-available/rental_prop" "/etc/nginx/sites-enabled/rental_prop"
        sudo nginx -t || { print_error "Nginx config test failed!"; exit 1; }
        sudo systemctl restart nginx || { print_error "Failed to restart nginx!"; exit 1; }
        print_message "Nginx configuration updated and restarted."

        print_message "Remote operations completed successfully."
EOF

    # Check the exit status of the SSH command block
    SSH_EXIT_CODE=$?
    if [ $SSH_EXIT_CODE -ne 0 ]; then
        print_error "SSH command block failed with exit code $SSH_EXIT_CODE"
        exit 1
    fi

    print_message "Deployment completed successfully!"
    print_message "You can access the application at http://${REMOTE_HOST}.box:5000 (or your configured domain)"
fi

</file_content>
</error><environment_details>
# VSCode Visible Files
sync_to_pi.sh

# VSCode Open Tabs
project-metadata.json
context_index.json
feature-roadmap.json
market-analysis.json
strategic-content.json
technical-architecture.json
user-personas.json
app.py
templates/index.html
templates/add_property.html
static/css/style.css
requirements.txt
rental_prop.service
nginx.conf
sync_to_pi.sh

# Current Time
7/27/2025, 11:18:12 AM (Pacific/Honolulu, UTC-10:00)

# Context Window Usage
101,686 / 1,048.576K tokens used (10%)

# Current Mode
ACT MODE
</environment_details>
