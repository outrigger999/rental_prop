# Flask + Nginx + Raspberry Pi Project Template

## How to Clone This Project and Avoid Permission Issues

This guide ensures you can replicate this project setup without encountering the nginx static file permission issues that took extensive troubleshooting to resolve.

## Project Template Structure

### 1. Essential Files to Copy
```
your_new_project/
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── nginx.conf                      # Nginx configuration template
├── your_project.service           # Systemd service file
├── sync_to_pi.sh                  # Enhanced deployment script
├── static/
│   ├── css/
│   └── js/
├── templates/
├── windsurf_docs/
│   ├── nginx_permissions_troubleshooting.md
│   └── improved_sync_strategies.md
└── userInstructions/
    └── permissions_fix_reference.md
```

### 2. Key Configuration Changes for New Project

#### A. Update nginx.conf
```nginx
server {
    listen 80;
    server_name your_new_domain.box;  # Change this
    
    location / {
        proxy_pass http://localhost:YOUR_PORT;  # Change port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /home/smashimo/your_new_project/static/;  # Change path
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
}
```

#### B. Update systemd service file
```ini
[Unit]
Description=Gunicorn instance for Your New Project
After=network.target

[Service]
User=smashimo
Group=www-data
WorkingDirectory=/home/smashimo/your_new_project  # Change path
Environment="PATH=/home/smashimo/miniconda3/envs/your_env/bin"  # Change env
ExecStart=/home/smashimo/miniconda3/envs/your_env/bin/gunicorn --workers 4 --bind 0.0.0.0:YOUR_PORT app:app  # Change port
Restart=always

[Install]
WantedBy=multi-user.target
```

#### C. Update sync_to_pi.sh variables
```bash
# Configuration - UPDATE THESE FOR NEW PROJECT
LOCAL_DIR="/Volumes/Projects/Python Projects/your_new_project/"
REMOTE_HOST="movingdb"  # or your Pi hostname
REMOTE_USER="smashimo"  # or your Pi username
REMOTE_DIR="~/your_new_project/"
CONDA_ENV="your_env_name"
PROJECT_PORT="YOUR_PORT"
```

## Enhanced Sync Script Template

### The Key: Prevention-First Approach

```bash
#!/bin/bash

# Enhanced Sync Script Template
# This version PREVENTS permission issues instead of fixing them afterward

# Configuration - UPDATE FOR EACH PROJECT
LOCAL_DIR="/Volumes/Projects/Python Projects/YOUR_PROJECT/"
REMOTE_HOST="movingdb"
REMOTE_USER="smashimo"
REMOTE_DIR="~/YOUR_PROJECT/"
CONDA_ENV="YOUR_ENV"
PROJECT_PORT="YOUR_PORT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# CRITICAL: Enhanced rsync that sets permissions during transfer
echo -e "${GREEN}[INFO]${NC} Syncing files with correct permissions..."
rsync -avz --delete \
    --chmod=D755,F644 \              # Directories 755, Files 644
    --chown=smashimo:www-data \      # Correct ownership
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
    echo -e "${RED}[ERROR]${NC} Failed to sync files to $REMOTE_HOST"
    exit 1
fi

# SSH operations on Pi
ssh $REMOTE_HOST << EOF
    # Set umask for consistent permissions
    umask 022
    
    # Navigate to project
    cd $REMOTE_DIR
    
    # Git operations
    git pull origin main
    
    # MINIMAL permission verification (should not be needed with enhanced rsync)
    # Only verify, don't fix - if this fails, the rsync approach needs adjustment
    if ! sudo -u www-data cat static/css/style.css > /dev/null 2>&1; then
        echo -e "${RED}[WARNING]${NC} www-data cannot access static files - rsync permissions may need adjustment"
    else
        echo -e "${GREEN}[SUCCESS]${NC} Static file permissions verified"
    fi
    
    # Install/update service and nginx config
    sudo cp YOUR_PROJECT.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable YOUR_PROJECT
    
    sudo cp nginx.conf /etc/nginx/sites-available/YOUR_PROJECT
    sudo ln -sf /etc/nginx/sites-available/YOUR_PROJECT /etc/nginx/sites-enabled/
    
    # Test and reload services
    sudo nginx -t && sudo systemctl reload nginx
    sudo systemctl restart YOUR_PROJECT
    
    echo -e "${GREEN}[SUCCESS]${NC} Deployment complete on port $PROJECT_PORT"
EOF
```

## Project Cloning Checklist

### Step 1: Initial Setup
- [ ] Copy project template files
- [ ] Update all configuration files with new project name/port
- [ ] Create new conda environment
- [ ] Update requirements.txt if needed

### Step 2: Sync Script Configuration
- [ ] Update LOCAL_DIR path
- [ ] Update REMOTE_DIR path  
- [ ] Update CONDA_ENV name
- [ ] Update PROJECT_PORT
- [ ] Update service file name references

### Step 3: Pi Configuration
- [ ] Create project directory on Pi
- [ ] Set up Git repository
- [ ] Create conda environment
- [ ] Test enhanced rsync approach

### Step 4: Verification
- [ ] Run sync script
- [ ] Verify static files load without 403 errors
- [ ] Test deployment timestamp feature
- [ ] Confirm service starts automatically

## Key Prevention Strategies

### 1. Use Enhanced rsync (Primary Prevention)
The `--chmod=D755,F644 --chown=smashimo:www-data` options prevent permission issues during transfer.

### 2. Set Consistent umask
Always use `umask 022` in scripts to ensure consistent default permissions.

### 3. Verification, Not Fixing
The new approach verifies permissions work rather than fixing them, indicating if the prevention strategy needs adjustment.

### 4. Template Documentation
Keep this guide and the troubleshooting docs with every project clone.

## Benefits of This Approach

1. **No more 403 errors** - permissions set correctly from the start
2. **Faster deployments** - no post-sync permission operations
3. **More reliable** - less chance of human error
4. **Easier debugging** - if permissions fail, the rsync approach needs adjustment
5. **Reusable** - same template works for multiple projects

## Emergency Fallback

If you ever encounter permission issues despite this approach, the emergency fix commands are documented in `userInstructions/permissions_fix_reference.md`.

## Testing New Projects

Always test a new project clone with:
```bash
# After first deployment
ssh smashimo@movingdb "sudo -u www-data cat ~/your_project/static/css/style.css"
```

If this succeeds, your project is properly configured and will not have permission issues.
