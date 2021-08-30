import json
from copy import deepcopy

from typing import List
from jinja2 import Environment, PackageLoader, select_autoescape

from jinja2 import FileSystemLoader
import pathlib
from IPython.core.display import display, HTML

WIDTH = 80

p = pathlib.Path(__file__)
path = '{}/templates/'.format(p.parent.absolute())

env = Environment(
    loader=FileSystemLoader(path),
)

def turn_html_to_ascii(html):
    with open('tmp.html', 'w') as f:
        f.write(html)
    import subprocess
    full = subprocess.run(["w3m", "-dump","-cols" ,f'{WIDTH}','tmp.html'], stdout=subprocess.PIPE)

    return full.stdout.decode('utf-8')

# 讀入存放反轉查詢表的 json 檔
def load_json(path: str):
    value = None
    with open(path) as f:
        value = json.load(f)
    return value

# 輔助拿到 verb tree 的資料
def get_verb_describe(verb_index):
    return PT[verb_index[0]][verb_index[1]][verb_index[2]]

# 把 json 轉換成 html 格式
def turn_json_to_html(verb_describe):
    full = ''.join(verb_describe['describe'])
    verb_lists = verb_describe['verb']

    verb_html_lists = []

    for verb_list in verb_lists:
        header = verb_list[0]
        datas = []
        data = []
        for idx, verb in enumerate(verb_list[1:]):
 
            data.append(verb)

            if (idx + 1) % 4 == 0:
                datas.append(data)
                data = []
        datas.append(data)
        template = env.get_template('verb_table.html')
        html = template.render(header=header, datas=datas)
        verb_html_lists.append(html)
    
    full += '<br>'.join(verb_html_lists)
    full += f"<div> chapter: {verb_describe['chapter']} page: {verb_describe['page']} </div> "


    return full

# 通用轉換格式
def convert_to_return_format(json_format, return_format='json'):
    html = turn_json_to_html(json_format['info'])
    if return_format == 'html':
        return html
    elif return_format == 'ascii':
        return turn_html_to_ascii(html)
    else: # json format
        return json_format

PT = load_json('./pattern_tree.json')
VT = load_json('./verb_tree.json')

# 查詢 動詞 反轉表 verb tree
def get_verb(verb = None, index = None, return_format='json'):

    pattern_info = ""
    candidate = []

    # 如果有缺漏的 function 就回傳 candidate 讓使用者可以知道有哪些選項
    if verb is None:
        candidate = list(VT.keys())
    elif index is None:
        candidate = list(VT[verb])
    else:
        candidate = []
        pattern_info = get_verb_describe(VT[verb][index])

    reval = {}
    reval['info'] = pattern_info
    reval['candidate'] = candidate
    

    all_filled =  (verb is not None and index is not None)
    if return_format == 'json' or not all_filled:
        return reval

    return convert_to_return_format(reval, return_format)

# 查詢 pattern tree
def get_pattern(pattern = None, struct = None, verb_group = None, return_format='json'):

    verb_info = ""
    candidate = []


    # 如果有缺漏的 function 就回傳 candidate 讓使用者可以知道有哪些選項
    if pattern is None:
        candidate = list(PT.keys())
    elif struct is None:
        candidate = list(PT[pattern].keys())
    elif verb_group is None:
        candidate = list(PT[pattern][struct].keys())
    else:
        candidate = []
        verb_info = PT[pattern][struct][verb_group]

    reval = {}
    reval['info'] = verb_info
    reval['candidate'] = candidate

    all_filled = pattern is not None and struct is not None and verb_group is not None
    if return_format == 'json' or not all_filled:
        return reval

    return convert_to_return_format(reval, return_format)
    
