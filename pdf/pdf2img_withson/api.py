from cut import cut, generate_subimg
from pdf2img import pdf2pic
from models.experimental import attempt_load
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel
import os, sys, json, shutil
import shutil
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def load_yolo(model_path):
    
    device = select_device('0')
    model = attempt_load(model_path, map_location=device)
    half = device.type != 'cpu'
    if half:
        model.half()
    return model

err_pdf = []
def resume(data_path):
    # 读取错误日志 清除错误输出结果 重新解析
    try:
        with open (os.path.join(data_path, 'err.log' ),'r') as f:
            err_pdfs = f.readlines()
        for file_path in err_pdfs:
            file_path = file_path.strip('\n')
            if os.path.exists(file_path):
                try:
                    shutil.rmtree(file_path[:-4])
                except Exception as e:
                    pass
    except Exception as e:
        pass
    
    # 读取已处理PDF目录 跳过解析
    pdf_list = os.listdir(data_path)
    test_list = []
    for filename in pdf_list:
        if filename[-4:] == '.pdf':
            sub_img_path = os.path.join(os.path.join(data_path, filename[:-4]), 'sub_img')
            sub_json_path = os.path.join(os.path.join(data_path, filename[:-4]), 'subimg_json')
            try:
                subimgs = os.listdir(sub_img_path)
                _ = subimgs[1]
            except Exception as e:
                try:
                    sub_jsons = os.listdir(sub_json_path)
                    _ = sub_jsons[1]
                except Exception as e:
                    test_list.append(filename)    
    return test_list
def movefile(oripath,tardir):
    filename = os.path.basename(oripath)
    tarpath = os.path.join(tardir, filename)
    #判断原始文件路劲是否存在
    if not os.path.exists(oripath):
        print('the dir is not exist:%s' % oripath)
        status = 0
    else:
     #判断目标文件夹是否存在
        if os.path.exists(tardir):
        #判断目标文件夹里原始文件是否存在，存在则删除
            if os.path.exists(tarpath):
                os.remove(tarpath)
        else:
         #目标文件夹不存在则创建目标文件夹
            os.makedirs(tardir)
          #移动文件
        shutil.move(oripath, tardir)

        status = 1
    return status
def single_pdf(pdf_path, require_json, require_subimg):
    WEIGHTS = './checkpoint/paper-cut-large-epoch100.pt'
    pic_path = pdf_path[:-4]
    pic_path = pic_path.replace("data","new_data")
    full_path = os.path.join(pic_path, 'full_img')
    sub_path = os.path.join(pic_path, 'sub_img')
    json_path = os.path.join(pic_path, 'subimg_json')
    os.makedirs(full_path, exist_ok=True)
    os.makedirs(sub_path, exist_ok=True)
    os.makedirs(json_path, exist_ok=True)
    print(f'开始解析 {pdf_path} ...')
    try:
        with HiddenPrints():
            pdf2pic(pdf_path, pic_path)
    except Exception as e:
        print(f'{pdf_path}解析失败，原因：{e}')
        err_pdf.append(pdf_path)
    pic_list = os.listdir(full_path)
    pic_list = sorted(pic_list)
    print(f'解析结束，共提取 {len(pic_list)} 张图片，保存在 "{full_path}" ')
    print(f'开始加载子图分割模型 "{WEIGHTS}" ...')
    model = load_yolo(WEIGHTS)
    print(f'加载子图分割模型结束')
    for index, pic_name in enumerate (pic_list):
        print(f'开始分割第 {index+1} 张图片...')
        pic_file = os.path.join(full_path, pic_name)
        try:
            subpic_result = cut(file_path=pic_file, model=model)
        except Exception as e:
            print(f'第 {index+1} 张图片 {pic_file} 切图失败，原因：{e}')
            if pdf_path not in err_pdf:
                err_pdf.append(pdf_path)
        #1. 保存json
        if require_json:
            with open (os.path.join(json_path, f'subimg_{index+1}.json'), 'w', encoding='utf-8') as f:
                json.dump(subpic_result, f, ensure_ascii=False)
        #2. 生成子图像
        if require_subimg:
            generate_subimg(pic_file, subpic_result, sub_path )
    sub_pic_list = os.listdir(sub_path)
    print(f'子图分割结束，共提取 {len(sub_pic_list)} 张图片，保存在 "{sub_path}" ')
    print(f'{pdf_path} 完成解析！')
    movefile(pdf_path,"./new_pdf")
    #以下是对pdf文件进行剪切
    #把处理完之后把pdf剪切到另一个文件夹
    #把full_img , sub_img , subimg_json 也放到另一个文件夹里面
def main(data_path = './data/', require_json = True, require_subimg = True):
    '''
    data_path : PDF存放路径
    require_json : 是否生成子图标签的json文件
    require_subimg : 是否生成子图的图片文件
    '''
    test_list = resume(data_path)
    for filename in test_list:
        if filename[-4:] == '.pdf':
            single_pdf(os.path.join(data_path, filename), require_json, require_subimg)
        with open (data_path + 'err.log', 'w') as f:
            for name in err_pdf:
                f.write(name + '\n')

if __name__ == '__main__':
    main()
