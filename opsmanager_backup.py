import requests
import json
import logging
import os
from datetime import datetime

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ops Manager API details
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
API_KEY = "<your-api-key>"
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

# Backup folder setup
BACKUP_DIR = "backup_data"
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_group_configs():
    response = requests.get(f"{BASE_URL}/groups", headers=HEADERS)
    response.raise_for_status()
    
    groups = response.json()['results']
    for group in groups:
        group_id = group['id']
        logging.info(f"Backing up configuration for Group {group_id}")
        
        config_response = requests.get(f"{BASE_URL}/groups/{group_id}/automationConfig", headers=HEADERS)
        config_response.raise_for_status()
        
        backup_file = os.path.join(BACKUP_DIR, f"group_{group_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(backup_file, "w") as file:
            json.dump(config_response.json(), file, indent=4)
    
    logging.info("Backup completed successfully.")

if __name__ == "__main__":
    backup_group_configs()
