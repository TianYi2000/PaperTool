import sys
import time

import requests
import json
from os.path import join as Join

# It is possible to specify one or more DOIs as input of this operation.
# In this case, the DOI should be separated with a double underscore ("__")
# e.g. "10.1108/jd-12-2013-0166__10.1016/j.websem.2012.08.001__...".
from tqdm import tqdm

TOKEN = "c758fd7f-81a9-435e-ad6c-9d6c60b8d558"
HTTP_HEADERS = {"authorization": TOKEN}

def meta(doi):
    time.sleep(3)
    if type(doi) == list:
        url = f"https://w3id.org/oc/meta/api/v1/metadata/{'__'.join(['doi:' + x for x in doi])}"
    else:
        url = f"https://w3id.org/oc/meta/api/v1/metadata/doi:{doi}"
    search_result, err = None, None
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=(5, 10))
        search_result = response.json()
    except requests.exceptions.RequestException as e:
        err = e
    return search_result, err

class META():
    def __init__(self, save_path) -> None:
        self.save_path = save_path
        f = open(save_path, 'w')
        self.Dict = {}
        tmp = []
    def read(self, doi_list):
        ret = []
        new_list = []
        for doi in doi_list:
            if doi in self.Dict:
                ret.append(self.Dict[doi])
            else:
                new_list.append(doi)
        tot_num = len(new_list)
        index = 0
        while index < tot_num:
            result, err = meta(new_list[index: min(index + 10, tot_num)])
            index += 10
            if err == None and len(result) > 0:
                for item in result:
                    doi = item['id'].split(' ')[0].split(':')[-1]
                    self.Dict[doi] = item
                    self.Dict[doi]['doi'] = doi
                    ret.append(self.Dict[doi])
            else:
                print(err)
        self.save_cache()
        return ret
    def save_cache(self):
        print(f'meta num = {len(list(self.Dict))}, saved in {self.save_path}')
        b = json.dumps(self.Dict)
        with open(self.save_path, 'w') as f:
                 f.write(b)
