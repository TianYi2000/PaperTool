'''
pdf转img by 胡天翼

使用前，请安装安装fitz与依赖PyMuPDF
$pip install fitz
$pip install pymupdf
'''
import os
import time
import shutil

CACHE_ROOT = './.cache/fitz_image'

def run(pdf_path,img_path):
    '''
    pdf转img
    pdf_path: 原始pdf路径
    img_path: 输出图片路径，需要确保路径为空
    '''
    cache_dir = os.path.join(CACHE_ROOT, str(time.time()))
    if os.path.exists(cache_dir):
        os.removedirs(cache_dir)
    os.makedirs(cache_dir)
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    if len(os.listdir(img_path)) > 0:
        raise('img_path is not empty!')
    os.system(f'python -m fitz extract -images {pdf_path} -output {cache_dir}')
    filelist = os.listdir(cache_dir)
    filelist = sorted(filelist)
    for index, srcname in enumerate(filelist):
        shutil.copy(os.path.join(cache_dir, srcname) , os.path.join(img_path, f'image-{index + 1}.png'))
