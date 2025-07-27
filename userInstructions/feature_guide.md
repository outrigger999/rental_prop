# Rental Property Tracker Feature Guide

This guide explains the core features of the Rental Property Tracker application and how to use them.

## Core Features

### 1. Create New Rental Properties

The application allows you to add new rental properties with the following information:

- **Property Type**: Home, Apartment, or Townhome
- **Address**: Full address of the property
- **Price**: Monthly rental price
- **Square Footage**: Size of the property in square feet
- **Number of Bedrooms**: Number of bedrooms in the property
- **Cat Friendly**: Whether the property allows cats
- **Air Conditioning**: Whether the property has air conditioning
- **Parking Type**: Available parking options (Off Street or On Street)
- **Commute Times**: Morning, midday, and evening commute times from the property to your office

To add a new property:
1. Click "Add New Property" on the main page
2. Fill in the property details
3. Click "Add Property" to save

### 2. List Rentals

The main page displays all your saved rental properties in an easy-to-read card format. Each card shows:

- Property address
- Property type
- Price
- Square footage
- Number of bedrooms
- Cat friendly status
- Air conditioning status
- Parking type
- Commute times

### 3. Search Rentals

The search functionality allows you to filter properties based on various criteria:

- **Price Range**: Set minimum and maximum price
- **Minimum Bedrooms**: Filter by number of bedrooms
- **Property Type**: Filter by home, apartment, or townhome
- **Cat Friendly**: Show only cat-friendly properties
- **Air Conditioning**: Show only properties with air conditioning

To search properties:
1. Use the search form at the top of the main page
2. Enter your search criteria
3. Click "Search" to filter the results
4. Click "Clear Filters" to reset and show all properties

### 4. Export and Backup

You can export your rental property data in two formats:

- **CSV Format**: Compatible with spreadsheet software like Excel or Google Sheets
- **JSON Format**: Useful for data interchange or programmatic access

To export your data:
1. Click "Export Data" on the main page
2. Choose your preferred format (CSV or JSON)
3. The file will download automatically with a timestamp in the filename

## Tips for Effective Use

- **Regular Backups**: Export your data regularly to prevent data loss
- **Detailed Addresses**: Include complete addresses for better organization
- **Commute Times**: Use consistent formats for commute times (e.g., "25 mins" or "1.5 hours")
- **Search Combinations**: Combine multiple search criteria for more specific results

## Technical Notes

- The application stores data in a SQLite database
- Exports include timestamps to track when backups were created
- All data is stored locally on your Raspberry Pi
