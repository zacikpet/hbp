import pandas as pd

df = pd.read_csv('sm.csv')

counter = 0

for _, item in df.iterrows():
    if item['model'] == 'SM':
        with open('sm/paper' + str(counter) + '.txt', 'w') as out_file:
            out_file.write(item['text'])

    elif item['model'] == 'BSM':
        with open('bsm/paper' + str(counter) + '.txt', 'w') as out_file:
            out_file.write(item['text'])

    counter += 1
