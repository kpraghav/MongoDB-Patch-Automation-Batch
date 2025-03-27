import requests
import csv
import os
import argparse
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ops Manager API details
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
API_KEY = "<your-api-key>"
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

# Directory for batch files
BATCH_DIR = "batch_group_files"
os.makedirs(BATCH_DIR, exist_ok=True)

def get_group_ids():
    response = requests.get(f"{BASE_URL}/groups", headers=HEADERS)
    response.raise_for_status()
    return [group['id'] for group in response.json()['results']]

def create_batches(batch_size):
    group_ids = get_group_ids()
    total_batches = (len(group_ids) // batch_size) + (1 if len(group_ids) % batch_size else 0)

    for i in range(total_batches):
        batch_file = os.path.join(BATCH_DIR, f"group_batch_{i+1}.csv")
        with open(batch_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["groupId"])
            for group_id in group_ids[i * batch_size:(i + 1) * batch_size]:
                writer.writerow([group_id])

        logging.info(f"Created batch file: {batch_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate batch files for group IDs.")
    parser.add_argument("--batch-size", type=int, required=True, help="Number of group IDs per batch file.")
    args = parser.parse_args()

    create_batches(args.batch_size)
