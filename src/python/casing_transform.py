import ast, copy
import sys
import astunparse
import ast_scope

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
    def __init__(self, scope_info):
        self.changed = set()
        self.existing = set()
        self.args = set()
        self.not_assignments = set()
        self.scope_info = scope_info
        self.reserved = ['False','def', 'if','raise', 'None', 'del', 'import','return', 'True', 'elif','in','try', 'and', 'else', 'is', 'while', 'as', 'except', 'lambda', 'with', 'assert','finally', 'nonlocal', 'yield','break','for','not','class', 'from','or', 'continue', 'global','pass']
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
                self.args.add(arg.arg)
            return p1.name == p2

        else:
            return False

    def has_assignment(self, node):
        if isinstance(self.scope_info[node], ast_scope.scope.ClassScope):
            return False
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
            if self.has_assignment(node) and not node.id.startswith('_'):
                self.changed.add((node.id, scope_info[node]))
        if isinstance(node, ast.Attribute):
            self.not_assignments.add((node.attr, None))
        if isinstance(node, ast.FunctionDef):
            self.not_assignments.add((node.name,scope_info[node]))
        if isinstance(node, ast.ClassDef):
            self.not_assignments.add((node.name,scope_info[node]))
        if isinstance(node, ast.Global):
            for n in node.names:
                if n.lower().replace("_","") not in self.reserved:
                    self.changed.add(n)
    

class toLowerAll(ast.NodeTransformer):
    
    def __init__(self, changed, existing, args, not_assignments, scope_info):
        self.changed = changed
        self.existing = existing
        self.args = args
        self.not_assignments = not_assignments
        self.reserved = ['False','def', 'if','raise', 'None', 'del', 'import','return', 'True', 'elif','in','try', 'and', 'else', 'is', 'while', 'as', 'except', 'lambda', 'with', 'assert','finally', 'nonlocal', 'yield','break','for','not','class', 'from','or', 'continue', 'global','pass']
        self.existing.update(self.reserved)
        self.actual_changes = {}
        self.changed_file = False

    def visit_Global(self, node):
        new_names = []
        for n in node.names:
            t = n.lower().replace("_","")
            if t not in self.existing:
                new_names.append(t)
            else:
                new_names.append(n)
                
        n = copy.deepcopy(node)
        n.names = new_names
        return n

    def visit_Name(self, node):
        new_id = node.id.lower().replace("_","")
        ischanged = (node.id, scope_info[node]) in self.changed and (node.id, scope_info[node]) not in self.not_assignments
        if ischanged and new_id not in self.existing and node.id not in self.args and new_id not in self.args:
            if new_id not in self.actual_changes or (new_id in self.actual_changes and self.actual_changes[new_id] == node.id):
                self.actual_changes[new_id] = node.id
                n = copy.deepcopy(node)
                n.id = new_id
                self.changed_file = True
                return n
            else:
                return node
        else:
            return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        new_attr = node.attr.lower().replace("_","")
        is_not_assignment = (node.attr, None) in self.not_assignments
        if node.attr in self.changed and new_attr not in self.existing and not is_not_assignment:
            node.attr = node.attr.lower().replace("_","")
            self.changed_file = True
            return node
        else:
            return node
        
    
with open(sys.argv[1]) as f:
    code = f.read()
    
thecode = ast.parse(code)
scope_info = ast_scope.annotate(thecode)

#print(ast.dump(thecode, indent=4))
names = CollectAllNames(scope_info)

names.visit(thecode)
#print(names.changed)

toLower = toLowerAll(names.changed, names.existing, names.args, names.not_assignments, scope_info)

thecode = ast.fix_missing_locations(toLower.visit(thecode))

zz = astunparse.unparse(thecode)

if toLower.changed_file:
    with open(sys.argv[1] + "_casing_transform.py", "w") as f:
        f.write(zz)

