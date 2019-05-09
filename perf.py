import csv
import numpy as np

res = 'results_FINAL.csv'

with open(res, 'r') as r:
    reader = csv.reader(r)
    next(reader)

    s = [float(l[-1]) for l in reader]
    p = np.sum(s) / len(s)

    print(f'Num Tests: {len(s)}')
    print(f'Avg Percentile: {p}')
