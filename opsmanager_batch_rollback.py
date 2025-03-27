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

SUCCESS_LOG_FILE = "opsmanager_success.log"
ERROR_LOG_FILE = "opsmanager_errors.log"

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

def rollback_group(group_id):
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    
    response = requests.get(url, auth=AUTH)
    if response.status_code != 200:
        log_error(f"Failed to fetch automation config for Group {group_id}", response)
        return False

    config = response.json()
    
    # Decrement the version
    config['version'] -= 1

    response = requests.put(url, auth=AUTH, json=config)
    if response.status_code == 200:
        success_msg = f"Rollback successful for Group {group_id}"
        logging.info(success_msg)
        log_success(success_msg)
        return True
    else:
        log_error(f"Rollback failed for Group {group_id}", response)
        return False

def process_batch(file_name):
    with open(file_name, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_id = row['groupId']
            rollback_group(group_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rollback MongoDB Ops Manager Groups from a batch file")
    parser.add_argument('--batch-file', required=True, help="Batch CSV file containing group IDs")
    args = parser.parse_args()

    process_batch(args.batch_file)
