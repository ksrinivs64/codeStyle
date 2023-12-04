import pandas
import sys

columns=['file_name','expected_changes', 'missing_changes', 'unexpected_changes', 'gold_changes']
df = pandas.read_csv(sys.argv[1],names=columns, sep=' ')
#print(df)

df = df.drop(['file_name'], axis=1)
mask = df['gold_changes'] == 0
df = df[~mask]
#print(df)

df['expected_lines_changed'] = df['expected_changes'] == df['gold_changes']
df['lines_changed_correctly_and_no_unexpected_changes'] = (df['expected_changes'] == df['gold_changes']) & (df['unexpected_changes'] == 0)
df['percent_expected_lines_changed'] = df['expected_changes'] / df['gold_changes']

print('means')
df_mean = df.mean()
df_st = df.std()

index = df_mean.index
for idx, val in enumerate(df_mean):
    print(index[idx], round(val, 3), '+-', round(df_st.values[idx], 3))

print('total', len(df))

