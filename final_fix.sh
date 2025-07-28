#!/bin/bash

# FINAL FIX - Direct solution based on debug findings
echo "===== FINAL FIX FOR 403 FORBIDDEN ERRORS ====="

PI_HOST="movingdb"
PI_USER="smashimo"

# Create the final fix commands
cat > final_fix_commands.sh << 'EOL'
#!/bin/bash

echo "===== APPLYING FINAL FIX ====="
echo "Root cause: Directory permissions are 700 instead of 755"
echo "www-data cannot traverse directories to reach static files"
echo

# 1. Fix directory permissions - THIS IS THE CRITICAL FIX
echo "1. FIXING DIRECTORY PERMISSIONS (the root cause):"
sudo chmod 755 /home/smashimo/rental_prop
sudo chmod 755 /home/smashimo/rental_prop/static
sudo chmod 755 /home/smashimo/rental_prop/static/css
sudo chmod 755 /home/smashimo/rental_prop/static/js 2>/dev/null || true
sudo chmod 755 /home/smashimo/rental_prop/templates 2>/dev/null || true

echo "Directory permissions fixed."
echo

# 2. Ensure file permissions are correct
echo "2. FIXING FILE PERMISSIONS:"
sudo find /home/smashimo/rental_prop/static -type f -exec chmod 644 {} \;
sudo find /home/smashimo/rental_prop/templates -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "File permissions fixed."
echo

# 3. Set correct ownership
echo "3. FIXING OWNERSHIP:"
sudo chown -R smashimo:www-data /home/smashimo/rental_prop/static/
sudo chown -R smashimo:www-data /home/smashimo/rental_prop/templates/ 2>/dev/null || true

echo "Ownership fixed."
echo

# 4. Install nginx configuration properly
echo "4. INSTALLING NGINX CONFIGURATION:"
if [ -f "/home/smashimo/rental_prop/nginx.conf" ]; then
    sudo cp /home/smashimo/rental_prop/nginx.conf /etc/nginx/sites-available/rental
    sudo chmod 644 /etc/nginx/sites-available/rental
    sudo ln -sf /etc/nginx/sites-available/rental /etc/nginx/sites-enabled/
    echo "Nginx configuration installed."
else
    echo "Creating basic nginx configuration..."
    sudo tee /etc/nginx/sites-available/rental << 'EOF'
server {
    listen 80;
    server_name rental.box;
    
    location / {
        proxy_pass http://localhost:6000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /home/smashimo/rental_prop/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
}
EOF
    sudo ln -sf /etc/nginx/sites-available/rental /etc/nginx/sites-enabled/
    echo "Basic nginx configuration created and installed."
fi
echo

# 5. Test and reload nginx
echo "5. TESTING AND RELOADING NGINX:"
sudo nginx -t
if [ $? -eq 0 ]; then
    sudo systemctl reload nginx
    echo "Nginx reloaded successfully."
else
    echo "Nginx configuration test failed!"
    exit 1
fi
echo

# 6. Verify the fix
echo "6. VERIFYING THE FIX:"
echo "Testing if www-data can now access the CSS file:"
sudo -u www-data cat /home/smashimo/rental_prop/static/css/style.css > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "SUCCESS: www-data can now read the CSS file!"
else
    echo "FAILED: www-data still cannot read the CSS file"
fi

echo "Testing directory traversal:"
sudo -u www-data ls /home/smashimo/rental_prop/static/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "SUCCESS: www-data can now access the static directory!"
else
    echo "FAILED: www-data still cannot access the static directory"
fi
echo

echo "7. FINAL PERMISSIONS CHECK:"
echo "Project directory: $(ls -ld /home/smashimo/rental_prop | awk '{print $1}')"
echo "Static directory: $(ls -ld /home/smashimo/rental_prop/static | awk '{print $1}')"
echo "CSS directory: $(ls -ld /home/smashimo/rental_prop/static/css | awk '{print $1}')"
echo "CSS file: $(ls -l /home/smashimo/rental_prop/static/css/style.css | awk '{print $1}')"
echo

echo "===== FINAL FIX COMPLETE ====="
echo "Check rental.box in your browser now!"
EOL

echo "Copying final fix script to Pi..."
scp final_fix_commands.sh $PI_USER@$PI_HOST:/home/$PI_USER/rental_prop/

echo "Running final fix on Pi..."
ssh $PI_USER@$PI_HOST "cd /home/$PI_USER/rental_prop && chmod +x final_fix_commands.sh && ./final_fix_commands.sh"

# Clean up
rm final_fix_commands.sh

echo "===== FINAL FIX APPLIED ====="
echo "The root cause was directory permissions set to 700 instead of 755."
echo "www-data could not traverse the directories to reach the static files."
echo "This should now be fixed. Check rental.box in your browser!"
