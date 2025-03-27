import requests
import json
import time
import logging
import argparse
import csv
from requests.auth import HTTPDigestAuth

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ops Manager Credentials
USERNAME = "<your-ops-manager-username>"
PASSWORD = "<your-ops-manager-password>"
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}

def read_batch_file(batch_file):
    """ Read group IDs from batch file """
    with open(batch_file, mode='r') as file:
        return [row['groupId'] for row in csv.DictReader(file)]

def get_automation_config(group_id):
    """ Fetch the current automationConfig """
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    response = requests.get(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD))
    response.raise_for_status()
    return response.json()

def upgrade_version(group_id, new_version):
    """ Upgrade MongoDB version for the group """
    logging.info(f"Upgrading Group {group_id} to version {new_version}...")
    
    config = get_automation_config(group_id)

    # Increment the "version" field at the end of the JSON
    config['version'] += 1

    for process in config.get('processes', []):
        process['version'] = new_version  # Update to new MongoDB version

    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    response = requests.put(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD), json=config)
    response.raise_for_status()
    logging.info(f"Upgrade initiated for Group {group_id}.")

def monitor_upgrade(group_id):
    """ Monitor upgrade progress """
    logging.info(f"Monitoring upgrade for Group {group_id}...")
    while True:
        time.sleep(30)
        config = get_automation_config(group_id)
        states = [proc.get('lastKnownVersion') == proc['version'] for proc in config.get('processes', [])]
        if all(states):
            logging.info(f"Upgrade successful for Group {group_id}.")
            return True
        logging.info(f"Upgrade in progress for Group {group_id}...")

def main():
    parser = argparse.ArgumentParser(description="Batch Upgrade Script for MongoDB Ops Manager")
    parser.add_argument('--batch-file', required=True, help="CSV file containing batch of group IDs")
    parser.add_argument('--version', required=True, help="MongoDB version to upgrade to")
    args = parser.parse_args()

    group_ids = read_batch_file(args.batch_file)
    patch_status = []

    for group_id in group_ids:
        try:
            upgrade_version(group_id, args.version)
            if monitor_upgrade(group_id):
                patch_status.append({'groupId': group_id, 'status': 'Success'})
            else:
                raise Exception("Upgrade failed.")
        except Exception as e:
            logging.error(f"Upgrade failed for Group {group_id}: {str(e)}. Rolling back...")
            patch_status.append({'groupId': group_id, 'status': 'Failed'})

    output_file = f"patch_status_{int(time.time())}.csv"
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['groupId', 'status'])
        writer.writeheader()
        writer.writerows(patch_status)

    logging.info(f"Patch status written to {output_file}")

if __name__ == "__main__":
    main()
