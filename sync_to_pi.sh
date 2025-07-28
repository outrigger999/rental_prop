#!/bin/bash

# Rental Property Tracker Sync Script
# Version 1.0
#
# This script syncs the project files to the Raspberry Pi and restarts the service
# It includes a dry-run option, better error handling, conda environment support,
# branch detection, and reverse sync for database and uploads

# Configuration
LOCAL_DIR="/Volumes/Projects/Python Projects/rental_prop/" # Updated to current project path
REMOTE_HOST="movingdb"  # Using hostname for SSH authentication
REMOTE_IP="192.168.10.10"  # Actual IP for direct URL access
REMOTE_USER="smashimo"  # Username for SSH connection
REMOTE_DIR="~/rental_prop/"  # Project directory on Pi
CONDA_ENV="rental_prop_env"
GITHUB_REPO="https://github.com/outrigger999/rental_prop.git"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Constants
VERSION="1.0"

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
    echo -e "${GREEN}║${NC}  Rental Property Tracker Sync Script v${VERSION}       ${GREEN}║${NC}"
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

# --- Main Deployment via Git Pull on Pi ---
if [ "$DRY_RUN" = true ]; then
    print_message "DRY RUN: Would execute Git pull and service restart on Pi"
else
    print_message "Pulling latest changes from branch '$TARGET_BRANCH', updating dependencies, and restarting service on $REMOTE_HOST..."

    ssh $REMOTE_USER@$REMOTE_HOST UPDATE_CONDA=$UPDATE_CONDA TARGET_BRANCH="$TARGET_BRANCH" CONDA_ENV="$CONDA_ENV" << 'EOF'
        # Define colors directly in the SSH session
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        RED='\033[0;31m'
        NC='\033[0m' # No Color
        
        echo -e "${GREEN}[INFO]${NC} Activating conda environment $CONDA_ENV..."
        # Source conda setup script
        source ~/miniconda3/etc/profile.d/conda.sh || { echo -e "${RED}[ERROR]${NC} Failed to source conda setup"; exit 1; }
        conda activate "$CONDA_ENV" || { echo -e "${RED}[ERROR]${NC} Failed to activate conda env $CONDA_ENV"; exit 1; }

        echo -e "${GREEN}[INFO]${NC} Changing to project directory ~/rental_prop..."
        cd ~/rental_prop || { echo -e "${RED}[ERROR]${NC} Could not cd to project directory!"; exit 1; }

        # Explicitly tell Git to use the SSH key
        export GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa"

        # Reset any local changes and pull latest from Git
        echo -e "${GREEN}[INFO]${NC} Resetting local changes..."
        git reset --hard HEAD
        git clean -fd
        
        # Check current branch and switch to target branch if needed
        CURRENT_PI_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        if [ "$CURRENT_PI_BRANCH" != "$TARGET_BRANCH" ]; then
            echo -e "${YELLOW}[WARNING]${NC} Pi is on '$CURRENT_PI_BRANCH' branch, switching to '$TARGET_BRANCH' branch..."
            git fetch origin
            git checkout $TARGET_BRANCH || git checkout -b $TARGET_BRANCH origin/$TARGET_BRANCH || { echo -e "${RED}[ERROR]${NC} Failed to switch to $TARGET_BRANCH branch!"; exit 1; }
            echo -e "${GREEN}[INFO]${NC} Successfully switched to '$TARGET_BRANCH' branch."
        fi
        
        echo -e "${GREEN}[INFO]${NC} Pulling latest changes from branch '$TARGET_BRANCH'..."
        git pull origin $TARGET_BRANCH || { echo -e "${RED}[ERROR]${NC} Git pull failed for branch '$TARGET_BRANCH'!"; exit 1; }
        echo -e "${GREEN}[INFO]${NC} Git pull from branch '$TARGET_BRANCH' successful."

        # Fix permissions for static files
        echo -e "${GREEN}[INFO]${NC} Fixing static file permissions..."
        if [ -d "static" ]; then
            find static -type d -exec chmod 755 {} \;
            find static -type f -exec chmod 644 {} \;
            echo -e "${GREEN}[INFO]${NC} Static file permissions fixed."
        fi
        
        # Generate deployment timestamp
        echo -e "${GREEN}[INFO]${NC} Generating deployment timestamp..."
        CURRENT_TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S') (from sync_to_pi.sh)"
        echo "$CURRENT_TIMESTAMP" > deployment_timestamp.txt
        echo -e "${GREEN}[INFO]${NC} Timestamp generated: $CURRENT_TIMESTAMP"

        # Update dependencies if requested
        if [ "$UPDATE_CONDA" = "true" ]; then
            echo -e "${GREEN}[INFO]${NC} Updating conda environment dependencies..."
            conda env update -f environment.yml || pip install -r requirements.txt || echo -e "${YELLOW}[WARNING]${NC} Could not update dependencies"
        fi

        # Install/update systemd service file
        echo -e "${GREEN}[INFO]${NC} Installing/updating systemd service file..."
        if [ -f "rental_prop.service" ]; then
            sudo cp rental_prop.service /etc/systemd/system/
            sudo systemctl daemon-reload
            echo -e "${GREEN}[INFO]${NC} Systemd service file installed/updated."
        else
            echo -e "${YELLOW}[WARNING]${NC} rental_prop.service file not found in repository"
        fi

        # Install/update nginx configuration
        echo -e "${GREEN}[INFO]${NC} Installing/updating nginx configuration..."
        if [ -f "nginx.conf" ]; then
            sudo cp nginx.conf /etc/nginx/sites-available/rental
            sudo ln -sf /etc/nginx/sites-available/rental /etc/nginx/sites-enabled/
            sudo nginx -t && sudo systemctl reload nginx
            echo -e "${GREEN}[INFO]${NC} Nginx configuration installed/updated."
        else
            echo -e "${YELLOW}[WARNING]${NC} nginx.conf file not found in repository"
        fi

        # Stop the service
        echo -e "${GREEN}[INFO]${NC} Stopping rental_prop service..."
        sudo systemctl stop rental_prop || echo -e "${YELLOW}[WARNING]${NC} Service may not be running"

        # Start the service
        echo -e "${GREEN}[INFO]${NC} Starting rental_prop service..."
        sudo systemctl start rental_prop || { echo -e "${RED}[ERROR]${NC} Failed to start service!"; exit 1; }

        # Enable the service for auto-start
        sudo systemctl enable rental_prop || echo -e "${YELLOW}[WARNING]${NC} Could not enable service for auto-start"

        # Check service status
        echo -e "${GREEN}[INFO]${NC} Checking service status..."
        sudo systemctl status rental_prop --no-pager -l || echo -e "${YELLOW}[WARNING]${NC} Could not get service status"

        echo -e "${GREEN}[INFO]${NC} Deployment completed successfully!"
EOF

    if [ $? -eq 0 ]; then
        print_message "Deployment completed successfully!"
        print_message "Application should be accessible at: http://$REMOTE_IP:6000"
        print_message "You can also access it via hostname: http://$REMOTE_HOST:6000"
    else
        print_error "Deployment failed!"
        exit 1
    fi
fi

print_message "Sync script completed."
