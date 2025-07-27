# Current Task - Rental Property Tracker

## Current Objectives
Fix deployment and browser accessibility issues for the Rental Property Tracker application on Raspberry Pi 4.

## Context
The application has been developed as a Flask-based web app for tracking rental properties. Previous AI work created a sync script with syntax errors, and while the app runs on the Pi, it's not accessible via browser from other devices.

## Specific Issues to Resolve

### 1. Sync Script Syntax Error
- **Problem:** Current `sync_to_pi.sh` has syntax errors preventing proper deployment
- **Solution:** Reference working sync script from `__archive/sync_to_pi.sh` and adapt for this project
- **Requirements:** Must use Git-based deployment (pull from GitHub on Pi, not direct file sync)

### 2. Browser Accessibility Issue
- **Problem:** App runs on RPi4 but not accessible via browser from other devices
- **Likely Cause:** Flask app bound to localhost (127.0.0.1) instead of all interfaces (0.0.0.0)
- **Solution:** Update app.py to bind to 0.0.0.0 and appropriate port

### 3. Git Workflow Implementation
- **Requirement:** All changes must be committed to Git
- **Workflow:** Create branches for changes, merge to main after testing
- **Deployment:** Pi pulls from Git repository, no direct file transfers

## Next Steps

1. **Commit current changes** - User approval required for git operations
2. **Test sync script** - Run sync_to_pi.sh from Mac to deploy to Pi
3. **Test on Pi** - SSH to movingdb, activate rental_prop_env, test app
4. **Verify browser access** - Confirm app accessible at http://192.168.10.10:5000
5. **Complete MVP testing** - Ensure all basic functionality works on Pi

## Related Files
- `/app.py` - Main Flask application (needs host binding fix)
- `/sync_to_pi.sh` - Current broken sync script (needs complete rewrite)
- `/__archive/sync_to_pi.sh` - Working reference implementation
- `/windsurf_docs/` - Project documentation (being created)

## Success Criteria
- [ ] App accessible via browser from any device on network
- [ ] Sync script successfully deploys code from Git to Pi
- [ ] All changes properly committed to Git with branch workflow
- [ ] Documentation complete and up-to-date
