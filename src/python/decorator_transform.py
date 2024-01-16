import ast
import os
import sys
import astunparse


class RemoveDecorator(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        print(node.name)
        print(node.decorator_list)
        node.decorator_list = []
        self.generic_visit(node)
        return node
    def visit_AsyncFunctionDef(self, node):
        print(node.name)
        print(node.decorator_list)
        node.decorator_list = []
        self.generic_visit(node)
        #print("async decorators stripped")
        return node
    def visit_ClassDef(self, node):
        print(node.name)
        node.decorator_list = []
        #print("async classes")
        self.generic_visit(node)
        return node    
        # return ast.FunctionDef(**{**node.__dict__, 'name':node.name.lower().replace("_","")})

def remove_decorator(input_code):
    decorators = False
    parsed = ast.parse(input_code)
    parsed_code = astunparse.unparse(parsed)
    final_code = astunparse.unparse(RemoveDecorator().visit(parsed))
    if parsed_code == final_code:
        return input_code, decorators

    decorators = True
    return final_code, decorators


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        code = f.read()
        processed_script, decorators = remove_decorator(code)
        if decorators:
            with open(sys.argv[1] + "_decorator_transform.py", "w") as f:
                f.write(processed_script)

        
