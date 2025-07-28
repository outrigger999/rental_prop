#!/bin/bash

# Direct Fix for Nginx 403 Forbidden on Static Files
# This script focuses exclusively on fixing nginx config and static files permissions

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== EMERGENCY FIX FOR 403 FORBIDDEN ERRORS =====${NC}"
echo "This script will aggressively fix nginx static file permissions"

# Configuration
PI_HOST="movingdb"
PI_USER="smashimo"
APP_DIR="/home/smashimo/rental_prop"

# Create a very explicit and aggressive nginx config
cat > emergency_nginx.conf << 'EOF'
server {
    listen 80;
    server_name rental.box;
    
    # Add very permissive headers for troubleshooting
    add_header X-Debug-Message "Rental Property App";
    
    # Main application
    location / {
        proxy_pass http://localhost:6000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Static files with extremely permissive settings
    location /static/ {
        # Absolute path with trailing slash is critical
        alias /home/smashimo/rental_prop/static/;
        
        # Very permissive settings for troubleshooting
        autoindex on;
        allow all;
        
        # Disable all caching during troubleshooting
        expires off;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
    }
}
EOF

# Create a script to run directly on the Pi
cat > emergency_fix_commands.sh << 'EOL'
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

APP_DIR="/home/smashimo/rental_prop"
STATIC_DIR="$APP_DIR/static"

echo -e "${YELLOW}[EMERGENCY FIX]${NC} Applying aggressive fixes to resolve 403 Forbidden errors"

# 1. Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}[CRITICAL]${NC} nginx not found! Installing..."
    sudo apt-get update && sudo apt-get install -y nginx
fi

# 2. Check nginx user
NGINX_USER=$(ps aux | grep "nginx: master" | grep -v grep | awk '{print $1}')
echo -e "${YELLOW}[INFO]${NC} nginx is running as user: $NGINX_USER"

# 3. Force very permissive permissions
echo -e "${YELLOW}[AGGRESSIVE FIX]${NC} Setting global read permissions on all files"
sudo chmod -R a+r "$APP_DIR"  # Make all files readable by everyone
sudo find "$APP_DIR" -type d -exec chmod a+x {} \;  # Make all directories executable by everyone

# 4. Create test static file with debug information
echo -e "${YELLOW}[DEBUG]${NC} Creating test static files"
mkdir -p "$STATIC_DIR/css"
mkdir -p "$STATIC_DIR/test"

# Create a test CSS file
cat > "$STATIC_DIR/css/test.css" << 'EOF'
/* Test CSS file */
body {
    background-color: yellow;
    color: black;
    padding: 20px;
}
h1 {
    color: red;
}
EOF

# Create a test HTML file
cat > "$STATIC_DIR/test/debug.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Static File Debug Test</title>
    <link rel="stylesheet" href="/static/css/test.css">
</head>
<body>
    <h1>Static File Debug Test</h1>
    <p>If you can see this page with a yellow background and red heading, static files are working!</p>
    <p>Time: <script>document.write(new Date().toString())</script></p>
</body>
</html>
EOF

# 5. Set ownership explicitly
echo -e "${YELLOW}[AGGRESSIVE FIX]${NC} Setting ownership to www-data"
sudo chown -R www-data:www-data "$STATIC_DIR"

# 6. Install emergency nginx config
echo -e "${YELLOW}[EMERGENCY CONFIG]${NC} Installing emergency nginx configuration"
sudo cp emergency_nginx.conf /etc/nginx/sites-available/rental
sudo chmod 644 /etc/nginx/sites-available/rental
sudo ln -sf /etc/nginx/sites-available/rental /etc/nginx/sites-enabled/

# 7. Remove default nginx site if it exists (to avoid conflicts)
echo -e "${YELLOW}[CONFIG FIX]${NC} Removing default nginx site if it exists"
sudo rm -f /etc/nginx/sites-enabled/default

# 8. Check nginx config and restart
echo -e "${YELLOW}[VERIFY]${NC} Testing and restarting nginx"
sudo nginx -t
if [ $? -eq 0 ]; then
    sudo systemctl restart nginx
    echo -e "${GREEN}[SUCCESS]${NC} nginx restarted successfully"
else
    echo -e "${RED}[CRITICAL FAILURE]${NC} nginx config test failed"
    exit 1
fi

# 9. Display nginx error log
echo -e "${YELLOW}[DEBUG]${NC} Recent nginx error log entries:"
sudo tail -n 20 /var/log/nginx/error.log

# 10. Print debug information
echo -e "${GREEN}[DEBUG INFO]${NC} Static directory structure and permissions:"
ls -la "$STATIC_DIR"
ls -la "$STATIC_DIR/css"

echo -e "${GREEN}[TEST URLS]${NC} Please check these URLs in your browser:"
echo "http://rental.box/ - Main application"
echo "http://rental.box/static/test/debug.html - Debug test page"
echo "http://rental.box/static/css/test.css - Test CSS file"
EOL

# Make the remote script executable
chmod +x emergency_fix_commands.sh

echo -e "${YELLOW}[INFO]${NC} Copying emergency fix script and nginx config to Pi..."
scp emergency_nginx.conf emergency_fix_commands.sh $PI_USER@$PI_HOST:/home/$PI_USER/rental_prop/

echo -e "${YELLOW}[INFO]${NC} Executing emergency fix on Pi..."
ssh $PI_USER@$PI_HOST "cd /home/$PI_USER/rental_prop && chmod +x emergency_fix_commands.sh && ./emergency_fix_commands.sh"

# Clean up temporary files
rm emergency_nginx.conf emergency_fix_commands.sh

echo -e "${GREEN}[COMPLETE]${NC} Emergency fix applied!"
echo -e "${YELLOW}[IMPORTANT]${NC} After running this script, test these URLs:"
echo "1. http://rental.box/ - Main application"
echo "2. http://rental.box/static/test/debug.html - Debug test page"
echo "3. http://rental.box/static/css/test.css - Test CSS file"
echo
echo -e "${YELLOW}[NOTE]${NC} You may need to clear your browser cache or use incognito mode"
