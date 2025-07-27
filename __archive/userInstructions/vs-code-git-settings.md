# Hiding Ignored Files in VS Code Git UI

Visual Studio Code's Git integration can sometimes display files that are ignored by your `.gitignore` file, which creates unnecessary clutter in the Source Control panel. Here's how to configure VS Code to hide these ignored files:

## Method 1: Using the Settings UI

1. Open VS Code Settings:
   - On Mac: `Cmd+,` (Command + Comma)
   - On Windows/Linux: `Ctrl+,` (Control + Comma)
   - Or click on the gear icon in the lower left corner and select "Settings"

2. Search for: `git.ignoredResourceStatus`

3. Find the checkbox for "Git: Ignored Resource Status" and uncheck it to hide ignored files

4. Alternatively, search for `SCM: Always Show Ignored` and ensure this setting is unchecked

## Method 2: Editing settings.json Directly

1. Open VS Code settings.json:
   - On Mac: `Cmd+Shift+P` (Command + Shift + P)
   - On Windows/Linux: `Ctrl+Shift+P` (Control + Shift + P)
   - Type "Preferences: Open Settings (JSON)" and select it

2. Add these lines to your settings.json:
   ```json
   "git.ignoredResourceStatus": false,
   "scm.alwaysShowActions": true,
   "scm.alwaysShowRepositories": false,
   "scm.showActionButton": true,
   "scm.alwaysShowIgnoredResources": false
   ```

3. Save the file and close it

## Additional Git Settings for Better Experience

You may also want to add these settings for a better Git experience in VS Code:

```json
"git.enableSmartCommit": true,
"git.confirmSync": false,
"git.autofetch": true
```

These settings will:
- Enable Smart Commit (automatically stages all changes when there are no staged changes)
- Disable confirmation for sync operations
- Enable automatic fetching of changes from remote repositories

After applying these settings, the ignored files should no longer appear in your Source Control panel, giving you a cleaner UI focused only on the files that need your attention.

## Note

These settings are user-specific and stored in your VS Code user settings, so they'll apply to all projects you work on with VS Code on this machine.
