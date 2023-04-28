import ast, copy
import sys
import astunparse


class VisitorWithContext(object):

    def __init__(self):
        self.parents = []

    def visit(self, node):
        self.pre(node)
        self.parents.append(node)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        self.parents.pop()
        self.post(node)
    
    def pre(self, node):
        pass

    def post(self, node):
        pass

class CollectAllNames(VisitorWithContext):
    def __init__(self):
        self.changed = set()
        self.existing = set()
        VisitorWithContext.__init__(self)
        
    def is_assignment(self, p1, p2):
        if isinstance(p1, ast.Assign):
            for target in p1.targets:
                if target == p2:
                    return True
        elif isinstance(p1, ast.AugAssign) or isinstance(p1, ast.AnnAssign):
            if p1.target == p2:
                return True

        elif isinstance(p1, ast.FunctionDef):
            for arg in p1.args.args:
                self.existing.add(arg.arg)
                
            return p1.name == p2

        else:
            return False

    def has_assignment(self, node):
        p2 = node
        p1 = self.parents[-1]
        while p1 is not None:
            if isinstance(p1, ast.Subscript) and p2 != p1.value:
                return False
            
            if self.is_assignment(p1, p2):
                return True

            if self.parents.index(p1)==0:
                p2, p1 = p1, None
            else:
                p2, p1 = p1, self.parents[self.parents.index(p1)-1]

        return False
                
    def pre(self, node):
        if isinstance(node, ast.Name):
            self.existing.add(node.id)
            assert len(self.parents) != 0
            if self.has_assignment(node) and node.id != '_':
                self.changed.add(node.id)
                
    

class toLowerAll(ast.NodeTransformer):
    
    def __init__(self, changed, existing):
        self.changed = changed
        self.existing = existing
        reserved = ['False','def', 'if','raise', 'None', 'del', 'import','return', 'True', 'elif','in','try', 'and', 'else', 'is', 'while', 'as', 'except', 'lambda', 'with', 'assert','finally', 'nonlocal', 'yield','break','for','not','class', 'from','or', 'continue', 'global','pass']
        self.existing.update(reserved)

    def visit_Name(self, node):
        new_id = node.id.lower().replace("_","")
        if node.id in self.changed and new_id not in self.existing and node.id not in self.existing:
            n = copy.deepcopy(node)
            n.id = node.id.lower().replace("_","")
            return n
        else:
            return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        new_attr = node.attr.lower().replace("_","")
        if node.attr in self.changed and new_attr not in self.existing:
            node.attr = node.attr.lower().replace("_","")
            return node
        else:
            return node
        
    
with open(sys.argv[1]) as f:
    code = f.read()
    
names = CollectAllNames()
thecode = ast.parse(code)
#print(ast.dump(thecode, indent=4))

names.visit(thecode)
#print(names.changed)
    
toLower = toLowerAll(names.changed, names.existing)
thecode = ast.fix_missing_locations(toLower.visit(thecode))

zz = astunparse.unparse(thecode)
print(zz)
