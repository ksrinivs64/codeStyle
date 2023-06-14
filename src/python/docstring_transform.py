import ast
import pandas as pd
from tqdm import tqdm
import astunparse
import sys
test = "import ast\n class MyClass: \n\t\"\"\"A simple example class\"\"\" \n\ti = 12345 # le epic comment\n\tVAR = 1 \n\tWhoa = [i + 1 for i in range(0,10)]\n\n\tdef f(self):\n\t\treturn 'hello world'"
print (test)  #"\"\"\"start doc\"\"\"\n
#import astor
def undocstring(source):
    try:
        parsed = ast.parse(source)
        
        for node in ast.walk(parsed):
            print("Node is : ",node)
            #print("Node value is : ",node.body[0].value.s)
                    
            if not isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                continue

            if not len(node.body):
                continue

            if not isinstance(node.body[0], ast.Expr):
                continue

            if not hasattr(node.body[0], 'value') or not isinstance(node.body[0].value, ast.Str):
                continue

            node.body = node.body[1:]
        class toLower(ast.NodeTransformer):

            def visit_arg(self, node):
                return ast.arg(**{**node.__dict__, 'arg':node.arg.lower()})
            def visit_Name(self, node):
                #print("node id is : ",node.id)
                return ast.Name(**{**node.__dict__, 'id':node.id.lower()})

        new_code = astunparse.unparse(parsed)#toLower().visit(parsed))
        #print(new_code)
        return new_code
    except BaseException as e:
        print("Exception in docstring", e)
        parsed = 'nan'
        return parsed

if __name__ == "__main__":

    data_input = pd.read_csv(sys.argv[1])
    print("Length of input data : ", len(data_input))
    data_output = []
    for file_name in tqdm(data_input["orig"]):
        with open(file_name) as f:
            data = f.read()
        processed_script = undocstring(data)
        with open(file_name[:-3]+"_docstring_transform.py", "w") as f:
            if processed_script is None or processed_script == 'nan':
                f.write(data)
            else:
                print("file changed")
                f.write("# File changed\n")
                f.write(processed_script)
        data_output.append({"orig":file_name, "transform":file_name[:-3]+"_docstring_transform.py"})
    out_df = pd.DataFrame.from_records(data_output, columns = ['orig', 'transform'])
    out_df.to_csv("docstring_out.csv")
