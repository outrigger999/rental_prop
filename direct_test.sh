#!/bin/bash

# Direct Connection Test Script for Rental Property App
# This will connect directly to the Pi and create diagnostic files to verify connectivity

echo "===== DIRECT CONNECTION TEST ====="
echo "This script will connect directly to the Pi and check deployment status"
echo

# Configuration
PI_HOST="movingdb"
PI_USER="smashimo"
PI_DIR="/home/smashimo/rental_prop"

# Generate unique identifier for this test
TEST_ID=$(date +%s)
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")

echo "Test ID: $TEST_ID"
echo "Timestamp: $CURRENT_TIME"
echo

# Create test file locally
echo "Creating local test file..."
cat > test_file_$TEST_ID.txt << EOF
DIRECT CONNECTION TEST
Test ID: $TEST_ID
Created: $CURRENT_TIME
This file was created by direct_test.sh
EOF

echo "Attempting direct SCP transfer to Pi..."
scp test_file_$TEST_ID.txt $PI_USER@$PI_HOST:$PI_DIR/

echo
echo "Checking if file exists on Pi..."
ssh $PI_USER@$PI_HOST "if [ -f $PI_DIR/test_file_$TEST_ID.txt ]; then echo 'TEST FILE FOUND ON PI!'; cat $PI_DIR/test_file_$TEST_ID.txt; else echo 'TEST FILE NOT FOUND ON PI'; fi"

echo
echo "Checking service status..."
ssh $PI_USER@$PI_HOST "sudo systemctl status rental_prop || echo 'Could not get service status'"

echo
echo "Checking if port 6000 is in use..."
ssh $PI_USER@$PI_HOST "sudo netstat -tuln | grep ':6000' || echo 'Port 6000 not in use'"

echo
echo "Checking nginx configuration..."
ssh $PI_USER@$PI_HOST "if [ -f /etc/nginx/sites-enabled/rental ]; then echo 'NGINX CONFIG FOUND'; sudo nginx -t; else echo 'NGINX CONFIG NOT FOUND'; fi"

echo
echo "Creating direct test marker in deployment_timestamp.txt..."
ssh $PI_USER@$PI_HOST "echo 'DIRECT TEST $TEST_ID - $CURRENT_TIME' > $PI_DIR/deployment_timestamp.txt"

echo
echo "Test complete - check rental.box in your browser"
echo "You should see: DIRECT TEST $TEST_ID"
echo "If you don't see this message, there is a problem with the web service"
