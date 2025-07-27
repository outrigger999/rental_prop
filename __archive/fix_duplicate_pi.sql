-- Find duplicate categories
SELECT name, COUNT(*) as count, GROUP_CONCAT(id) as ids
FROM categories 
GROUP BY name 
HAVING count > 1;

-- For each duplicate found, keep the first one (lowest ID) and update boxes
-- Example for "Scott's Office" (you'll need to update IDs based on results):
-- UPDATE boxes SET category_id = 1 WHERE category_id = 123;
-- DELETE FROM categories WHERE id = 123;

-- After running the query above, use these commands with the correct IDs:
-- This keeps ID 1 and removes other duplicates with their specific IDs
