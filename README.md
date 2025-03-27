# MongoDB-Patch-Automation-Batch

# 1️⃣ Install dependencies
- pip install requests pandas
- python opsmanager_backup.py
- python opsmanager_batch_generator.py --batch-size 25
- python opsmanager_batch_upgrade.py --file batch_group_files/group_batch_1.csv --version 7.0.16
- python opsmanager_batch_rollback.py --file batch_group_files/group_batch_1.csv
🛠 1️⃣ opsmanager_backup.py (Backup Script)
✅ Purpose: Takes a backup of all Ops Manager group configurations.
Command below - 
- python opsmanager_backup.py

🛠 2️⃣ opsmanager_batch_generator.py (Batch File Generator)

✅ Purpose: Fetches all group IDs and creates batch files (CSV) based on user-defined batch size
Command below - 
- python opsmanager_batch_generator.py --batch-size 25


🛠 3️⃣ opsmanager_batch_upgrade.py
(Upgrade Patch Execution)
✅ Purpose: Reads batch file and upgrades only the group IDs listed in that file.

Command below - 
- python opsmanager_batch_upgrade.py --file batch_group_files/group_batch_1.csv --version 7.0.16

🛠 opsmanager_batch_rollback.py (Rollback Script)
✅ Purpose: Reads the batch file and rolls back the MongoDB version only for the group IDs in that file.

Command below - 
- python opsmanager_batch_rollback.py --file batch_group_files/group_batch_1.csv --version 7.0.15


