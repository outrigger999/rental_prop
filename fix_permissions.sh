#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== FIXING NGINX AND STATIC FILE PERMISSIONS =====${NC}"
echo "This script will fix permissions for static files and update the nginx configuration"

# Configuration
PI_HOST="movingdb"
PI_USER="smashimo"
APP_DIR="/home/smashimo/rental_prop"

# Create a temporary file with commands to run on the Pi
cat > fix_permissions_commands.sh << 'EOL'
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_DIR="/home/smashimo/rental_prop"
STATIC_DIR="$APP_DIR/static"

echo -e "${GREEN}Fixing permissions for static files...${NC}"

# Make sure the static directory exists
if [ ! -d "$STATIC_DIR" ]; then
    echo -e "${RED}Static directory not found!${NC}"
    echo "Creating static directory"
    mkdir -p "$STATIC_DIR"
fi

# Fix permissions for the entire app directory
echo "Setting app directory permissions..."
sudo chown -R smashimo:smashimo "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"

# Make static files world-readable
echo "Setting static file permissions..."
sudo find "$STATIC_DIR" -type d -exec chmod 755 {} \;
sudo find "$STATIC_DIR" -type f -exec chmod 644 {} \;

echo "Checking nginx configuration..."
# Backup the current nginx configuration
sudo cp /etc/nginx/sites-available/rental /etc/nginx/sites-available/rental.bak 2>/dev/null

# Create a proper nginx config that explicitly allows access to static files
cat > temp_nginx.conf << 'EOF'
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
        autoindex off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        
        # Explicitly allow access
        allow all;
    }
}
EOF

echo "Installing updated nginx configuration..."
sudo cp temp_nginx.conf /etc/nginx/sites-available/rental

# Test and reload nginx
echo "Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "Reloading nginx..."
    sudo systemctl reload nginx
    echo -e "${GREEN}All permissions and configurations fixed!${NC}"
else
    echo -e "${RED}Nginx configuration test failed. Restoring backup...${NC}"
    sudo cp /etc/nginx/sites-available/rental.bak /etc/nginx/sites-available/rental
    sudo systemctl reload nginx
fi

# Clean up
rm temp_nginx.conf

echo "Creating a test file in static directory..."
echo "<html><body><h1>Static file test</h1><p>If you can see this, static files are working.</p></body></html>" > "$STATIC_DIR/test.html"

echo -e "${GREEN}Done! Now check these URLs in your browser:${NC}"
echo "http://rental.box/ - Main app"
echo "http://rental.box/static/test.html - Static file test"
EOL

# Make the remote script executable
chmod +x fix_permissions_commands.sh

echo "Copying fix permissions script to the Pi..."
scp fix_permissions_commands.sh $PI_USER@$PI_HOST:/home/$PI_USER/rental_prop/

echo "Executing fix permissions script on the Pi..."
ssh $PI_USER@$PI_HOST "cd /home/$PI_USER/rental_prop && chmod +x fix_permissions_commands.sh && ./fix_permissions_commands.sh"

# Clean up the temporary file
rm fix_permissions_commands.sh

echo -e "${GREEN}Done! Now check rental.box in your browser${NC}"
echo "If you still see 403 errors, try clearing your browser cache or open in incognito mode"
