import requests
import json
import time
import logging
import argparse
import csv
from requests.auth import HTTPDigestAuth

# Configurations
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
USERNAME = "<your-username>"
PASSWORD = "<your-password>"
AUTH = HTTPDigestAuth(USERNAME, PASSWORD)

# Log Files
SUCCESS_LOG_FILE = "opsmanager_upgrade_success.log"
ERROR_LOG_FILE = "opsmanager_upgrade_errors.log"

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(message, response=None):
    """ Log errors to a separate error log file """
    with open(ERROR_LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {message}\n")
        if response:
            f.write(f"Status Code: {response.status_code}\nResponse: {response.text}\n\n")

def log_success(message):
    """ Log successful operations to a separate success log file """
    with open(SUCCESS_LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - SUCCESS: {message}\n")

def get_upgrade_status(group_id):
    """ Check the upgrade status of the group """
    url = f"{BASE_URL}/groups/{group_id}/automationStatus"
    response = requests.get(url, auth=AUTH)

    if response.status_code == 200:
        return response.json().get("goalVersion", "UNKNOWN")
    else:
        log_error(f"Failed to fetch upgrade status for Group {group_id}", response)
        return None

def monitor_upgrade(group_id):
    """ Monitor upgrade status every 30 seconds until completion """
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        status = get_upgrade_status(group_id)
        if status == "COMPLETED":
            log_success(f"Upgrade completed for Group {group_id}")
            return True
        elif status is None:
            log_error(f"Could not retrieve status for Group {group_id}")
            return False

        logging.info(f"Group {group_id} is still upgrading... (Status: {status})")
        time.sleep(30)
        retry_count += 1

    log_error(f"Upgrade timed out for Group {group_id}")
    return False

def upgrade_group(group_id):
    """ Upgrade the group by incrementing the version """
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    
    # Fetch current automation config
    response = requests.get(url, auth=AUTH)
    if response.status_code != 200:
        log_error(f"Failed to fetch automation config for Group {group_id}", response)
        return False

    config = response.json()
    if 'version' not in config:
        log_error(f"Missing 'version' field in automation config for Group {group_id}")
        return False

    old_version = config['version']
    config['version'] += 1  # Increment the version

    response = requests.put(url, auth=AUTH, json=config)
    if response.status_code == 200:
        log_success(f"Upgrade started for Group {group_id} (Version: {old_version} → {config['version']})")
        return monitor_upgrade(group_id)
    else:
        log_error(f"Upgrade failed for Group {group_id}", response)
        return False

def process_batch(file_name):
    """ Process the batch file and upgrade each group """
    with open(file_name, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_id = row['groupId']
            upgrade_group(group_id)

def main():
    parser = argparse.ArgumentParser(description="Upgrade MongoDB Ops Manager Groups from a batch file")
    parser.add_argument('--batch-file', required=True, help="Batch CSV file containing group IDs")
    args = parser.parse_args()

    process_batch(args.batch_file)

if __name__ == "__main__":
    main()
