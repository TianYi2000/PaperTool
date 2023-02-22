import pdfplumber
from math import fabs

FONT_CONFIG = {
    'EURREV':{
        'FONT_SIZE' : {
            'chapter' : [11.4, 12],
            'section' : [9.4, 11],
            'maintext' : [9.4, 11, 11],
        },
        'FONT_NAME' : {
            'chapter' : ['ErasUltra', 'ErasDemi'],
            'section' : ['Frutiger-Black', 'ErasDemiItalic'],
            'maintext' : ['Helvetica-Bold', 'TimesNewRomanPSMT', 'TimesNewRomanPS-ItalicMT'],
        }
    },
    'Cellular_Biochemistry':{
        'FONT_SIZE' : {
            'chapter' : [10, 12, 10, 12, 10, 12],
            'section' : [],
            'maintext' : [10, 10, 10],
        },
        'FONT_NAME' : {
            'chapter' : ['AdvOT5d4a5f24.B', 'AdvOT5d4a5f24.B', 'AdvOTe3b1fbf3.B', 'AdvOTe3b1fbf3.B', 'STIX-Bold', 'STIX-Bold'],
            'section' : [],
            'maintext' : ['AdvOTee460ee4','AdvOTb0c9bf5d', 'STIX-Regular'],
        }
    },
    'ORIGINAL_RESEARCH_ARTICLE' :{
        'FONT_SIZE' : {
            'chapter' : [16, 16, 12 ,11],
            'section' : [12, 12, 12],
            'maintext' : [12, 12, 11, 11],
        },
        'FONT_NAME' : {
            'chapter' : ['TimesNewRomanPS-BoldMT', 'Times New Roman,Bold','TimesNewRomanPS-BoldMT', 'TimesNewRomanPS-BoldMT'],
            'section' : ['TimesNewRomanPS-BoldMT', 'Times New Roman,Bold', 'TimesNewRomanPS-BoldItalicMT'],
            'maintext' : ['TimesNewRomanPSMT', 'Times New Roman', 'TimesNewRomanPSMT', 'TimesNewRomanPS-BoldMT'],
        }
    }
}
class Section:
    def __init__(self, name):
        self.name = name
        while len(self.name) > 0 and self.name[0] in ['–', ' ', '.', ':']:
             self.name = self.name[1:]
        while len(self.name) > 0 and self.name[-1]in ['–', ' ', '.', ':']:
             self.name = self.name[:-1]
        self.text = ''
    def add_text(self, text):
        self.text += text
    def print_text(self):
        if self.text != ' ':
            print('###', self.name)
            print(self.text)
    def to_json(self):
        dict = {}
        if self.text != ' ':
            dict['name'] = self.name
            dict['text'] = self.text
            return dict
        else:
            return None

class Chapter:
    def __init__(self, name):
        self.name = name

        while len(self.name) > 0 and self.name[0] in ['–', ' ', '.', ':']:
             self.name = self.name[1:]
        while len(self.name) > 0 and self.name[-1] in ['–', ' ', '.', ':']:
             self.name = self.name[:-1]
        self.sections = []
    def get_cursec(self):
        if len(self.sections) == 0:
            self.sections.append(Section('Head Section'))
        return self.sections[-1]
    def add_sec(self, name):
        self.sections.append(Section(name))
    def print_sections(self):
        sections = self.sections
        print('##', self.name)
        # print('   All Sections', [x.name for x in sections])
        for index, section in enumerate(sections):
            section.print_text()
    def to_json(self):
        dict = {}
        sections = self.sections
        dict['name'] = self.name
        dict['section_num'] = len(sections)
        dict['sections'] = []
        for index, section in enumerate(sections):
            section_dict = section.to_json()
            if section_dict:
                dict['sections'].append(section_dict)
        return dict

    def convert2sec(self):
        if len(self.sections) == 0 or len(self.sections) > 1 or self.sections[0].name != 'Head Section':
            raise Exception(f"Chapter {self.name} cannot conver to section!")
        newsec = Section(self.name)
        newsec.add_text(self.sections[0].text)
        return newsec

