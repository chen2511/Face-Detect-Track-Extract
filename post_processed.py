from multiprocessing.spawn import import_main_path
from typing import Dict, List
import cv2
import numpy as np
from tqdm import tqdm
import os
from PIL import Image
import shutil

from my_utils import JsonUtils

def align_face(position: List, frame_width, frame_height, margin = 10): 
    """
        对齐人脸，防止越界，变成正方形
    """
    [x1, y1, x2, y2] = position

    # 0.收缩一点，因为原本有一个 margin的扩大
    shink_size = margin 
    x1 = max(x1 + shink_size, 0)
    y1 = max(y1 + shink_size, 0)
    x2 = min(x2 - shink_size, frame_width - 1)
    y2 = min(y2 - shink_size, frame_height - 1)

    # 1.正式计算
    face_width = x2 - x1
    face_height = y2 - y1
    max_edge = max(face_height, face_width)

    x_padding = max_edge - face_width
    y_padding = max_edge - face_height

    # 先直接强行补成正方形
    x1 -= x_padding // 2
    y1 -= y_padding // 2
    x2 = x1 + max_edge
    y2 = y1 + max_edge

    # 2.然后越界就平移回来
    # 只考虑x的一边越界，不考虑两边都越界
    if(x1 < 0):
        x2 = x2 - x1
        x1 = 0
    elif(x2 >= frame_width):
        x1 = x1 - (x2 - frame_width + 1)
        x2 = frame_width - 1

    if(y1 < 0):
        y2 = y2 - y1
        y1 = 0
    elif(y2 >= frame_height):
        y1 = y1 - (y2 - frame_height + 1)
        y2 = frame_height - 1

    assert x2 - x1 == y2 - y1, "仍然不为正方形"
    # 部分人脸占整个屏幕的
    x1 = max(x1, 0)
    y1 = max(y1, 0)
    x2 = min(x2, frame_width - 1)
    y2 = min(y2, frame_height - 1)

    return x1, y1, x2, y2
 
def detect_background_4frame():
    """
        Test
    """
    return 
    #读入图像
    video = cv2.VideoCapture("E:\\BaiduNetdiskDownload\\无用\\4CRKa9OoynE.mp4")
    videoIsOpen=video.isOpened
    print(videoIsOpen)
    width=int(video.get(cv2.CAP_PROP_FRAME_WIDTH))#宽度
    height=int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))#高度
    fps=video.get(cv2.CAP_PROP_FPS)#获取帧率
    print(fps,width,height)
    #创建窗口
    cv2.namedWindow('MOG2')
    # cv2.namedWindow('MOG22')
    cv2.namedWindow('input video')
    # cv2.namedWindow('KNN')
    bsmaskMOG2 = np.zeros([height,width],np.uint8)
    bsmaskKnn = np.zeros([height,width],np.uint8)
    #两种消除的方案
    pMOG2 = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    # PKNN = cv2.createBackgroundSubtractorKNN(detectShadows=True)
    #形态学处理
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3))
    
    while videoIsOpen:
        (flag,frame)=video.read()
        if not flag:
            break
        cv2.imshow('input video',frame)
        # bsmaskKnn= PKNN.apply(frame)
        # cv2.imshow('KNN',bsmaskKnn)
        bsmaskMOG2 = pMOG2.apply(frame)
        # cv2.imshow('MOG22',bsmaskMOG2)
        OPEND=cv2.morphologyEx(bsmaskMOG2,cv2.MORPH_OPEN,kernel)
        cv2.imshow('MOG2',OPEND)
        
        c = cv2.waitKey(40)
        if c==27:
            break
    video.release()
    
    cv2.waitKey(0)

def detect_background_4face():
    pass

def get_frameinfo_from_json(jsonfile_name: str) -> Dict:
    """
        根据视频名字（json），返回这个处理这个视频后的信息。
    """
    return JsonUtils.load_json(jsonfile_name)

def judge_face_size(face = None, min_size : int = 40) -> bool:
    """
        判断人脸是否太小
    """
    pass

def judge_face_total_frames(output_dir, result_dir):
    """
        检查每个ID对应的人脸帧长度和帧大小
    """
