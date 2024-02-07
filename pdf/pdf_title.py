import os
from math import fabs
from tqdm import tqdm
import pdfplumber

class Article:
    def __init__(self):
        self.font_set = {}
        self.titles = []

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
                index += 1
                continue
            new_index, text = self.read_text(pdf_crop.chars, index, fontname ,fontsize)

            if index == 0:
                if not self.equal(pdf_crop.chars[new_index]['y0'], pdf_crop.chars[new_index - 2]['y0']) and \
                    (self.equal(pdf_crop.chars[new_index]['size'], self.main_size) and pdf_crop.chars[new_index]['fontname'] == self.main_font) and \
                    fontsize + 0.001 >= self.main_size:
                        self.titles.append(text)
                index = new_index
                continue
            if new_index >= len(pdf_crop.chars):
                if not self.equal(pdf_crop.chars[index]['y0'], pdf_crop.chars[index - 2]['y0']) and \
                        (self.equal(pdf_crop.chars[index - 2]['size'], self.main_size) and pdf_crop.chars[index - 2]['fontname'] == self.main_font) and \
                        fontsize + 0.001 >= self.main_size:
                    self.titles.append(text)
                index = new_index
                continue
            if not self.equal(pdf_crop.chars[index]['y0'], pdf_crop.chars[index - 2]['y0']) or \
                        not self.equal(pdf_crop.chars[new_index]['y0'], pdf_crop.chars[new_index - 2]['y0']) and \
                        (self.equal(pdf_crop.chars[index - 2]['size'], self.main_size) and pdf_crop.chars[index - 1]['fontname'] == self.main_font or
                         self.equal(pdf_crop.chars[new_index]['size'], self.main_size) and pdf_crop.chars[new_index]['fontname'] == self.main_font) and \
                        fontsize + 0.001 >= self.main_size:
                self.titles.append(text)
            index = new_index
def run(pdf_path):
    article = Article()
    pdf = pdfplumber.open(pdf_path)
    for page in tqdm(pdf.pages):
        article.count(page)
    article.get_main()
    for page in tqdm(pdf.pages):
        article.parse(page)
    return article.titles

if __name__ == '__main__':
    print(run(r'D:\Projects\PaperTool\test\download_部分4(1).pdf'))
    exit(0)
    root_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\pdf'
    save_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\titles'
    filelist = os.listdir(root_path)
    for filename in tqdm (filelist):
        pdf_path = os.path.join(root_path, filename)
        titles = run(pdf_path)
        with open(os.path.join(save_path, filename.replace('pdf', 'txt')), 'w', encoding='utf-8') as f:
            f.write('\n'.join(titles))





