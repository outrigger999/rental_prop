1. Overview

This rule set governs project management, code workflow, and documentation practices for Python-based projects using the Windsurf system. It enforces a Git-centric, branch-based workflow, ensures up-to-date documentation, and mandates IDE-based file editing (except for necessary Git operations).

---

2. Git Workflow

2.1 Repository Initialization

- Existing Project:
If the project is already a Git repository, continue using it.
- New Project:
If no Git repository exists, prompt the user:
"No Git repository found. Would you like to create one and initialize it now?"
If yes, run:
      text
      git init
      git add .
      git commit -m "Initial commit"
  Then prompt for a remote repository setup and push if desired.

2.2 Branching Strategy

- All new features/fixes must branch from main.
- Branch naming: use clear, descriptive names (e.g., feature/add-login, bugfix/fix-typo).
- Before starting work, ensure you are on main and up to date:
      text
      git checkout main
      git pull
      git checkout -b <branch-name>
- Work is performed on the feature branch.
- After testing and code review, merge back into main:
      text
      git checkout main
      git merge <branch-name>
      git push
- Delete the feature branch after merge if desired.

2.3 Commit and Push Policy

- All changes must be committed with clear, concise messages.
- Push to remote after each logical unit of work.
- No direct commits to main unless merging a tested branch.

---

3. File Modification Policy

- Primary Rule:
All file modifications must be performed using the IDE’s file editor.
- Terminal Use:
Only allowed for:
  - Git operations (commit, push, branch, merge, etc.)
  - Environment setup if absolutely required.
- Avoid direct file editing via the terminal or external scripts unless no alternative exists.

---

4. Documentation Management

4.1 Continuous Documentation

- Documentation (e.g., README.md, docstrings, API docs) must be updated:
  - At the start of each new feature/branch.
  - After each significant code generation or change.
  - After merging a branch back into main.
- Use the Windsurf memory function to track and prompt for documentation updates.
- Documentation should accurately reflect the current state and usage of the codebase.

4.2 Documentation Sections

- Project Overview:
Brief summary of the project’s purpose and major features.
- Installation & Setup:
Steps to install dependencies and set up the environment.
- Usage:
How to run, test, and use the application or library.
- API Reference:
Document all public classes, functions, and endpoints.
- Changelog:
Maintain a section summarizing major changes, linked to branch merges.

---

5. Branch Merge and Main Branch Management

- After a successful merge:
  - Update all relevant documentation sections.
  - Ensure the project is on the main branch.
  - Prompt for any post-merge clean-up (e.g., branch deletion, dependency updates).
  - Confirm that the documentation reflects all merged changes.

---

6. Python-Specific Guidelines

- Follow PEP 8 for code style.
- Use type hints and docstrings for all functions and classes.
- Write unit tests for new features and bug fixes.
- Use virtual environments (venv or conda) to manage dependencies.
- List all dependencies in requirements.txt or pyproject.toml.
- Run tests locally before merging any branch.

---

7. Windsurf Memory Function Integration

- The Windsurf memory function must be used to:
  - Track branch creation, code changes, and documentation updates.
  - Prompt for documentation updates at required intervals.
  - Store summaries of changes for use in changelogs and documentation.

---

8. Enforcement and Best Practices

- Adherence:
All contributors must follow these rules for every project using this file.
- Review:
Code reviews should verify compliance with branching, documentation, and file modification policies.
- Automation:
Where possible, automate checks for documentation updates and branch management.

---

9. Appendix: Quick Reference

- Start new feature:
  1. git checkout main
  2. git pull
  3. git checkout -b feature/<name>
- Commit and push:
  1. Make changes in IDE
  2. git add .
  3. git commit -m "Describe your changes"
  4. git push
- Merge to main:
  1. Test and review
  2. git checkout main
  3. git merge feature/<name>
  4. Update documentation
  5. git push
- Update documentation:
  1. Edit docs in IDE
  2. Commit and push changes
