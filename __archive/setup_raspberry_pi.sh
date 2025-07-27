#!/bin/bash

# Update system
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3-pip python3-venv nginx

# Create project directory
mkdir -p /home/pi/moving-box-tracker
cd /home/pi/moving-box-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run initial database migrations
alembic upgrade head

# Setup systemd service
sudo cp moving-box-tracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable moving-box-tracker
sudo systemctl start moving-box-tracker

# Setup Nginx as reverse proxy
sudo tee /etc/nginx/sites-available/moving-box-tracker << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the Nginx site
sudo ln -sf /etc/nginx/sites-available/moving-box-tracker /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "Installation complete!"
echo "You can access the application at http://[raspberry-pi-ip]"
