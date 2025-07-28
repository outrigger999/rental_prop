# Improved Sync Strategies to Prevent Permission Issues

## Current Problem
File synchronization (via rsync or git) can change permissions, causing nginx 403 Forbidden errors on static files.

## Root Causes
1. **Git doesn't preserve file permissions** (only executable bit)
2. **rsync preserves source permissions** which may not match nginx requirements
3. **umask settings** affect newly created files
4. **Different OS defaults** between Mac (source) and Linux Pi (destination)

## Solution 1: Enhanced rsync with Permission Control (Recommended)

### Modified rsync Command
```bash
rsync -avz --delete \
    --chmod=D755,F644 \     # Force directories to 755, files to 644
    --chown=smashimo:www-data \  # Set ownership during transfer
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude '*.db' \
    --exclude 'backups/' \
    --exclude 'logs/' \
    -e ssh \
    "$LOCAL_DIR" \
    "$REMOTE_HOST:$REMOTE_DIR"
```

### Benefits
- Sets correct permissions during transfer
- Eliminates need for post-sync permission fixes
- More efficient (one operation instead of two)
- Prevents permission issues from occurring

## Solution 2: Git-Only Workflow with Hooks

### Setup Git Post-Receive Hook
```bash
# On the Pi: /home/smashimo/rental_prop/.git/hooks/post-receive
#!/bin/bash
cd /home/smashimo/rental_prop
git --git-dir=.git --work-tree=. checkout -f

# Set permissions immediately after checkout
find static templates -type d -exec chmod 755 {} \; 2>/dev/null
find static templates -type f -exec chmod 644 {} \; 2>/dev/null
chown -R smashimo:www-data static/ templates/ 2>/dev/null

# Restart services
sudo systemctl reload nginx
sudo systemctl restart rental_prop
```

### Benefits
- Pure Git workflow (no rsync needed)
- Automatic permission fixing on every push
- Cleaner deployment process

## Solution 3: Umask Configuration

### Set Default umask on Pi
Add to `/home/smashimo/.bashrc`:
```bash
# Set umask for proper default permissions
umask 022  # Creates files as 644, directories as 755
```

### Set umask in Sync Script
```bash
# At the start of sync operations on Pi
umask 022
```

## Solution 4: ACL (Access Control Lists)

### Set Default ACLs (Advanced)
```bash
# Set default ACLs so new files inherit correct permissions
sudo setfacl -d -m u::rwx,g::r-x,o::r-x /home/smashimo/rental_prop/static
sudo setfacl -d -m u::rw-,g::r--,o::r-- /home/smashimo/rental_prop/static
```

## Recommended Implementation

### Phase 1: Enhanced rsync (Immediate)
Update the current sync script to use the enhanced rsync command with `--chmod` and `--chown` options.

### Phase 2: Git Hooks (Future)
Migrate to a pure Git workflow with post-receive hooks for even cleaner deployment.

### Phase 3: System Configuration (Optional)
Configure umask and potentially ACLs for system-level permission management.

## Testing the Enhanced Approach

### Test Commands
```bash
# Test enhanced rsync locally
rsync -avzn --chmod=D755,F644 --chown=smashimo:www-data \
    /local/path/ user@remote:/remote/path/

# Verify permissions after sync
ssh user@remote "ls -la /remote/path/static/"
ssh user@remote "sudo -u www-data cat /remote/path/static/css/style.css"
```

## Benefits of This Approach
1. **Prevents issues** instead of fixing them after they occur
2. **More efficient** - no post-sync permission operations needed
3. **More reliable** - reduces chance of human error
4. **Cleaner code** - less complex permission handling in scripts

## Migration Strategy
1. Test enhanced rsync in a dry-run mode
2. Update sync script with new rsync options
3. Remove post-sync permission fixing code
4. Test thoroughly
5. Document the new approach
