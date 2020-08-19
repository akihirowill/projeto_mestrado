#!/usr/bin/python3
import os
import pickle

path = '/home/william/ida_logs'

results = {}

for filename in os.listdir(path):
    if not filename.endswith('.log'):
        continue
    basename = os.path.basename(filename)
    binname = basename[:-4]
    filename = os.path.join(path, filename)
    count_arr = []
    with open(filename) as f:
        state = 0
        curr_count = None
        for line in f:
            if state == 0:
                if line.startswith('==>'):
                    state = 1
                    curr_count = 0
            elif state == 1:
                if line.strip() == '':
                    state = 0
                    count_arr.append(curr_count)
                else:
                    curr_count += 1
    max_count = max(count_arr)
    print(binname, max_count)
    results[binname] = max_count

with open('num_funcs_per_bin.pickle', 'wb') as f:
    pickle.dump(results, f)
