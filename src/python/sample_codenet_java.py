import os
import pandas as pd
base_dir = "/data/codenet-java-original"
list_file_name = []
for directory_name in os.listdir(base_dir):
    nested_path = os.path.join(base_dir, directory_name)
    for file_name in os.listdir(nested_path):
        file_path = os.path.join(nested_path, file_name, "Main.java")
        print(file_path)
        list_file_name.append(file_path)
        break

df = pd.DataFrame(list_file_name, columns=['orig'])
df.to_csv("codenet_subset_java.csv")

