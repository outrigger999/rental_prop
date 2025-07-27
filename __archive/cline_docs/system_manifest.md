# System Manifest

## 1. Project Overview

*   **Project Name:** Moving DB
*   **Version:** 1.0 (based on `simplified_app.py` comment)
*   **Date:** 2025-05-15
*   **High-Level Goal:** A web application to efficiently track items packed into moving boxes, providing features for box creation, editing, listing, searching, data export, and automated database backups.

## 2. Core Functionality

*   **Box Management (CRUD):**
    *   Create new boxes with details like priority, category, size, and description.
    *   View a paginated list of all boxes.
    *   Edit details of existing boxes.
    *   Soft-delete boxes (mark as deleted).
    *   Search boxes by box number, priority, category, size, or description content.
*   **Automated Box Numbering:** Assigns the next available box number, attempting to fill gaps in the sequence.
*   **Box History Tracking:** Logs creation, updates, and deletion events for each box.
*   **Data Export:**
    *   Export box data to CSV format.
    *   Export box data to JSON format.
    *   Export box data to PDF format (table view).
    *   Export box data to Markdown format.
    *   Generate printable PDF labels for individual boxes.
*   **Database Backup & Restore:**
    *   Automated daily backups of the SQLite database.
    *   Manual backup trigger via the web interface.
    *   Configuration for backup directory, retention policy (max backups).
    *   Ability to download and delete specific backup files.
    *   Ability to purge soft-deleted box data from the database.
    *   A standalone `backup.py` script offers alternative/supplementary backup management with task tracking.
*   **User Interface:** Web-based interface built with Flask and HTML templates (Bootstrap for styling), providing access to all core functionalities. Includes mobile-responsive design.
*   **API Endpoints:**
    *   List boxes (with filtering).
    *   Delete a box.
    *   Clear the entire database (for testing).
    *   Purge soft-deleted data.
*   **Logging:** Structured logging for application events, requests, responses, and errors to both file (with rotation) and console.

## 3. System Architecture

*   **Key Technologies:**
    *   Backend: Python 3.11, Flask 3.1.0
    *   Database: SQLite
    *   Frontend: HTML, CSS (Bootstrap 5.3), JavaScript
    *   PDF Generation: ReportLab
    *   Scheduling: APScheduler (for in-app daily backups)
*   **Architectural Style:** Monolithic web application.
*   **Deployment Environment:** All code is executed on a Raspberry Pi 4 device at IP address `192.168.10.10`. Nginx is used as a reverse proxy, typically forwarding requests from port 80 to the application running on an internal port (e.g., 8000 as per `setup_raspberry_pi.sh`, or 5000 if `simplified_app.py` is run directly).
*   **Synchronization:** The `sync_to_pi.sh` script is used to synchronize application files to the Raspberry Pi. `sync_from_pi.sh` can be used to retrieve files from the Pi.
*   **Service Management:** A systemd service (`moving-box-tracker.service` or `moving_boxes.service`) is intended for managing the application process on the Raspberry Pi.

## 4. Domain Modules

*   **Core Application (`simplified_app.py`):** Handles web requests, business logic for box management, database interactions (via helper functions), and serves HTML templates.
*   **Database Management:** SQLite database (`moving_boxes.db`) with schema defined in `schema.sql` and managed by `simplified_app.py`. Includes `boxes` and `box_history` tables.
*   **User Interface (Templates & Static Assets):**
    *   HTML Templates (`templates/`): Defines the structure and presentation of web pages using Jinja2 and Bootstrap. Key templates include `base.html` (layout), `create.html` (add/edit box), `list.html` (box listing), `search.html`, `export.html`, `backup.html`.
    *   Static Assets (`static/`): Contains CSS (`styles.css`) and client-side JavaScript (`main.js`) for styling and dynamic interactions.
*   **Data Export (`export.py`):** Provides functions to export box data into CSV, JSON, PDF, and Markdown formats, and to generate PDF box labels.
*   **Logging (`logger.py`):** Implements a structured logging system for application events, with file and console output, and log rotation.
*   **Backup System (`simplified_app.py` internal logic & `backup.py` standalone script):**
    *   In-app: Automated daily backups via APScheduler, manual trigger, configuration via `backup_config.json`.
    *   Standalone `backup.py`: More detailed task-based backup management, also using `backup_config.json`, with features for listing, rotating, and deleting specific backups.
*   **Deployment & Setup Scripts:**
    *   `setup_raspberry_pi.sh`: Automates application deployment on a Raspberry Pi, including system updates, dependency installation, virtual environment setup, systemd service creation, and Nginx configuration.
    *   `sync_to_pi.sh`: Synchronizes project files from local machine to Raspberry Pi.
    *   `sync_from_pi.sh`: Synchronizes project files from Raspberry Pi to local machine.
*   **Developer Utilities:**
    *   `insert-variables.sh`: Script for customizing development tool configuration files (e.g., for "Roo-Code/Roo-Cline").

## 5. Key Stakeholders

*   **Primary User(s):** Individuals or families managing items during a move.
*   **Developer/Maintainer:** Scott (mentioned as author in `simplified_app.py`).

## 6. Assumptions and Constraints

*   **Assumptions:**
    *   The Raspberry Pi 4 at `192.168.10.10` is accessible and configured for code execution as per `setup_raspberry_pi.sh`.
    *   The `sync_to_pi.sh` script is functional and available for deployment.
    *   Dependencies listed in `requirements.txt` are compatible and sufficient.
    *   SQLite is adequate for the scale of data and concurrency needs.
    *   Nginx is correctly configured as a reverse proxy on the Raspberry Pi.
*   **Constraints:**
    *   The application must be compatible with the Raspberry Pi 4 environment (Python 3.9+ as per script comments).
    *   Modifications require a synchronization step using `sync_to_pi.sh` before they are live on the target device.
    *   The `setup_raspberry_pi.sh` script mentions `alembic upgrade head`, but Alembic is not in `requirements.txt`, indicating a potential inconsistency or an undocumented dependency/process.
    *   The application port might differ between direct execution (`simplified_app.py` runs on 5000) and the Nginx proxied setup (expects app on 8000).

## 7. Future Considerations (Optional)

*   User authentication and multi-user support.
*   Direct PDF/Markdown export options in the UI.
*   Integration of the more robust `backup.py` features into the web UI or a clearer definition of its role alongside the in-app backup.
*   Clarification and potential removal/integration of the Alembic step in deployment.
*   Image uploads for boxes or items.

## 8. Document History

| Version | Date       | Author        | Changes                                                                 |
|---------|------------|---------------|-------------------------------------------------------------------------|
| 0.1     | 2025-05-15 | Cline         | Initial draft                                                           |
| 0.2     | 2025-05-15 | Cline         | Populated with comprehensive details after project file analysis.         |
