import os
from typing import Counter
import pandas as pd
import time
import re
import sys
import requests

api_key = os.getenv("BAM_API_KEY")
eval_dataset_path=sys.argv[1]
task_name = sys.argv[2]
output_file_path = eval_dataset_path[:-4]+"_prompting_output.csv"
num_concurrent_prompts = 5
df = pd.read_csv(eval_dataset_path)
task_params = {
    'casing_java':{
        'orig_text_col':"script_uncased",
        'transformed_col':"script_raw",
        'control_prompt':"Change the casing of identifiers to language standard:"},
    'method_extraction':{
        'orig_text_col':"script_raw",
        'transformed_col': "script_refactored",
        'control_prompt':"Refactor code to encapsulate repeated bits of code in functions:"},
    'list_comp':{
        'orig_text_col':"no_comp_content",
        'transformed_col':"uncommented_content",
        'control_prompt':"Replace for loops by list comprehension:"},
    'casing_python':{
        'orig_text_col':"no_casing_content",
        'transformed_col':"uncommented_content",
        'control_prompt':"Change the casing of identifiers to language standard (PEP-8):"},
    'decorators':{
        'orig_text_col':"no_decorator_content",
        'transformed_col':"uncommented_content",
        'control_prompt':"Add decorators to methods as appropriate:"},
    'comments':{
        'orig_text_col':"uncommented_content",
        'transformed_col':"content",
        'control_prompt':"Add comments to code:"},
    'docstrings':{
        'orig_text_col':"no_docstring_content",
        'transformed_col':"uncommented_content",
        'control_prompt':"Add docstrings to code:"},#TODO: check

}

def get_generated_text(api_key, prompt, max_new_tokens=100, model_id='salesforce/codegen-16b-mono', stop_sequences=None):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    if isinstance(prompt, str):
        prompt=[prompt]

    json_data = {
        'model_id': model_id,
        'inputs': prompt,
        'parameters': {
            'decoding_method': 'greedy',
            'stop_sequences': stop_sequences,
            'temperature': 0,
            'max_new_tokens': max_new_tokens,
        },
    }

    response = requests.post('https://bam-api.res.ibm.com/v0/generate', headers=headers, json=json_data)#TODO:anonymize
    return(response)

def postprocess_output(model_output: str) -> str:
    idx = model_output.find('Original code:')
    if idx != -1:
        return model_output[0:idx]
    else:
        return model_output

