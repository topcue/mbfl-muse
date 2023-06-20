## Read Stmt Information from mutants.log 
with open('./killmaps/Chart/1/mutants.log', 'r') as f:
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
with open('./killmaps/Chart/1/killmap.csv', 'r') as f:
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