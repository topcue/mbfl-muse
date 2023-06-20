with open('mutants.log', 'r') as f:
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
        # print(key, value)

# New dictionary to count occurrences
occurrences = {}
for value in result.values():
    if value in occurrences:
        occurrences[value] += 1
    else:
        occurrences[value] = 1

# Print the dictionary with occurrences
print(occurrences)
