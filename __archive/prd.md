# Moving Box Tracking System - Technical Overview

## Description

This is a project for moving. I want to track boxes and the stuff that's put into them into a database which we can access on the desktop, and on the iphone (mobile). The idea is that we put things in boxes, label and track them and on the other side we're able to look at what's in them and unpack the boxes which have the stuff we're looking for.

The interface needs to have 3 sections, the Add Box, The List View, and Search.

### Add Box

- Add box is the default interface and you should stay on this page unless it's switched to another page manually. The idea is that when entering boxes into the system, someone or multiple people are entering new boxes and when they're done with the current box, they can move the next one quickly.
- The box number should be in sequence and and auto generated, even across multiple people. If someone needs to pause fully loading a box, they should be able to come back to it and put more stuff in it--at anytime.
- The description field needs to be large enough so a lot of things can be tracked in each box. If necessary, a scroll bar should be added to this field to accomodate as many things as someone wants to put in there.
- The drop down for each of the pull downs is detailed below.
	
	### Buttons
	- The buttons are listed below however the functionality should not use php as outlined below.
	- Add Box - This button should add the information entered including all pulldowns, and the details info. You should say at the top of the screen that the data was saved. This information needs to saved to the sqlite db.
	- Update Box - I'm not sure this button is needed. If data was already saved via 'Add Box', then we should change the button to update box which indicates to the user that the box was already saved before and now you are updating the box. Just combine both buttons into one.
	- Delete Last Box - There should be a way to delete a box. Please remove this button from the Add Box screen and only show it on the List View. Right now in List View there is a button which allows you to edit any box, Put a delete Icon (trash can) next to that button and put a fail safe dialog box which asks the user if they really want to delete it. This means that the functionality of the button has changed and it's not just delete last box but it will allow deleting any box and all the list entries should have an icon next to them for delete.
	- If a box is deleted, highlight it in red in the list view but don't actually delete the record just mark it as deleted. Do not reuse a number, when someone is starting another box, give them the next number in sequence.
	- Export Data - This button should export a CSV file. It should not be the second to last button but actually be the last button (if other's are added) and should have a little space separating it from the other buttons.
	- Delete All Boxes - This button is really for me to test the system and I don't really want it available to people in the final version. If there's a way to do that, then figure it out and implement it. However, like the Delete Last Box, we should put a dialog box up every time it's pressed so it's not accidentally pressed.
	- Another thought - Both the delete all boxes and the edit box could be in a pulldown list in the list view with checkboxes next to the box. The default pulldown would say 'Actions...' and would allow you to save some download space for all the icons on the right side which would represent the ability to 'edit' or 'delete' a box. Again, any delete action should have a dialog box which asks the user if they're sure before executing.
## List View

- When in list view, in fact, all views, please highlight or change the color of the top menu to indicated which view someone is in. So if you're in "ad box" or in List View, highlight each of those so that someone knows what view they're in.
- this view is designed so that someone can see a list of boxes that have already been put into the database. This means that it could be a lot of boxes and so the list view needs to have some way of navigating in the case that there are a lot of boxes.
- there needs to be a scroll box or rather a scroll on the right side to accommodate a long list of boxes.
- at the top of the screen, there is a section for actions which I think I discussed earlier we should change to check boxes next to the side of the box on the left side so that we can have a pull down which will allow them to check a box and then either edit the box or delete the box.
## Search
- search needs to have all the box numbers categories priorities size and way to type in a description which will search the description field and then list the boxes which match those descriptions
- the action pull down should also work on this screen once you searched up the right box if you need to delete it or edit it, you should be able to do that here
- 




## System Architecture

- py4web Framework
- Will run on nginx
- Latest Python
- Sqlite DB
- Needs to add boxes over multiple boxes simultaneously
- no php

## Database Schema (SQLite)

### Tables

1. `boxes`
   
    - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    - `box_number` (INTEGER UNIQUE)
    - `priority` (TEXT)
    - `category` (TEXT)
    - `box_size` (TEXT)
    - `description` (TEXT)
    - `created_at` (TEXT)
    - `last_modified` (TEXT)
2. `in_progress` (for concurrent access management)
   
    - `box_number` (INTEGER PRIMARY KEY)
    - `timestamp` (INTEGER)

## Frontend Components

### Form Fields

1. **Box Number**
   
    - Auto-incrementing number
    - Read-only field
    - Starts at 1, automatically increments
2. **Priority** (Dropdown)
   
    - Options:
        - Priority 1
        - Priority 2
        - Important
        - Store
3. **Category** (Dropdown)
   
    - Location-based categories:
        - Cars
        - Cat Related
        - Downstairs Closet
        - Ethan's Bathroom
        - Ethan's Bedroom
        - Ethan's Bedroom Closet
        - Kitchen
        - Laundry Room
        - Living Room
        - Master Bathroom
        - Master Bedroom
        - Master Closet
        - Outside Middle Room
        - Scott's Office
        - Scott's Office Closet
        - Tina's Office
        - Tina's Office Closet
4. **Box Size** (Dropdown)
   
    - Options:
        - Small
        - Medium
        - Large
        - X-Large
        - Wardrobe
5. **Description**
   
    - Multi-line text area
    - Free-form text input
    - Minimum height: 200px

## Key Features

### 1. Navigation

- **Add Box**: Form for adding new boxes
- **List View**: Table display of all boxes
- **Search**: Search functionality for existing boxes

### 2. Box Management

- Auto-incrementing box numbers
- Concurrent access protection
- Edit existing boxes
- Delete last box functionality
- Box reservation system to prevent duplicates

### 3. Data Operations

- **Create**: Add new boxes with auto-numbered IDs
- **Read**: View all boxes in sortable list
- **Update**: Edit existing box information
- **Delete**: Remove boxes (last box or clear all)
- **Search**: Filter boxes by various criteria

### 4. Mobile Features

- Responsive design using Bootstrap
- Mobile-optimized interface
- Touch-friendly inputs
- Scrollable table view

### 5. Data Export

- Download functionality for box data
- CSV format export

## API Endpoints (api.php) (deprecated)

### GET /api.php

- Retrieves all boxes and reserved numbers
- Returns JSON with boxes array and reserved numbers

### POST /api.php (deprecated)

Handles multiple operations:

6. **Reserve Box Number**
   
    json
    
    CopyInsert
    
    `{ "reserve": number }`
    
7. **Add Box**
   
    json
    
    CopyInsert
    
    `{ "boxes": [{ box_data }] }`
    
8. **Update Box**
   
    json
    
    CopyInsert
    
    `{ "updateBox": { box_data } }`
    
9. **Delete Last Box**
   
    json
    
    CopyInsert
    
    `{ "deleteLastBox": true }`
    

### DELETE /api.php (Deprecated)

- Clears all boxes from database

## Implementation Notes

10. **Concurrency Handling**
    
    - Uses SQLite transactions
    - Box number reservation system
    - Lock file mechanism
11. **Error Handling**
    
    - Comprehensive error logging
    - Client-side validation
    - Server-side data verification
12. **Mobile Optimization**
    
    - Responsive table layout
    - Touch-friendly input controls
    - Optimized viewport settings

## Setup Requirements

1. ~~PHP environment with SQLite support~~
2. Write permissions for database file
3. Modern web browser with JavaScript enabled

This system is designed to be easily deployable and modifiable. The code structure allows for easy addition of new categories, priorities, or box sizes by modifying the HTML select options. The database schema is simple but effective for tracking moving boxes, and the concurrent access protection makes it suitable for multiple users accessing the system simultaneously.