class Article:
    def __init__(self, name, journal):
        self.name = name
        self.journal = journal
        self.chapters = []
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
    def judge(self, char):
        # FONT_SIZE ={
        #     'chapter' : [12, 11.4, 11.4, 12],
        #     'section' : [11, 9.4, 9.4, 11.0],
        #     'maintext' : [11, 11, 9.4, 9.4, 11],
        # }
        # FONT_NAME ={
        #     'chapter' : ['OFALOU+ErasDemi', 'OFALOU+ErasUltra', 'QKTRPQ+ErasUltra', 'QKTRPQ+ErasDemi'],
        #     'section' : ['OFALOU+ErasDemiItalic', 'OFALOU+Frutiger-Black', 'QKTRPQ+Frutiger-Black', 'QKTRPQ+ErasDemiItalic'],
        #     'maintext' : ['OFALOU+TimesNewRomanPSMT', 'OFALOU+TimesNewRomanPS-ItalicMT', 'OFALOU+Helvetica-Bold', 'QKTRPQ+Helvetica-Bold', 'QKTRPQ+TimesNewRomanPSMT'],
        # }
        FONT_SIZE = FONT_CONFIG[self.journal]['FONT_SIZE']
        FONT_NAME = FONT_CONFIG[self.journal]['FONT_NAME']
        fontname = char['fontname']
        fontsize = char['size']
        for type_name in ['chapter', 'section', 'maintext']:
            namelist = FONT_NAME[type_name]
            sizelist = FONT_SIZE[type_name]
            for i in range(len(namelist)):
                if  namelist[i] in fontname and self.equal(fontsize, sizelist[i]):
                    return type_name
        return 'none'
    def parse(self, pdf_crop):
        index = 0
        while index < len(pdf_crop.chars):
            char = pdf_crop.chars[index]
            type_name = self.judge(char)
            if type_name == 'chapter':
                index, text = self.read_text(pdf_crop.chars, index, char['fontname'] ,char['size'])
                self.add_chap(text)
            elif type_name == 'section':
                index, text = self.read_text(pdf_crop.chars, index, char['fontname'] ,char['size'])
                self.add_sec(text)
            elif type_name ==  'maintext':
                index, text = self.read_text(pdf_crop.chars, index, char['fontname'] ,char['size'])
                self.add_text(text)
            else:
                index += 1
    def get_curchap(self):
        if len(self.chapters) == 0:
            self.chapters.append(Chapter('Head Chapter'))
        return self.chapters[-1]
    def add_chap(self, name):
        self.chapters.append(Chapter(name))
    def add_sec(self, text):
        chap = self.get_curchap()
        sec = chap.add_sec(text)
    def add_text(self, text):
        chap = self.get_curchap()
        sec = chap.get_cursec()
        sec.add_text(text)
    def print_chapters(self):
        chapters = self.chapters
        print('#', self.name)
        # print('# All Chapters', [x.name for x in chapters])
        for index, chapter in enumerate(chapters):
            chapter.print_sections()
    def to_json(self, filter = True):
        dict = {}
        chapters = self.chapters
        dict['chapters'] = []
        for index, chapter in enumerate(chapters):
            dict['chapters'].append(chapter.to_json())
        dict['chapter_num'] = len(dict['chapters'])
        return dict
    def raw(self, pdf_crop, manual_add_space = True, word_distance = 1.5):
        index = 0
        chars = pdf_crop.chars
        text = ''
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
        self.add_text(text)

def run(pdf_path, font_config = None):
    pdf = pdfplumber.open(pdf_path)
    FONT_CONFIG['current'] = font_config
    article = Article('title', 'current')
    for page in pdf.pages:
        if font_config is None:
            article.raw(page)
        else:
            article.parse(page)
    return article.to_json()
if __name__ == '__main__':
    print(run('D:\\Projects\\PaperTool\\test.pdf'))
