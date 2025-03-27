# MongoDB-Patch-Automation-Batch

# 1️⃣ Install dependencies
pip install requests pandas

# 2️⃣ Run the Ops Manager backup script
python opsmanager_backup.py

# 3️⃣ Generate batch files (e.g., 25 groups per batch)
python opsmanager_batch_generator.py --batch-size 25

# 4️⃣ Upgrade a batch of groups (pick batch file manually)
python opsmanager_batch_upgrade.py --file batch_group_files/group_batch_1.csv --version 5.0.14

# 5️⃣ If needed, rollback the batch
python opsmanager_batch_rollback.py --file batch_group_files/group_batch_1.csv --version 4.4.18

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


#####OVERALL DESIGN APPROACH 

🟢 What’s Good?
✔ Modular Execution – Segregated backup, batch processing, upgrades, and rollback into distinct scripts, making it easier to manage.
✔ Parameterization – The ability to control batch sizes and select specific files for patching gives you full flexibility.
✔ Fail-Safe Design – Rollback is properly integrated, and failures are logged, ensuring minimal risk during upgrades.
✔ CSV-Based Execution Flow – This lets you decide which groups go for patching instead of upgrading everything at once, reducing unexpected failures.
✔ Scalable for Large Deployments – Whether you have 100 or 10,000 group IDs, this setup can handle it efficiently.

🟡 What Can Be Improved?
🔸 Automate Next Batch Execution – Right now, a batch file is picked manually. Can enhance the script to automatically pick the next batch based on success/failure.
🔸 Logging Enhancements – Store logs in a structured file (logs/upgrade_<timestamp>.log) for easier debugging.
🔸 Parallel Execution (Optional) – If the MongoDB Ops Manager API allows it, you could run upgrades in parallel for different group IDs to speed things up.

🔴 Possible Risks?
⚠ Rollback Dependency on API Responses – Ensure that rollback works properly even if the upgrade partially succeeds.
⚠ Long Execution Times – If some groups have slow agents, a batch might take too long to complete. Maybe add a timeout or a way to skip problematic groups.
