import os
import sys

def build_put(target):
    cmd = ""
    cmd += "clang-12 -fexperimental-new-pass-manager "
    cmd += "-fpass-plugin=/usr/lib/mull-ir-frontend-12 "
    cmd += "-g -grecord-command-line "
    cmd += "-fprofile-instr-generate -fcoverage-mapping "
    cmd += "%s.c -o %s" % (target, target)
    print("[DEBUG] cmd:", cmd)
    os.system(cmd)


def generate_mutants(target: str, report_name: str, args: str):
    cmd = ""
    cmd += "mull-runner-12 --reporters=Patches --report-dir=reports "
    cmd += "--report-name=%s %s " % (report_name, target)
    cmd += "-test-program=python3 -- test_helper.py ./%s %s" % (target, args)
    print("[DEBUG] cmd:", cmd)
    os.system(cmd)


##! TODO: Fix me
def set_args_for_max(args: tuple):
    return " ".join(map(str, args))


##! TODO: Fix me
def test_max():
    target = "max"

    ##! build put w/ mull-lib
    build_put(target)

    args_list = [(3, 1), (5, -4), (0,-4), (0,7), (-1,3)]
    for idx, args in enumerate(args_list):
        ##! TODO: Rename args
        args_ = set_args_for_max(args)
        report_name = "TC" + str(idx + 1)

        ##! run w/ mull-runner to generate mutants
        generate_mutants(target, report_name, args_)


def main():
    test_max()


if __name__ == "__main__":
    main()

# EOF
