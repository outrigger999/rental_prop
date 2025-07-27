# Test Sync Script

This script helps verify that the deployment process for the Moving Box Tracker application works correctly with the conda environment on Raspberry Pi.

## Purpose

The `test_sync_script.sh` performs several checks to ensure that the deployment process will work correctly:

1. Verifies that the sync_to_pi.sh script exists and is executable
2. Checks if the updated service file (moving_boxes.service.new) exists
3. Tests the sync_to_pi.sh script with the --dry-run option
4. Verifies SSH connection to the Raspberry Pi
5. Checks if the conda environment exists on the Raspberry Pi
6. Determines if the service is already using conda

## Usage

```bash
./test_sync_script.sh
```

The script will run through all the tests and provide feedback on each step. If any test fails, the script will exit with an error message explaining what went wrong.

## Prerequisites

- SSH access to the Raspberry Pi must be configured
- The Raspberry Pi must be powered on and accessible
- The conda environment must be set up on the Raspberry Pi

## Output

The script provides colored output to make it easy to identify:
- Information messages (green)
- Warning messages (yellow)
- Error messages (red)

## Integration with Deployment Process

This test script should be run before the actual deployment to ensure that everything is set up correctly. It is now included in the deployment checklist as a pre-deployment check.

## Troubleshooting

If the test script fails:

1. Check SSH connectivity to the Raspberry Pi
2. Verify that the conda environment is properly set up
3. Ensure that the sync_to_pi.sh script is properly configured
4. Check that the moving_boxes.service.new file exists if you want to update the service file