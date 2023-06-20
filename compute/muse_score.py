import os
import re
import pandas as pd
from collections import Counter

#1. The number of mutants at each statement
with open('../Chart_1/killmaps/Chart/1/mutants.log','r') as f:
    data = f.read()

lines = data.split('\n')
numbers = []

mut_states = dict()
for line in lines:
    parts = line.split(':')

    if len(parts) > 6:
        number= int(parts[5])
        if number in mut_states:
            mut_states[number] += 1
        else:
            mut_states[number] = 1
    

#2,3 The number of failing tests and passing tests at each statement
file_path = '../Chart_1/gzoltars/Chart/1/matrix'

data = pd.read_csv(file_path, delimiter=' ', header=None)

FP_dict = {}
plus_minus_values = data.iloc[:,-1]

for column in range(data.shape[1] - 1):
    column_values = data.iloc[:, column]
    column_dict = {'+': 0, '-': 0}

    for idx, value in enumerate(column_values):
        if plus_minus_values[idx] == '+':
            column_dict['+'] += value
        elif plus_minus_values[idx] == '-':
            column_dict['-'] += value

    FP_dict[column] = column_dict



#4,5 F->P, P-F statements
    ## Read Stmt Information from mutants.log 
with open('../Chart_1/killmaps/Chart/1/mutants.log', 'r') as f:
    lines = f.readlines()

result = {}
for line in lines:
    # Check if line starts with a digit
    if line[0].isdigit():
        parts = line.split(':')
        # Store the first and fifth part as key and value
        key = int(parts[0])
        value = int(parts[5])
        result[key] = value

sorted_result = dict(sorted(result.items(), key=lambda x: x[0]))

## Read from killmap to collect runtime information
with open('../Chart_1/killmaps/Chart/1/killmap.csv', 'r') as f:
    lines = f.readlines()

with open('output.csv', 'w') as output_file:
    for line in lines:
        parts = line.split(',')
        
        # Store the first, second and fourth part as tc, key, and value
        tc = parts[0]
        mut = int(parts[1])
        value = parts[3].strip()

        # Replace mut with its corresponding value in sorted_result
        if mut in sorted_result:
            mut = sorted_result[mut]
        
        # Write to the output file
        output_file.write(f'{mut},{tc},{value}\n')

# Load the file
with open('output.csv', 'r') as f:
    lines = f.readlines()

# Prepare a set to store the second index of the lines to be removed
original_fail = set()
original_pass = set()

# First pass: identify all the second indices where first index is '0' and third index is 'FAIL'
for line in lines:
    parts = line.split(',')
    if parts[0] == '0' and parts[2].strip() == 'FAIL':
        original_fail.add(parts[1])

    elif parts[0] == '0' and parts[2].strip() == 'PASS':
        original_pass.add(parts[1])

# Second pass: write only those lines to the output whose second index is not in the blacklist
with open('original_pass.csv', 'w') as output_file:
    for line in lines:
        parts = line.split(',')
        if parts[1] not in original_fail:
            output_file.write(line)

with open('original_fail.csv', 'w') as output_file:
    for line in lines:
        parts = line.split(',')
        if parts[1] not in original_pass:
            output_file.write(line)


# Load the originally passed files
with open('original_pass.csv', 'r') as f:
    lines = f.readlines()

# Iterate over the lines
fail_counts = Counter()
for line in lines:
    parts = line.split(',')
    if parts[2].strip() == 'FAIL' or parts[2].strip() == 'CRASH' or parts[2].strip() == 'TIMEOUT':
        fail_counts[int(parts[0])] += 1

# Load the originally failed files
with open('original_fail.csv', 'r') as f:
    lines = f.readlines()

# Iterate over the lines
pass_counts = Counter()
for line in lines:
    parts = line.split(',')
    if parts[2].strip() == 'PASS':
        pass_counts[int(parts[0])] += 1


sorted_fail_counts = dict(sorted(fail_counts.items(), key=lambda item: int(item[0]))) #P -> F
sorted_pass_counts = dict(sorted(pass_counts.items(), key=lambda item: int(item[0]))) #F -> P

muse_score = {}
for stmt in mut_states:
    total_mut = mut_states[stmt]

    if stmt in FP_dict :
        total_F = FP_dict[stmt]['-']
        total_P = FP_dict[stmt]['+']
    else :
        continue

    if stmt in sorted_fail_counts: 
        P_F_switched = sorted_fail_counts[stmt]
    else :
        P_F_switched = 0

    if stmt in sorted_pass_counts: 
        F_P_switched = sorted_pass_counts[stmt]
    else :
        F_P_switched = 0

    if total_F != 0 and total_P != 0:
        susp_score = 1/total_mut * ((F_P_switched/total_F) - 0.5*(P_F_switched/total_P))
    elif total_F == 0 and total_P != 0:
        susp_score = 1/total_mut * ( -0.5*(P_F_switched/total_P))
    elif total_F != 0 and total_P == 0:
        susp_score = 1/total_mut * (F_P_switched/total_F)
    else :
        continue
    
    
    muse_score[stmt] = susp_score

sorted_muse_dict = dict(sorted(muse_score.items(), key=lambda x: x[1]))

print(sorted_muse_dict)