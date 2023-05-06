'''
pdf转img by 胡天翼

使用前，请安装安装fitz与依赖PyMuPDF
$pip install fitz
$pip install pymupdf
'''
import os
import re
import time
import shutil
import fitz
import concurrent.futures
from multiprocessing import  Process

CACHE_ROOT = './.cache/fitz_image'

'''
    pdf转img
    
    输入：
    pdf_path: 原始pdf路径
    img_path: 输出图片路径，需要确保路径为空
    
    无返回
'''
def run(pdf_path,img_path):

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

def run_fitz(pdf_dir):

    # 设置图像尺寸的最小值
    min_width = 100
    min_height = 100

    # 遍历PDF目录中的所有文件
    for pdf_file in os.listdir(pdf_dir):
        # 如果文件扩展名是PDF
        if pdf_file.endswith(".pdf"):
            # 打开PDF文件
            doc = fitz.open(os.path.join(pdf_dir, pdf_file))
            pages_count = doc.page_count
            print(f'"{pdf_file}"总共{pages_count}页')

            # images save path
            images_save_prefix = os.makedirs(os.path.join(pdf_dir, pdf_file[:-4]), exist_ok=True)

            # 逐页读取数据
            for i in range(pages_count):

                # 读取PDF第i页
                print(f"开始读取第{i + 1}页")
                page = doc.load_page(i)

                # 获取图片信息
                page_images = doc.get_page_images(i)

                page_img_idx = 0
                # 转存图片数据
                for image in page_images:
                    # load img data
                    xref = image[0]
                    pix = fitz.Pixmap(doc, xref)
                    if not pix.colorspace.name in (fitz.csGRAY.name, fitz.csRGB.name):
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    # image save path
                    page_img_idx += 1
                    save_path = f"{images_save_prefix}_page{i}_{page_img_idx:03d}.png"
                    # save
                    if pix.n < 5:
                        # GRAY or RGB
                        pix.save(save_path)
                    else:
                        # CMYK
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        pix1.save(save_path)
                        pix1 = None
                    pix = None


            # # 遍历PDF页面
            # for page in doc:
            #     # 遍历页面内的图像
            #     for img in page.get_images():
            #         # 获取图像的XREF编号和尺寸
            #         xref, _, size, _ = img
            #         # 使用XREF编号获取图像对象
            #         pix = fitz.Pixmap(doc, xref)
            #         # 如果图像存在
            #         if pix.n > 0:
            #             # 获取图像的尺寸
            #             width = pix.width
            #             height = pix.height
            #             # 如果图像尺寸大于指定值
            #             if width >= min_width and height >= min_height:
            #                 # 保存图像到文件
            #                 img_file = re.sub('\.pdf$', '', pdf_file)
            #                 img_file = "page%s-%s.png" % (page.number, xref)
            #                 pix.writePNG(os.path.join(pdf_dir, img_file))
            #         # 释放图像对象
            #         pix = None
            # # 关闭PDF文件
            # doc.close()


