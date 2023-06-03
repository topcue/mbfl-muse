import sys
import subprocess

##! https://mull.readthedocs.io/en/0.20.0/tutorials/NonStandardTestSuite.html#tests-in-interpreted-languages


cmd = sys.argv[1:]

print("[DEBUG] test_helper: %s" % (" ".join(cmd)))

subprocess.run(cmd, check=True)

# EOF
