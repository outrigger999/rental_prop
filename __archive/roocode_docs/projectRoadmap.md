# Project Roadmap

## High-Level Goals
- [ ] Establish robust and reliable sync between Mac and Raspberry Pi for project files
- [ ] Maintain clear documentation and workflow for ongoing development
- [ ] Ensure scalability and maintainability of the sync and project management system

## Key Features
- [ ] Automated sync scripts for Mac ↔ Pi
- [ ] Error handling and logging for sync operations
- [ ] Documentation system for project context and progress

## Completion Criteria
- [ ] Sync scripts function reliably for all project files
- [ ] Documentation is up-to-date and accessible
- [ ] System is easy to extend for new features or platforms

## Progress Tracker
- [ ] Create and initialize documentation system
- [x] Audit and update sync scripts for correct paths and error handling
- [ ] Test end-to-end sync between Mac and Pi
- [ ] Fix category management issues in the moving box tracker application

## Completed Tasks
- **2025-05-30**: Fixed error message handling for duplicate categories in the moving box tracker application — Updated frontend code to properly detect and display error messages when attempting to add or edit a category with a name that already exists.
- **2025-05-26**: Audit and update sync scripts for correct paths and error handling — Confirmed [`sync_to_pi.sh`](../sync_to_pi.sh) already uses the correct path `/Volumes/Projects/Python Projects/moving`; no changes required.
