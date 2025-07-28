#!/usr/bin/env python3
# Diagnostic script to verify deployment and configurations
import os
import sys
import platform
import subprocess
import socket
import time
import random

# Generate a random identifier for this diagnostic run
run_id = random.randint(10000, 99999)
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

print(f"===== DEPLOYMENT DIAGNOSTIC TOOL v1.0 =====")
print(f"Run ID: {run_id}")
print(f"Timestamp: {timestamp}")

# Create a file with the diagnostic information that will be easy to spot
with open('DIAGNOSTIC.txt', 'w') as f:
    f.write(f"Diagnostic Run: {run_id}\n")
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"Hostname: {platform.node()}\n")
    f.write(f"OS: {platform.system()} {platform.release()}\n")
    f.write(f"Python: {sys.version}\n")

print(f"Diagnostic file created: DIAGNOSTIC.txt with Run ID {run_id}")
print("This file should appear in the root directory of your application.")
print("If you see this file with this specific Run ID on your Pi, it confirms files are syncing correctly.")
print("\nCheck rental.box in your browser after deployment. You should see:")
print(f"Run ID: {run_id}")
print("If you don't see this ID, the deployment is not working correctly.")
