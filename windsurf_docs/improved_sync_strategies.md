# Improved Sync Strategies to Prevent Permission Issues

## Current Problem

## CRITICAL: Git-First Strategy (MANDATORY)

### Primary Deployment Method: Git-Based Sync
**This is the ONLY recommended deployment method for all future projects.**

```bash
# STEP 1: Always commit and push changes FIRST
git add .
git commit -m "Descriptive commit message"
git push origin main

# STEP 2: Run sync script (which does git pull on Pi)
./sync_to_pi_working.sh
```

**Why Git-First is Essential:**
- ✅ Prevents "deployment reverted to old version" issues
- ✅ Ensures deployed code matches development environment
- ✅ Provides version control and rollback capability
- ✅ Eliminates code synchronization problems
- ✅ Enables proper collaboration and change tracking

### Git-Based Sync Script Process:
1. **Local Mac**: Commit and push changes to GitHub
2. **Sync Script**: Transfers any new files via rsync
3. **Pi**: Pulls latest code from GitHub repository
4. **Pi**: Updates dependencies and restarts services
5. **Pi**: Automatically fixes permissions

## Strategy Evolution History

### 1. Basic rsync (Original - Had Issues)
```bash
rsync -avz --delete --exclude 'venv' --exclude '__pycache__' \
    -e ssh "$LOCAL_DIR" "$REMOTE_HOST:$REMOTE_DIR"
```

**Problems:**
- Required manual permission fixes after sync
- Inconsistent ownership
- Static files often inaccessible to nginx
- No version control
- Code could get out of sync

### 2. Enhanced rsync with Permission Control (Intermediate)
```bash
rsync -avz --delete \
    --chmod=D755,F644 \              # Directories 755, Files 644
    --chown=smashimo:www-data \      # Correct ownership during transfer
    --exclude 'venv' --exclude '__pycache__' \
    -e ssh "$LOCAL_DIR" "$REMOTE_HOST:$REMOTE_DIR"
```

**Benefits:**
- Prevented permission issues during transfer
- Eliminated need for post-sync permission fixes
- More reliable deployments

**Remaining Issues:**
- Still no version control
- Could deploy uncommitted changes
- No rollback capability

### 3. Git-Based Deployment (CURRENT - BEST SOLUTION)
```bash
# Hybrid approach: rsync for files + git pull for code
# 1. Rsync transfers any new files with correct permissions
rsync -avz --delete \
    --chmod=D755,F644 \
    --chown=smashimo:www-data \
    --exclude 'venv' --exclude '__pycache__' \
    -e ssh "$LOCAL_DIR" "$REMOTE_HOST:$REMOTE_DIR"

# 2. Git pull ensures latest committed code is deployed
ssh $REMOTE_HOST << 'EOF'
    cd ~/project_directory
    git reset --hard HEAD
    git clean -fd
    git pull origin main
EOF
```

**Benefits:**
- ✅ Version control integration
- ✅ Prevents deployment of uncommitted changes
- ✅ Automatic permission handling
- ✅ Rollback capability
- ✅ Change tracking and history
- ✅ Eliminates code synchronization issues

## SSH Configuration for Sync Scripts

### CRITICAL: SSH Host Alias Setup
**Always use SSH host aliases to prevent authentication issues:**

```bash
# ~/.ssh/config
Host movingdb
    HostName 192.168.10.10
    User smashimo
    IdentityFile ~/.ssh/id_rsa
```

### Sync Script SSH Configuration:
```bash
# CORRECT - Use host alias
REMOTE_HOST="movingdb"
ssh $REMOTE_HOST "commands"

# WRONG - Don't use username@hostname
REMOTE_HOST="rental.box"
REMOTE_USER="smashimo"
ssh $REMOTE_USER@$REMOTE_HOST "commands"  # This causes auth issues
```

## Implementation Details

### Git Repository Configuration
```bash
# In sync script - UPDATE FOR EACH PROJECT
GITHUB_REPO="https://github.com/YOUR_USERNAME/YOUR_PROJECT.git"
TARGET_BRANCH="main"  # or your default branch
```

### Database Synchronization
```bash
# CRITICAL: Update database name for each project
# In sync script:
if ssh $REMOTE_HOST "test -f ~/YOUR_PROJECT/YOUR_DATABASE.db"; then
    rsync -avz --update -e ssh "$REMOTE_HOST:$REMOTE_DIR/YOUR_DATABASE.db" "$LOCAL_DIR"
fi
```

### Permission Strategy (Automatic)
The sync script automatically handles permissions:
```bash
# Directory permissions (755 = rwxr-xr-x)
find static templates -type d -exec chmod 755 {} \;

# File permissions (644 = rw-r--r--)
find static templates -type f -exec chmod 644 {} \;
```

### Conda Environment Management
```bash
# Automatic conda environment activation
source ~/miniconda3/etc/profile.d/conda.sh
conda activate $CONDA_ENV
pip install -r requirements.txt
```

## Verification Commands

After deployment, verify everything works:
```bash
# 1. Check Git status
ssh movingdb "cd ~/YOUR_PROJECT && git status"

# 2. Check permissions
ssh movingdb "ls -la ~/YOUR_PROJECT/static/"
# Should show: drwxr-xr-x smashimo www-data

# 3. Test nginx access
ssh movingdb "sudo -u www-data cat ~/YOUR_PROJECT/static/css/style.css"
# Should display file contents without errors

# 4. Check service status
ssh movingdb "systemctl status YOUR_PROJECT"

# 5. Test application access
curl http://192.168.10.10:YOUR_PORT
1. Test enhanced rsync in a dry-run mode
2. Update sync script with new rsync options
3. Remove post-sync permission fixing code
4. Test thoroughly
5. Document the new approach
