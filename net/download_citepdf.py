import os


import sys
import os
import argparse
import requests
import time
from lxml import etree
from contextlib import closing
from tqdm import tqdm

SCIHUB_URL = "https://www.sci-hub.se/"      # 2023.2.21 scihub地址，若不可访问请自行更新
HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
XPATH = '//*[@id="buttons"]/button/@onclick'

def download(doi, save_path):
    print(doi, end= ' ')
    file_name = doi.replace("/", "@")+".pdf"
    if os.path.exists(os.path.join(save_path,file_name)):
        message = f'{file_name} already exist'
        return message
    os.makedirs(save_path,exist_ok=True)
    message = f'{file_name} saved in {save_path}'
    try:
        req = requests.get(url=SCIHUB_URL+doi, headers=HEADER,timeout=(3, 10))
        root = etree.HTML(req.content)
        elementDownloadLink = root.xpath(XPATH)[0]
        pdf_link = elementDownloadLink.replace('location.href=', '').replace("'", '')
        if 'sci-hub.st' not in pdf_link:
            pdf_link = '//sci-hub.st' + pdf_link
        if 'https' not in pdf_link:
            pdf_link = 'https:' + pdf_link
        time.sleep(1)
        reqFile = requests.get(url=pdf_link, stream=True, headers=HEADER,timeout=(3, 10))
        chunk_size = 512
        with open(os.path.join(save_path, file_name), mode='wb') as f:
            for chunk in reqFile.iter_content(chunk_size):
                f.write(chunk)
    except Exception as e:
        message = e
    return message


cites = open('dataset/cited.txt', 'r').read().split('\n')
save_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\mill_cite_pdf'
if not os.path.exists(save_path ):
    os.makedirs(save_path)
for cite in tqdm(cites):
    try:
        citing, cited, _ = cite.split(' ')
        print(download(citing, save_path))
        time.sleep(3)
    except Exception as e:
        print(e)