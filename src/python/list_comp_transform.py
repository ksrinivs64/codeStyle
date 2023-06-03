import ast
import uuid
import sys
import astunparse
import traceback

def for_loop(text):
    changed_file = False
    def wrap_if(body, compare):
        return  ast.If(
                    test= compare,
                    body=[body],
                    orelse=[])
    
    def wrap_for(body, a, index):
        return ast.For(
                    target = a.value.generators[index].target,
                    iter = a.value.generators[index].iter,
                    body = body,
                    lineno = a.lineno + 1,
                    orelse = [])
    
    def comp_to_expl(tree):
        changed_file = False
        if hasattr(tree, 'body'):
          i = 0
          while i < len(tree.body):
            if isinstance(a:=tree.body[i], ast.Assign) and isinstance(a.value, ast.ListComp):
                list_name = a.targets[0].id
                try:
                    names_of_iterating_objects = [generator.iter.id for generator in a.value.generators]
                    if list_name in names_of_iterating_objects:
                        list_name = "lst_"+str(uuid.uuid4()).split("-")[0]
                except:
                    pass
                for_loop_body = [ast.Expr(
                                 value = ast.Call(
                                           func = ast.Attribute(value = ast.Name(id = list_name), attr = 'append', ctx = ast.Load()),
                                           args = [a.value.elt],
                                           keywords = [] ))]
                
                for ind, for_loop in enumerate(a.value.generators[::-1]):
                    ind = len(a.value.generators) - 1 - ind
                    for if_state in a.value.generators[ind].ifs:
                        for_loop_body = wrap_if(for_loop_body, if_state)
                        
                    for_loop_body = wrap_for(for_loop_body, a, ind)

                if list_name != a.targets[0].id: #it has changed because it conflicted with names_of_iterating_objects                
                    for_loop_body_to_add = [for_loop_body, ast.Assign(
                       targets=[ast.Name(id = a.targets[0].id)], value = ast.Name(id = list_name),
                       lineno = a.lineno)]
                else:
                    for_loop_body_to_add = [for_loop_body]
                tree.body = tree.body[:i] + \
                    [ast.Assign(
                       targets=[ast.Name(id = list_name)], value = ast.List(elts = []),
                       lineno = a.lineno
                    )] + \
                    for_loop_body_to_add + \
                    tree.body[i+1:]
                changed_file = True
                print("The file should have changed")
                i += 1
            i += 1
       for i in getattr(tree, '_fields', []):
          if isinstance(v:=getattr(tree, i, None), list):
             for i in v:
                try:
                    changed_file_1 = comp_to_expl(i)
                    changed_file = changed_file | changed_file_1
                except:
                    pass
          elif isinstance(v, ast.AST):
             try:
                 changed_file_1 = comp_to_expl(v)
                 changed_file = changed_file | changed_file_1
             except:
                 pass
       print("Now what is the value here?", changed_file)
       return changed_file

    try:
        parsed = ast.parse(text)
    except:
        print("Exception in place 2")
        return "Nan", False
    
    try:
        changed_file = comp_to_expl(parsed)
        print("did the file change here?", changed_file)
    except BaseException as e:
        traceback.print_exc()
        print("Exception in place 1", changed_file)
        #changed_file=False
        pass
    
    print("I am returning", changed_file)
    return astunparse.unparse(parsed), changed_file

if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("/home/ksrinivs/codeStyle/src/python/casing_transform.csv")
    records_dict = []
    for i, row in df.iterrows():
        try:
            with open(row['orig']) as f:
                code = f.read()
                transformed_code, changed_file = for_loop(code)
                f_out = open(row['orig'][:-3]+"_transformed_uncomp.py", "w")
                if changed_file:
                    print("writing file changed")
                    f_out.write("# File changed\n")
                f_out.write(transformed_code)
                print(row['orig'])
                records_dict.append({'orig':row['orig'],
                        'transform':row['orig'][:-3]+"_transformed_uncomp.py"})
            if i==10000:
                break
        except FileNotFoundError:
            print("file not found", row['orig'])
            continue
    df_out = pd.DataFrame.from_records(records_dict)
    df_out.to_csv("out.csv")
            

