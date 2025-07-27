# Functional Requirements Document: Moving DB

## 1. Introduction

### 1.1 Purpose
This document specifies the functional requirements for the "Moving DB" application. It details the operations, interactions, and behaviors of the system from a user's perspective, building upon the Product Requirements Document (PRD).

### 1.2 Scope
The scope of this FRD is defined by the "In Scope" items listed in Section 1.3 of the `MovingDB_PRD.md`.

### 1.3 Definitions, Acronyms, and Abbreviations
*   **FRD:** Functional Requirements Document
*   **PRD:** Product Requirements Document
*   **UI:** User Interface
*   **API:** Application Programming Interface
*   **CRUD:** Create, Read, Update, Delete
*   **DB:** Database
*   **RPi:** Raspberry Pi

## 2. Overall Description

### 2.1 Product Perspective
Moving DB is a self-hosted web application designed for tracking items packed into moving boxes. It runs on a Raspberry Pi and is accessed via a web browser.

### 2.2 Product Functions
A summary of product functions can be found in Section 4 of the `MovingDB_PRD.md`. This FRD will elaborate on these functions.

### 2.3 User Characteristics
Refer to Section 2 of the `MovingDB_PRD.md`.

### 2.4 General Constraints
Refer to Section 6 of the `MovingDB_PRD.md` and Section 6 of `cline_docs/system_manifest.md`.

### 2.5 Assumptions and Dependencies
Refer to Section 6 of the `MovingDB_PRD.md` and Section 6 of `cline_docs/system_manifest.md`.

## 3. Specific Functional Requirements

This section details the specific functional requirements of the Moving DB application. Each requirement will be assigned a unique identifier (e.g., FR-BOX-CREATE).

---

### 3.1 FR-BOX-CREATE: Create New Box

*   **3.1.1 Description and Priority:**
    *   This function allows users to create a new box entry in the system.
    *   Priority: High. This is a core function.
*   **3.1.2 Stimulus/Response Sequence:**
    1.  User navigates to the "Create Box" page (e.g., via navigation link `/create`).
    2.  System displays a form with fields for Box Number (read-only, auto-suggested), Priority, Category, Box Size, and Description.
    3.  User fills in the required and optional fields.
    4.  User submits the form.
    5.  System validates the input.
        *   If validation fails, system re-displays the form with error messages.
        *   If validation succeeds, system creates a new box record in the database, assigns the confirmed box number, logs the creation in box history, and redirects the user to the "List Boxes" page. A success message may be displayed.
*   **3.1.3 Functional Requirements:**
    *   **Inputs:**
        *   Priority (string, required, from predefined list)
        *   Category (string, required, from predefined list)
        *   Box Size (string, required, from predefined list)
        *   Description (string, optional)
        *   Submitted Box Number (integer, from read-only field, for confirmation)
    *   **Processing:**
        1.  The system shall determine the next available box number, attempting to fill gaps in the sequence. This number is displayed on the form.
        2.  Upon submission, the system shall re-verify the availability of the submitted box number. If taken while the form was open, it shall use the next truly available number and inform the user.
        3.  The system shall validate that all required fields (Priority, Category, Box Size) are provided.
        4.  The system shall store the new box record in the `boxes` table with `is_deleted` set to false, and `created_at` and `last_modified` set to the current timestamp.
        5.  The system shall create an entry in the `box_history` table for the 'create' action, noting the editor (e.g., 'user') and timestamp.
    *   **Outputs:**
        *   A new box record persisted in the database.
        *   A new box history record.
        *   Redirection to the box list page.
        *   (Optional) A success or error message displayed to the user (e.g., via flash message).
    *   **Error Handling:**
        *   If required fields are missing, an error message shall be displayed, and the form shall not be submitted.
        *   If a database error occurs during creation, an appropriate error message shall be displayed.

---

### 3.2 FR-BOX-LIST: List Boxes

*   **3.2.1 Description and Priority:**
    *   This function allows users to view a list of all non-deleted boxes.
    *   Priority: High.
