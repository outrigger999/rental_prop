# Tech Stack

## Scripting & Automation
- **Bash**: Used for sync scripts between Mac and Raspberry Pi (e.g., sync_to_pi.sh)
- **Python**: Used for data processing, migration scripts, and web application

## Web Application
- **Flask**: Web framework for the moving box tracker application
- **SQLite**: Database for storing box and category information
- **JavaScript**: Client-side scripting for interactive UI components
- **HTML/CSS**: Frontend markup and styling

## Project Structure & Management
- **Markdown**: For documentation and workflow management
- **Git**: Version control for all project files

## Platforms
- **macOS**: Primary development and sync origin
- **Raspberry Pi OS**: Sync target and secondary compute node

## Rationale
- Bash is chosen for its native compatibility with Unix-like systems and ease of automation.
- Python is used for its flexibility and readability in data-related tasks and web development.
- Flask provides a lightweight web framework that's easy to deploy on Raspberry Pi.
- SQLite offers a serverless database solution that's perfect for small to medium applications.
- JavaScript enhances the user experience with client-side interactivity without requiring page reloads.
- Markdown ensures documentation is accessible and easy to maintain.
- Git provides robust version control and collaboration support.
