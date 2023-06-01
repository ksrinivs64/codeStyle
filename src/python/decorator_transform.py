import ast
import pandas as pd
from tqdm import tqdm

import astunparse
class toFuncLower(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.decorator_list = []
        return node
        # return ast.FunctionDef(**{**node.__dict__, 'name':node.name.lower().replace("_","")})


def remove_decorator(input_code):
    try:
        parsed = ast.parse(input_code)
        parsed_code = astunparse.unparse(parsed)
        final_code = astunparse.unparse(toFuncLower().visit(parsed))
        if parsed_code == final_code:
            return None
    except SyntaxError:
        return None
    except RecursionError:
        return None
    except TypeError:
        return None
    except ValueError:
        return None

    return final_code


if __name__ == "__main__":
    df = pd.read_csv("/home/ksrinivs/codeStyle/src/python/casing_transform.csv")
    records_dict = []
    for i, row in df.iterrows():
        try:
            with open(row['orig']) as f:
                code = f.read()
                transformed_code = remove_decorator(code)
                f_out = open(row['orig'][:-3]+"_transformed_decorators.py", "w")
                if transformed_code is not None:
                    f_out.write("# File changed\n")
                    f_out.write(transformed_code)
                else:
                    f_out.write(code)
                print(row['orig'])
                records_dict.append({'orig':row['orig'],
                        'transform':row['orig'][:-3]+"_transformed_decorators.py"})
            #if i==1000:
            #    break
        except FileNotFoundError:
            print("file not found", row['orig'])
            continue
    df_out = pd.DataFrame.from_records(records_dict)
    df_out.to_csv("out_decorators.csv")
