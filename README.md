# PaperTool


论文检索与信息提取工具

## 环境安装

`pip install requirements.txt`

## 爬虫相关（net/）


### scihub_getpdf.py - scihub下载pdf

**函数接口**: `def download(doi, save_path)`

```
输入：
doi：待爬取论文doi号
save_path：pdf保存路径
```

    返回：
    无

**开发进度**：

基本功能已实现，稳定性较低

**TODO**：

- [ ] 提高爬虫稳定性

### download_meta.py - 获取论文元数据

**函数接口**: 

- `def meta(doi)`：

  函数功能：单个doi元数据获取

  ```
  输入：
  doi：待爬取论文doi号
  ```

  ```
  返回：
  search_result, err
  search_result：opencitation搜索结果
  err：错误信息
  ```

- `def META(save_path)`：

  函数功能：批量doi元数据获取

  1、创建类META，指定save_path为元数据字典存储路径

  2、调用META.read(doi_list)，传入大量doi_list，自动批量爬取

  3、read完成后，自动在save_path存储元数据字典，并且函数返回该字典

**opencitation爬到的元数据包含以下信息**：

- doi：str 论文doi
- title : str 论文标题
- author : list[str] 作者姓名列表
- journal : str 期刊名
- publisher : str 出版社名
- pub_date : date 出版日期
- pub_type : str 出版类型

**开发进度**：

基本功能已实现，稳定性较低

**TODO**：

- [ ] 提高爬虫稳定性

### 爬取引用与施引

见`download_citepdf.py` 和 `download_refpdf.py`

---

## PDF解析相关（pdf/）

### pdf_text.py - pdf全文转文字

 函数接口: `def run(pdf_path, font_config = None)`

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
    可以使用pdfplumber自行查询需要解析文件的字体，在pdf/notebook/viewPDF.ipynb 查看示例
    
    font_config可以传入None，在这种情况下将不返回结构化文本，而是pdf中的所有文字。
    
    返回：
    文章结构化文本json文件

**开发进度**：

基本功能已实现，但font_config仍需人工提取

**TODO**：

- [ ] 自动化抽取font_config

### pdf_maintext.py - pdf正文转文字

**函数接口**: `def run(pdf_path)`

    输入：
    pdf_path: 原始pdf路径
    
    返回：
    pdf的正文文本。（注：这里的正文定义为“PDF中出现最多次数的字体，所对应文本内容”）

**参数细节**：

`read_text(self, chars, index, fontname, fontsize, manual_add_space = False, word_distance = 1.5, max_buffer = 5)`

```
manual_add_space ：是否手动添加空格？（在提取结果出现字符粘连时使用）
word_distance：在手动添加空格时，以字符间距离作为添加的条件
max_buffer：最多允许连续正文中出现几个字体或字号不同的字符（如公式、上下标等）
```

**开发进度**：

基本功能已实现

**TODO**：

- [ ] “PDF中出现最多次数的字体”有时候不是正文的字体，比如参考文献的字数比正文还多的情况

### pdf_abstract.py - pdf 摘要转文字

**函数接口**: `def run(pdf_path)`

    输入：
    pdf_path: 原始pdf路径
    
    返回：
    pdf的摘要文本。

**开发思路**：

摘要定义为：“Abstract”后的文本或“Introduction”前的文本

**TODO**：

- [ ] 部分情况下，摘要提取的不够精准

### pdf_title.py - pdf小标题转文字

**注意：此功能开发中，未完全实现**

思路：pdf小标题具有粗体、换行、上下间距大等规则，根据这些规则挖掘标题

**TODO**：

- [ ] 完善代码

### pdf_tabel.py - pdf表格提取

**注意：此代码只是pdfplumber原有功能的验证**

### pdf2img_withson - pdf论文图片与子图提取

在https://pan.quark.cn/s/dc107bbf826f下载`paper-cut-large-epoch100.pt`，放置到`checkpoint/`中

1. install

`pip install -r requirements.txt`


2. using

use api.py

- `main(data_path)`
- data_path means the path of pdf folder
