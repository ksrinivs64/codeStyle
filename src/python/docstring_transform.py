import ast
import pandas as pd
from tqdm import tqdm
import astunparse
import sys
test = "import ast\n class MyClass: \n\t\"\"\"A simple example class\"\"\" \n\ti = 12345 # le epic comment\n\tVAR = 1 \n\tWhoa = [i + 1 for i in range(0,10)]\n\n\tdef f(self):\n\t\treturn 'hello world'"

#import astor
def undocstring(source):
    try:
        parsed = ast.parse(source)
        has_docstring = False
        
        for node in ast.walk(parsed):
                    
            if not isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                continue

            if not len(node.body):
                continue

            if not isinstance(node.body[0], ast.Expr):
                continue

            if not hasattr(node.body[0], 'value') or not isinstance(node.body[0].value, ast.Str):
                continue
            has_docstring = True
            node.body = node.body[1:]

        new_code = astunparse.unparse(parsed)#toLower().visit(parsed))
        #print(new_code)
        return new_code, has_docstring
    
    except BaseException as e:
        print("Exception in docstring", e)
        parsed = 'nan'
        return parsed

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        code = f.read()
        processed_script, has_docstring = undocstring(code)
        if has_docstring:
            with open(sys.argv[1]+"_docstring_transform.py", "w") as f:
                f.write(processed_script)
        
