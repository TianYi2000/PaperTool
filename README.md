# PaperTool
 论文检索与信息提取工具

## 环境安装

`pip install requirements.txt`


## translate.py - 英文转中文
函数接口: `def eng2chn(query)`
    输入：
    query: 英文字符串
    
    返回：
    翻译中文字符串

## pdf_text.py - pdf转文字
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
    可以使用pdfplumber自行查询需要解析文件的字体
    font_config可以传入None，在这种情况下将不返回结构化文本，而是pdf中的所有文字。
    
    返回：
    文章结构化文本json文件

## pdf_img.py pdf转img
函数接口: `def run(pdf_path,img_path)`

    输入：
    pdf_path: 原始pdf路径
    img_path: 输出图片路径，需要确保路径为空
    
    无返回