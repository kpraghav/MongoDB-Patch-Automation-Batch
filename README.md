# MongoDB-Patch-Automation-Batch


python opsmanager_backup.py
python opsmanager_batch_generator.py --batch-size 25
python opsmanager_batch_upgrade.py --file batch_group_files/group_batch_1.csv --version 7.0.16
python opsmanager_batch_rollback.py --file batch_group_files/group_batch_1.csv
