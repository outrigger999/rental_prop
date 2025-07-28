# Git Workflow and Deployment Instructions

## Overview
This project uses a Git-based deployment workflow where all changes are committed to the repository and then pulled to the Raspberry Pi. This ensures consistency and version control for all deployments.

**Important Notes:**
- All Git actions require user approval before execution
- ALL testing is performed on the Raspberry Pi 4 (accessed via SSH movingdb)
- Mac is used only for development and running the sync script
- Python environment on Pi: `rental_prop_env` (conda)

## Git Workflow

### For Initial Development (Current State)
1. **Work directly on main branch** for initial MVP completion
2. **Commit all changes** before deployment
3. **Use sync script** to deploy to Pi

### For Future Changes (After MVP)
1. **Create a feature branch** for any new work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit regularly:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

3. **Push branch to GitHub**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Test on Pi** using the sync script with branch option:
   ```bash
   ./sync_to_pi.sh --branch=feature/your-feature-name
   ```

5. **After testing is complete**, merge to main:
   ```bash
   git checkout main
   git merge feature/your-feature-name
   git push origin main
   ```

6. **Deploy main branch** to Pi:
   ```bash
   ./sync_to_pi.sh
   ```

7. **Clean up** the feature branch:
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

## Deployment Commands

### Basic Deployment
Deploy current branch to Pi:
```bash
./sync_to_pi.sh
```

### Deployment Options
- **Dry run** (see what would be deployed without making changes):
  ```bash
  ./sync_to_pi.sh --dry-run
  ```

- **Deploy specific branch**:
  ```bash
  ./sync_to_pi.sh --branch=your-branch-name
  ```

- **Update conda environment** (slower but ensures all dependencies):
  ```bash
  ./sync_to_pi.sh --conda
  ```

- **Help and options**:
  ```bash
  ./sync_to_pi.sh --help
  ```

## Testing Workflow

### Development and Testing Process
1. **Develop on Mac** - Edit code, create features
2. **User commits to Git** - All git actions require your approval
3. **Run sync script from Mac** - Deploys code to Pi via Git pull
4. **Test on Pi only** - SSH to movingdb, test in `rental_prop_env`
5. **Iterate** - Make changes on Mac, repeat process

### Testing Commands on Pi
```bash
# SSH to Pi
ssh smashimo@movingdb

# Activate conda environment
conda activate rental_prop_env

# Navigate to project
cd ~/rental_prop

# Run application manually for testing
python app.py

# Check service status
sudo systemctl status rental_prop

# View service logs
sudo journalctl -u rental_prop -f
```

## What the Sync Script Does

### 1. Local Git Operations (Mac)
- **Note:** Git operations require user approval
- Commits any uncommitted changes with automatic message
- Pushes current branch to GitHub

### 2. Reverse Sync (Pi to Local)
- Downloads database file from Pi (if newer)
- Downloads uploaded images from Pi
- Preserves data created on the Pi

### 3. Deployment (Local to Pi)
- Pi pulls latest code from GitHub (Git-based deployment)
- Updates dependencies if requested
- Fixes file permissions
- Restarts the rental_prop service
- Verifies service is running

## Access URLs
After successful deployment, the application will be accessible at:
- **By IP**: http://192.168.10.10:5000
- **By hostname**: http://movingdb:5000
- **Custom domain**: http://rental.box (via nginx proxy)

## Troubleshooting

### If deployment fails:
1. Check that you can SSH to the Pi: `ssh smashimo@movingdb`
2. Verify the Pi has the rental_prop directory: `ls ~/rental_prop`
3. Check service status on Pi: `sudo systemctl status rental_prop`
4. View service logs: `sudo journalctl -u rental_prop -f`

### If app is not accessible:
1. Verify service is running on Pi: `sudo systemctl status rental_prop`
2. Check if port 5000 is open: `sudo netstat -tlnp | grep :5000`
3. Verify Flask app is bound to 0.0.0.0 (not 127.0.0.1)

### Common Issues:
- **SSH key problems**: Ensure your SSH key is added to the Pi
- **Git authentication**: Verify GitHub SSH key is set up on Pi
- **Service not starting**: Check Python environment and dependencies
- **Permission errors**: The sync script automatically fixes static file permissions

## Important Notes
- Always commit changes before deploying
- Database and uploads are automatically synced FROM Pi to local
- Never edit files directly on the Pi - always use Git workflow
- Use feature branches for any changes after initial MVP
- Test thoroughly before merging to main branch