def get_sample_examples(control_prompt):
    examples_dict = {
        #examples from https://python.plainenglish.io/list-comprehension-cheatsheet-converting-to-for-loops-vice-versa-2f0af9aa29e0
        "Change the casing of identifiers to language standard:":pd.DataFrame(data={"script_uncased":["""package p03281.s252075069;


import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {

        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        boolean[] isprime = new boolean[n+1];
        Arrays.fill(isprime, true);
        isprime[0] = false;
        isprime[1] = false;
        for(int i = 2; i <= n; i++){
            if(isprime[i]){
                for(int j = i*2; j <= n; j+=i){
                    isprime[j] = false;
                }
            }
        }

        int ans = 0;
        for(int i = 1; i <= n; i+=2){
            int[] primes = new int[n+1];
            for(int j = 2; j <= n; j++){
                if(isprime[j]){
                    int target = i;
                    while( target % j== 0 ){
                        target /= j;
                        primes[j]++;
                    }
                }
            }

            int cnt = 1;
            for(int j = 2; j <= n; j++){
                if( primes[j] > 0 ) cnt *= (primes[j]+1);
            }
            if(cnt == 8) ans++;
        }

        System.out.println(ans);

    }
}"""], "script_raw":["""package p03281.s252075069;


import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {

        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        boolean[] isPrime = new boolean[N+1];
        Arrays.fill(isPrime, true);
        isPrime[0] = false;
        isPrime[1] = false;
        for(int i = 2; i <= N; i++){
            if(isPrime[i]){
                for(int j = i*2; j <= N; j+=i){
                    isPrime[j] = false;
                }
            }
        }

        int ans = 0;
        for(int i = 1; i <= N; i+=2){
            int[] primes = new int[N+1];
            for(int j = 2; j <= N; j++){
                if(isPrime[j]){
                    int target = i;
                    while( target % j== 0 ){
                        target /= j;
                        primes[j]++;
                    }
                }
            }

            int cnt = 1;
            for(int j = 2; j <= N; j++){
                if( primes[j] > 0 ) cnt *= (primes[j]+1);
            }
            if(cnt == 8) ans++;
        }

        System.out.println(ans);

    }
}"""]}),
        #examples from https://python.plainenglish.io/list-comprehension-cheatsheet-converting-to-for-loops-vice-versa-2f0af9aa29e0
        "Refactor code to encapsulate repeated bits of code in functions:":pd.DataFrame(data={"script_raw":["""package p02255.s727365101;


import java.util.Scanner;

public class Main { 
    public static void main(String[] args) {
    	
    	Scanner sc = new Scanner(System.in);
        int i, j, k, l;
        int N = sc.nextInt();
        int A[] = new int[N];
        
        for(i = 0; i < N; i++){
            j = sc.nextInt();
            A[i] =j;
        }
 
        for(i = 1; i <= N - 1; i++){
            for(k = 0; k < N; k++){
                System.out.print(A[k]);
                
                if(k != N - 1) System.out.print(" ");
            }
            
            System.out.println();
            l = A[i];
            j = i - 1;
            while(j >= 0 && A[j] > l){
                A[j + 1] = A[j];
                j--;
            }
            A[j + 1] = l;   
        }
        for(k = 0; k < N; k++){
            System.out.print(A[k]);
            if( k != N - 1) System.out.print(" ");
        }
        System.out.println();
    }
}
"""], "script_refactored":["""package p02255.s727365101;


import java.util.Scanner;

public class Main { 
    public static void main(String[] args) {
    	
    	Scanner sc = new Scanner(System.in);
        int i, j, k, l;
        int N = sc.nextInt();
        int A[] = new int[N];
        
        for(i = 0; i < N; i++){
            j = sc.nextInt();
            A[i] =j;
        }
 
        for(i = 1; i <= N - 1; i++){
            k = extracted_0(N, A);
            l = A[i];
            j = i - 1;
            while(j >= 0 && A[j] > l){
                A[j + 1] = A[j];
                j--;
            }
            A[j + 1] = l;
        }
        k = extracted_0(N, A);
    }

	private static int extracted_0(int N, int[] A) {
		int k;
		for(k = 0; k < N; k++){
		    System.out.print(A[k]);
		    
		    if(k != N - 1) System.out.print(" ");
		}
		
		System.out.println();
		return k;
	}
}
"""]}),
        "Replace for loops by list comprehension:":pd.DataFrame(data={"no_comp_content":["""lis = []
for fruit in fruits:
    lis.append(len(fruit))""",
    """lis = []
for fruit in fruits:
    if len(fruit) == 5:
        lis.append("yes")
    else:
        lis.append("no")""",
        """lis = []
for fruit in fruits:
    if len(fruit) >= 5:
        lis.append(fruit)""",
        """lis = []
for f in fruits:
    for r in recipes:
        for s in sugar_levels:
            lis.append(f + r + s)"""], "uncommented_content":["""lis = [len(fruit) for fruit in fruits]""",
        """lis = ["yes" if len(fruit)==5 else "no" for fruit in fruits]""",
        """lis = [fruit for fruit in fruits if len(fruit)>=5]""",
        """lis = [f+r+s for f in fruits for r in recipes for s in sugar_levels]"""]}),
        "Change the casing of identifiers to language standard (PEP-8):":pd.DataFrame(data={"no_casing_content":["""from collections import defaultdict
M = 998244353
B = ((10 ** 18) % M)

def mex(s):
    for i in range((max(s) + 2)):
        if (i not in s):
            return i

def ext_euc(a, b):
    (x1, y1, z1) = (1, 0, a)
    (x2, y2, z2) = (0, 1, b)
    while (z1 != 1):
        (d, m) = divmod(z2, z1)
        (x1, x2) = ((x2 - (d * x1)), x1)
        (y1, y2) = ((y2 - (d * y1)), y1)
        (z1, z2) = (m, z1)
    return (x1, y1)

def inv_mod(a, b, m):
    (x, y) = ext_euc(a, m)
    return ((x * b) % m)

def calc_grundy(e):
    g = {}
    sumg = defaultdict(int)
    sumg[0] = inv_mod((B - 1), (pow(B, (N + 1), M) - B), M)
    for i in sorted(e.keys(), reverse=True):
        m = mex({g.get(j, 0) for j in e[i]})
        if m:
            g[i] = m
            x = pow(B, i, M)
            sumg[m] += x
            sumg[0] -= x
    return sumg

def get_edge():
    M = int(input())
    e = defaultdict(set)
    for i in range(M):
        (a, b) = sorted(map(int, input().split()))
        e[a].add(b)
    return e

def solve(N, edge):
    sumg = list(map(calc_grundy, edge))
    ret = 0
    for (gx, x) in sumg[0].items():
        for (gy, y) in sumg[1].items():
            gz = (gx ^ gy)
            z = sumg[2][gz]
            ret = ((ret + ((x * y) * z)) % M)
    return ret
N = int(input())
edge = [get_edge() for i in range(3)]
print(solve(N, edge))
        """], "uncommented_content":["""from collections import defaultdict

M = 998244353
B = 10**18 % M

def mex(s):
  for i in range(max(s)+2):
    if i not in s:
      return i

def ext_euc(a, b):
  x1, y1, z1 = 1, 0, a
  x2, y2, z2 = 0, 1, b
  while z1 != 1:
    d, m = divmod(z2,z1)
    x1, x2 = x2-d*x1, x1
    y1, y2 = y2-d*y1, y1
    z1, z2 = m, z1
  return x1, y1

def inv_mod(a, b, m):
  x, y = ext_euc(a, m)
  return (x * b % m)

def calc_grundy(e):
  g = {}
  sum_g = defaultdict(int)
  sum_g[0] = inv_mod(B-1, pow(B, N+1, M)-B, M)
  for i in sorted(e.keys(), reverse=True):
    m = mex({g.get(j,0) for j in e[i]})
    if m:
      g[i] = m
      x = pow(B, i, M)
      sum_g[m] += x
      sum_g[0] -= x
  return sum_g

def get_edge():
  M = int(input())
  e = defaultdict(set)
  for i in range(M):
    a, b = sorted(map(int, input().split()))
    e[a].add(b)
  return e

def solve(N, edge):
  sum_g = list(map(calc_grundy, edge))
  ret = 0
  for gx, x in sum_g[0].items():
    for gy, y in sum_g[1].items():
      gz = gx^gy
      z = sum_g[2][gz]
      ret = (ret + x*y*z)%M
  return ret

N = int(input())
edge = [get_edge() for i in range(3)]

print(solve(N, edge))"""]}),
"Add decorators to methods as appropriate:":pd.DataFrame(data={"no_decorator_content":["""import pytest
from pinkerton.base import EntityType
from pinkerton.extractor import EntityExtractor

def extractor():
    return EntityExtractor('https://natasha.b-labs.pro/api/')

def test_text():
    return

def test_correct_api_urls(extractor):
    assert (extractor.api_extract_url == 'https://natasha.b-labs.pro/api/extract')
    assert (extractor.api_version_url == 'https://natasha.b-labs.pro/api/version')

async def test_that_api_returns_some_results(extractor, test_text):
    (objects, spans) = (await extractor.extract(test_text))
    assert objects
    assert spans
    assert (objects[0]['type'] == EntityType.Person)
    assert (objects[0]['fields']['firstname'] == 'Иван')
    assert (objects[0]['fields']['middlename'] == 'Василиевич')
    assert (objects[0]['fields']['lastname'] == 'Иванов')"""], "uncommented_content": ["""import pytest
from pinkerton.base import EntityType
from pinkerton.extractor import EntityExtractor

@pytest.fixture
def extractor():
    return EntityExtractor('https://natasha.b-labs.pro/api/')

@pytest.fixture
def test_text():
    return

def test_correct_api_urls(extractor):
    assert (extractor.api_extract_url == 'https://natasha.b-labs.pro/api/extract')
    assert (extractor.api_version_url == 'https://natasha.b-labs.pro/api/version')

@pytest.mark.asyncio
async def test_that_api_returns_some_results(extractor, test_text):
    (objects, spans) = (await extractor.extract(test_text))
    assert objects
    assert spans
    assert (objects[0]['type'] == EntityType.Person)
    assert (objects[0]['fields']['firstname'] == 'Иван')
    assert (objects[0]['fields']['middlename'] == 'Василиевич')
    assert (objects[0]['fields']['lastname'] == 'Иванов')"""]}),
    "Add docstrings to code:":pd.DataFrame(data={"no_docstring_content":["""import math
import pandas
from talib import abstract
from analyzers.utils import IndicatorUtils

class RSI(IndicatorUtils):

    def analyze(self, historical_data, period_count=14, signal=['rsi'], hot_thresh=None, cold_thresh=None):
        dataframe = self.convert_to_dataframe(historical_data)
        rsi_values = abstract.RSI(dataframe, period_count).to_frame()
        rsi_values.dropna(how='all', inplace=True)
        rsi_values.rename(columns={rsi_values.columns[0]: 'rsi'}, inplace=True)
        if rsi_values[signal[0]].shape[0]:
            rsi_values['is_hot'] = (rsi_values[signal[0]] < hot_thresh)
            rsi_values['is_cold'] = (rsi_values[signal[0]] > cold_thresh)
        return rsi_values
    """], "uncommented_content": ["""' RSI Indicator\n'
import math
import pandas
from talib import abstract
from analyzers.utils import IndicatorUtils

class RSI(IndicatorUtils):

    def analyze(self, historical_data, period_count=14, signal=['rsi'], hot_thresh=None, cold_thresh=None):
        'Performs an RSI analysis on the historical data\n\n        Args:\n            historical_data (list): A matrix of historical OHCLV data.\n            period_count (int, optional): Defaults to 14. The number of data points to consider for\n                our RSI.\n            signal (list, optional): Defaults to rsi. The indicator line to check hot/cold\n                against.\n            hot_thresh (float, optional): Defaults to None. The threshold at which this might be\n                good to purchase.\n            cold_thresh (float, optional): Defaults to None. The threshold at which this might be\n                good to sell.\n\n        Returns:\n            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.\n        '
        dataframe = self.convert_to_dataframe(historical_data)
        rsi_values = abstract.RSI(dataframe, period_count).to_frame()
        rsi_values.dropna(how='all', inplace=True)
        rsi_values.rename(columns={rsi_values.columns[0]: 'rsi'}, inplace=True)
        if rsi_values[signal[0]].shape[0]:
            rsi_values['is_hot'] = (rsi_values[signal[0]] < hot_thresh)
            rsi_values['is_cold'] = (rsi_values[signal[0]] > cold_thresh)
        return rsi_values
"""]}),
"Add comments to code:":pd.DataFrame(data={"uncommented_content":["""from urllib.parse import urlparse
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.view import view_config, view_defaults

@view_defaults(route_name='index')
class IndexViews():

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.enabled = request.registry.settings['enable_front_page']

    @view_config(request_method='GET', renderer='via:templates/index.html.jinja2')
    def get(self):
        if (not self.enabled):
            return HTTPNotFound()
        self.request.response.headers['X-Robots-Tag'] = 'all'
        return {}

    @view_config(request_method='POST')
    def post(self):
        if (not self.enabled):
            return HTTPNotFound()
        try:
            url = self.context.url_from_query()
        except HTTPBadRequest:
            return HTTPFound(self.request.route_url(route_name='index'))
        parsed = urlparse(url)
        url_without_query = parsed._replace(query='', fragment='').geturl()
        return HTTPFound(self.request.route_url(route_name='proxy', url=url_without_query, _query=parsed.query))"""],
"content": ["""from urllib.parse import urlparse

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.view import view_config, view_defaults


@view_defaults(route_name="index")
class IndexViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.enabled = request.registry.settings["enable_front_page"]

    @view_config(request_method="GET", renderer="via:templates/index.html.jinja2")
    def get(self):
        if not self.enabled:
            return HTTPNotFound()

        self.request.response.headers["X-Robots-Tag"] = "all"

        return {}

    @view_config(request_method="POST")
    def post(self):
        if not self.enabled:
            return HTTPNotFound()

        try:
            url = self.context.url_from_query()
        except HTTPBadRequest:
            # If we don't get a URL redirect the user to the index page
            return HTTPFound(self.request.route_url(route_name="index"))

        # In order to replicate the URL structure from original Via we need to
        # create a path like this:
        # http://via.host/http://proxied.site?query=1
        # This means we need to pop off the query string and then add it
        # separately from the URL, otherwise we'll get the query string encoded
        # inside the URL portion of the path.

        # `context.url_from_query` protects us from parsing failing
        parsed = urlparse(url)
        url_without_query = parsed._replace(query="", fragment="").geturl()

        return HTTPFound(
            self.request.route_url(
                route_name="proxy", url=url_without_query, _query=parsed.query
            )
        )"""]})
    }
    return examples_dict[control_prompt]

