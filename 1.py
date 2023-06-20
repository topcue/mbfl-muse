import os
import re

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
    