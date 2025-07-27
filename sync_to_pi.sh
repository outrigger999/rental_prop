#!/bin/bash

# Define variables
RPI_USER="pi" # Assuming default pi user
RPI_HOST="movingdb"
RPI_PROJECT_DIR="/home/${RPI_USER}/rental_prop" # Assuming project lives in user's home directory
GITHUB_REPO="https://github.com/outrigger999/rental_prop.git" # Your GitHub repository URL

echo "--- Pushing changes to GitHub ---"
git add .
git commit -m "Syncing changes to Pi" || echo "No changes to commit or commit failed."
git push origin main

echo "--- Syncing to Raspberry Pi (${RPI_HOST}) ---"
ssh ${RPI_USER}@${RPI_HOST} "
    echo 'Navigating to project directory or creating it...'
    mkdir -p ${RPI_PROJECT_DIR}
    cd ${RPI_PROJECT_DIR}

    if [ -d ".git" ]; then
        echo 'Pulling latest changes from GitHub...'
        git pull origin main
    else
        echo 'Cloning repository from GitHub...'
        git clone ${GITHUB_REPO} .
    fi

    echo 'Installing/updating Python dependencies...'
    # Assuming conda environment is already set up and activated
    # You might need to adjust this based on your conda setup on the Pi
    # For example, if you have a specific conda environment name:
    # source /path/to/your/conda/bin/activate rental_prop_env
    # pip install -r requirements.txt

    echo 'Activating conda environment and installing dependencies...'
    # Assuming conda is initialized for the user on the Pi
    source /home/${RPI_USER}/miniconda3/etc/profile.d/conda.sh # Adjust path if miniconda/anaconda is installed elsewhere
    conda activate rental_prop_env
    pip install -r requirements.txt

    echo 'Restarting Flask application (if running)...'
    # This is a simple way to restart. For production, consider a systemd service.
    # Find the process running app.py and kill it, then restart.
    # You might need to adjust the command to find your Flask app process.
    pkill -f "python app.py" || true # Kill existing process if any
    # Start the Flask app in the background. Use gunicorn for production.
    # For development: nohup python app.py &
    # For production: nohup gunicorn -w 4 app:app -b 0.0.0.0:5000 &
    nohup gunicorn -w 4 app:app -b 0.0.0.0:5000 &

    echo 'Sync complete on Raspberry Pi.'
"

echo "--- Local sync script finished ---"
