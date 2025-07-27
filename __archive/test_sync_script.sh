#!/bin/bash

# Test script for sync_to_pi.sh
# This script helps verify that the sync_to_pi.sh script works correctly with the --dry-run option

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Check if sync_to_pi.sh exists
if [ ! -f "./sync_to_pi.sh" ]; then
    print_error "sync_to_pi.sh not found in the current directory"
    exit 1
fi

# Make sure sync_to_pi.sh is executable
if [ ! -x "./sync_to_pi.sh" ]; then
    print_warning "sync_to_pi.sh is not executable. Making it executable..."
    chmod +x ./sync_to_pi.sh
fi

# Check if moving_boxes.service.new exists
if [ ! -f "./moving_boxes.service.new" ]; then
    print_warning "moving_boxes.service.new not found. The service file update will not be tested."
else
    print_message "moving_boxes.service.new found. Service file update will be tested."
fi

# Test 1: Run with --dry-run option
print_header "Test 1: Running sync_to_pi.sh with --dry-run option"
print_message "This will show what files would be synced without making any changes"
print_message "Running: ./sync_to_pi.sh --dry-run"
./sync_to_pi.sh --dry-run

# Check the exit code
if [ $? -eq 0 ]; then
    print_message "Test 1 completed successfully"
else
    print_error "Test 1 failed with exit code $?"
    exit 1
fi

# Test 2: Verify SSH connection to Raspberry Pi
print_header "Test 2: Verifying SSH connection to Raspberry Pi"
print_message "Checking if we can connect to the Raspberry Pi..."

# Extract REMOTE_HOST from sync_to_pi.sh
REMOTE_HOST=$(grep "REMOTE_HOST=" sync_to_pi.sh | cut -d'"' -f2)

if [ -z "$REMOTE_HOST" ]; then
    print_error "Could not extract REMOTE_HOST from sync_to_pi.sh"
    exit 1
fi

print_message "Attempting to connect to $REMOTE_HOST..."
ssh -q $REMOTE_HOST exit
if [ $? -eq 0 ]; then
    print_message "SSH connection to $REMOTE_HOST successful"
else
    print_error "SSH connection to $REMOTE_HOST failed"
    print_error "Please check your SSH configuration and make sure the Raspberry Pi is accessible"
    exit 1
fi

# Test 3: Verify conda environment on Raspberry Pi
print_header "Test 3: Verifying conda environment on Raspberry Pi"
print_message "Checking if the conda environment exists on the Raspberry Pi..."

# Extract CONDA_ENV from sync_to_pi.sh
CONDA_ENV=$(grep "CONDA_ENV=" sync_to_pi.sh | cut -d'"' -f2)

if [ -z "$CONDA_ENV" ]; then
    print_error "Could not extract CONDA_ENV from sync_to_pi.sh"
    exit 1
fi

print_message "Checking for conda environment: $CONDA_ENV"
ssh $REMOTE_HOST "/home/smashimo/miniconda3/bin/conda env list | grep $CONDA_ENV" > /dev/null
if [ $? -eq 0 ]; then
    print_message "Conda environment $CONDA_ENV exists on the Raspberry Pi"
else
    print_error "Conda environment $CONDA_ENV not found on the Raspberry Pi"
    print_error "Please create the conda environment before deploying"
    exit 1
fi

# Test 4: Check if the service is already using conda
print_header "Test 4: Checking current service configuration"
print_message "Checking if the service is already using conda..."

ssh $REMOTE_HOST "cat /etc/systemd/system/moving-box-tracker.service | grep conda" > /dev/null
if [ $? -eq 0 ]; then
    print_message "The service is already configured to use conda"
else
    print_message "The service is not yet configured to use conda. It will be updated during deployment."
fi

# Summary
print_header "Test Summary"
print_message "All tests completed successfully"
print_message "The sync_to_pi.sh script appears to be working correctly with the --dry-run option"
print_message "You can now proceed with the actual deployment by running: ./sync_to_pi.sh"