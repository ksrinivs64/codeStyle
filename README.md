This repository contains the code to create the parallel corpora for the Code Style Benchmark (CSB) and the code for the experiments mentioned in the paper such as fine-tuning and few-shot prompting.

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



## Data Preprocessing For Finetuning

### Raw Script Tokenization

The script is used for directly tokenizing the full dataset
- `train`: training set that named `bq_data_outlier.csv`
- `eval`: eval set that named `evaluation_set.csv`
```bash
python tokenize_raw_script.py [train|eval]
```


### Splitting Long Sequences
For keeping dataset in the range of the max sequence length, use this script for filtering out the short sequence data and extracting function/class level codes out of the long sequences. The output will be 2 files: short and long datasets. 
```bash
python split_long_data.py [train|eval]
```


## Fine-tuning using CodeT5
### 1. Parallel Corpus Tokenization

Tokenizing and filtering out all the NULL value examples.
```bash
python parallel_preprocessing_script.py FEATURES CSV_NAME OUTPUT_PATH
```


**CSV_NAME**: CSV file that contains all individual features


**OUTPUT_PATH**: The output dataset path, whatever you want, which will be a `.hf` file

> Preprocessing on the docstring transfer will be done for removing very long sequence data.
#### Example
```bash
# inidividual
## i.e. class
### train
python parallel_preprocessing_script.py \
    class \
    bq_data_outlier_no_class.csv \
    train_class_dataset.hf
### eval
python parallel_preprocessing_script.py \
    class \
    eval_set_individual_feat.csv \
    eval_class_dataset.hf


```


### 2. Training
#### Finetuning for Seq2Seq Model
The Seq2Seq Generation finetuning with CodeT5. 
```bash
# individual
export CUDA_VISIBLE_DEVICES=$(python gpu.py | tail -n 1); python seq2seq_train.py

```
You will need to configure the training in the script:
**seq2seq_train.py**
1. `fname_prefix`: your repo directory i.e. `/home/you/code-style-probing/`
2. `train_dataset_hf_name`: train set. But in the script, we dowsized it due to the training time constraint. i.e. `train_class_dataset.hf`
3. `test_dataset_hf_name`: test set. i.e. `test_class_dataset.hf`
4. `output_dir_name`: checkpoint folder  i.e.`codet5-class-checkpoints/`
5. `model_checkpoint`: checkpoint name, can be the folder or huggingface checkpoint, i.e. `Salesforce/codet5-small`
6. `inference_only`: whether only do the inference on the test set,  i.e. `False`
7. `down_size_test_set`: whether downsize the test set for saving time. i.e. `True`
8. `is_baseline`: if baseline, the CodeT5 will be trained from scratch.  i.e. `False`
9. `batch_size`: i.e. `16`

### 3. Seq2Seq Inference
```
Usage: seq2seq_inference.py [OPTIONS] INFERENCE_DATASET MODEL_CKPT_PATH
                            OUTPUT_CSV_FILENAME

Arguments:
  INFERENCE_DATASET    [required]
  MODEL_CKPT_PATH      [required]
  OUTPUT_CSV_FILENAME  [required]

Options:
  --batch-size INTEGER            [default: 8]
  --is-nl / --no-is-nl            [default: no-is-nl]
  --is-downsize / --no-is-downsize
                                  [default: no-is-downsize]

Example:
rm -rf codestylist ; \
export CUDA_VISIBLE_DEVICES=1; \
python seq2seq_inference.py \
/data/code/curated_eval_set/curated_docstring_dataset_with_prompt.hf \
codestylist/combined_code_style_transformer \
combined_model_results/docstring.non_downsized.output.csv \
--batch-size 64 \
--is-nl ;
```

- **DATASET_PATH**: The path of the test set. (`.hf`)
- **CHECKPOINT**: The model checkpoint path.
- **OUTPUT_FILE_PATH**: The path of the prediction output
- **IS_NL**: [true|false], whether use the control tokens.
- **IS_DOWNSIZE**: [true|false], whether need to downsize the test set, will downsize it to 2000 examples.

The output will be a prediction file that contains input/prediction/label.
> The removal of `codestylist` folder is because the trainer will create a foler automatically and will have error if we try to load the model from the hub, it will try to load from the empty folder created by trainer instead. So it is needed to remove the folder first no matter whether it exists.
### 4. Evaluation
Please see `seq2seq_eval.ipynb`(individual) for evaluation.

#### Script Usage
We now have a script `evaluate_score` for running the evaluation:
```
Usage: evaluate_score.py [OPTIONS] PRED_DIR OUTPUT_DIR TARGET_FEAT

Arguments:
  PRED_DIR     [required]
  OUTPUT_DIR   [required]
  TARGET_FEAT  [required]

Options:
  --is-nl-tokens-added / --no-is-nl-tokens-added
                                  [default: no-is-nl-tokens-added]
  --clean-diff / --no-clean-diff  [default: clean-diff]

Example:
python evaluate_score.py \
/data/ken/data/code/decorator.output_post_process.csv \
./test.json decorator \
--clean-diff
```

- PRED_DIR: You prediction csv file
- OUTPUT_DIR: You score output json file name
- is-nl-tokens-added: N/A
- clean-diff: will clean some inconsistent characters caused by AST parse and unparse before calculating DiffBLEU

## Few-shot Prompting

The scripts `prompting_for_test_set.py`, `prompting_for_codenet.py`, and `prompting_for_codenet_java.py` all do the 1-shot prompting mentioned in the paper. 
The main difference is the input data format. 
Note that we use a proprietary API which hosts multiple models for inference, so we need two environment variables `API_KEY` and `API_ENDPOINT` to connect to that service.
In theory, any model inferencing API can be used instead of this service.

For example, `prompting_for_test_set.py` takes the evaluation dataset csv path from `eval_parallel_corpora_neurips.zip` (this is uploaded to the [dataset link](https://zenodo.org/record/8021947)) and a task name as the two command line parameters.

It can be run as follows:
```
python prompting_for_test_set.py <path_to_evaluation_dataset_csv> <task_name>
```
