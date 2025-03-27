import requests
import json
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

def rollback_version(group_id):
    """ Rollback MongoDB version for the group """
    logging.info(f"Rolling back Group {group_id}...")

    config = get_automation_config(group_id)

    # Increment the "version" field before applying rollback
    config['version'] += 1

    for process in config.get('processes', []):
        process['version'] = process.get('lastKnownVersion', process['version'])

    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    response = requests.put(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD), json=config)
    response.raise_for_status()
    logging.info(f"Rollback completed for Group {group_id}.")

def main():
    parser = argparse.ArgumentParser(description="Batch Rollback Script for MongoDB Ops Manager")
    parser.add_argument('--batch-file', required=True, help="CSV file containing batch of group IDs")
    args = parser.parse_args()

    group_ids = read_batch_file(args.batch_file)
    rollback_status = []

    for group_id in group_ids:
        try:
            rollback_version(group_id)
            rollback_status.append({'groupId': group_id, 'status': 'Rollback Success'})
        except Exception as e:
            logging.error(f"Rollback failed for Group {group_id}: {str(e)}")
            rollback_status.append({'groupId': group_id, 'status': 'Rollback Failed'})

    output_file = f"rollback_status_{int(time.time())}.csv"
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['groupId', 'status'])
        writer.writeheader()
        writer.writerows(rollback_status)

    logging.info(f"Rollback status written to {output_file}")

if __name__ == "__main__":
    main()
