#!/bin/bash

# Direct 403 Debug Script
# This will show us exactly what's happening on the Pi

echo "===== DIRECT 403 DEBUG SCRIPT ====="

# Configuration
PI_HOST="movingdb"
PI_USER="smashimo"

# Create debug commands to run on Pi
cat > debug_commands.sh << 'EOL'
#!/bin/bash

echo "===== DEBUGGING 403 FORBIDDEN ERRORS ====="
echo "Current time: $(date)"
echo

echo "1. CHECKING NGINX STATUS:"
sudo systemctl status nginx --no-pager
echo

echo "2. CHECKING NGINX ERROR LOG (last 20 lines):"
sudo tail -n 20 /var/log/nginx/error.log
echo

echo "3. CHECKING NGINX ACCESS LOG (last 10 lines):"
sudo tail -n 10 /var/log/nginx/access.log
echo

echo "4. CHECKING NGINX CONFIGURATION:"
echo "--- /etc/nginx/sites-enabled/rental ---"
sudo cat /etc/nginx/sites-enabled/rental
echo

echo "5. CHECKING NGINX USER:"
ps aux | grep nginx | head -5
echo

echo "6. CHECKING FILE PERMISSIONS:"
echo "Home directory permissions:"
ls -ld /home/smashimo
echo
echo "Project directory permissions:"
ls -ld /home/smashimo/rental_prop
echo
echo "Static directory permissions:"
ls -ld /home/smashimo/rental_prop/static
echo
echo "CSS directory permissions:"
ls -ld /home/smashimo/rental_prop/static/css
echo
echo "CSS file permissions:"
ls -la /home/smashimo/rental_prop/static/css/style.css
echo

echo "7. TESTING FILE ACCESS AS NGINX USER:"
echo "Testing if www-data can read the CSS file:"
sudo -u www-data cat /home/smashimo/rental_prop/static/css/style.css > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "SUCCESS: www-data can read the CSS file"
else
    echo "FAILED: www-data CANNOT read the CSS file"
fi
echo

echo "8. CHECKING DIRECTORY TRAVERSAL:"
echo "Testing if www-data can traverse to the file:"
sudo -u www-data ls /home/smashimo/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "SUCCESS: www-data can access /home/smashimo/"
else
    echo "FAILED: www-data CANNOT access /home/smashimo/"
fi

sudo -u www-data ls /home/smashimo/rental_prop/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "SUCCESS: www-data can access /home/smashimo/rental_prop/"
else
    echo "FAILED: www-data CANNOT access /home/smashimo/rental_prop/"
fi

sudo -u www-data ls /home/smashimo/rental_prop/static/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "SUCCESS: www-data can access /home/smashimo/rental_prop/static/"
else
    echo "FAILED: www-data CANNOT access /home/smashimo/rental_prop/static/"
fi
echo

echo "9. CHECKING SELINUX/APPARMOR:"
if command -v getenforce > /dev/null 2>&1; then
    echo "SELinux status: $(getenforce)"
else
    echo "SELinux not found"
fi

if command -v aa-status > /dev/null 2>&1; then
    echo "AppArmor status:"
    sudo aa-status | grep nginx
else
    echo "AppArmor not found"
fi
echo

echo "10. MANUAL NGINX TEST:"
echo "Testing nginx configuration:"
sudo nginx -t
echo

echo "11. CHECKING PORTS:"
echo "Services listening on port 80:"
sudo netstat -tuln | grep :80
echo
echo "Services listening on port 6000:"
sudo netstat -tuln | grep :6000
echo

echo "===== DEBUG COMPLETE ====="
EOL

echo "Copying debug script to Pi..."
scp debug_commands.sh $PI_USER@$PI_HOST:/home/$PI_USER/rental_prop/

echo "Running debug script on Pi..."
ssh $PI_USER@$PI_HOST "cd /home/$PI_USER/rental_prop && chmod +x debug_commands.sh && ./debug_commands.sh"

# Clean up
rm debug_commands.sh

echo "Debug complete. Check the output above for clues about the 403 error."
