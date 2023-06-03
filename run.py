import re
import os
import sys
import json
import subprocess

##! ==================== utils ====================
def get_file_names(dir_path):
    file_names = []
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            file_names.append(path)
    return file_names


##! TODO: Fix me
def set_args_for_max(args: tuple):
    return " ".join(map(str, args))


def pathces_line_number(file_name):
    pattern = r"-L(\d+)-"
    match = re.search(pattern, file_name)
    return match.group(1)

##! ==============================================


class Muse():
    target = ""
    target_path = ""
    target_dir_path = ""

    def __init__(self, target, tc_list):
        self.target = target
        self.target_dir_path = os.path.join("targets", target)
        self.target_path = os.path.join("targets", target, target)
        self.tc_list = tc_list


    def build_put(self):
        target_source_path = os.path.join(self.target_dir_path, self.target)
        cmd = ""
        cmd += "clang-12 -fexperimental-new-pass-manager "
        cmd += "-fpass-plugin=/usr/lib/mull-ir-frontend-12 "
        cmd += "-g -grecord-command-line "
        cmd += "-fprofile-instr-generate -fcoverage-mapping "
        cmd += "%s.c -o %s.exec" % (target_source_path, target_source_path)
        # print("[DEBUG] cmd:", cmd)
        os.system(cmd)


    def generate_patches(self, report_name: str, args: str):
        report_path = os.path.join(self.target_dir_path, "reports", report_name)
        target_bin_path = os.path.join(self.target_dir_path, self.target + ".exec")

        # os.system("cp /home/topcue/mbfl-muse/mull.yml /home/topcue/mbfl-muse/targets/max/")
        ##! generate patches
        cmd = ""
        cmd += "mull-runner-12 --reporters=Patches --reporters=Elements "
        cmd += "--ide-reporter-show-killed " ##! for debugging
        cmd += "--report-name=%s --report-dir=%s %s " % (report_name, report_path, target_bin_path)
        cmd += "-test-program=python3 -- test_helper.py ./%s %s" % (target_bin_path, args)
        # print("[DEBUG] cmd:", cmd)
        os.system(cmd)
        
        ##! clean up
        os.system("rm %s.html" % os.path.join(report_path, report_name))


    def dry_run(self):
        ##! generate reports dir
        reports_path = os.path.join(self.target_dir_path, "reports")
        os.system("rm -rf %s && mkdir -p %s" % (reports_path, reports_path))

        tcs = self.tc_list
        tc_for_dry_run = set_args_for_max(tcs[0])
        report_name = "dry_run"
        self.generate_patches(report_name, tc_for_dry_run)


    def patch_and_build(self):
        target = self.target
        target_path = self.target_path

        ##! generate mutants dir
        mutants_path = os.path.join(self.target_dir_path, "mutants")
        os.system("rm -rf %s && mkdir -p %s" % (mutants_path, mutants_path))

        ##! build mu0 (mu0: original code)
        mu0_path = os.path.join(mutants_path, "mu0")
        os.system("cp %s.c %s.c" % (target_path, mu0_path))
        os.system("cp %s/oracle_%s.c %s" % (self.target_dir_path, target, mutants_path))
        os.system("clang-12 %s.c -o %s.exec" % (mu0_path, mu0_path))

        ##! build mutants
        patches_dir_path = os.path.join(self.target_dir_path, "reports/dry_run/dry_run-patches") 
        file_names = get_file_names(patches_dir_path)
        sorted_file_names = sorted(file_names, key=pathces_line_number)
        for idx, file_name in enumerate(sorted_file_names):
            os.system("cp %s %s/" % (os.path.join(patches_dir_path, file_name), mutants_path))
            line_num = pathces_line_number(file_name)

            ##! patch
            mutant_name = "mu%s-L%s" % (idx+1, line_num)
            cmd_patch = ""
            cmd_patch += "cd %s; " % (mutants_path)
            cmd_patch += "patch < %s mu0.c -o %s.c" % (file_name, mutant_name)
            # print("[DEBUG] cmd:", cmd_patch)
            os.system(cmd_patch)
            os.system("rm %s" % (os.path.join(mutants_path, file_name)))
            
            ##! build mutant
            cmd_compile = ""
            cmd_compile += "cd %s; " % (mutants_path)
            cmd_compile += "clang-12 %s.c -o %s.exec" % (mutant_name, mutant_name)
            os.system(cmd_compile)





##! TODO: Fix me
def test_max():
    ##! 0) set target and target path
    target = "max"
    max_tc_list = [(3, 1), (5, -4), (0,-4), (0,7), (-1,3)]
    muse_max = Muse(target, max_tc_list)
    

    ##! 1) build put w/ mull-lib
    muse_max.build_put()

    ##! 2) generate patches for mutants
    muse_max.dry_run()

    ##! 3) build w/ patches
    muse_max.patch_and_build()


    # tmp(target, args_list)


def main():
    test_max()


if __name__ == "__main__":
    main()

# EOF
