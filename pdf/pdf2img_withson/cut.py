import argparse
import os
import time
from pathlib import Path

import cv2
import math
import torch
import torch.backends.cudnn as cudnn
from numpy import random
from PIL import Image
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

WEIGHTS = '/root/子图分割训练/runs/train/paper-cut-large4/weights/best.pt'
IMG_SIZE = 1280
CONF_THRES = 0.5
IOU_THRES = 0.55
SAVE_TXT = True
SAVE_CONF = False
PROJECT = 'runs/detect'
NAME = 'exp'
DEVICE = '0'
AUGMENT = False
CLS_NAME = ['统计图', '条带图', '染色图', '示意图', '其他', '造影图', '实物图']

'''
切割论文子图
输入：jpg、jpeg、png单张图片的路径
输出：每个子图的坐标，输出样例见"API样例.txt"
'''

def calculate_overlap(box1, box2):
    """
    计算两个矩形的重叠面积
    """
    x_overlap = max(0, min(box1['xmax'], box2['xmax']) - max(box1['xmin'], box2['xmin']))
    y_overlap = max(0, min(box1['ymax'], box2['ymax']) - max(box1['ymin'], box2['ymin']))
    overlap_area = x_overlap * y_overlap
    return overlap_area

def process_objects(objects):
    """
    处理对象列表，保留重叠度小于90%的对象中score更高的那个
    """
    result_objects = []
    for i in range(len(objects)):
        keep_current = True
        for j in range(i+1, len(objects)):
            overlap = calculate_overlap(objects[i]['bndbox'], objects[j]['bndbox'])
            overlap_percentage1 = overlap / ((objects[i]['bndbox']['xmax'] - objects[i]['bndbox']['xmin']) * (objects[i]['bndbox']['ymax'] - objects[i]['bndbox']['ymin']))
            overlap_percentage2 = overlap / ((objects[j]['bndbox']['xmax'] - objects[j]['bndbox']['xmin']) * (objects[j]['bndbox']['ymax'] - objects[j]['bndbox']['ymin']))
            overlap_percentage = (overlap_percentage1 + overlap_percentage2) / 2.0
            if overlap_percentage >= 0.9:
                # 如果重叠度大于90%，去掉
                    keep_current = False
                    break
        if keep_current:
            result_objects.append(objects[i])
    return result_objects


def cut(file_path,model):
    extension = file_path.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        raise "Image must be jpg, jpeg or png format!"
    detect_labels = detect(model,file_path)
    detect_labels['object'] = process_objects(detect_labels['object'])
    return detect_labels

Image.MAX_IMAGE_PIXELS = 2800000000
LIMIT_SIZE = 36000000
def secure_open(source): 
    img = Image.open(source)
    width, height = img.size 
    divide_times = math.sqrt ((width * height) / LIMIT_SIZE)
    if divide_times > 1:
        new_width, new_height = int(width/divide_times), int(height/divide_times)
        img = img.resize((new_width, new_height))
        img.save(source)
    return img
    
def generate_subimg(file_path, cut_results, save_path):
    full_img = cv2.imread(file_path)
    count = 0
    for object in cut_results['object']:
        object_name = object['name']
        box = object['bndbox']
        img = full_img[int(box['ymin']):int(box['ymax']), int(box['xmin']):int(box['xmax'])]
        count += 1
        filename = file_path.split('/')[-1][:-4]
        cv2.imwrite(os.path.join(save_path ,f'{filename}_{count}_{object_name}.png' ) , img)

def add_label(detect_labels, line):
    width = detect_labels['size']['width']
    height = detect_labels['size']['height']
    cls = int(line[0].item ())
    x, y, w, h = line[1:5]
    xmin = width * (x - w / 2)
    xmax = width * (x + w / 2)
    ymin = height * (y - h / 2)
    ymax = height * (y + h / 2)
    detect_labels['object'].append({
        "name": CLS_NAME[cls],
        "bndbox": {
            "xmin": round(xmin, 2),
            "ymin": round(ymin, 2),
            "xmax": round(xmax, 2),
            "ymax": round(ymax, 2)
        }
    })

def detect(model,source:str,
           save_img=False):
    weights, view_img, save_txt, imgsz, trace = WEIGHTS, False, SAVE_TXT, IMG_SIZE, False
    # save_img = not source.endswith('.txt')  # save inference images
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))

    # Directories
    save_dir = Path(increment_path(Path(PROJECT) / NAME, exist_ok=False))  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Initialize
    set_logging()
    device = select_device(DEVICE)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model

    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size

    if trace:
        model = TracedModel(model, device, IMG_SIZE)

    # if half:
    #     model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    old_img_w = old_img_h = imgsz
    old_img_b = 1

    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Warmup
        if device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]
            for i in range(3):
                model(img, augment=AUGMENT)[0]

        # Inference
        t1 = time_synchronized()
        with torch.no_grad():   # Calculating gradients would cause a GPU memory leak
            pred = model(img, augment=AUGMENT)[0]
        t2 = time_synchronized()

        # Apply NMS
        pred = non_max_suppression(pred, CONF_THRES, IOU_THRES)
        t3 = time_synchronized()

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)
        
        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            
            source_image = secure_open(source)
            detect_labels = {   
                "object" : [] ,
                "size": {
                    "width": source_image.width,
                    "height": source_image.height,
                    "depth": 3,
            }}
            
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if SAVE_CONF else (cls, *xywh)  # label format
                        add_label(detect_labels, line)
                        # with open(txt_path + '.txt', 'a') as f:
                        #     f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or view_img:  # Add bbox to image
                        label = f'{names[int(cls)]} {conf:.2f}'
                        plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=2)

            # Print time (inference + NMS)
            print(f'{s}Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS')

            # Stream results
            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                    print(f" The image with the result is saved in: {save_path}")
                else:  # 'video' or 'stream'
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                            save_path += '.mp4'
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer.write(im0)

    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        #print(f"Results saved to {save_dir}{s}")

    print(f'Done. ({time.time() - t0:.3f}s)')
    return detect_labels


if __name__ == '__main__':
    WEIGHTS = '/root/pdf2img_withson/checkpoint/paper-cut-large-epoch100.pt'
    device = select_device('')
    model = attempt_load(WEIGHTS, map_location=device)  # load FP32 model
    half = device.type != 'cpu'
    model.half()
    result = cut(model=model, file_path='test_img.jpg')
    generate_subimg('test_img.jpg', result ,'./')
    print(result)