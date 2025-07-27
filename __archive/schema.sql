-- Schema for Moving Box Tracker
-- Simplified single-file version

-- Drop tables if they exist
DROP TABLE IF EXISTS box_history;
DROP TABLE IF EXISTS boxes;

-- Create boxes table
CREATE TABLE boxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    box_number INTEGER UNIQUE,
    priority TEXT,
    box_size TEXT,
    description TEXT,
    created_at TIMESTAMP,
    last_modified TIMESTAMP,
    category_id INTEGER REFERENCES categories(id),
    category TEXT
);

-- Create box_history table for tracking changes
CREATE TABLE box_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    box_id INTEGER,
    action TEXT,
    changes TEXT,
    editor TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (box_id) REFERENCES boxes(id)
);

-- Create index on box_id for faster history lookups
CREATE INDEX idx_box_history_box_id ON box_history(box_id);

-- Create index on category_id for faster lookups
CREATE INDEX idx_boxes_category_id ON boxes(category_id);
