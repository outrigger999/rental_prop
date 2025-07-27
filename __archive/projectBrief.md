# Moving Box Tracker - Project Brief

## Overview
The Moving Box Tracker is a web-based application designed to help users track and manage boxes during a move. It provides a simple, intuitive interface for creating, editing, and searching boxes with various attributes such as priority, category, and size. The application is specifically designed to be mobile-friendly and deployable on a Raspberry Pi, making it accessible from any device within a home network during the moving process.

## Purpose
Moving can be chaotic, and it's easy to lose track of what items are packed in which boxes. This application solves that problem by providing a centralized system to:
- Track box contents with detailed descriptions
- Prioritize boxes based on importance
- Categorize boxes by room or purpose
- Quickly locate specific items through search functionality

## Target Users
- Individuals or families in the process of moving
- Anyone needing to organize and track boxed items in storage
- Small moving companies that need a simple inventory system

## Core Features
- **Box Creation**: Create new boxes with auto-incremented box numbers
- **Box Management**: Edit existing box details or delete boxes
- **Box Listing**: View all boxes with filtering options
- **Search Functionality**: Find boxes by number, priority, category, size, or description
- **Mobile-First Design**: Optimized for use on smartphones and tablets
- **Responsive UI**: Bootstrap-based interface that works across devices

## Technical Implementation
- **Backend**: Flask (Python) with SQLite database
- **Frontend**: HTML, CSS (Bootstrap 5), and vanilla JavaScript
- **Deployment**: Designed for Raspberry Pi with Nginx as reverse proxy
- **Architecture**: Single-file Flask application for simplicity and reliability

## Current Status
The application is functional with all core features implemented. The codebase is organized in a simplified structure for ease of maintenance and deployment.