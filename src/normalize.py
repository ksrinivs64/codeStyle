import ast, copy
import sys
import astunparse

with open(sys.argv[1]) as f:
    code = f.read()
try:
    thecode = ast.parse(code)
    zz = astunparse.unparse(thecode)
    print(zz)
except:
    print(code)
