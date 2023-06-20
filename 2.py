import pandas as pd

file_path = './gzoltars/Chart/1/matrix'

data = pd.read_csv(file_path, delimiter=' ', header=None)

columns_dict = {}
plus_minus_values = data.iloc[:,-1]

for column in range(data.shape[1] - 1):
    column_values = data.iloc[:, column]
    column_dict = {'+': 0, '-': 0}

    for idx, value in enumerate(column_values):
        if plus_minus_values[idx] == '+':
            column_dict['+'] += value
        elif plus_minus_values[idx] == '-':
            column_dict['-'] += value

    columns_dict[column] = column_dict

print(columns_dict)
