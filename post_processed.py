from multiprocessing.spawn import import_main_path
from typing import Dict, List
import cv2
import numpy as np
from tqdm import tqdm
import os
from PIL import Image

from my_utils import JsonUtils

def align_face(position: List, frame_width, frame_height, margin = 10): 
    """
        对齐人脸，防止越界，变成正方形
    """
    [x1, y1, x2, y2] = position

    # 0.收缩一点，因为原本有一个 margin的扩大
    # shink_size = margin 
    # x1 = max(x1 + shink_size, 0)
    # y1 = max(y1 + shink_size, 0)
    # x2 = min(x2 - shink_size, frame_width - 1)
    # y2 = min(y2 - shink_size, frame_height - 1)

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
    x1 = int(max(x1, 0))
    y1 = int(max(y1, 0))
    x2 = int(min(x2, frame_width - 1))
    y2 = int(min(y2, frame_height - 1))

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


def judge_face_total_frames(output_dir):
    """
        检查每个ID对应的人脸帧长度和帧大小
    """
    person_list = os.listdir(output_dir)
    person_nums = len(person_list)
    print("筛选文件夹：")
    pbar = tqdm(total=person_nums)
    
    
    for i in person_list: # 遍历视频文件夹 得到单人文件夹sub_dir
        sub_dir = os.path.join(output_dir, i)
        # print(sub_dir)
        if os.path.isdir(sub_dir): # 如果sub_dir是文件夹 遍历sub_dir 得到单张图片pic           
            for j in os.listdir(sub_dir):
                pic = os.path.join(sub_dir, j)
                if pic.split('.')[-1] == 'jpg': # 如果pic是图片 读取pic
                    img = Image.open(pic)
                    imgSize = img.size
                    img.close()
                    if imgSize[0] > 96 or imgSize[1] > 96:
                        # 图片进行resize操作
                        # img = Image.open(pic)
                        # resize_pic = img.resize((128,128), Image.ANTIALIAS)
                        # resize_pic.save(res)
                        # img.close()
                        # shutil.copyfile(pic,res) # 将pic移动到result文件夹
                        pass
                    else:
                        for file in os.listdir(sub_dir):
                            #进入下一个文件夹中进行删除
                            os.remove(os.path.join(sub_dir,file))
                        #如果是空文件夹，直接删除
                        os.rmdir(sub_dir)
                        # print(sub_dir,"文件夹删除成功")
                        break
        pbar.update(1)
    
    pbar.close()


def process_single_video(video_path, json_path, output_dir):
    JsonUtils.mkdir(output_dir)
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

            # 1、输出人脸，保存结果：一个视频一个大文件夹，然后里面按ID分成不同文件夹
            cropped = frame[y1:y2, x1:x2]

            cv2.imwrite(image_dir + img_name, cropped)

        pbar.update(1)

    # end frames_info
    pbar.close()

    # 2、最后检查每个ID对应的人脸帧大小；判断大小 96*96
    judge_face_total_frames(output_dir)




if __name__ == "__main__":
    process_single_video("input_videos/-6G6CZT7h4k.mp4", "./output/json/-6G6CZT7h4k.json", "./output/images/-6G6CZT7h4k")
    # process_single_video("input_videos/9-CAHxo8t-c.mp4", "./output/json/9-CAHxo8t-c.json", "./output/images/9-CAHxo8t-c")
