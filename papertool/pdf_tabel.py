import os
from math import fabs
from tqdm import tqdm
import pdfplumber
import time

class Table:
    def __init__(self):
        self.tables = []

    def extract(self, page):
        tables = page.extract_table()
        if tables != None:
            print(tables)
            self.tables += tables

def run(pdf_path):
    pdf_tabel = Table()
    pdf = pdfplumber.open(pdf_path)
    for page in pdf.pages:
        pdf_tabel.extract(page)
    return pdf_tabel.tables


if __name__ == '__main__':
    print(run(r'D:\Projects\PaperTool\10.2147@ott.s228637.pdf'))