# 选取大小合适的图片 移动到result文件夹
    if os.path.exists(result_dir):
        pass
    else:
        os.makedirs(result_dir)
    
    for i in os.listdir(output_dir): # 遍历视频文件夹 得到单人文件夹sub_dir
        sub_dir = os.path.join(output_dir, i)
        # print(sub_dir)
        if os.path.isdir(sub_dir): # 如果sub_dir是文件夹 遍历sub_dir 得到单张图片pic
            res_dir = os.path.join(result_dir, i)
            if os.path.exists(res_dir):
                pass
            else:
                os.makedirs(res_dir)
            
            for j in os.listdir(sub_dir):
                pic = os.path.join(sub_dir, j)
                res = os.path.join(res_dir, j)
                if pic.split('.')[-1] == 'jpg': # 如果pic是图片 读取pic
                    # print(pic)
                    img = Image.open(pic)
                    imgSize = img.size
                    img.close()
                    # print(imgSize)
                    if imgSize[0] > 96 or imgSize[1] > 96:
                        # 图片进行resize操作
                        img = Image.open(pic)
                        resize_pic = img.resize((128,128), Image.ANTIALIAS)
                        resize_pic.save(res)
                        img.close()
                        # shutil.copyfile(pic,res) # 将pic移动到result文件夹
                    else:
                        # os.remove(pic) # 删除文件
                        pass

# 判断文件夹大小 分割大文件夹
    for k in os.listdir(result_dir):
        check_dir = os.path.join(result_dir, k)
        # print(check_dir)
        num = len(os.listdir(check_dir))
        # print(k)
        # print(num)
        if num <= 50:
            for file in os.listdir(check_dir):
                #进入下一个文件夹中进行删除
                os.remove(os.path.join(check_dir,file))
            #如果是空文件夹，直接删除
            os.rmdir(check_dir)
            # print(check_dir,"文件数",num,"删除成功")

        t = 0
        while num > 200: # 如果文件夹中图片数量超过200 将其分割
            # print(k)
            k_split = k+'_'+str(t)
            # print(k_split)
            mv_dir = os.path.join(result_dir, k_split)
            if os.path.exists(mv_dir):
                pass
            else:
                os.makedirs(mv_dir)

            # '''
            # test
            # '''
            # for root, dirs, files in os.walk(check_dir):
            #     files.sort()
            #     print(111)

            cnt = 0
            for pics in sorted(os.listdir(check_dir)):
                pic = os.path.join(check_dir, pics)
                mv_pic = os.path.join(mv_dir, pics)
                shutil.move(pic, mv_pic)
                cnt += 1
                if cnt >= 200:
                    break
            num = len(os.listdir(check_dir))
            t = t+1
        
        if t != 0:
            os.rename(check_dir, os.path.join(result_dir, k+'_'+str(t)))


def process_single_video(video_path, json_path, output_dir, result_dir):
    # 读取 json 数据
    json_data = get_frameinfo_from_json(json_path)
    capture = cv2.VideoCapture(video_path)
    pbar = tqdm(total=json_data["total_frame"])

    frame_width = json_data["frame_size"][0]
    frame_height = json_data["frame_size"][1]

    frames_info = json_data["frames"] 

    for frame_info in frames_info:   # 逐帧分析
        # 读取视频
        ret, frame = capture.read()
        if not ret:
            pbar.close()
            break

        if frame is None:
            break

        # 0、背景检测算法（全帧做）   = 不做
        # detect_background_4frame()

        # 获取帧id，当前帧人脸信息
        frame_id = frame_info["frame_id"]
        faces_info = frame_info["face_info"]

        for face in faces_info:
            # 输出文件路径， 视频名字/人脸ID/帧序号.jpg
            image_dir = '%s/%s/' % (output_dir, face["face_id"])
            img_name = face["count"] + '.jpg'
            JsonUtils.mkdir(image_dir)

            x1 = face["position"][0]
            y1 = face["position"][1]
            x2 = face["position"][2]
            y2 = face["position"][3]
            # 0、背景检测算法，检测当前人脸是否为背景 = 不做
            # detect_background_4face()

            # x1, y1, x2, y2 = align_face([x1, y1, x2, y2], frame_width, frame_height)

            # 1、输出人脸，保存结果：一个视频一个大文件夹，然后里面按ID分成不同文件夹
            cropped = frame[y1:y2, x1:x2]

            cv2.imwrite(image_dir + img_name, cropped)

        pbar.update(1)

    # end frames_info
    pbar.close()

    # 2、最后检查每个ID对应的人脸帧长度和帧大小；1、先删除少的，分开多的 2、判断大小 96*96（太小的删除整个id的人脸，大的 resize）
    # TODO 2
    judge_face_total_frames(output_dir, result_dir)




if __name__ == "__main__":
    process_single_video("input_videos/质量高_40s.mp4", "./output/json/质量高_40s.json", "./output/images/质量高_40s","./output/results/质量高_40s")
    # process_single_video("input_videos/9-CAHxo8t-c.mp4", "./output/json/9-CAHxo8t-c.json", "./output/images/9-CAHxo8t-c","./output/results/质量高_40s")
