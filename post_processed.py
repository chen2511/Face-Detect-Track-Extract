from typing import Dict, List
import cv2
import numpy as np
from tqdm import tqdm

from my_utils import JsonUtils
 
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
    """
        TODO
    """
    pass

def get_frameinfo_from_json(jsonfile_name: str) -> Dict:
    """
        TODO 根据视频名字（json），返回这个处理这个视频后的信息。
    """
    return JsonUtils.load_json(jsonfile_name)

def judge_face_size(face = None, min_size : int = 40) -> bool:
    """
        TODO 判断人脸是否太小
    """
    pass

def judge_background(face = None) -> bool:
    """
        TODO 判断这个人脸是不是背景
            需要考虑计算量的问题
    """
    pass


def align_face(face = None): 
    """
        TODO 对齐人脸，变成正方形这种，这一部分可能需要问师兄具体的大小
    """
    pass

def judge_face_total_frames():
    """
        检查文件夹，太长的分开，太短的删除
    """


def process_single_video(video_path, json_path, output_dir):
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

        # 0、背景检测算法（全帧做）
        detect_background_4frame()

        # 获取帧id，当前帧人脸信息
        frame_id = frame_info["frame_id"]
        faces_info = frame_info["face_info"]

        for face in faces_info:
            image_dir = '%s/%s/' % (output_dir, face["face_id"])
            img_name = face["count"] + '.jpg'

            JsonUtils.mkdir(image_dir)
            # cropped = img[upper:lower, left:right]
            x1 = face["position"][0]
            y1 = face["position"][1]
            x2 = face["position"][2]
            y2 = face["position"][3]
            """
                注意：这里可能会越界，因为检测算法中已经 +- 了一个 margin，相当于放大了范围
                align_face 里面需要 做一下
            """


            # 1、当前人脸太小，可能可以跳过
            judge_face_size()

            # 2、背景检测算法，检测当前人脸是否为背景
            detect_background_4face()

            # 3、输出前准备：对齐（这里的输入图像可能不是正方形）
            align_face()

            # 4、输出人脸，保存结果：一个视频一个大文件夹，然后里面按ID分成不同文件夹
            
            
            cropped = frame[y1:y2, x1:x2]

            cv2.imwrite(image_dir + img_name, cropped)

        pbar.update(1)

    # end frames_info
    pbar.close()

    # 5、最后检查每个ID对应的人脸长度
    judge_face_total_frames()




if __name__ == "__main__":
    # process_single_video("input_videos/质量高_40s.mp4", "./output/json/质量高_40s.json", "./output/images/质量高_40s")
    process_single_video("input_videos/9-CAHxo8t-c.mp4", "./output/json/9-CAHxo8t-c.json", "./output/images/9-CAHxo8t-c")