def create_prompt(orig_code, sample_examples, orig_text_col, transformed_col, control_prompt):
    prompt = control_prompt+"\n"
    for _, sample in sample_examples.iterrows():
        prompt = prompt+"Original code:"
        prompt = prompt+"\n"+sample[orig_text_col]
        prompt = prompt+"\n\n"+"Transformed code:"
        prompt = prompt+"\n"+sample[transformed_col]+"\n\n"
    prompt = prompt + "Original code:"
    prompt = prompt + "\n"+ orig_code
    prompt = prompt+"\n\n"+"Transformed code:\n"
    return prompt

def get_model_output(df, orig_text_col, transformed_col, control_prompt, num_shots=1):
    num_rows = df.shape[0]
    print(f"Number of rows in the input:{num_rows}")
    output = []
    count = 0
    err_count = 0
    errors = {}
    concurrent_prompt_list = []
    max_tokens_list=[]
    row_list = []
    for i, row in df.iterrows():
        if i>=0:
            sample_examples = get_sample_examples(control_prompt)
            with open(row['transform']) as f:
                orig_code = f.read()
            code_prompt = create_prompt(orig_code, sample_examples, orig_text_col, transformed_col, control_prompt)
            #Compute max_tokens based on the source code num tokens
            #max_tokens = len(row[orig_text_col].split(" "))+100
            max_tokens = len(re.sub('[=\t\n ]', '\n', orig_code).split("\n"))+300
            if max_tokens > 1536:
                max_tokens=1536
            #print(code_prompt)
            concurrent_prompt_list.append(code_prompt)
            max_tokens_list.append(max_tokens)
            row_list.append(row)
            if (i+1)%num_concurrent_prompts==0 or (i+1)==df.shape[0]:
                try:
                    response = get_generated_text(api_key, concurrent_prompt_list, max_new_tokens=max(max_tokens_list), model_id='bigcode/starcoder', stop_sequences=None)
                    generated_code_list =response.json().get("results", None)
                    if generated_code_list is not None:
                        for j, generated_code in enumerate(generated_code_list):
                            with open(row_list[j]['transform'][:-3]+"_prompting.py", "w") as f:
                                f.write(postprocess_output(generated_code["generated_text"]))
                            output.append({'orig':row_list[j]['transform'], 'transform':row_list[j]['transform'][:-3]+"_prompting.py"})
                            count = count+1
                            print(count)
                    else:
                        print("generated code is none.")
                        err_count +=1
                    concurrent_prompt_list = []
                    max_tokens_list = []
                    row_list = []
                except BaseException as e:
                    print(e)
                    import pdb;pdb.set_trace()
                    err_count +=1
                    errors[i] = str(e)
                if count%10==0:
                    print(f"Done processing {count} rows out of {i+1} rows.")
                    out_df = pd.DataFrame.from_records(output, columns = ['orig', 'transform'])
                    out_df.to_csv(output_file_path, index=False)
    out_df = pd.DataFrame.from_records(output, columns = ['orig', 'transform'])
    out_df.to_csv(output_file_path, index=False)
    print(errors)
    print(f"Successfully obtained model output for {count} rows. {err_count} number of errors.")
get_model_output(df,
    task_params[task_name]['orig_text_col'],
    task_params[task_name]['transformed_col'],
    task_params[task_name]['control_prompt'])
