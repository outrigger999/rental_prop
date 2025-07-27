# Development Workflow Guide

## Overview
This guide explains how to safely develop new features using Git branches while keeping your main branch stable and working.

## Branch Strategy

### Main Branch (`main`)
- **Purpose**: Always contains stable, working code
- **Protection**: Never develop directly on main
- **Deployment**: This is what gets deployed to production

### Feature Branches
- **Purpose**: Develop new features or fixes
- **Naming**: Use descriptive names like `feature/search-improvements` or `fix/pagination-bug`
- **Lifecycle**: Create → Develop → Test → Merge → Delete

## Workflow Steps

### 1. Starting a New Feature

```bash
# Make sure you're on main and it's up to date
git checkout main
git pull origin main

# Create and switch to a new feature branch
git checkout -b feature/your-feature-name

# Example: Adding a new search filter
git checkout -b feature/advanced-search-filters
```

### 2. Working on Your Feature

```bash
# Make your changes to files
# Edit code, add features, fix bugs

# Stage your changes
git add .

# Commit with descriptive messages
git commit -m "Add advanced search filters for priority and date range

- Added date range picker for created_at field
- Enhanced priority filter with multiple selection
- Updated search form layout for better UX"

# Push your feature branch to GitHub
git push -u origin feature/your-feature-name
```

### 3. Testing Your Feature

```bash
# Run your application to test
python simplified_app.py

# Test thoroughly:
# - Does the feature work as expected?
# - Did you break any existing functionality?
# - Are there any errors in the logs?
```

### 4. Merging Back to Main (When Ready)

```bash
# Switch back to main
git checkout main

# Pull any updates from GitHub
git pull origin main

# Merge your feature branch
git merge feature/your-feature-name

# Push the updated main branch
git push origin main

# Clean up: delete the feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## Alternative: Using GitHub Pull Requests (Recommended)

Instead of merging locally, you can create Pull Requests on GitHub for better review:

1. Push your feature branch: `git push -u origin feature/your-feature-name`
2. Go to GitHub and create a Pull Request
3. Review the changes, test if needed
4. Merge the Pull Request on GitHub
5. Delete the branch on GitHub
6. Update your local main: `git checkout main && git pull origin main`

## Quick Reference Commands

### Common Branch Operations
```bash
# List all branches
git branch -a

# Switch to a branch
git checkout branch-name

# Create and switch to new branch
git checkout -b new-branch-name

# Delete a local branch
git branch -d branch-name

# Delete a remote branch
git push origin --delete branch-name

# See current status
git status

# See branch history
git log --oneline --graph
```

### Emergency: Undo Changes
```bash
# Undo uncommitted changes
git checkout -- filename.py

# Undo last commit (but keep changes)
git reset --soft HEAD~1

# Undo last commit (lose changes - be careful!)
git reset --hard HEAD~1
```

## Best Practices

### 1. Branch Naming Conventions
- `feature/description` - New features
- `fix/description` - Bug fixes  
- `hotfix/description` - Urgent production fixes
- `docs/description` - Documentation updates

### 2. Commit Message Guidelines
- Use present tense: "Add feature" not "Added feature"
- Be descriptive but concise
- Include details in the body if needed

### 3. Before Merging to Main
- ✅ Feature works completely
- ✅ All existing features still work
- ✅ No errors in console/logs
- ✅ Code is clean and commented
- ✅ Test on your local environment

### 4. Keep Branches Small
- One feature per branch
- Merge frequently (don't let branches get too far behind)
- Delete branches after merging

## Example Workflow: Adding a New Feature

Let's say you want to add a "favorite boxes" feature:

```bash
# 1. Start from clean main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/favorite-boxes

# 3. Make changes (edit files, add code)
# ... work on your feature ...

# 4. Commit changes
git add .
git commit -m "Add favorite boxes functionality

- Add favorite column to boxes table
- Add star icon to box list for favoriting
- Add favorite filter to search options
- Update database schema"

# 5. Push to GitHub
git push -u origin feature/favorite-boxes

# 6. Test thoroughly
python simplified_app.py
# Test the feature, make sure nothing is broken

# 7. If more changes needed, repeat steps 3-6

# 8. When satisfied, merge to main
git checkout main
git pull origin main
git merge feature/favorite-boxes
git push origin main

# 9. Clean up
git branch -d feature/favorite-boxes
git push origin --delete feature/favorite-boxes
```

## Safety Notes

- **Never force push to main**: `git push --force` on main can break everything
- **Always test before merging**: Your main branch should always work
- **Backup important work**: Push branches to GitHub regularly
- **When in doubt**: Ask for help or create a backup branch first

This workflow ensures your main branch stays stable while allowing you to experiment safely with new features!
