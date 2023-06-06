import ast
test = "import ast\n class MyClass: \n\t\"\"\"A simple example class\"\"\" \n\ti = 12345 # le epic comment\n\tVAR = 1 \n\tWhoa = [i + 1 for i in range(0,10)]\n\n\tdef f(self):\n\t\treturn 'hello world'"
print (test)  #"\"\"\"start doc\"\"\"\n
#import astor
def undocstring(source):
    try:
        parsed = ast.parse(source)
        
        for node in ast.walk(parsed):
            print("Node is : ",node)
            #print("Node value is : ",node.body[0].value.s)
                    
            if not isinstance(node, (ast.Module)): #, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef
                continue

            if not len(node.body):
                continue

            if not isinstance(node.body[0], ast.Expr):
                continue

            if not hasattr(node.body[0], 'value') or not isinstance(node.body[0].value, ast.Str):
                continue

            # Uncomment lines below if you want print what and where we are removing
            # 
            # 

            node.body = node.body[1:]
        class toLower(ast.NodeTransformer):

            def visit_arg(self, node):
                return ast.arg(**{**node.__dict__, 'arg':node.arg.lower()})
            def visit_Name(self, node):
                #print("node id is : ",node.id)
                return ast.Name(**{**node.__dict__, 'id':node.id.lower()})

        new_code = ast.unparse(parsed)#toLower().visit(parsed))
        #print(new_code)
        return new_code
    except:
        parsed = 'nan'
        return parsed