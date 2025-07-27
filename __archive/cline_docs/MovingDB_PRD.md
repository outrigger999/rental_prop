# Product Requirements Document: Moving DB

## 1. Introduction

### 1.1 Purpose
This document outlines the product requirements for the "Moving DB" application. It serves as a guide for understanding the application's objectives, features, and target users.

### 1.2 Project Goals
The primary goal of Moving DB is to provide a simple, efficient, and reliable web application for users to track items packed into moving boxes. Key objectives include:
*   Ease of use for creating, viewing, editing, and searching for boxes.
*   Clear organization of box contents and attributes (priority, category, size).
*   Robust data management with export capabilities and automated backups.
*   Deployment on a low-cost, accessible platform like a Raspberry Pi.

### 1.3 Scope
**In Scope:**
*   Core box management functionalities (Create, Read, Update, Soft Delete).
*   Advanced search and filtering capabilities.
*   Data export to CSV, JSON, PDF (table and labels), and Markdown.
*   Automated and manual database backup and restore functionalities.
*   A web-based user interface accessible via modern browsers, with mobile responsiveness.
*   Basic API for box listing and deletion.
*   Deployment on a Raspberry Pi using Nginx and a systemd service.

**Out of Scope (for initial version):**
*   User authentication and multi-user accounts.
*   Real-time collaboration features.
*   Image attachments for boxes or items.
*   Complex inventory management features beyond box tracking.

## 2. Target Audience

### 2.1 Primary Users
*   Individuals or families preparing for a move who need to organize and track packed items.
*   Users who prefer a self-hosted solution for privacy and control over their data.
*   Users comfortable with basic web application interaction.

## 3. User Stories

*   **As a user preparing for a move, I want to easily create a new box entry with its number, priority, category, size, and a description of its contents, so I can quickly catalog what I've packed.**
*   **As a user, I want to view a list of all my boxes, with key details visible at a glance, so I can quickly find information.**
*   **As a user, I want to edit the details of an existing box if I make a mistake or need to update its contents, so my inventory remains accurate.**
*   **As a user, I want to search for boxes based on their number, priority, category, size, or keywords in their description, so I can locate specific items or types of boxes quickly.**
*   **As a user, I want to export my box inventory to common formats (CSV, JSON, PDF), so I can have a portable copy or share it with others.**
*   **As a user, I want to print labels for my boxes, so I can easily identify them physically.**
*   **As a user, I want the application to automatically back up my data, so I don't have to worry about data loss.**
*   **As a user, I want to be able to manually trigger a backup before making significant changes, for peace of mind.**
*   **As a user, I want to access the application from my desktop or mobile device, so I can manage my boxes conveniently.**

## 4. Product Features

### 4.1 Box Management (CRUD)
*   **F1.1 Create Box:** Users can create new box entries.
    *   Box number is automatically suggested (filling gaps) but confirmed on submission.
    *   Required fields: Priority, Category, Box Size.
    *   Optional field: Description.
*   **F1.2 List Boxes:** Users can view a paginated list of all non-deleted boxes.
    *   Displays box number, priority (color-coded), category, size, and description.
    *   Provides options to edit or delete each box.
*   **F1.3 Edit Box:** Users can modify the priority, category, box size, and description of an existing box.
*   **F1.4 Delete Box (Soft Delete):** Users can mark a box as deleted. Soft-deleted boxes are hidden from normal views but remain in the database.
*   **F1.5 Box History:** System automatically logs creation, update, and deletion events for each box, including editor and timestamp.

### 4.2 Search and Filtering
*   **F2.1 Basic Search:** Users can search for boxes by keywords in the description.
*   **F2.2 Attribute Search:** Users can search/filter boxes by:
    *   Box Number
    *   Priority
    *   Category
    *   Box Size
*   **F2.3 Dynamic Results:** Search results are displayed dynamically on the page.

### 4.3 Data Export
*   **F3.1 CSV Export:** Export all or filtered box data to a CSV file.
*   **F3.2 JSON Export:** Export all or filtered box data to a JSON file.
*   **F3.3 PDF Table Export:** Export all or filtered box data as a formatted table in a PDF document.
*   **F3.4 Markdown Export:** Export all or filtered box data to a Markdown file.
*   **F3.5 PDF Label Export:** Generate a PDF document with printable labels for selected or all boxes.

### 4.4 Database Backup and Restore
*   **F4.1 Automated Backups:** The system performs automated daily backups of the SQLite database (configurable interval).
*   **F4.2 Manual Backups:** Users can trigger a manual backup at any time via the web interface.
*   **F4.3 Backup Configuration:** Users can configure the maximum number of backups to retain.
*   **F4.4 Backup Management:** Users can view a list of available backups, download specific backup files, and delete backup files.
*   **F4.5 Data Purge:** Users can permanently remove soft-deleted box data from the database.
*   **F4.6 Restoration Guide:** The UI provides instructions for manual database restoration.
*   **F4.7 Standalone Backup Script (`backup.py`):** An alternative script provides task-tracked backup capabilities. Its integration with the main app's backup system should be considered.

### 4.5 User Interface
*   **F5.1 Web-Based Interface:** Accessible via a standard web browser.
*   **F5.2 Responsive Design:** The UI is designed to be usable on both desktop and mobile devices.
*   **F5.3 Navigation:** Clear navigation for accessing Create, List, Search, Export, and Backup functionalities.
*   **F5.4 Visual Feedback:** Uses Bootstrap styling for a clean and consistent look. Flash messages provide feedback on operations.

### 4.6 API
*   **F6.1 List Boxes API (`/api/boxes`):** Allows fetching a list of boxes, supporting filtering parameters.
*   **F6.2 Delete Box API (`/api/boxes/<id>`):** Allows programmatic deletion of a box.
*   **F6.3 Clear Database API (`/api/clear-database`):** Allows clearing all box data (primarily for testing).
*   **F6.4 Purge Deleted API (`/api/purge-deleted`):** Allows programmatic purging of soft-deleted data.

### 4.7 Logging
*   **F7.1 Comprehensive Logging:** The application logs important events, requests, responses, database operations, and errors.
*   **F7.2 File & Console Output:** Logs are written to a rotating log file and to the console (with configurable levels).

## 5. Deployment and Operations

### 5.1 Raspberry Pi Deployment
*   The application is designed to be deployed on a Raspberry Pi 4.
*   A setup script (`setup_raspberry_pi.sh`) automates the installation of dependencies, Python virtual environment, systemd service, and Nginx reverse proxy configuration.

### 5.2 Synchronization
*   Scripts (`sync_to_pi.sh`, `sync_from_pi.sh`) are provided for synchronizing application files between a development machine and the Raspberry Pi.

## 6. Assumptions and Constraints
*   Refer to Section 6 of `cline_docs/system_manifest.md`. Key items include reliance on Raspberry Pi environment, SQLite suitability, and potential inconsistencies (Alembic, port numbers).

## 7. Success Metrics (High-Level)
*   **Usability:** Users can easily learn and efficiently use the application for its intended purpose.
*   **Reliability:** The application functions consistently without data loss or frequent errors. Backups are performed reliably.
*   **Performance:** The application responds quickly to user actions, especially for listing and searching boxes.
*   **Completeness:** All core features for box tracking and data management are implemented.

## 8. Future Considerations
*   Refer to Section 7 of `cline_docs/system_manifest.md`. Includes user authentication, image uploads, etc.
