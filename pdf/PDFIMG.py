'''
pdf转img by 胡天翼

使用前，请安装安装fitz与依赖PyMuPDF
$pip install fitz
$pip install pymupdf

本文件包含两个方法 pdf2pic 与 batch2pic
1. pdf2pic
> from PDFIMG import pdf2pic
    提取单个PDF图像
    输入：
    pdf_path: 原始pdf路径
    pic_path: 输出图片路径，需要确保路径为空
              若不传入pic_path，则默认在原始pdf路径下

    返回：
    如果执行异常则抛出

2. batch2pic
> from PDFIMG import batch2pic
    批量提取PDF图像
    输入：
    pdf_dir:  原始pdf目录
    pic_path: 输出图片目录，需要确保路径为空
              若不传入pic_path，则默认在原始pdf目录下
    batch_size: 多进程数量
    返回：
    无
'''

import os
import re
import time
import fitz
from multiprocessing import Process
from math import fabs

# 设置图像尺寸的最小值
min_width = 95
min_height = 95
EPS = 1e-5

def check_overpage(index_page, index_img, docimg_list):

    if index_page == 0:
        return True
    cur_img = docimg_list[index_page][index_img]
    for img in docimg_list[index_page-1]:
        if fabs(cur_img[1] - img[1]) < EPS and fabs(cur_img[2] - img[2]) < EPS:
            return False
    return True

def pdf2pic(path, pic_path = None):
    '''
    pdf转img（单张）

    输入：
    pdf_path: 原始pdf路径
    pic_path: 输出图片路径，需要确保路径为空
              若不传入pic_path，则默认在原始pdf路径下

    返回：
    如果执行异常则抛出
    '''
    # 使用正则表达式来查找图片
    checkIM = r"/Subtype(?= */Image)"
    # 打开pdf
    try:
        doc = fitz.open(path)
        page_nums = len(doc)
    except Exception as e:
        raise Exception(f'Failed to open {path}')
    if pic_path == None:
        pic_path = path[:-4]
    os.makedirs(pic_path, exist_ok=True)

    docimg_list = []
    for page_num in range(page_nums):
        pageimg_list = []
        page = doc.convert_to_pdf(page_num,page_num)
        image_bbox = doc[page_num].get_image_info()
        page = fitz.open("pdf", page)
        lenXREF= page.xref_length()
        for i in range(1, lenXREF):
            # 定义对象字符串
            text = page.xref_object(i)  #getObjectString()不适用，要改成xref_object()
            isImage = re.search(checkIM, text)
            # 如果不是对象也不是图片，则continue
            if not isImage:
                continue
            # 根据索引生成图像
            try:
                pix = fitz.Pixmap(page, i)
                width = float(pix.width)
                height = float(pix.height)
                # 如果图像尺寸大于指定值
                if pix.size / (width * height) < 2:
                    continue
                for img in image_bbox:
                    if img is not None:
                        if fabs(img["width"] - width) < EPS  and fabs(img["height"] - height) < EPS :
                            # print(img)
                            box = img["transform"]
                            # print(box)
                            box = list(box)
                            w = float(box[0])
                            h = float(box[3])
                            x0 = float(box[4])
                            y0 = float(box[5])
                            # print(width, height)
                            # print(w, h)
                            if w < min_width or h < min_height or w * h < min_width * min_height:
                                continue
                            pix0 = fitz.Pixmap(fitz.csRGB, pix)
                            pageimg_list.append([page_num + 1, w, h, x0, y0, pix0])
                            pix = None
                            pix0 = None
            except Exception as e :
                pass
                # print(f'Runtime Error in {path}, object index {i}:{e}')
        docimg_list.append(pageimg_list)
    count = 0
    for index_page, pageimg in enumerate(docimg_list):
        for index_img, img in enumerate(pageimg):
            if check_overpage(index_page, index_img, docimg_list):
                count += 1
                pdf_name = path.split('\\')[-1][:-4]
                new_name = pdf_name + "_img{}.png".format(count)
                img[5].save(os.path.join(pic_path, new_name))

    doc.close()

def batch2pic(pdf_dir, pic_path = None, batch_size = 16):
    '''
    pdf转img（批量）

    输入：
    pdf_dir:  原始pdf目录
    pic_path: 输出图片目录，需要确保路径为空
              若不传入pic_path，则默认在原始pdf目录下
    batch_size: 多进程数量
    返回：
    无
    '''
    if pic_path == None:
        pic_path = pdf_dir
    file_list = os.listdir(pdf_dir)
    process_maxlen = batch_size
    process_list = []
    for pdf_file in file_list:
        # 如果文件扩展名是PDF
        if pdf_file.endswith(".pdf"):
            if len(process_list) == process_maxlen:
                [p.start() for p in process_list]
                [p.join() for p in process_list]
                process_list = []
            process_list.append(Process(target=pdf2pic, args=(os.path.join(pdf_dir,pdf_file), os.path.join(pic_path, pdf_file[:-4]))))
    if len(process_list) > 0:
        [p.start() for p in process_list]
        [p.join() for p in process_list]

if __name__ == '__main__':
    t0 = time.time()
    pdf2pic(r'D:\Projects\PaperTool\1909105.pdf.pdf')
    # batch2pic(r'D:\Projects\PaperTool\问题整理 - 测试')
    t1 = time.time()
    print("总运行时间:{}s".format(t1 - t0))