# Technical Stack - Rental Property Tracker

## Core Technologies

### Backend
- **Language:** Python 3.x
- **Framework:** Flask
- **Database:** SQLite (embedded, file-based)
- **ORM:** Direct SQLite operations (no heavy ORM needed for this scale)

### Frontend
- **Templates:** Jinja2 (Flask's built-in templating)
- **Styling:** Custom CSS
- **JavaScript:** Vanilla JavaScript for interactive elements
- **Build Process:** None required (simple static files)

### Infrastructure
- **Deployment Platform:** Raspberry Pi 4 (local network)
- **Operating System:** Raspberry Pi OS (Linux-based)
- **Web Server:** Flask development server (production consideration: nginx + gunicorn)
- **Process Management:** systemd service (`rental_prop.service`)

## Development Tools

### Version Control
- **System:** Git
- **Repository:** GitHub (outrigger999/rental_prop)
- **Workflow:** Feature branches → main branch
- **Deployment:** Git pull on Pi (no direct file sync)

### Environment Management
- **Python Environment:** Conda environment (`rental_prop_env`)
- **Dependencies:** requirements.txt
- **Sync Script:** Custom bash script for deployment automation

## Architecture Patterns

### Application Structure
- **Pattern:** Model-View-Controller (implied by Flask structure)
- **Database Access:** Direct SQLite connections with proper connection handling
- **Static Files:** Flask's built-in static file serving
- **Templates:** Jinja2 template inheritance

### Security Considerations
- **Input Validation:** Prevent SQL injection through parameterized queries
- **File Upload Security:** Validate file types and sizes for image uploads
- **Network Access:** Internal network only (no external exposure planned)

## Key Integrations

### Planned External Services
- **Google Maps API:** For route image generation and commute analysis
- **Criticality:** Medium (manual image upload as fallback)
- **Implementation:** Phase 2 feature

## Development Practices

### Code Quality
- **Testing Strategy:** Manual testing (personal project scale)
- **Documentation:** Markdown files in `windsurf_docs/`
- **Code Review:** Not applicable (single developer)

### Deployment Strategy
- **Method:** Git-based deployment via sync script
- **Automation:** Bash script handles sync, service restart, environment updates
- **Rollback:** Git branch/commit-based rollback capability

## Performance Considerations

### Raspberry Pi Optimization
- **Database:** SQLite suitable for single-user, moderate data volume
- **Images:** Optimize file sizes, implement lazy loading
- **Memory:** Monitor Flask memory usage, restart service if needed
- **Storage:** Regular cleanup of temporary files and logs

## Future Technical Debt
- **Flask Route Organization:** Refactor into blueprints as features grow
- **Error Handling:** Implement comprehensive logging and error pages
- **Database Queries:** Add indexing and query optimization as data grows
- **Security Hardening:** Add CSRF protection, secure headers if external access needed
