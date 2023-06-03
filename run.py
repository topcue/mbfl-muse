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
    return sorted(file_names)


##! TODO: Fix me
def set_args_for_max(args: tuple):
    return " ".join(map(str, args))

def set_args_for_quicksort(args: tuple):
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
        ##! TODO: Fix me
        if self.target == "max":
            tc_for_dry_run = set_args_for_max(tcs[0])
        elif self.target == "quicksort":
            tc_for_dry_run = set_args_for_quicksort(tcs[0])
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


    ##! binary_path = "targets/max/mutants/mu0.exec"
    def get_covered_lines(self, mutant, test_case):
        mutants_dir_path = os.path.join(self.target_dir_path, "mutants")
        mutant_name = os.path.splitext(mutant)[0]

        # Compile the C program with gcov options
        compile_command = ""
        compile_command += f"cd {mutants_dir_path}; "
        compile_command += f"gcc -fprofile-arcs -ftest-coverage {mutant_name}.c -o {mutant_name}_for_gcov.exec"
        subprocess.run(compile_command, shell=True)
        
        # Run the program
        run_command = ""
        run_command += f"cd {mutants_dir_path}; "
        run_command += f"./{mutant_name}_for_gcov.exec {test_case}"
        subprocess.run(run_command, shell=True)

        # get cov
        gcov_command = ""
        gcov_command += f"cd {mutants_dir_path}; "
        gcov_command += f"gcov {mutant_name}.c"
        subprocess.run(gcov_command, shell=True)
        
        # create a list of all the lines that were executed
        executed_lines = []
        gcov_file_path = f"{mutants_dir_path}/{mutant_name}.c.gcov"
        with open(gcov_file_path, 'r') as f:
            for line in f:
                if line.startswith('    ######'):
                    continue
                line = line.strip()
                line_number = line.split(':')[0]
                if line_number != '-' and line_number[-1] != '#':
                    executed_lines.append(int(line.split(':')[1]))

        # delete created files
        # wait for subprocess job to finish
        ##! TODO
        # subprocess.run("rm %s %s.gcda %s.gcno" % (binary_file, new_file_path[:-2], new_file_path[:-2]), shell=True)

        return executed_lines


    def get_pf_table(self, test_cases):
        mutants_dir_path = os.path.join(self.target_dir_path, "mutants")
        tmp_mutatns = get_file_names(mutants_dir_path)
        mutants = [ x for x in tmp_mutatns if x.endswith(".exec") ]
        mutants.remove("mu0.exec")

        for tc_idx, test_case in enumerate(test_cases):
            ##! test mu0
            binary_path = os.path.join(mutants_dir_path, "mu0.exec")
            args_ = [str(test_case[0]), str(test_case[1])]
            result = subprocess.run([binary_path] + args_, capture_output=True)
            mu0_res = "P" if result.returncode == 0 else "F"
            print("[*] TC:", test_case)

            ##! test mutants
            for idx_mu, mutant in enumerate(mutants):
                executed_lines = self.get_covered_lines(mutant, "3 1") ##! TODO: fix me
                continue
                binary_path = os.path.join(mutants_dir_path, mutant)
                args_ = [str(test_case[0]), str(test_case[1])]
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
    ##! 0) set target and target path
    target = "max"
    test_cases = [(3, 1), (5, -4), (0,-4), (0,7), (-1,3)]
    muse_max = Muse(target, test_cases)
    

    ##! 1) build put w/ mull-lib
    muse_max.build_put()

    ##! 2) generate patches for mutants
    muse_max.dry_run()

    ##! 3) build w/ patches
    muse_max.patch_and_build()

    ##! 4) get P/F table
    muse_max.get_pf_table(test_cases)


def test_quicksort():
    ##! 0) set target and target path
    target = "quicksort"

    ##! TODO: Fix me
    test_cases = [(3, 1), (5, 4)]
    muse_max = Muse(target, test_cases)
    
    ##! 1) build put w/ mull-lib
    muse_max.build_put()

    ##! 2) generate patches for mutants
    muse_max.dry_run()

    ##! 3) build w/ patches
    muse_max.patch_and_build()

    ##! 4) get P/F table
    muse_max.get_pf_table(test_cases)

def main():
    test_max()
    # test_quicksort()

if __name__ == "__main__":
    main()

# EOF
