import sys
import subprocess

##! https://mull.readthedocs.io/en/0.20.0/tutorials/NonStandardTestSuite.html#tests-in-interpreted-languages

test_executable = sys.argv[1]

##! TODO: Generalize me
# test_arguments = " ".join(sys.argv[2:])
arg1 = sys.argv[2]
arg2 = sys.argv[3]

print("[DEBUG] test_helper: %s %s %s" % (test_executable, arg1, arg2))
subprocess.run([test_executable, arg1, arg2], check=True)

# EOF
