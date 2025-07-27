# Sync and Test Instructions

To apply the recent code changes and verify the fixes, please follow these steps:

1.  **Commit Changes to Git:**
    Ensure all your local changes in `simplified_app.py` and `fix_box_categories.py` are committed to your Git repository.

2.  **Sync to Raspberry Pi:**
    Execute the `sync_to_pi.sh` script from your terminal to transfer the updated `simplified_app.py` and the new `fix_box_categories.py` to your Raspberry Pi.
    ```bash
    ./sync_to_pi.sh
    ```

3.  **Run the Data Fix Script on Raspberry Pi (IMPORTANT!):**
    This script needs to be run directly on your Raspberry Pi to fix the database used by the application. SSH into your Raspberry Pi and execute the `fix_box_categories.py` script. This script will correct any inconsistencies in the category names stored in your box data.
    ```bash
    ssh movingdb "cd ~/moving_box_tracker && python3 fix_box_categories.py"
    ```

4.  **Restart the Application on Raspberry Pi:**
    After running the fix script, you will need to restart the `moving_boxes` service on your Raspberry Pi to load the new code and ensure the database changes are reflected.
    ```bash
    ssh movingdb "sudo systemctl restart moving_boxes.service"
    ```

5.  **Test the Fixes:**
    Once the application has restarted, access the Moving Box Tracker application in your browser and perform the following tests:

    *   **Category Duplication (Case-Insensitive):**
        *   Go to the "Manage Categories" section.
        *   Try to add a new category with a name that already exists, but with different casing (e.g., if "Books" exists, try adding "books" or "BOOKS"). The application should reject the new category and display an appropriate error message.
        *   Try to edit an existing category to a name that already exists (case-insensitively). This should also be rejected.

    *   **"None" Display in Box List View:**
        *   Go to the "List Boxes" view.
        *   Verify that no boxes display "none" for their category. All boxes should show their correct category name, even if the underlying `category_id` was previously broken.
        *   If you have a box that previously showed "none", try editing it and saving it again to see if the category name persists correctly.

Please let me know the results of your testing.