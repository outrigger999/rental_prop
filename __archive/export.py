#!/usr/bin/env python3
"""
Moving Box Tracker - Data Export Module
======================================

Provides functionality to export box data in various formats (CSV, PDF).
Supports filtering and customization of exported data.

Target Platform: Raspberry Pi 4
Python Version: Python 3.9+
Code Version: 1.0
"""

import os
import csv
import json
import sqlite3
from datetime import datetime
import logger
from xml.sax.saxutils import escape

# Try to import PDF generation libraries, with fallbacks
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not installed. PDF export will not be available.")

# Configuration
EXPORT_DIRECTORY = 'exports'
DATE_FORMAT = '%Y-%m-%d_%H-%M-%S'

# Ensure export directory exists
if not os.path.exists(EXPORT_DIRECTORY):
    os.makedirs(EXPORT_DIRECTORY)
    logger.info(f"Created export directory: {EXPORT_DIRECTORY}")

def get_db_connection(db_path='moving_boxes.db'):
    """Get a connection to the database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_boxes_for_export(
    conn, 
    include_deleted=False, 
    box_number=None, 
    priority=None, 
    category=None, 
    box_size=None, 
    search_term=None
):
    """Get boxes from the database with optional filtering"""
    query = 'SELECT * FROM boxes'
    params = []
    conditions = []
    
    if not include_deleted:
        conditions.append('NOT is_deleted')
    
    if box_number:
        conditions.append('box_number = ?')
        params.append(box_number)
    
    if priority:
        conditions.append('priority = ?')
        params.append(priority)
    
    if category:
        conditions.append('category = ?')
        params.append(category)
        
    if box_size:
        conditions.append('box_size = ?')
        params.append(box_size)
        
    if search_term:
        search_like = f'%{search_term}%'
        conditions.append('(description LIKE ? OR notes LIKE ?)')
        params.append(search_like)
        params.append(search_like)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY box_number'
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()

def export_to_csv(
    db_connection,
    search_term=None, 
    category=None, 
    priority=None, 
    custom_filename=None
):
    """
    Export box data to CSV format.
    
    Args:
        db_connection: SQLite database connection
        search_term: Optional search term to filter boxes
        category: Optional category to filter boxes
        priority: Optional priority to filter boxes
        custom_filename: Optional custom filename for the export
        
    Returns:
        tuple: (success, filepath or error message)
    """
    try:
        os.makedirs(EXPORT_DIRECTORY, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            safe_filename = "".join([c if c.isalnum() else "_" for c in custom_filename])
            filename = f"{safe_filename}_{timestamp}.csv"
        else:
            filename = f"box_export_{timestamp}.csv"
            
        filepath = os.path.join(EXPORT_DIRECTORY, filename)
        
        boxes = get_boxes_for_export(
            db_connection, 
            search_term=search_term,
            category=category,
            priority=priority
        )
        
        if not boxes:
            logger.warning("No boxes found for export")
            return (False, "No boxes found matching the criteria")
            
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = boxes[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for box in boxes:
                writer.writerow(dict(box))
        
        logger.info(f"Exported {len(boxes)} boxes to CSV: {filepath}")
        return (True, filepath)
    
    except Exception as e:
        logger.exception(f"Error exporting to CSV: {str(e)}")
        return (False, str(e))

def export_to_json(
    db_connection, 
    search_term=None, 
    category=None, 
    priority=None, 
    custom_filename=None
):
    """
    Export box data to JSON format.
    
    Args:
        db_connection: SQLite database connection
        search_term: Optional search term to filter boxes
        category: Optional category to filter boxes
        priority: Optional priority to filter boxes
        custom_filename: Optional custom filename for the export
        
    Returns:
        tuple: (success, filepath or error message)
    """
    try:
        os.makedirs(EXPORT_DIRECTORY, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            safe_filename = "".join([c if c.isalnum() else "_" for c in custom_filename])
            filename = f"{safe_filename}_{timestamp}.json"
        else:
            filename = f"box_export_{timestamp}.json"
            
        filepath = os.path.join(EXPORT_DIRECTORY, filename)
        
        boxes = get_boxes_for_export(
            db_connection, 
            search_term=search_term,
            category=category,
            priority=priority
        )
        
        if not boxes:
            logger.warning("No boxes found for export")
            return (False, "No boxes found matching the criteria")
        
        serializable_boxes = []
        for box in boxes:
            box_dict = dict(box)
            for key, value in box_dict.items():
                if isinstance(value, datetime):
                    box_dict[key] = value.isoformat()
            serializable_boxes.append(box_dict)
            
        with open(filepath, 'w') as jsonfile:
            json.dump({
                "export_date": datetime.now().isoformat(),
                "box_count": len(serializable_boxes),
                "boxes": serializable_boxes
            }, jsonfile, indent=2)
        
        logger.info(f"Exported {len(boxes)} boxes to JSON: {filepath}")
        return (True, filepath)
    
    except Exception as e:
        logger.exception(f"Error exporting to JSON: {str(e)}")
        return (False, str(e))

def export_to_pdf(
    db_connection, 
    search_term=None, 
    category=None, 
    priority=None, 
    custom_filename=None
):
    """
    Export box data to PDF format.
    
    Args:
        db_connection: SQLite database connection
        search_term: Optional search term to filter boxes
        category: Optional category to filter boxes
        priority: Optional priority to filter boxes
        custom_filename: Optional custom filename for the export
        
    Returns:
        tuple: (success, filepath or error message)
    """
    if not REPORTLAB_AVAILABLE:
        logger.error("PDF export not available. Install reportlab package.")
        return (False, "PDF export not available. Install reportlab package.")
    
    try:
        os.makedirs(EXPORT_DIRECTORY, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            safe_filename = "".join([c if c.isalnum() else "_" for c in custom_filename])
            filename = f"{safe_filename}_{timestamp}.pdf"
        else:
            filename = f"box_export_{timestamp}.pdf"
            
        filepath = os.path.join(EXPORT_DIRECTORY, filename)
        
        boxes = get_boxes_for_export(
            db_connection, 
            search_term=search_term,
            category=category,
            priority=priority
        )
        
        if not boxes:
            logger.warning("No boxes found for export")
            return (False, "No boxes found matching the criteria")
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        title = Paragraph("Moving Box Tracker - Box Export", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        timestamp_str = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
        elements.append(timestamp_str)
        elements.append(Spacer(1, 12))
        
        data = []
        
        header = ['Box #', 'Priority', 'Category', 'Size', 'Description', 'Created', 'Modified']
        data.append(header)
        
        for box in boxes:
            created_at_val = box.get('created_at')
            created_at = created_at_val.strftime('%Y-%m-%d') if isinstance(created_at_val, datetime) else str(created_at_val or '')[:10]
            last_modified_val = box.get('last_modified')
            last_modified = last_modified_val.strftime('%Y-%m-%d') if isinstance(last_modified_val, datetime) else str(last_modified_val or '')[:10]

            description_text = str(box.get('description', ""))
            escaped_description = escape(description_text)

            row = [
                str(box.get('box_number', '')),
                str(box.get('priority', '')),
                str(box.get('category', '')),
                str(box.get('box_size', '')),
                escaped_description, 
                created_at,
                last_modified
            ]
            data.append(row)
        
        table = Table(data, colWidths=[40, 60, 80, 50, 200, 70, 70]) 
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'), 
            ('ALIGN', (1, 1), (1, -1), 'CENTER'), 
            ('ALIGN', (3, 1), (3, -1), 'CENTER'), 
            ('ALIGN', (5, 1), (6, -1), 'CENTER'), 
            ('VALIGN', (4, 1), (4, -1), 'TOP'), 
        ])
        table.setStyle(style)
        
        elements.append(table)
        
        doc.build(elements)
        
        logger.info(f"Exported {len(boxes)} boxes to PDF: {filepath}")
        return (True, filepath)
    
    except Exception as e:
        problematic_box_info = "Unknown" 
        try:
            problematic_box_info = f"Box Number: {box.get('box_number', 'N/A')}"
        except NameError: 
            pass
        except Exception as inner_e:
            problematic_box_info = f"Error getting box info: {inner_e}"
            
        logger.exception(f"Error exporting to PDF: {str(e)}. Last processed box info: {problematic_box_info}")
        return (False, f"PDF Export Error: {str(e)}")

def export_to_markdown(
    db_connection, 
    search_term=None, 
    category=None, 
    priority=None, 
    custom_filename=None
):
    """
    Export box data to Markdown format.
    
    Args:
        db_connection: SQLite database connection
        search_term: Optional search term to filter boxes
        category: Optional category to filter boxes
        priority: Optional priority to filter boxes
        custom_filename: Optional custom filename for the export
        
    Returns:
        tuple: (success, filepath or error message)
    """
    try:
        os.makedirs(EXPORT_DIRECTORY, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if custom_filename:
            safe_filename = "".join([c if c.isalnum() else "_" for c in custom_filename])
            filename = f"{safe_filename}_{timestamp}.md"
        else:
            filename = f"box_export_{timestamp}.md"

        filepath = os.path.join(EXPORT_DIRECTORY, filename)

        boxes = get_boxes_for_export(
            db_connection, 
            search_term=search_term,
            category=category,
            priority=priority
        )

        if not boxes:
            logger.warning("No boxes found for export")
            return (False, "No boxes found matching the criteria")

        with open(filepath, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# Moving Box Inventory\n\n")
            md_file.write(f"*Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

            filters = []
            if search_term:
                filters.append(f"Search term: '{search_term}'")
            if category:
                filters.append(f"Category: '{category}'")
            if priority:
                filters.append(f"Priority: '{priority}'")

            if filters:
                md_file.write("**Filters applied:** " + ", ".join(filters) + "\n\n")

            md_file.write(f"**Total Boxes:** {len(boxes)}\n\n")

            md_file.write("| Box # | Priority | Category | Box Size | Description | Notes | Created | Modified |\n")
            md_file.write("|-------|----------|----------|----------|-------------|-------|---------|----------|\n")

            for box in boxes:
                box_num_str = str(box.get('box_number', ''))
                priority_str = str(box.get('priority', ''))
                category_str = str(box.get('category', ''))
                box_size_str = str(box.get('box_size', ''))
                description = str(box.get('description', '')).replace('|', '\\|').replace('\n', ' ')
                notes = str(box.get('notes', '')).replace('|', '\\|').replace('\n', ' ')
                
                created_at_val = box.get('created_at')
                created_at = created_at_val.strftime('%Y-%m-%d') if isinstance(created_at_val, datetime) else str(created_at_val or '')[:10]
                last_modified_val = box.get('last_modified')
                last_modified = last_modified_val.strftime('%Y-%m-%d') if isinstance(last_modified_val, datetime) else str(last_modified_val or '')[:10]

                row = f"| {box_num_str} | {priority_str} | {category_str} | {box_size_str} | {description} | {notes} | {created_at} | {last_modified} |\n"
                md_file.write(row)

            md_file.write("\n## Box Categories\n\n")

            categories = {}
            for box in boxes:
                cat = box.get('category', 'Uncategorized')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(box)

            for category_name, cat_boxes in sorted(categories.items()):
                md_file.write(f"### {category_name}\n\n")
                md_file.write(f"**Number of boxes:** {len(cat_boxes)}\n\n")
                box_numbers = [str(b.get('box_number', '?')) for b in cat_boxes]
                md_file.write("Box Numbers: " + ", ".join(box_numbers) + "\n\n")

        logger.info(f"Successfully exported {len(boxes)} boxes to Markdown: {filepath}")
        return (True, filepath)

    except Exception as e:
        problematic_box_info = "Unknown" 
        try:
            problematic_box_info = f"Box Number: {box.get('box_number', 'N/A')}"
        except NameError: 
            pass
        except Exception as inner_e:
            problematic_box_info = f"Error getting box info: {inner_e}"

        logger.exception(f"Error exporting to Markdown: {str(e)}. Last processed box info: {problematic_box_info}")
        return (False, f"Markdown Export Error: {str(e)}")

def export_box_labels(
    db_connection, 
    box_ids=None, 
    filename=None, 
    label_size='4x6'  # Standard shipping label size
):
    """
    Export box labels to a PDF file.
    
    Args:
        db_connection: SQLite database connection
        box_ids: Optional list of box IDs to filter labels
        filename: Optional custom filename for the export
        label_size: Optional label size (default: 4x6)
        
    Returns:
        tuple: (success, filepath or error message)
    """
    if not REPORTLAB_AVAILABLE:
        logger.error("PDF export not available. Install reportlab package.")
        return (False, "PDF export not available. Install reportlab package.")
    
    try:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"box_labels_{timestamp}.pdf"
        
        filepath = os.path.join(EXPORT_DIRECTORY, filename)
        
        if box_ids:
            placeholders = ','.join('?' for _ in box_ids)
            query = f'SELECT * FROM boxes WHERE id IN ({placeholders}) AND NOT is_deleted ORDER BY box_number'
            cursor = db_connection.cursor()
            cursor.execute(query, box_ids)
        else:
            cursor = db_connection.cursor()
            cursor.execute('SELECT * FROM boxes WHERE NOT is_deleted ORDER BY box_number')
        
        boxes = cursor.fetchall()
        
        if not boxes:
            logger.warning("No boxes found for label export")
            return (False, "No boxes found matching the criteria")
        
        if label_size == '4x6':
            pagesize = (4 * 72, 6 * 72)
        else:
            pagesize = letter
        
        doc = SimpleDocTemplate(filepath, pagesize=pagesize, leftMargin=10, rightMargin=10, topMargin=10, bottomMargin=10)
        styles = getSampleStyleSheet()
        
        box_number_style = styles['Title']
        box_number_style.alignment = 1  # Center alignment
        
        text_style = styles['Normal']
        text_style.alignment = 1  # Center alignment
        
        all_elements = []
        
        for box in boxes:
            elements = []
            
            box_number = Paragraph(f"BOX #{box['box_number']}", box_number_style)
            elements.append(box_number)
            elements.append(Spacer(1, 10))
            
            priority_text = f"Priority: {box['priority']}"
            priority = Paragraph(priority_text, text_style)
            elements.append(priority)
            elements.append(Spacer(1, 5))
            
            category = Paragraph(f"Category: {box['category']}", text_style)
            elements.append(category)
            elements.append(Spacer(1, 5))
            
            size = Paragraph(f"Size: {box['box_size']}", text_style)
            elements.append(size)
            elements.append(Spacer(1, 10))
            
            description = Paragraph(f"Contents: {box['description']}", text_style)
            elements.append(description)
            
            if box != boxes[-1]:
                all_elements.extend(elements)
                all_elements.append(PageBreak())
            else:
                all_elements.extend(elements)
        
        doc.build(all_elements)
        
        logger.info(f"Exported {len(boxes)} box labels to PDF: {filepath}")
        return (True, filepath)
    
    except Exception as e:
        logger.exception(f"Error exporting box labels: {str(e)}")
        return (False, str(e))

# Add PageBreak class if not imported
if not REPORTLAB_AVAILABLE:
    class PageBreak:
        pass
else:
    from reportlab.platypus import PageBreak