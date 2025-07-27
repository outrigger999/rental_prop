# Raspberry Pi Deployment Diagnosis Checklist

Follow these steps to determine why the project is not running on your Pi and to verify it matches your Mac build.

## 1. SSH into the Pi
```sh
ssh movingdb
```

## 2. Check the Project Directory
Navigate to your project directory (e.g., `~/moving_box_tracker`).

## 3. Check the Current Git Branch and Commit
```sh
cd ~/moving_box_tracker
git status
git log -1
```
- Confirm you are on `stable-build-2025-05-26`.
- Confirm the latest commit hash matches your Mac.

## 4. Pull the Latest Code
```sh
git pull origin stable-build-2025-05-26
```

## 5. Check Python Environment
- Activate your conda environment:
  ```sh
  conda activate movingbox
  ```
- Check Python version:
  ```sh
  python --version
  ```
- Check installed packages:
  ```sh
  pip freeze
  ```

## 6. Check for Service Errors
- View the status and logs for the service:
  ```sh
  sudo systemctl status moving_boxes.service
  sudo journalctl -u moving_boxes.service -n 50 --no-pager
  ```

## 7. Try Running the App Manually
- Stop the service:
  ```sh
  sudo systemctl stop moving_boxes.service
  ```
- Run the app manually:
  ```sh
  python simplified_app.py
  ```
- Observe any errors in the terminal.

## 8. Compare Key Files
- Ensure `requirements.txt`, `nginx.conf`, and `moving_boxes.service` match your Mac.

## 9. Report Findings
- Note any errors, mismatches, or issues and share them for further troubleshooting.

---
If you encounter errors at any step, copy the error message for further analysis.
# How to Log Into the Pi and Start the Service

Follow these steps to log into your Raspberry Pi and attempt to get the service running:

1. **SSH into the Pi**
   ```sh
   ssh movingdb
   ```

2. **Change to the service directory**
   ```sh
   cd moving_box_tracker
   ```

3. **List the files to identify the service or startup script**
   ```sh
   ls -l
   ```

4. **If you see a .service file (e.g., moving_boxes.service), try to start it:**
   ```sh
   sudo systemctl start moving_boxes
   sudo systemctl status moving_boxes
   ```
   *(Replace `moving_boxes` with the actual service name if different.)*

5. **If you see a Python script (e.g., app.py or main.py), try:**
   ```sh
   python3 app.py
   ```
   or
   ```sh
   python3 main.py
   ```

6. **If you encounter errors or the service does not start, copy the error message and let me know so I can help troubleshoot.**

---
*If you need to automate these steps or want a script, let me know!*
# How to Free a Port in Use on the Pi

If you get an error that a port is already in use, follow these steps to identify and kill the process using that port:

1. **Find the process using the port (replace 8000 with your port number):**
   ```sh
   sudo lsof -i :8000
   ```
   - Look for the PID (Process ID) in the output.

2. **Kill the process (replace 1234 with the actual PID):**
   ```sh
   sudo kill 1234
   ```
   - If the process does not terminate, use:
   ```sh
   sudo kill -9 1234
   ```

3. **Try starting your service again.**

---

**Example for port 8000:**
```sh
sudo lsof -i :8000
sudo kill <PID>
```

If you’re not sure which port is in use, check your service’s configuration or error message for the port number.

*If you need to automate this or want a script, let me know!*