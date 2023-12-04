import pandas
import sys
import os

df = pandas.read_csv(sys.argv[1])

for index, row in df.iterrows():
    labels = row['labels']
    outputs = row['preds']
    inputs = row['inputs']

    with open(os.path.join(sys.argv[2], str(index) + '_expected.py'), 'w') as f:
        f.write(labels)

    with open(os.path.join(sys.argv[2], str(index) + '_output.py'), 'w') as f:
        f.write(outputs)

    with open(os.path.join(sys.argv[2], str(index) + '_input.py'), 'w') as f:
        f.write(inputs)

