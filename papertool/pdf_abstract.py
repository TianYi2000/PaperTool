import os

import pdfplumber
from math import fabs

from tqdm import tqdm


class Article:
    def __init__(self, name, journal):
        self.name = name
        self.journal = journal
        self.chapters = []
        self.stop = False
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
    def read_text(self, chars, index, fontname, fontsize, manual_add_space = True, word_distance = 1.5, max_buffer = 15):
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
                else:
                    break
            index += 1
        index -= (buffer_len - 1)
        if manual_add_space or self.check_space(text):
            return text
        else:
            return self.read_text(chars, begin_index, fontname, fontsize, manual_add_space = True)

    def raw_abstract(self, pdf_crop, manual_add_space = True, word_distance = 1.5):
        if self.stop:
            return
        index = 0
        chars = pdf_crop.chars
        text = ''
        all_text = ''.join([x['text'] for x in chars])
        while index < len(chars):
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
            index += 1
        name = ['Abstract' , 'ABSTRACT']
        for n in name:
            if n in text:
                pos = all_text.index(n)
                start_pos = pos + 8
                prase_text = self.read_text(pdf_crop.chars, start_pos,  pdf_crop.chars[start_pos]['fontname'] ,pdf_crop.chars[start_pos]['size'])
                raw_text = ' '.join(text[start_pos : ].split(' ')[:510])
                if len(prase_text.split(' ')) < 100:
                    return raw_text
                return prase_text
        name = ['INTRODUCTION' , 'Introduction']
        for n in name:
            if n in text:
                pos = text.index(n)
                # prase_text = self.read_text(pdf_crop.chars, start_pos,  pdf_crop.chars[start_pos]['fontname'] ,pdf_crop.chars[start_pos]['size'])
                word_list = text[ : pos].split(' ')
                start_word = max (0, len(word_list) - 510)
                raw_text = ' '.join(word_list[start_word : ])
                # if len(prase_text.split(' ')) < 100:
                #     return raw_text
                return raw_text
        return None
'''
    pdf转文字
    
    输入：
    pdf_path: 原始pdf路径
    font_config: 论文中三级结构（一级标题、二级标题、正文）的字体信息，json文件
    - 示例
        {
            'FONT_SIZE' : {
                'chapter' : [12],
                'section' : [11],
                'maintext' : [11, 11],
            },
            'FONT_NAME' : {
                'chapter' : ['ErasUltra'],
                'section' : ['Frutiger-Black'],
                'maintext' : ['Helvetica-Bold', 'TimesNewRomanPS-ItalicMT'],
            }
        }
    FONT_SIZE为字号，FONT_NAME为字体名称，'chapter'为一级标题、'section'为二级标题、'maintext'正文，所有可能出现的字号字体以列表形式传入
    注意：FONT_SIZE与FONT_NAME中任一结构的字体列表，字体名称与字号要一一对应
    可以使用pdfplumber自行查询需要解析文件的字体
    font_config可以传入None，在这种情况下将不返回结构化文本，而是pdf中的所有文字。
    
    返回：
    文章结构化文本json文件
'''



def run(pdf_path):
    pdf = pdfplumber.open(pdf_path)
    article = Article('title', 'current')
    for page in pdf.pages:
        abstrct = article.raw_abstract(page)
        if abstrct != None:
            return abstrct
    return None

def main_normal():
    # print(run(r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\pdf\10.1002@ar.24367.pdf'))
    # exit(0)
    root_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\new_normal_pdf'
    save_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\new_normal_abstract'
    os.makedirs(save_path, exist_ok=True)
    mill_list = os.listdir(root_path)
    for normal_doi in tqdm (mill_list):
        pdf_path = os.path.join(root_path, normal_doi)
        try:
            text = run(pdf_path)
            if text is None:
                raise Exception('None')
            with open(os.path.join(save_path, normal_doi.replace('pdf', 'txt')), 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(normal_doi, e)
def main_mill():
    # print(run(r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\pdf\10.1002@ar.24367.pdf'))
    # exit(0)
    root_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\pdf'
    save_path = r'D:\Projects\PaperMill\论文工厂数据\论文工厂数据1\mill_abstract'
    os.makedirs(save_path, exist_ok=True)
    mill_list = os.listdir(root_path)
    for mill_doi in tqdm (mill_list):
        pdf_path = os.path.join(root_path, mill_doi)
        try:
            text = run(pdf_path)
            if text is None:
                raise Exception('None')
            with open(os.path.join(save_path, mill_doi.replace('pdf', 'txt')), 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(mill_doi, e)
if __name__ == '__main__':
    # print(run(r'D:\Projects\PaperTool\test.pdf'))
    main_normal()
