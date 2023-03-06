import os
from math import fabs
from tqdm import tqdm
import pdfplumber
import time

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
    def read_text(self, chars, index, fontname, fontsize, manual_add_space = False, word_distance = 1.5, max_buffer = 2):
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
def run(pdf_path):
    article = Article()
    pdf = pdfplumber.open(pdf_path)
    for page in pdf.pages:
        article.count(page)
    article.get_main()
    for page in pdf.pages:
        article.parse(page)
    return article.main_text

def main():
    # print(run(r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\pdf\10.1002@ar.24367.pdf'))
    # exit(0)
    root_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\mill_ref_pdf'
    save_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\normal_maintext'
    mill_list = os.listdir(root_path)
    for mill_doi in tqdm (mill_list):
        filelist = os.listdir(os.path.join(root_path, mill_doi))
        for ref_doi in filelist:
            if os.path.exists(os.path.join(os.path.join(root_path, mill_doi), ref_doi.replace('pdf', 'txt'))):
                continue
            pdf_path = os.path.join( os.path.join(root_path, mill_doi), ref_doi )
            if not os.path.exists(os.path.join(save_path, mill_doi)):
                os.makedirs(os.path.join(save_path, mill_doi))
            try:
                text = run(pdf_path)
                with open(os.path.join(os.path.join(save_path, mill_doi), ref_doi.replace('pdf', 'txt')), 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60 * 60)


