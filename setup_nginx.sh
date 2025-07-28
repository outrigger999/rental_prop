#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== NGINX CONFIGURATION SETUP =====${NC}"
echo "This script will set up the nginx configuration for rental.box"

# Configuration
PI_HOST="movingdb"
PI_USER="smashimo"
NGINX_CONF_FILE="nginx.conf"
LOCAL_PATH="./$NGINX_CONF_FILE"

# Check if nginx.conf exists locally
if [ ! -f "$LOCAL_PATH" ]; then
    echo -e "${RED}Error: $NGINX_CONF_FILE not found in the current directory${NC}"
    exit 1
fi

echo "Found local nginx.conf file"

# Create a temporary file with commands to run on the Pi
cat > nginx_setup_commands.sh << 'EOL'
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up nginx on the Pi...${NC}"

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}nginx not found! Please install nginx first:${NC}"
    echo "sudo apt-get update && sudo apt-get install -y nginx"
    exit 1
fi

# Ensure nginx directory exists
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# Copy the configuration file to sites-available
echo "Copying configuration to /etc/nginx/sites-available/rental"
sudo cp nginx.conf /etc/nginx/sites-available/rental

# Create a symlink to sites-enabled
echo "Creating symlink in sites-enabled"
sudo ln -sf /etc/nginx/sites-available/rental /etc/nginx/sites-enabled/

# Test nginx configuration
echo "Testing nginx configuration"
sudo nginx -t

# Reload nginx
echo "Reloading nginx"
sudo systemctl reload nginx

# Check nginx status
echo -e "${GREEN}Checking nginx status:${NC}"
sudo systemctl status nginx
EOL

# Make the remote script executable
chmod +x nginx_setup_commands.sh

echo "Copying nginx.conf and setup script to the Pi..."
scp "$LOCAL_PATH" nginx_setup_commands.sh $PI_USER@$PI_HOST:/home/$PI_USER/rental_prop/

echo "Executing nginx setup on the Pi..."
ssh $PI_USER@$PI_HOST "cd /home/$PI_USER/rental_prop && chmod +x nginx_setup_commands.sh && ./nginx_setup_commands.sh"

# Clean up the temporary file
rm nginx_setup_commands.sh

echo -e "${GREEN}Done! Now check rental.box in your browser${NC}"
