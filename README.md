This repository contains the code to create the parallel corpora for the Code Style Benchmark (CSB).

The directory `src/python` contains the code for the Python transforms.

`src/python/requirements.txt` provides the dependencies required to execute the code.
The dependencies can be installed in a Python virtual environment by `pip install -r requirements.txt`.

### Parallel Corpora Generation:

1. list_comp_transform.py: This script takes a command line argument a path to a csv file with a column `orig` that points to paths of files that need to be transformed.

It can be run as:
```Python
python list_comp_transform.py <path_to_the_input_csv_file>
```

The output transformed files are written to the same paths with a suffix `_transformed_uncomp.py`

2. decorator_transform.py: This script takes a command line argument a path to a csv file 
with a column `content` that has the original code snippets to be transformed.

It can be run as:
```Python
python decorator_transform.py <path_to_the_input_csv_file>
```

The output transformed code snippets with no decorators are written as a new column
`decorator_modified` to a csv.

3. casing_transform.py: This script takes a command line argument a path to a code file
to be transformed. The output after transforming case is printed to stdout.

It can be run as:
```Python
python casing_transform.py <path_to_a_Python_code_file>
```

4. docstring_transform.py: This script takes a command line argument a path to a csv file with a column `orig` that points to paths of files that need to be transformed.

It can be run as:
```Python
python docstring_transform.py <path_to_the_input_csv_file>
```

The output transformed files are written to the same paths with a suffix `_docstring_transform.py`

5. comment_transform.py: This script takes a command line argument a path to a csv file with a column `orig` that points to paths of files that need to be transformed.

It can be run as:
```Python
python comment_transform.py <path_to_the_input_csv_file>
```

The output transformed files are written to the same paths with a suffix `_comment_transform.py`
