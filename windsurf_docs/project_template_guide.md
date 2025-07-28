# Flask + Nginx + Raspberry Pi Project Template

## CRITICAL: Complete Guide to Avoid ALL Deployment Issues

This comprehensive guide incorporates ALL lessons learned from rental_prop project deployment issues to ensure future projects work flawlessly from the start.

## MOST IMPORTANT: Git-First Workflow (MANDATORY)

**🚨 CRITICAL RULE: ALWAYS use Git-based deployment as PRIMARY method 🚨**

### Why Git-First is Essential:
- Prevents code version mismatches between Mac and Pi
- Ensures deployed code matches what you're developing
- Eliminates "deployment reverted to old version" issues
- Provides proper version control and rollback capability

### Git Workflow Commands (MEMORIZE THESE):
```bash
# BEFORE EVERY DEPLOYMENT - NO EXCEPTIONS:
git add .
git commit -m "Descriptive commit message about changes"
git push origin main

# THEN run sync script (which does git pull on Pi):
./sync_to_pi_working.sh
```

### Git Setup for New Project:
1. Create GitHub repository for new project
2. Clone to your Mac development environment
3. Update sync script with correct GitHub repository URL
4. Ensure Pi has SSH key access to GitHub repository

## SSH Configuration (CRITICAL FOR SYNC SCRIPT)

### SSH Host Alias Setup:
Ensure your `~/.ssh/config` has proper host alias:
```
Host movingdb
    HostName 192.168.10.10
    User smashimo
    IdentityFile ~/.ssh/id_rsa
```

### Sync Script SSH Configuration:
- **ALWAYS use SSH host alias** (e.g., `movingdb`)
- **NEVER use** `username@hostname` format in sync script
- **Test SSH connection** before running sync: `ssh movingdb echo "test"`

## Project Template Structure
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

## Complete Project Cloning Checklist

### Step 1: Repository Setup
- [ ] Create new GitHub repository
- [ ] Clone repository to Mac development environment
- [ ] Copy sync_to_pi_working.sh from rental_prop project
- [ ] Copy windsurf_docs folder structure

### Step 2: Sync Script Configuration (CRITICAL)
- [ ] Update LOCAL_DIR path to new project
- [ ] Update REMOTE_DIR path to new project
- [ ] Update CONDA_ENV to new environment name
- [ ] Update GITHUB_REPO URL to new repository
- [ ] Update database filename references
- [ ] Test SSH connection: `ssh movingdb echo "test"`

### Step 3: Flask Application Updates
- [ ] Update app.py port number (unique for each project)
- [ ] Update DATABASE variable to match project
- [ ] Update secret_key to project-specific value
- [ ] Test local development: `python app.py`

### Step 4: Nginx Configuration
- [ ] Copy nginx.conf template
- [ ] Update server_name to new domain
- [ ] Update proxy_pass port to match Flask app
- [ ] Update static file alias path

### Step 5: Systemd Service
- [ ] Copy service file template
- [ ] Update service name and description
- [ ] Update WorkingDirectory path
- [ ] Update conda environment path

### Step 6: Initial Deployment
- [ ] Commit all changes to Git: `git add . && git commit -m "Initial project setup"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Run sync script: `./sync_to_pi_working.sh`
- [ ] Test application access: `http://192.168.10.10:YOUR_PORT`

## Troubleshooting Common Issues

### SSH Authentication Errors:
- Verify SSH host alias in ~/.ssh/config
- Test direct SSH: `ssh movingdb`
- Check sync script uses `REMOTE_HOST="movingdb"`

### Permission Denied (403) Errors:
- Sync script automatically fixes permissions
- Verify nginx.conf static path is correct
- Check that sync completed successfully

### Application Not Accessible:
- Verify Flask app binds to 0.0.0.0, not localhost
- Check port conflicts with other services
- Verify nginx proxy_pass port matches Flask port

### Deployment Reverts to Old Version:
- **ALWAYS commit and push changes before deployment**
- Verify Git repository URL in sync script
- Check that Pi can access GitHub repository

## Success Verification

After deployment, verify:
1. ✅ Application accessible via browser
2. ✅ Static files (CSS, JS, images) load correctly
3. ✅ Database operations work
4. ✅ File uploads work (if applicable)
5. ✅ All features function as expected

## Key Lessons Learned

1. **Git-first workflow prevents version mismatches**
2. **SSH host aliases eliminate authentication issues**
3. **Automatic permission fixing prevents 403 errors**
4. **Project-specific configuration prevents conflicts**
5. **Comprehensive testing catches issues early**

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
