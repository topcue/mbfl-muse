import os
import re
import pandas as pd

with open('./killmaps/Chart/1/mutants.log','r') as f:
    data = f.read()

lines = data.split('\n')
numbers = []

states_dict = dict()
for line in lines:
    parts = line.split(':')

    if len(parts) > 6:
        number= int(parts[5])
        if number in states_dict:
            states_dict[number] += 1
        else:
            states_dict[number] = 1
    

sorted_keys = sorted(states_dict.keys())
for key in sorted_keys:
    print(f"{key}: {states_dict[key]}")
    



# file_path = './gzoltars/Chart/1/matrix'

# data = pd.read_csv(file_path, delimiter=' ', header=None)

# columns_dict = {}
# plus_minus_values = data.iloc[:,-1]

# for column in range(data.shape[1] - 1):
#     column_values = data.iloc[:, column]
#     column_dict = {'+': 0, '-': 0}

#     for idx, value in enumerate(column_values):
#         if plus_minus_values[idx] == '+':
#             column_dict['+'] += value
#         elif plus_minus_values[idx] == '-':
#             column_dict['-'] += value

#     columns_dict[str(column)] = column_dict

# print(columns_dict)