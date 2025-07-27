# VSCode + Cline + Claude GitHub Workflow

## Overview
This guide explains how to continue developing your Moving Box Tracker project using VSCode, Cline, and Claude while maintaining the GitHub branching workflow we established.

## The Development Stack

### Tools Integration
- **VSCode**: Your code editor with built-in Git support
- **Cline**: AI assistant that can execute commands and modify files
- **Claude (Sonnet)**: AI that understands your project and can write code
- **Git/GitHub**: Version control and remote repository

### How They Work Together
1. You describe what feature you want to add
2. Claude (through Cline) can:
   - Create feature branches
   - Write/modify code
   - Test changes
   - Commit and push to GitHub
   - Merge back to main when ready

## Starting a New Development Session

### 1. Open Your Project in VSCode
```bash
# Navigate to your project
cd "/Volumes/Projects/Python Projects/moving"

# Open in VSCode
code .
```

### 2. Tell Cline What You Want to Build
Simply describe your feature request, for example:
- "Add a search filter for boxes by date range"
- "Create a favorites system for important boxes"
- "Add export to Excel functionality"
- "Improve the mobile responsive design"

### 3. Claude Will Handle the Git Workflow
I can automatically:
- Check current branch status
- Create appropriate feature branches
- Make code changes
- Test the changes
- Commit with proper messages
- Push to GitHub
- Merge back to main when ready

## Example Development Session

### Scenario: You Want to Add Box Photos

**You say**: "I want to add the ability to upload and display photos for each box"

**Claude will**:
1. **Check current status**:
   ```bash
   git status
   git checkout main
   git pull origin main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/box-photos
   ```

3. **Plan and implement**:
   - Modify database schema to add photo fields
   - Update the create/edit forms to handle file uploads
   - Add photo display to the box list
   - Update CSS for proper photo sizing
   - Test the functionality

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "Add photo upload functionality for boxes
   
   - Add photo_filename column to boxes table
   - Implement file upload in create/edit forms
   - Display thumbnails in box list
   - Add photo storage directory
   - Include proper file validation"
   ```

5. **Test and merge**:
   ```bash
   git checkout main
   git merge feature/box-photos
   git push origin main
   git branch -d feature/box-photos
   ```

## VSCode Git Integration Benefits

### Built-in Git Features
- **Source Control Panel**: Visual diff and staging
- **Branch Indicator**: Shows current branch in status bar
- **Integrated Terminal**: Where Cline executes Git commands
- **File Status Icons**: See which files are modified

### What You'll See in VSCode
- Modified files highlighted in orange
- New files highlighted in green
- Current branch name in bottom status bar
- Git changes in the Source Control panel (Ctrl+Shift+G)

## Workflow Commands Claude Uses

### Branch Management
```bash
# See all branches
git branch -a

# Create and switch to feature branch
git checkout -b feature/feature-name

# Switch between branches
git checkout main
git checkout feature/feature-name

# Delete completed feature branch
git branch -d feature/feature-name
```

### Development Cycle
```bash
# Check what's changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Descriptive commit message"

# Push to GitHub
git push origin branch-name

# Pull updates from GitHub
git pull origin main
```

## Best Practices for Our Workflow

### 1. Always Start Sessions by Checking Status
When you start a new Cline session, I'll check:
- Current branch
- Any uncommitted changes
- If main branch is up to date

### 2. Feature-Based Development
Each new feature gets its own branch:
- `feature/search-improvements`
- `feature/mobile-optimization`
- `fix/pagination-bug`
- `enhancement/better-ui`

### 3. Testing Before Merging
I'll always:
- Run the application to test changes
- Check for errors in the console
- Verify existing features still work
- Only merge when everything works

### 4. Clean Commit History
Each commit will:
- Have a descriptive title
- Include bullet points of changes
- Reference any related issues
- Be focused on one logical change

## Handling Different Scenarios

### Starting Fresh Each Session
```bash
# I'll always check this first
git checkout main
git pull origin main
git status
```

### Multiple Features in Progress
```bash
# Switch between feature branches
git checkout feature/search-filters
# ... work on search
git checkout feature/export-excel  
# ... work on export
```

### Emergency Fixes
```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug-fix
# ... make urgent fix
git checkout main
git merge hotfix/critical-bug-fix
git push origin main
```

### Collaboration with Others
```bash
# Always pull before starting new work
git pull origin main

# Check for conflicts
git status

# Handle merge conflicts if needed
```

## VSCode Extensions That Help

### Recommended Extensions
1. **GitLens**: Enhanced Git capabilities
2. **Git Graph**: Visual branch history
3. **Git History**: File and branch history
4. **Python**: For Python development
5. **Bracket Pair Colorizer**: Better code readability

### Already Built-in
- Source Control (Git integration)
- Integrated Terminal
- File Explorer with Git status
- Diff viewer

## Troubleshooting

### If Git Gets Confused
```bash
# Check status
git status

# Discard uncommitted changes
git checkout -- filename

# Reset to last commit
git reset --hard HEAD

# Force clean state
git clean -fd
```

### If You Need to Undo
```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit and lose changes
git reset --hard HEAD~1

# Create backup branch before major changes
git checkout -b backup-branch
```

## Summary

**Your role**: Describe what you want to build or fix
**Claude's role**: Handle all the Git workflow, coding, and testing
**VSCode's role**: Provide the development environment and Git visualization
**GitHub's role**: Store your code safely and track all changes

The beauty of this setup is that you can focus on **what** you want to build, and I'll handle **how** to build it safely using proper Git workflows. Your main branch stays stable, your code is always backed up to GitHub, and you get professional development practices automatically.

Just tell me what feature you want to add next, and I'll handle the entire development lifecycle!
