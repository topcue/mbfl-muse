import sys
import subprocess

cmd = sys.argv[1:]
subprocess.run(cmd, check=True)

# print("[DEBUG] test_helper: %s" % (" ".join(cmd)))

# EOF
