import os
import pandas as pd
base_dir = "/data/codenet_python3_accepted/"
list_file_name = []
for directory_name in os.listdir(base_dir):
    nested_path = os.path.join(base_dir, directory_name, "Python")
    for file_name in os.listdir(nested_path):
        if "transformed" in file_name:
            continue
        elif ".py" in file_name:#ignore .so and directories
            print(file_name)
            list_file_name.append(os.path.join(nested_path, file_name))
            break

df = pd.DataFrame(list_file_name, columns=['orig'])
df.to_csv("codenet_subset.csv")

