import ast, copy
import sys
import astunparse

class toFuncLower(ast.NodeTransformer):

    def __init__(self):
        self.changed = set()

    def visit_FunctionDef(self, node):
        self.changed.add(node.name)
        n = copy.deepcopy(node)
        n.name = node.name.lower().replace("_","")
        self.generic_visit(n)
        return n

    def visit_Assign(self, node):
        n = copy.deepcopy(node)
        tgts = []
        for t in n.targets:
            self.changed.add(t.id)
            nm = copy.deepcopy(t)
            tgts.append(nm)
            print('renaming' + t.id)
            nm.id = t.id.lower().replace("_","")
        n.targets = tgts
        self.generic_visit(n)

        return n

    def helper(self, node):
        self.changed.add(node.target.id)
        n = copy.deepcopy(node)
        x = copy.deepcopy(node.target)
        x.id.lower().replace("_","")
        n.target = x
        self.generic_visit(n)
        return n
    
    def visit_AugAssign(self, node):
        n = self.helper(node)
        return n

    def visit_AnnAssign(self, node):
        n = self.helper(node)
        return n

    def get_changed(self):
        return self.changed

class toLowerAll(ast.NodeTransformer):
    
    def __init__(self, changed):
        self.changed = changed

    def visit_Name(self, node):
        if node.id in self.changed:
            print('changing node:' + node.id)
            n = copy.deepcopy(node)
            n.id = node.id.lower().replace("_","")
            return n
        else:
            return node

    def visit_Attribute(self, node):
        if node.attr in self.changed:
            n = copy.deepcopy(node)
            print('changing attribute node:' + node.attr)
            n.attr = node.attr.lower().replace("_","")
            return n
        else:
            return node

with open(sys.argv[1]) as f:
    code = f.read()
    
func = toFuncLower()
thecode = ast.parse(code)
thecode = ast.fix_missing_locations(func.visit(thecode))
toLower = toLowerAll(func.get_changed())
thecode = ast.fix_missing_locations(toLower.visit(thecode))

zz = astunparse.unparse(thecode)
print(zz)
