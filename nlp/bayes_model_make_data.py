import csv
import numpy as np

results = []
MAX = 100

with open('../ner/shuffled.txt') as input_file:
    count = 0
    for line in input_file:
        if count >= MAX:
            break
        count += 1
        print(line)
        while True:
            category = input('Standard model (s) or Beyond the standard model (b) ?')
            if category == 's':
                results.append((line, 'SM'))
                break
            if category == 'b':
                results.append((line, 'BSM'))
                break
            else:
                print('Try again')


with open('sm.csv', 'w') as out:
    csv_out = csv.writer(out)
    csv_out.writerow(['text', 'model'])
    for row in results:
        csv_out.writerow(row)
