import numpy as np
import rank_stmt

conversion_dict = {'+': 2, '-': -1}

# Load the file 
with open('../Chart_1/gzoltars/Chart/1/matrix', 'r') as f:
    lines = f.readlines()

# Iterate through each line and convert elements
converted_list = []
for line in lines:
    elements = line.strip().split()
    converted_line = []
    for elem in elements:
        if elem in conversion_dict:
            converted_line.append(conversion_dict[elem])
        else:
            converted_line.append(int(elem))
    converted_list.append(converted_line)

# Convert the list to numpy array
np_arr = np.array(converted_list)
num_columns = np_arr.shape[1]

# Calculate Values 
e_p = np.zeros((1, num_columns))
e_f = np.zeros((1, num_columns))
n_p = np.zeros((1, num_columns))
n_f = np.zeros((1, num_columns))

# Create an empty list to store the selected rows
passed_test = []
failed_test = []

# Iterate through the array and check the last column value
for row in np_arr:
    if row[-1] == 2:
        passed_test.append(row)
    elif row[-1] == -1:
        failed_test.append(row)

# Convert the list to a NumPy array
passed_test = np.array(passed_test)
failed_test = np.array(failed_test)

# Calculate coverage results 
e_p = np.sum(passed_test, axis = 0)[:-1]
e_f = np.sum(failed_test, axis = 0)[:-1]
n_p = passed_test.shape[0] - e_p
n_f = failed_test.shape[0] - e_f

op2_score = e_f - e_p / (e_p + n_p + 1)
ochiai_score = e_p * e_f / np.sqrt((e_p + n_p) * (e_f + n_f))
jaccard_score = e_f / (e_p + e_f + n_f)

# Rank from scores 


rank_stmt_op2 = np.argsort(op2_score)[::-1]
top5_op2_indices = rank_stmt_op2[-5:]
top5_op2_indices = top5_op2_indices + 1
print('='*100)
print('op2 ranking')
rank_stmt.rank(top5_op2_indices)
print('='*100)

# Rank from scores 
rank_stmt_ochiai = np.argsort(ochiai_score)[::-1]
top10_ochiai_indices = rank_stmt_ochiai[-5:]
top10_ochiai_indices = top10_ochiai_indices + 1
print('='*100)
print('ochiai ranking')
rank_stmt.rank(top10_ochiai_indices)
print('='*100)

# Rank from scores 
rank_stmt_jaccard = np.argsort(jaccard_score)[::-1]
rank_stmt_jaccard_indices = rank_stmt_jaccard[-5:]
rank_stmt_jaccard_indices = rank_stmt_jaccard_indices + 1
print('='*100)
print('jaccard ranking')
rank_stmt.rank(rank_stmt_jaccard_indices)
print('='*100)

