import sys
import glob
import pandas

results = []
for filename in glob.iglob(sys.argv[1] + '**/*transform*.py', recursive=True):
    orig = filename.replace('_transformed.py', '')
    results.append({'orig': orig, 'transform': filename})
    
df = pandas.DataFrame(results)
df.to_csv('casing_transform.csv')
