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

def set_args_for_isPrime(args: int):
    return str(args)

def set_args_for_isEven(args: int):
    return str(args)

def set_args_for_getQuotient(args: tuple):
    return " ".join(map(str, args))

def set_args_for_stack(args: tuple):
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
        elif self.target == "isPrime":
            tc_for_dry_run = set_args_for_isPrime(tcs[0])
        elif self.target == "isEven":
            tc_for_dry_run = set_args_for_isEven(tcs[0])
        elif self.target == "getQuotient":
            tc_for_dry_run = set_args_for_getQuotient(tcs[0])
        elif self.target == "stack":
            tc_for_dry_run = set_args_for_stack(tcs[0])

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
        subprocess.run(compile_command, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        # Run the program
        run_command = ""
        run_command += f"cd {mutants_dir_path}; "
        run_command += f"./{mutant_name}_for_gcov.exec {test_case}"
        subprocess.run(run_command, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        # get cov
        gcov_command = ""
        gcov_command += f"cd {mutants_dir_path}; "
        gcov_command += f"gcov {mutant_name}.c"
        subprocess.run(gcov_command, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
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


    def generate_table(self, test_cases):
        # declare dictionary of using two keys: TC and line number
        table = {}
        coverage_table = {}
        fail_to_pass = {}
        pass_to_fail = {}
        line_corpus = []

        mutants_dir_path = os.path.join(self.target_dir_path, "mutants")
        tmp_mutatns = get_file_names(mutants_dir_path)
        mutants = [ x for x in tmp_mutatns if x.endswith(".exec") ]
        mutants.remove("mu0.exec")

        ##! get line corpus
        line_corpus = []
        for mut in mutants:
            mut = mut.replace(".exec", "")
            line_corpus.append(int(mut.split("-")[1][1:]))
        line_corpus = list(set(line_corpus))
        line_corpus = sorted(line_corpus, key=lambda x: int(x))
        print("line_corpus is: ", line_corpus)
    
        for test_case in test_cases:
            ##! test mu0
            binary_path = os.path.join(mutants_dir_path, "mu0.exec")
            args_ = [str(arg) for arg in test_case]

            result = subprocess.run([binary_path] + args_, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            mu0_res = "P" if result.returncode == 0 else "F"
            print("[*] TC:", test_case)

            executed_lines = self.get_covered_lines("mu0", " ".join(args_))
            coverage_table[(test_case, "mu0")] = mu0_res
            for line in line_corpus:
                if line in executed_lines:
                    coverage_table[(test_case, line)] = "1"
                else:
                    coverage_table[(test_case, line)] = "0"
        
            ##! test mutants
            for mutant in mutants:
                binary_path = os.path.join(mutants_dir_path, mutant)
                args_ = [str(test_case[0]), str(test_case[1])]
                # result = subprocess.run([binary_path] + args_, capture_output=True)
                result = subprocess.run([binary_path] + args_, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

                ret = "P" if result.returncode == 0 else "F"
                # print("  %s: " % (mutant), end="")

                linenum = mutant.split("-")[1][1:].replace(".exec", "")
                mut = mutant.split("-")[0]

                pass_to_fail[(linenum, mut)] = 0
                fail_to_pass[(linenum, mut)] = 0
                
                if ret != mu0_res:
                    # print("%s->%s" % (mu0_res, ret))
                    # save printed value to dictionary
                    table[(test_case, mut, linenum)] = "%s->%s" % (mu0_res, ret)
                else:
                    # print()
                    table[(test_case, mut, linenum)] = "      "
        
        self.table = table
        self.coverage_table = coverage_table
        self.fail_to_pass = fail_to_pass
        self.pass_to_fail = pass_to_fail
        self.line_corpus = line_corpus


    def print_table(self):
        table = self.table
        coverage_table = self.coverage_table
        fail_to_pass = self.fail_to_pass
        pass_to_fail = self.pass_to_fail
        line_corpus = self.line_corpus

        fail_cover = {}
        pass_cover = {}

        print("\n\n[*] table:")
        for key, value in table.items():
            print("  %s: %s" % (key, value))
        print("-" * 80)
        #print the dictionary as a table of line numbers by number of test cases
        
        #get every possible linenum from dictionary
        linenum = []
        for key in table.keys():
            linenum.append(key[2])
        linenum = list(set(linenum))
        linenum = sorted(linenum, key=lambda x: int(x))


        # make list of test cases
        tc = []
        for key in table.keys():
            tc.append(key[0])
        
        for t in tc:
            count = tc.count(t)
            if count > 1:
                for i in range(count-1):
                    tc.remove(t)

        for l in line_corpus:
            pass_cov = 0
            fail_cov = 0
            for t in tc:
                if coverage_table[(t, l)] == "1":
                    if coverage_table[(t, "mu0")] == "P":
                        pass_cov += 1
                    else:
                        fail_cov += 1
            pass_cover[l] = pass_cov
            fail_cover[l] = fail_cov
                    
        print("  ", end="\t")
        print("  ", end="\t")
        for t in tc:
            print("(%d, %d)" % (t[0], t[1]), end="\t")
        print()

        for l in linenum:
            mutants = []

            for key, value in table.items():
                if key[2] == l:
                    mutants.append(key[1])
            mutants = list(set(mutants))
            mutants = sorted(mutants)
            
            count = 0
            for mut in mutants:
                if count == 0:
                    print("  %s: " % (l), end="\t")
                else:
                    print("  %s: " % (" "), end="\t")
                print("%s " % (mut), end="\t")
                
                for key, value in table.items():
                    if key[2] == l and key[1] == mut:
                        print("%s " % (value), end="\t")
                        if value == "P->F":
                            pass_to_fail[(key[2], key[1])] += 1
                        elif value == "F->P":
                            fail_to_pass[(key[2], key[1])] += 1
                print()
                count += 1

            print()
        print("-" * 80)

        num_mut_P = len(table.keys()) // len(tc)
        num_p2f = sum(pass_to_fail.values())
        num_f2p = sum(fail_to_pass.values())
        fP = sum(fail_cover.values())
        pP = sum(pass_cover.values())
        alpha = (num_f2p / (num_mut_P * fP)) * ((num_mut_P * pP) / num_p2f)

        suspiciousness = {}
        for l in linenum:
            #get number of mutants
            mutants = []
            for key, value in table.items():
                if key[2] == l:
                    mutants.append(key[1])
            mutants = list(set(mutants))
            mutants = sorted(mutants)
            num_mutants = len(mutants)
            int_l = int(l)

            suspiciousness[int_l] = 0
            for mut in mutants:
                suspiciousness[int_l] += (fail_to_pass[(l, mut)]/fail_cover[int(l)] - alpha *  pass_to_fail[(l, mut)] / pass_cover[int(l)])
            suspiciousness[int_l] /= num_mutants
        #print pass_to_fail and fail_to_pass as a table
        for l in linenum:
            mutants = []

            for key, value in table.items():
                if key[2] == l:
                    mutants.append(key[1])
            mutants = list(set(mutants))
            mutants = sorted(mutants)

            for mut in mutants:
                print("  %s: " % (l), end="\t")
                print("%s " % (mut), end="\t")
                print("P->F: %d, F->P: %d" % (pass_to_fail[(l, mut)], fail_to_pass[(l, mut)]))
            print()

        print("-" * 80)

        print("  ", end="\t")
        for t in tc:
            print("(%d, %d)" % (t[0], t[1]), end="\t")
        print()

        for l in line_corpus:
            print("  %s: " % (l), end="\t")
            for t in tc:
                print("%s " % (coverage_table[(t, l)]), end="\t")
            print("f_P(s): %s, p_P(s): %s, suspiciousness: %s" % (fail_cover[l], pass_cover[l], suspiciousness[l]))
            print()
        
        print("  ", end="\t")
        for t in tc:
            print("%s" % (coverage_table[(t, "mu0")]), end="\t")

        print()
        print("-" * 80)


def test(target, test_cases):
    muse = Muse(target, test_cases)

    ##! 1) build put w/ mull-lib
    muse.build_put()

    ##! 2) generate patches for mutants
    muse.dry_run()

    ##! 3) build w/ patches
    muse.patch_and_build()

    ##! 4) get P/F table
    muse.generate_table(test_cases)

    ##! 5) show table
    muse.print_table()


##! TODO: Fix me
def test_max():
    target = "max"
    test_cases = [(3, 1), (5, -4), (0,-4), (0,7), (-1,3)]
    test(target, test_cases)


def test_quicksort():
    target = "quicksort"
    ##! TODO: Fix me
    test_cases = [(3, 1, 2, 3), (5, 4), (5, 4, 2, 1, 0, 6, 3), (2, 2)]
    test(target, test_cases)

def test_isPrime():
    target = "isPrime"
    test_cases = [2, 3, 8, 15, 17]
    test(target, test_cases)

def test_isEven():
    target = "isEven"
    test_cases = [1, 2, 3, 4, 5]
    test(target, test_cases)

def test_getQuotient():
    target = "getQuotient"
    test_cases = [(14, 7), (2, 0), (0, 41), (12, 11), (12, 4)]
    test(target, test_cases)

def test_stack():
    target = "stack"
    test_cases = [(2, 1), (10, 20), (20, 20), (42, 0), (0, 0)]
    test(target, test_cases)


def main():
    #test_max()
    # test_quicksort()
    #test_isPrime() # not tested
    # test_isEven() # not tested
    # test_getQuotient() # ok
    test_stack() # ok

if __name__ == "__main__":
    main()

# EOF
