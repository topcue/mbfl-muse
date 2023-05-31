import re
import os
import sys
import json
import subprocess

def get_file_names(dir_path):
  file_names = []
  for path in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, path)):
      file_names.append(path)
  return sorted(file_names)


def build_put(target):
    cmd = ""
    cmd += "clang-12 -fexperimental-new-pass-manager "
    cmd += "-fpass-plugin=/usr/lib/mull-ir-frontend-12 "
    cmd += "-g -grecord-command-line "
    cmd += "-fprofile-instr-generate -fcoverage-mapping "
    cmd += "%s.c -o %s" % (target, target)
    print("[DEBUG] cmd:", cmd)
    os.system(cmd)


##! TODO: Fix this dump way in single run
def generate_mutants_old(target: str, report_name: str, args: str):
    ##! generate patches
    cmd = ""
    cmd += "mull-runner-12 --reporters=Patches --report-dir=reports "
    cmd += "--report-name=%s %s " % (report_name, target)
    cmd += "-test-program=python3 -- test_helper.py ./%s %s" % (target, args)
    print("[DEBUG] cmd:", cmd)
    os.system(cmd)

    ##! create json file
    cmd = ""
    cmd += "mull-runner-12 --reporters=Elements --report-dir=reports "
    cmd += "--report-name=%s %s " % (report_name, target)
    cmd += "-test-program=python3 -- test_helper.py ./%s %s" % (target, args)
    print("[DEBUG] cmd:", cmd)
    os.system(cmd)
    os.system("rm reports/%s.html" % (report_name))


def generate_patches(target: str, report_name: str, args: str):
    ##! generate patches
    cmd = ""
    cmd += "mull-runner-12 --reporters=Patches --reporters=Elements "
    cmd += "--ide-reporter-show-killed " ##! for debugging
    cmd += "--report-dir=reports --report-name=%s %s " % (report_name, target)
    cmd += "-test-program=python3 -- test_helper.py ./%s %s" % (target, args)
    print("[DEBUG] cmd:", cmd)
    os.system(cmd)
    os.system("rm reports/%s.html" % (report_name))


##! TODO: Fix me
def set_args_for_max(args: tuple):
    return " ".join(map(str, args))


# ##! read json to judge P/F
# def foo(report_name):
#     file_path = "reports/%s.json" % report_name

#     with open(file_path, "r") as file:
#         data = json.load(file)

#     files = data["files"]
#     for file_path, file_data in files.items():
#         mutants = file_data["mutants"]
#         for mutant in mutants:
#             line_number = mutant["location"]["start"]["line"]
#             status = mutant["status"]
#             print(f"line: {line_number}, Status: {status}")



def pathces_line_number(file_name):
    pattern = r"-L(\d+)-"
    match = re.search(pattern, file_name)
    return match.group(1)


def patch_and_build(target, report_name):
    ##! for test
    os.system("rm -rf ./mutants && mkdir -p mutants")

    ##! mu0 means original code
    os.system("cp %s.c mutants/mu0.c" % (target))
    os.system("cp oracle_%s.c mutants/" % (target))
    ##! build mu0
    os.system("clang-12 mutants/mu0.c -o mutants/mu0")

    patches_path = "reports/%s-patches" % (report_name)
    file_names = get_file_names(patches_path)
    sorted_file_names = sorted(file_names, key=pathces_line_number)
    for idx, file_name in enumerate(sorted_file_names):
        os.system("cp %s mutants/" % (os.path.join(patches_path, file_name)))
        
        line_num = pathces_line_number(file_name)

        ##! patch
        mutant_name = "mu%s-L%s" % (idx+1, line_num)
        cmd_patch = "cd mutants; patch < %s mu0.c -o %s.c" % (file_name, mutant_name)
        # print("[DEBUG] cmd:", cmd_patch)
        os.system(cmd_patch)
        
        ##! TODO: Fix me
        ##! manually patch (resolve mull bug)
        os.system("cp mu1-L6.c mutants/mu1-L6.c")
        os.system("rm mutants/%s" % (file_name))

        ##! build mutant
        os.system("cd mutants; clang-12 %s.c -o %s" % (mutant_name, mutant_name))


def tmp(target, args_list):
    tmp_mutatns = get_file_names("mutants")
    mutants = [ x for x in tmp_mutatns if not x.endswith(".c") ]
    mutants.remove("mu0")
    
    for idx_args, args in enumerate(args_list):
        ##! test mu0
        binary_path = "./mutants/mu0"
        args_ = [str(args[0]), str(args[1])]
        result = subprocess.run([binary_path] + args_, capture_output=True)
        mu0_res = "P" if result.returncode == 0 else "F"
        print("[*] TC:", args)

        for idx_mu, mutant in enumerate(mutants):
            binary_path = "./mutants/%s" % (mutant)
            args_ = [str(args[0]), str(args[1])]
            result = subprocess.run([binary_path] + args_, capture_output=True)
            ret = "P" if result.returncode == 0 else "F"
            print("  %s: " % (mutant), end="")
            if ret != mu0_res:
                print("%s->%s" % (mu0_res, ret))
            else:
                print()
            # print("[+] (TC, result) = (%s, %s))" % (args, ret))
    

    
        


##! TODO: Fix me
def test_max():
    target = "max"
    args_list = [(3, 1), (5, -4), (0,-4), (0,7), (-1,3)]

    ##! build put w/ mull-lib
    build_put(target)

    ##! generate patches for mutants
    dry_run_args = set_args_for_max(args_list[0])
    report_name = "TC0"
    generate_patches(target, report_name, dry_run_args)

    ##! build w/ patches
    patch_and_build(target, report_name)
    tmp(target, args_list)
    

    # foo(report_name)
    # for idx, args in enumerate(args_list):
    #     ##! TODO: Rename args and args_
    #     args_ = set_args_for_max(args)
    #     report_name = "TC" + str(idx + 1)

    #     ##! run w/ mull-runner to generate mutants (patches and json file)
    #     generate_mutants(target, report_name, args_)
    
    # for idx in range(len(args_list)):
    #     report_name = "TC" + str(idx + 1)
    #     foo(report_name)
    #     ##! DEBUG: remove me
    #     return



def main():
    test_max()


if __name__ == "__main__":
    main()

# EOF
