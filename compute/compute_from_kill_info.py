from collections import Counter

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
        fail_counts[parts[0]] += 1

# Load the originally failed files
with open('original_fail.csv', 'r') as f:
    lines = f.readlines()

# Iterate over the lines
pass_counts = Counter()
for line in lines:
    parts = line.split(',')
    if parts[2].strip() == 'PASS':
        pass_counts[parts[0]] += 1


sorted_fail_counts = dict(sorted(fail_counts.items(), key=lambda item: int(item[0])))
sorted_pass_counts = dict(sorted(pass_counts.items(), key=lambda item: int(item[0])))

print(sorted_fail_counts)
print(sorted_pass_counts)

