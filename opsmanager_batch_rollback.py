import requests
import logging
import argparse
import csv
import time

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
API_KEY = "<your-api-key>"
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

ROLLBACK_STATUS_FILE = 'rollback_status.csv'

def get_automation_config(group_id):
    """Fetch the automation configuration for a given group ID."""
    response = requests.get(f"{BASE_URL}/groups/{group_id}/automationConfig", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def rollback_version(group_id):
    """Rollback MongoDB version for a given group ID by restoring lastKnownVersion."""
    logging.info(f"Fetching automation config for rollback of Group {group_id}")
    config = get_automation_config(group_id)

    updated = False
    for process in config.get('processes', []):
        if 'lastKnownVersion' in process:
            process['version'] = process['lastKnownVersion']  # Rollback to previous version
            updated = True
        else:
            logging.warning(f"No lastKnownVersion found for process in Group {group_id}, skipping rollback.")

    if updated:
        response = requests.put(
            f"{BASE_URL}/groups/{group_id}/automationConfig",
            headers=HEADERS,
            json=config
        )
        response.raise_for_status()
        logging.info(f"Rollback executed successfully for Group {group_id}")
        return {'groupId': group_id, 'status': 'Rollback Successful'}
    else:
        logging.warning(f"Rollback skipped for Group {group_id} (no lastKnownVersion found)")
        return {'groupId': group_id, 'status': 'No lastKnownVersion - Skipped'}

def main():
    parser = argparse.ArgumentParser(description="MongoDB Ops Manager Batch Rollback Script")
    parser.add_argument('--file', required=True, help="CSV file containing group IDs to rollback")
    args = parser.parse_args()

    rollback_status = []

    try:
        with open(args.file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header if exists
            for row in reader:
                group_id = row[0].strip()
                result = rollback_version(group_id)
                rollback_status.append(result)

    except Exception as e:
        logging.critical(f"Unexpected error: {str(e)}")

    # Write rollback status to CSV
    with open(ROLLBACK_STATUS_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['groupId', 'status'])
        writer.writeheader()
        writer.writerows(rollback_status)

    logging.info("Rollback status written to rollback_status.csv")

if __name__ == "__main__":
    main()
