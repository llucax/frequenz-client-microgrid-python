import sys
import subprocess

_ = subprocess.check_output(["gh", "pr", "comment", "41", "--body", "Migration failed. Please check the logs for more details."])

print("Migration failed. Please check the logs for more details.")

sys.exit(1)
