
import sys
import os
import argparse
import requests
import time
from lxml import etree
from contextlib import closing
from tqdm import tqdm

SCIHUB_URL = "https://www.sci-hub.st/"      # 2023.2.21 scihub地址，若不可访问请自行更新
HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
XPATH = '//*[@id="buttons"]/button/@onclick'

def download(doi, save_path):
    file_name = doi.replace("/", "@")+".pdf"
    os.makedirs(save_path,exist_ok=True)
    message = f'{file_name} saved in {save_path}'
    try:
        req = requests.get(url=SCIHUB_URL+doi, headers=HEADER)
        root = etree.HTML(req.content)
        elementDownloadLink = root.xpath(XPATH)[0]
        pdf_link = elementDownloadLink.replace('location.href=', '').replace("'", '')
        if 'sci-hub.st' not in pdf_link:
            pdf_link = '//sci-hub.st' + pdf_link
        if 'https' not in pdf_link:
            pdf_link = 'https:' + pdf_link
        time.sleep(5)
        reqFile = requests.get(url=pdf_link, stream=True, headers=HEADER)
        chunk_size = 512
        with open(os.path.join(save_path, file_name), mode='wb') as f:
            for chunk in reqFile.iter_content(chunk_size):
                f.write(chunk)
    except requests.exceptions.RequestException as e:
        message = e
    return message



if __name__ == "__main__":
    download('10.1182/blood-2010-10-310425', '.')
