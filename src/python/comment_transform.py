import ast
import astunparse
import pandas as pd
from tqdm import tqdm

def uncomment(source):
    """ 
    Takes input code and returns code with comments stripped
    Input: code (str)
    Output: code (str)
    """
    try:
        parse = astunparse.unparse(ast.parse(source))
    except:
        parse = 'nan'
    return parse

if __name__ == "__main__":

    data_input = pd.read_csv("codenet_subset.csv")
    print("Length of input data : ", len(data_input))
    data_output = []
    for file_name in tqdm(data_input["orig"]):
        with open(file_name) as f:
            data = f.read()
        processed_script = uncomment(data)
        with open(file_name[:-3]+"_comment_transform.py", "w") as f:
            if processed_script is None or processed_script == 'nan':
                f.write(data)
            else:
                print("file changed")
                f.write("# File changed\n")
                f.write(processed_script)
        data_output.append({"orig":file_name, "transform":file_name[:-3]+"_comment_transform.py"})
    out_df = pd.DataFrame.from_records(data_output, columns = ['orig', 'transform'])
    out_df.to_csv("comment_codenet_subset.csv")
