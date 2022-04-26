from typing_extensions import Self
import warnings
import cv2
import numpy as np
# warnings.filterwarnings("ignore")
import json
import os


"""
@create_time: 2022-04-24 16:39:37

视频另存工具
"""

class VideoWriterUtil:
    '''
        @description: 写视频的工具类，两个方法，写入和关闭文件
    '''
    def __init__(self, name, width, height, fps=25):
        # type: (str, int, int, int) -> None
        if not name.endswith('.mp4'):  # 保证文件名的后缀是.mp4
            name += '.mp4'
            warnings.warn('video name should ends with ".avi"')
        self.__name = name          # 文件名
        self.__height = height      # 高
        self.__width = width        # 宽
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # 如果是avi视频，编码需要为MJPG

        self.__writer = cv2.VideoWriter(name, fourcc, fps, (int(width), int(height)))

    def write(self, frame):
        if frame.dtype != np.uint8:  # 检查frame的类型
            raise ValueError('frame.dtype should be np.uint8')
        # 检查frame的大小
        row, col, _ = frame.shape
        if row != self.__height or col != self.__width:
            warnings.warn('长和宽不等于创建视频写入时的设置，此frame不会被写入视频')
            return
        self.__writer.write(frame)

    def close(self):
        self.__writer.release()


def create_videoWriter(capture, new_name: str) -> VideoWriterUtil:
    """
        构建视频写入工具，如果 capture 未打开，那么返回 None
        @capture:   cv2.VideoCapture 返回值
        @new_name:  新视频的文件名
        @return:    VideoWriterUtil
    """
    if capture.isOpened():                                  # VideoCaputre对象是否成功打开
        fps = capture.get(cv2.CAP_PROP_FPS)                 # 返回视频的fps--帧率
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)       # 返回视频的宽
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)     # 返回视频的高
        print('>>> 原始视频信息：', 'fps:', fps,'width:', width,'height:', height)

        return VideoWriterUtil(new_name, width, height, fps), width, height
    
    return None


class JsonUtils:
    def __init__(self, video_name: str, capture: cv2.VideoCapture, output_dir: str) -> None:
        if capture == None:
            return
            
        self.content = {
            "video_name": video_name,
            "total_frame": int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
            "frame_size": [int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                            int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))],
            "fps": capture.get(cv2.CAP_PROP_FPS),
            "total_faces": 0,
            "frames": []
        }
        # 记录人脸ID首次出现的帧数，从 0 开始计数
        self.face_occurrence_map = {}

        self.save_root_path = output_dir
        self.save_json_name = output_dir + video_name[:-4] + '.json'

    def append_frame_content(self, current_frame: dict):
        self.content["frames"].append(current_frame)

    def get_count_4_faceID(self, current_frame: int, faceID: str) -> int:
        """
            从这个人脸ID出现开始，现在已经出现了多少帧
        """
        if faceID in self.face_occurrence_map:
            return current_frame - self.face_occurrence_map[faceID]
        else:
            self.face_occurrence_map[faceID] = current_frame
            self.content["total_faces"] += 1
            return 0

    def close(self):
        JsonUtils.mkdir(self.save_root_path)
        JsonUtils.save_json(self.content, self.save_json_name)


    # 新建文件夹
    @staticmethod
    def mkdir(path: str) -> None:
        path.strip()
        path.rstrip('\\')
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)

    # 读取json文件到字典
    @staticmethod
    def load_json(filename: str) -> dict:
        file = open(filename, 'r', encoding='UTF-8')
        js = file.read()
        file.close()

        dic = json.loads(js)
        return dic

    # 从字典到json
    @staticmethod
    def save_json(data: dict, filename: str) -> None:
        js_content = json.dumps(data, ensure_ascii=False, indent=4, sort_keys=False)
        file = open(filename, 'w', encoding='UTF-8')
        file.write(js_content)
        file.close()


if __name__=="__main__":
    """
        测试使用方法
    """
    cam=cv2.VideoCapture('./20211111-2160-16s.mp4')

    if cam.isOpened():                                  # VideoCaputre对象是否成功打开
        fps = cam.get(cv2.CAP_PROP_FPS)                 # 返回视频的fps--帧率
        width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)       # 返回视频的宽
        height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)     # 返回视频的高
        print('fps:', fps,'width:',width,'height:',height)

        vw = VideoWriterUtil('./20211111-2160-16s-finished-count.mp4', width, height, fps)

        while(True):
            # 读取一帧视频
            readStatus, frame = cam.read()  
            frame_count = 0

            if(not readStatus):     # 视频读取完毕
                print('视频已处理完成')
                if vw != None:
                    vw.close()
                break
            else:                   # 视频还未处理完
                vw.write(frame)         
                frame_count += 1