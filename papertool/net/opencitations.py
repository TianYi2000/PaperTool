import requests
import json

# It is possible to specify one or more DOIs as input of this operation.
# In this case, the DOI should be separated with a double underscore ("__")
# e.g. "10.1108/jd-12-2013-0166__10.1016/j.websem.2012.08.001__...".
TOKEN = "c758fd7f-81a9-435e-ad6c-9d6c60b8d558"
HTTP_HEADERS = {"authorization": TOKEN}
def cite(doi, api):
    assert api in ['references', 'citations']
    url = f"https://opencitations.net/index/coci/api/v1/{api}/{doi}"
    search_result, err = None, None
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=(10, 15))
        search_result = response.json()
    except requests.exceptions.RequestException as e:
        err = e
    return search_result, err

def meta(doi):
    url = f"https://w3id.org/oc/index/api/v1/metadata/doi:{doi}"
    search_result, err = None, None
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=(10, 15))
        search_result = response.json()
    except requests.exceptions.RequestException as e:
        err = e
    return search_result, err

