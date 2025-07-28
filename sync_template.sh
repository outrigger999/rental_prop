#!/bin/bash

# Flask + Nginx + Raspberry Pi Sync Script Template
# Version 3.0 - Prevention-First Approach
#
# This template prevents permission issues instead of fixing them afterward
# Copy this file for new projects and update the configuration section

# =============================================================================
# CONFIGURATION - UPDATE THESE FOR EACH NEW PROJECT
# =============================================================================
LOCAL_DIR="/Volumes/Projects/Python Projects/YOUR_PROJECT_NAME/"
REMOTE_HOST="movingdb"  # Your Pi hostname
REMOTE_USER="smashimo"  # Your Pi username  
REMOTE_DIR="~/YOUR_PROJECT_NAME/"
CONDA_ENV="YOUR_ENV_NAME"
PROJECT_PORT="YOUR_PORT"  # e.g., 6000, 7000, etc.
SERVICE_NAME="YOUR_PROJECT_NAME"  # Name for systemd service
NGINX_SITE_NAME="YOUR_PROJECT_NAME"  # Name for nginx site config

# =============================================================================
# SCRIPT LOGIC - NO CHANGES NEEDED BELOW THIS LINE
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Constants
VERSION="3.0"

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

# Display banner
print_banner() {
    echo -e "\n${GREEN}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  Flask Project Sync Script v${VERSION}            ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  Prevention-First Approach                  ${GREEN}║${NC}"
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
    echo "  --conda            Update conda environment"
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

# Display the script banner
print_banner

# If no branch was specified, use the current branch
if [ -z "$TARGET_BRANCH" ]; then
    TARGET_BRANCH="$CURRENT_BRANCH"
    print_message "Using current branch: $TARGET_BRANCH"
fi

if [ "$DRY_RUN" = true ]; then
    print_message "Performing a dry run (no changes will be made)"
    
    # Show what would be synced
    print_message "Files that would be synced:"
    rsync -avzn --delete \
        --chmod=D755,F644 \
        --chown=$REMOTE_USER:www-data \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude '*.db' \
        --exclude 'backups/' \
        --exclude 'logs/' \
        --exclude '.conda/' \
        -e ssh \
        "$LOCAL_DIR" \
        "$REMOTE_HOST:$REMOTE_DIR"
    exit 0
fi

# Confirm before proceeding
read -p "This will sync files to $REMOTE_HOST and restart services. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_message "Operation cancelled"
    exit 0
fi

# CRITICAL: Enhanced rsync that PREVENTS permission issues
print_message "Syncing files with correct permissions (prevention-first approach)..."
rsync -avz --delete \
    --chmod=D755,F644 \              # Directories 755, Files 644
    --chown=$REMOTE_USER:www-data \  # Correct ownership during transfer
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude '*.db' \
    --exclude 'backups/' \
    --exclude 'logs/' \
    --exclude '.conda/' \
    -e ssh \
    "$LOCAL_DIR" \
    "$REMOTE_HOST:$REMOTE_DIR"

if [ $? -ne 0 ]; then
    print_error "Failed to sync files to $REMOTE_HOST"
    exit 1
fi

print_message "Files synced successfully with correct permissions"

# Execute operations on Pi
print_message "Updating code, dependencies, and services on $REMOTE_HOST..."

ssh $REMOTE_HOST UPDATE_CONDA=$UPDATE_CONDA TARGET_BRANCH="$TARGET_BRANCH" CONDA_ENV="$CONDA_ENV" REMOTE_DIR="$REMOTE_DIR" SERVICE_NAME="$SERVICE_NAME" NGINX_SITE_NAME="$NGINX_SITE_NAME" PROJECT_PORT="$PROJECT_PORT" << 'EOF'
    # Define colors for SSH session
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m'
    
    # Set umask for consistent permissions
    umask 022
    
    echo -e "${GREEN}[INFO]${NC} Activating conda environment $CONDA_ENV..."
    source ~/miniconda3/etc/profile.d/conda.sh || { echo -e "${RED}[ERROR]${NC} Failed to source conda"; exit 1; }
    conda activate $CONDA_ENV || { echo -e "${RED}[ERROR]${NC} Failed to activate conda env $CONDA_ENV"; exit 1; }

    echo -e "${GREEN}[INFO]${NC} Changing to project directory $REMOTE_DIR..."
    cd $REMOTE_DIR

    # Git operations
    export GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa"
    echo -e "${GREEN}[INFO]${NC} Pulling latest changes from branch '$TARGET_BRANCH'..."
    git pull origin $TARGET_BRANCH || { echo -e "${RED}[ERROR]${NC} Git pull failed!"; exit 1; }
    echo -e "${GREEN}[INFO]${NC} Git pull successful."

    # VERIFICATION: Test that www-data can access static files
    # This should work due to enhanced rsync - if it fails, the rsync approach needs adjustment
    echo -e "${GREEN}[INFO]${NC} Verifying static file permissions..."
    if sudo -u www-data cat static/css/style.css > /dev/null 2>&1; then
        echo -e "${GREEN}[SUCCESS]${NC} Static file permissions verified - www-data can access files"
    else
        echo -e "${RED}[WARNING]${NC} www-data cannot access static files - rsync permissions may need adjustment"
        echo -e "${YELLOW}[INFO]${NC} This indicates the prevention approach needs refinement"
    fi

    # Generate deployment timestamp
    echo -e "${GREEN}[INFO]${NC} Generating deployment timestamp..."
    CURRENT_TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S') (from sync script)"
    echo "$CURRENT_TIMESTAMP" > deployment_timestamp.txt
    echo -e "${GREEN}[INFO]${NC} Timestamp generated: $CURRENT_TIMESTAMP"

    # Update dependencies if requested
    if [ "$UPDATE_CONDA" = "true" ]; then
        echo -e "${GREEN}[INFO]${NC} Updating conda environment dependencies..."
        conda env update --file environment.yml --prune 2>/dev/null || pip install -r requirements.txt
        echo -e "${GREEN}[INFO]${NC} Dependencies updated."
    fi

    # Install/update systemd service
    if [ -f "${SERVICE_NAME}.service" ]; then
        echo -e "${GREEN}[INFO]${NC} Installing/updating systemd service..."
        sudo cp ${SERVICE_NAME}.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        echo -e "${GREEN}[INFO]${NC} Service installed/updated."
    fi

    # Install/update nginx configuration
    if [ -f "nginx.conf" ]; then
        echo -e "${GREEN}[INFO]${NC} Installing/updating nginx configuration..."
        sudo cp nginx.conf /etc/nginx/sites-available/$NGINX_SITE_NAME
        sudo chmod 644 /etc/nginx/sites-available/$NGINX_SITE_NAME
        sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE_NAME /etc/nginx/sites-enabled/
        
        # Test and reload nginx
        echo -e "${GREEN}[INFO]${NC} Testing nginx configuration..."
        sudo nginx -t && sudo systemctl reload nginx
        echo -e "${GREEN}[INFO]${NC} Nginx configuration updated and reloaded."
    fi

    # Restart the application service
    echo -e "${GREEN}[INFO]${NC} Restarting application service..."
    sudo systemctl restart $SERVICE_NAME
    
    # Check service status
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}[SUCCESS]${NC} Service $SERVICE_NAME is running"
    else
        echo -e "${RED}[ERROR]${NC} Service $SERVICE_NAME failed to start"
        sudo systemctl status $SERVICE_NAME --no-pager
        exit 1
    fi

    echo -e "${GREEN}[SUCCESS]${NC} All operations completed successfully"
EOF

if [ $? -eq 0 ]; then
    print_message "Deployment completed successfully!"
    print_message "Your application should be accessible on port $PROJECT_PORT"
    print_message "Check the deployment timestamp on your site to confirm the update"
else
    print_error "Deployment failed! Check the error messages above."
    exit 1
fi
