import requests
import logging
import argparse
import csv
import time
from requests.auth import HTTPDigestAuth

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ops Manager API Credentials (Use environment variables in production)
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
USERNAME = "<your-username>"
PASSWORD = "<your-password>"

AUTH = HTTPDigestAuth(USERNAME, PASSWORD)
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

UPGRADE_STATUS_FILE = 'upgrade_status.csv'

def get_automation_config(group_id):
    """Fetch the automation configuration for a given group ID."""
    response = requests.get(f"{BASE_URL}/groups/{group_id}/automationConfig", auth=AUTH, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def upgrade_version(group_id, version):
    """Upgrade MongoDB version for a given group ID."""
    logging.info(f"Fetching automation config for upgrade of Group {group_id}")
    config = get_automation_config(group_id)

    updated = False
    for process in config.get('processes', []):
        if process.get('version') != version:
            process['version'] = version  # Set new MongoDB version
            updated = True

    if updated:
        response = requests.put(
            f"{BASE_URL}/groups/{group_id}/automationConfig",
            auth=AUTH,
            headers=HEADERS,
            json=config
        )
        response.raise_for_status()
        logging.info(f"Upgrade initiated successfully for Group {group_id}")
        return {'groupId': group_id, 'status': 'Upgrade Initiated'}
    else:
        logging.warning(f"Group {group_id} is already on version {version}")
        return {'groupId': group_id, 'status': 'Already Upgraded'}

def monitor_upgrade(group_id, version):
    """Monitor upgrade process and confirm completion."""
    logging.info(f"Monitoring upgrade progress for Group {group_id}")
    timeout = 1800  # 30 minutes timeout
    start_time = time.time()

    while time.time() - start_time < timeout:
        time.sleep(30)
        config = get_automation_config(group_id)

        if all(process.get('version') == version for process in config.get('processes', [])):
            logging.info(f"Upgrade completed successfully for Group {group_id}")
            return {'groupId': group_id, 'status': 'Upgrade Successful'}
        logging.info("Upgrade still in progress...")

    logging.error(f"Upgrade timed out for Group {group_id}")
    return {'groupId': group_id, 'status': 'Upgrade Timeout'}

def main():
    parser = argparse.ArgumentParser(description="MongoDB Ops Manager Batch Upgrade Script")
    parser.add_argument('--file', required=True, help="CSV file containing group IDs to upgrade")
    parser.add_argument('--version', required=True, help="MongoDB patch version to upgrade to")
    args = parser.parse_args()

    upgrade_status = []

    try:
        with open(args.file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header if exists
            for row in reader:
                group_id = row[0].strip()
                result = upgrade_version(group_id, args.version)
                
                if result['status'] == 'Upgrade Initiated':
                    monitoring_result = monitor_upgrade(group_id, args.version)
                    upgrade_status.append(monitoring_result)
                else:
                    upgrade_status.append(result)

    except Exception as e:
        logging.critical(f"Unexpected error: {str(e)}")

    # Write upgrade status to CSV
    output_file = f'upgrade_status_{int(time.time())}.csv'
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['groupId', 'status'])
        writer.writeheader()
        writer.writerows(upgrade_status)

    logging.info(f"Upgrade status written to {output_file}")

if __name__ == "__main__":
    main()
