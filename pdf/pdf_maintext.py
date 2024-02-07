import os
from math import fabs
from tqdm import tqdm
import pdfplumber
import time
from multiprocessing import Process

class Article:
    def __init__(self):
        self.font_set = {}
        self.main_text = ''

    def count(self, pdf_crop):
        index = 0
        chars = pdf_crop.chars
        while index < len(chars):
            font_name = chars[index]['fontname']
            font_size = round(chars[index]['size'], 1)
            key = f'{font_name}:{font_size}'
            if key not in self.font_set:
                self.font_set[key] = 0
            self.font_set[key] += 1
            index += 1

    def get_main(self):
        count_result = sorted(self.font_set.items(),key = lambda x:x[1],reverse = True)
        self.main_font, self.main_size = count_result[0][0].split(':')
        self.main_size = float(self.main_size)

    def equal(self, x, y):
        EPS = 0.11
        if fabs(x -y) < EPS:
            return True
        else:
            return False
    def check_space(self, text):
        spacenum = sum([1 for x in text if x == ' '])
        if spacenum == 0 and len(text) <= 5:
            return True
        if len(text) > 5 and spacenum < 3 and spacenum / len(text) < 0.05 :
            return False
        return True
    def read_text(self, chars, index, fontname, fontsize, manual_add_space = False, word_distance = 1.5, max_buffer = 5):
        begin_index = index
        text = ''
        buffer_text = ''
        buffer_len = 0
        while index < len(chars):
            if chars[index]['fontname'] == fontname and self.equal(chars[index]['size'], fontsize):
                text += buffer_text
                buffer_text = ''
                buffer_len = 0
                if chars[index]['text'] != '-':
                    text += chars[index]['text']
                    if manual_add_space and index < len(chars) - 1:
                        if not self.equal(chars[index + 1]['y0'], chars[index]['y0']):
                            text += ' '
                        elif chars[index + 1]['x0'] - chars[index]['x1'] > word_distance:
                            text += ' '
                else:
                    if index < len(chars) - 1:
                        if self.equal(chars[index + 1]['y0'], chars[index]['y0']):
                            text += chars[index]['text']
                        else:
                            pass
                    else:
                        pass
            else:
                if buffer_len < max_buffer:
                    buffer_text += chars[index]['text']
                    buffer_len += 1
                break
            index += 1
        index -= (buffer_len - 1)
        if manual_add_space or self.check_space(text):
            return index, text
        else:
            return self.read_text(chars, begin_index, fontname, fontsize, manual_add_space = True)
    def parse(self, pdf_crop):
        index = 0

        while index < len(pdf_crop.chars):
            # print(index)
            fontname = pdf_crop.chars[index]['fontname']
            fontsize = pdf_crop.chars[index]['size']
            if fontname == self.main_font and self.equal(fontsize, self.main_size):
                new_index, text = self.read_text(pdf_crop.chars, index, fontname ,fontsize)
                self.main_text += ' ' + text
            else:
                new_index = index + 1

            index = new_index
def run(pdf_path, save_path):
    article = Article()
    try:
        pdf = pdfplumber.open(pdf_path)
    except Exception as e:
        print('[RunTime Error] ' + str(e))
        return
    for page in pdf.pages:
        article.count(page)
    article.get_main()
    for page in pdf.pages:
        article.parse(page)
    with open(os.path.join(save_path, pdf_path.split('\\')[-1].replace('.pdf', '_maintext.txt')) ,'w',
              encoding='utf-8', errors='ignore') as f:
        f.write(article.main_text)
    print(pdf_path.split('\\')[-1].replace('.pdf', '_maintext.txt') + 'saved in ' + save_path)
    return article.main_text

def batch2text(pdf_dir, save_path, batch_size = 16):
    file_list = os.listdir(pdf_dir)
    process_maxlen = batch_size
    process_list = []
    for pdf_file in  file_list:
        # 如果文件扩展名是PDF
        if pdf_file.endswith(".pdf"):
            if len(process_list) == process_maxlen:
                [p.start() for p in process_list]
                [p.join() for p in process_list]
                process_list = []
            process_list.append(Process(target=run, args=(os.path.join(pdf_dir,pdf_file), save_path)))
    if len(process_list) > 0:
        [p.start() for p in process_list]
        [p.join() for p in process_list]

def main():

    root_path = r'D:\Projects\PaperMill\论文工厂数据\wantdoi_pdf'
    save_path = r'D:\Projects\PaperMill\论文工厂数据\wantdoi_text'
    os.makedirs(save_path, exist_ok=True)
    batch2text(root_path, save_path)
if __name__ == '__main__':
    print(run(r'D:\Projects\PaperTool\test\download_部分4(1).pdf', r'D:\Projects\PaperTool\test'))
    exit(0)


    root_path = r'D:\Projects\PaperTool\test\2021'
    dir_list = os.listdir(root_path)
    for dir in dir_list:
        pdf_dir = os.path.join(root_path, dir)
        batch2text(pdf_dir, pdf_dir, 1)
    print(dir_list)
    # main()