*   **3.2.2 Stimulus/Response Sequence:**
    1.  User navigates to the "List Boxes" page (e.g., via navigation link `/list`).
    2.  System retrieves all non-deleted boxes from the database, ordered by box number.
    3.  System displays the boxes in a paginated list, showing key attributes (Box #, Priority, Category, Size, Description) and action buttons (Edit, Delete) for each.
*   **3.2.3 Functional Requirements:**
    *   **Inputs:**
        *   (Optional) Page number for pagination.
        *   (Optional) Filter parameters (Box #, Priority, Category, Size, Description - handled by search functionality but can apply to list view).
    *   **Processing:**
        1.  The system shall query the `boxes` table for records where `is_deleted` is false.
        2.  The system shall order the results by `box_number`.
        3.  The system shall implement pagination if the number of boxes exceeds a predefined limit per page (e.g., 20).
        4.  For each box, the system shall determine the display color for priority.
    *   **Outputs:**
        *   A rendered HTML page displaying the list of boxes.
        *   Pagination controls if applicable.
    *   **Error Handling:**
        *   If a database error occurs, an appropriate error message shall be displayed.

---
*(Further FR sections for Edit, Delete, Search, Export, Backup, API, etc., will follow a similar detailed pattern.)*

## 4. Interface Requirements

### 4.1 User Interfaces
*   **Main Layout (`base.html`):** Provides consistent navigation (desktop and mobile), header, and footer.
*   **Create/Edit Box Page (`create.html`):** Form for inputting box details.
*   **List Boxes Page (`list.html`):** Displays a paginated list of boxes with sort and filter options. Includes action buttons for each box.
*   **Search Page (`search.html`):** Forms for description-based and attribute-based search, with a dynamic results display area.
*   **Export Page (`export.html`):** Links/buttons to trigger CSV and JSON exports.
*   **Backup Page (`backup.html`):** Displays backup configuration, list of available backups, and controls for manual backup, deleting backups, and purging data.

### 4.2 API Interfaces
*   **GET `/api/boxes`**: Lists boxes. Supports query parameters for filtering. Returns JSON.
*   **DELETE `/api/boxes/<id>`**: Soft-deletes a box. Returns JSON confirmation.
*   **POST `/api/clear-database`**: Clears all box data. Returns JSON confirmation.
*   **POST `/api/purge-deleted`**: Permanently removes soft-deleted boxes. Returns JSON confirmation.

## 5. Non-Functional Requirements

### 5.1 Performance
*   Page loads for common views (List, Create) should be within 2-3 seconds on the target Raspberry Pi environment with a reasonable dataset (e.g., up to 1000 boxes).
*   Search operations should return results within 3-5 seconds.
*   Database backup operations should not significantly degrade application responsiveness for other users (if applicable, though primarily single-user focused).

### 5.2 Reliability
*   The application shall ensure data integrity for box information and backups.
*   Automated backups shall occur as scheduled.
*   The system should handle common user errors gracefully (e.g., invalid input).

### 5.3 Usability
*   The UI shall be intuitive and easy to navigate for non-technical users.
*   Forms and controls shall be clearly labeled.
*   The application shall be responsive and usable on common desktop and mobile browsers.

### 5.4 Security
*   As a self-hosted application without user authentication in its current scope, primary security relies on network security of the Raspberry Pi and the local environment.
*   Input sanitization should be practiced to prevent common web vulnerabilities (e.g., XSS, though Flask/Jinja2 provide some protection).
*   File paths for downloads/uploads (if any in future) should be carefully validated.

### 5.5 Maintainability
*   Code shall be well-commented and follow Python best practices.
*   The application is structured into logical modules (`simplified_app.py`, `export.py`, `logger.py`, `backup.py`).
*   Configuration is managed via `backup_config.json`.

### 5.6 Deployability
*   The application is designed for deployment on a Raspberry Pi 4.
*   Deployment is facilitated by `setup_raspberry_pi.sh` and sync scripts.

## 6. Data Requirements

### 6.1 Database Schema
*   The database uses SQLite. The schema is defined in `schema.sql` and includes `boxes` and `box_history` tables. Key fields include box number, priority, category, size, description, timestamps, and a soft-delete flag.

### 6.2 Data Retention
*   Box data is retained indefinitely unless explicitly purged (for soft-deleted items) or the database is cleared.
*   Backup retention is configurable via `backup_config.json` (max number of backups).

## 7. Logging Requirements
*   All significant application events, user actions (requests/responses), database operations, and errors shall be logged.
*   Logs shall be written to a rotating file (`logs/moving_box_tracker.log`) and to the console.
*   Log entries shall include timestamp, severity level, module, function name (for file logs), and a descriptive message.
