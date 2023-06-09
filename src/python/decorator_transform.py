import ast
import pandas as pd
from tqdm import tqdm
import os
import sys
import astunparse
class toFuncLower(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.decorator_list = []
        return node
    def visit_AsyncFunctionDef(self, node):
        node.decorator_list = []
        #print("async decorators stripped")
        return node
    def visit_ClassDef(self, node):
        node.decorator_list = []
        #print("async classes")
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
    processed_scripts = []
    data_input = pd.read_csv(sys.argv[1])
    print("Length of input data : ", len(data_input))
    for data in tqdm(data_input["content"]):
        processed_script = remove_decorator(data)
        processed_scripts.append(processed_script)
    data_input["decorator_modified"] = processed_scripts
    data_input.to_csv("transformed_no_decorators.csv")