def pdf2pic(path, pic_path = None):
    '''
    # 从pdf中提取图片
    :param path: pdf的路径
    :param pic_path: 图片保存的路径
    :return:
    '''
    if pic_path == None:
        pic_path = path[:-4]
    os.makedirs(pic_path, exist_ok=True)
    # 设置图像尺寸的最小值
    min_width = 100
    min_height = 100

    t0 = time.process_time()  #原先的time.clock()已经不适用，要改成time.process_time()
    # 使用正则表达式来查找图片
    checkXO = r"/Type(?= */XObject)"
    checkIM = r"/Subtype(?= */Image)"

    # 打开pdf
    doc = fitz.open(path)
    lenXREF = doc.xref_length()  #_getXrefLength()不适用，要改成xref_length()

    # 打印PDF的信息
    print("文件名:{}, 页数: {}, 对象: {}".format(path, len(doc), lenXREF - 1))

    count = 0
    # 遍历每一个对象
    for i in range(1, lenXREF):
        # 定义对象字符串
        text = doc.xref_object(i)  #getObjectString()不适用，要改成xref_object()
        isXObject = re.search(checkXO, text)
        # 使用正则表达式查看是否是图片
        isImage = re.search(checkIM, text)
        # 如果不是对象也不是图片，则continue
        if not isXObject or not isImage:
            continue
        # 根据索引生成图像
        pix = fitz.Pixmap(doc, i)
        # if not pix.colorspace.name in (fitz.csGRAY.name, fitz.csRGB.name):
        #     pix = fitz.Pixmap(fitz.csRGB, pix)

        width = pix.width
        height = pix.height
        # 如果图像尺寸大于指定值
        if width < min_width or height < min_height:
            continue
        # 根据pdf的路径生成图片的名称
        count += 1
        pdf_name = path.split('\\')[-1][:-4]
        new_name = pdf_name + "_img{}.png".format(count)
        # new_name = new_name.replace(':', '')

        # 如果pix.n<5,可以直接存为PNG
        # if pix.n < 5:
        pix0 = fitz.Pixmap(fitz.csRGB, pix)
        pix0.save(os.path.join(pic_path, new_name))
        pix = None
        pix0 = None
        #     # pix.save(os.path.join(pic_path, new_name))
        # # 否则先转换CMYK
        # else:
        #     pix0 = fitz.Pixmap(fitz.csRGB, pix)
        #     pix0.save(os.path.join(pic_path, new_name))
        #     pix0 = None
        # 释放资源

        t1 = time.process_time()    #同上，time.clock()不适用，改成time.process_time()
        print("运行时间:{}s".format(t1 - t0))
        print("提取了{}张图片".format(count))
    doc.close()

def main(pdf_dir, pic_dir = None):
    if pic_dir == None:
        pic_dir = pdf_dir
    # with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    #     # 遍历PDF目录中的所有文件
    #     for pdf_file in os.listdir(pdf_dir):
    #         # 如果文件扩展名是PDF
    #         if pdf_file.endswith(".pdf"):
    #             # 提交任务到线程池
    #             executor.submit(pdf2pic, os.path.join(pdf_dir,pdf_file), os.path.join(pic_dir, pdf_file[:-4]) )
    file_list = os.listdir(pdf_dir)
    process_maxlen = 16
    process_list = []
    for pdf_file in file_list:
        # 如果文件扩展名是PDF
        if pdf_file.endswith(".pdf"):
            # 提交任务到线程池
            if len(process_list) == process_maxlen:
                [p.start() for p in process_list]
                [p.join() for p in process_list]
                process_list = []
            process_list.append(Process(target=pdf2pic, args=(os.path.join(pdf_dir,pdf_file), os.path.join(pic_dir, pdf_file[:-4]))))
    if len(process_list) > 0:
        [p.start() for p in process_list]
        [p.join() for p in process_list]
    # for pdf_file in os.listdir(pdf_dir):
    #     if pdf_file.endswith(".pdf"):
    #         pdf2pic(os.path.join(pdf_dir,pdf_file), os.path.join(pic_dir, pdf_file[:-4]) )

# if __name__=='__main__':
#     # pdf路径
#     path = r'D:\Projects\PaperTool\10.2147@ott.s228637.pdf'
#     pic_path = r'try_img'
#     # 创建保存图片的文件夹
#     if os.path.exists(pic_path):
#         print("文件夹已存在，请重新创建新文件夹！")
#         # raise SystemExit
#     else:
#         os.mkdir(pic_path)
#     m = pdf2pic(path, pic_path)

if __name__ == '__main__':
    # run_fitz(r'D:\Projects\PaperTool\eurrev_mill_pdf')
    t0 = time.process_time()
    main(r'D:\Projects\PaperTool\eurrev_mill_pdf')
    t1 = time.process_time()
    print("16进程总运行时间:{}s".format(t1 - t0))