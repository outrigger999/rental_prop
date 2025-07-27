# Sync Script Testing Checklist

## Prerequisites
- [ ] SSH connection to Pi works: `ssh movingdb echo "Connection test successful"`
- [ ] Script is executable: `ls -la sync_to_pi.sh` (should show `-rwxr-xr-x`)

## Step 1: Dry Run Test (SAFE)
```bash
./sync_to_pi.sh --dry-run
```

**Expected Output:**
- [ ] Shows database/backup files that would be synced FROM Pi
- [ ] Shows project files that would be synced TO Pi  
- [ ] No actual changes made
- [ ] No errors or connection issues

## Step 2: Manual Pi Inspection
```bash
# Check what's currently on Pi
ssh movingdb "ls -la ~/moving_box_tracker/"
ssh movingdb "ls -la ~/moving_box_tracker/backups/"
ssh movingdb "ls -la ~/moving_box_tracker/moving_boxes.db"
```

**Expected:**
- [ ] moving_box_tracker directory exists
- [ ] Database file exists: moving_boxes.db
- [ ] Backups directory exists with backup files

## Step 3: Backup Current Local State
```bash
# Backup current local database (if exists)
cp moving_boxes.db moving_boxes.db.backup 2>/dev/null || echo "No local database to backup"

# Note current local backup count
ls -la backups/ | wc -l
```

## Step 4: First Real Sync Test
```bash
./sync_to_pi.sh
```

**Expected Sequence:**
- [ ] Script asks for confirmation (y/n)
- [ ] Phase 1: Syncs FROM Pi - database, backups, logs
- [ ] Phase 2: Syncs TO Pi - code files (excluding database/backups)
- [ ] Restarts Pi service successfully
- [ ] Shows "Deployment completed successfully!"
- [ ] Shows Pi URL: http://192.168.10.10

## Step 5: Verify Results

### Check Local Files (should have Pi's data):
```bash
ls -la moving_boxes.db  # Should exist/be updated
ls -la backups/         # Should have Pi's backup files
ls -la logs/            # Should have Pi's log files
```

### Check Pi Service:
```bash
ssh movingdb "systemctl status moving_boxes.service"
```
- [ ] Service should be "active (running)"

### Test Web Access:
- [ ] Open http://192.168.10.10 in browser
- [ ] Application loads correctly
- [ ] Can view box list (should show existing data)

## Step 6: Test Bidirectional Sync

### Make a small code change locally:
```bash
# Add a comment to simplified_app.py
echo "# Test sync change" >> simplified_app.py
```

### Run sync again:
```bash
./sync_to_pi.sh
```

### Verify:
- [ ] Code change appears on Pi: `ssh movingdb "tail -1 ~/moving_box_tracker/simplified_app.py"`
- [ ] Database on Pi unchanged (data preserved)
- [ ] Service restarts successfully

## Troubleshooting
If something goes wrong:

1. **SSH Issues**: Check network, hostname resolution
2. **Permission Issues**: Verify SSH keys, sudo access on Pi  
3. **Service Won't Start**: Check logs with `ssh movingdb "sudo journalctl -u moving_boxes.service -n 20"`
4. **Rsync Errors**: Check file permissions, disk space

## Recovery
If you need to restore:
```bash
# Restore local database backup
cp moving_boxes.db.backup moving_boxes.db

# Or pull fresh from Pi
rsync -avz movingdb:~/moving_box_tracker/moving_boxes.db ./
