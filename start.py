import argparse
import os
from time import time
from time import sleep
from typing import List
from tqdm import tqdm

import detect_align.detect_face as detect_face
import cv2
import numpy as np
from tracker.kalman_tracker import KalmanBoxTracker

import post_processed as pProcess
"""
注意：为了输出简洁。这里实际上过滤了一些低级的 警告信息，如果出bug，注释这里
"""
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 不显示等级2以下的提示信息
import tensorflow as tf
from lib.face_utils import judge_side_face
from lib.utils import Logger, mkdir
from project_root_dir import project_dir
from tracker.sort import Sort
import my_utils
import warnings
warnings.simplefilter("ignore")

logger = Logger()

def main():
    global colours, img_size
    args = parse_args()
    videos_dir = args.videos_dir
    base_output_path = args.output_path
    no_display = args.no_display
    detect_interval = args.detect_interval          # 间隔多少帧检测一次人脸
    margin = args.margin                            # 人脸的间隔，作者提示：如果视频中的人脸很大，可以将其设置得更大，以便更容易跟踪
    scale_rate = args.scale_rate                    # 如果设置得更小，则会使输入帧更小， 具体来说：cv2.resize 进行缩放 x，y分别缩放
    show_rate = args.show_rate                      # 如果将其设置为较小，则显示较小的帧
    face_score_threshold = args.face_score_threshold

    video_output_path = base_output_path+'/videos/'
    mkdir(video_output_path)
    json_output_path = base_output_path+'/json/'

    # for display
    if not no_display:
        colours = np.random.rand(32, 3)
    
    with tf.Graph().as_default():
        with tf.Session(config=tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True), 
                                                        log_device_placement=False)) as sess:
            """
                初始化、载入三个网络 PNet、RNet、ONet
                初始化人脸跟踪器
                初始化检测参数
            """
            pnet, rnet, onet = detect_face.create_mtcnn(sess, os.path.join(project_dir, "detect_align"))

            minsize = 40                    # mtcnn要检测的最小面部尺寸
            threshold = [0.6, 0.7, 0.7]     # 三个步骤的 threshold
            factor = 0.709                  # scale factor
    
            """
                开始处理：循环处理单个视频
            """
            logger.info('开始跟踪和提取人脸......')

            print('*' * 100)
            print('*' * 100)
            print('*' * 100)
            file_list = os.listdir(videos_dir)
            video_count = len(file_list)
            logger.info('要处理的视频文件【共有： %d 个】:' % video_count)
            # 视频太多的话 就不逐个打印名字了
            # for filename in file_list:
            #     logger.info('【{}】'.format(filename))
            print('*' * 100)
            print('*' * 100)
            print('*' * 100)

            sleep(5)

            video_ID = 0                    # 记录当前处理的视频的 序号
            for filename in file_list:
                video_ID += 1

                # 校验视频格式
                suffix = filename.split('.')[1] 
                if suffix != 'mp4' and suffix != 'avi':     # 一般来说，可以增加其他的格式，目前校验的是 MP4 和 avi
                    continue

                source_video_name = os.path.join(videos_dir, filename)
                directoryname = os.path.join(base_output_path, filename.split('.')[0])

                """
                    检查当前文件是否已经处理过了
                    检查方法：与视频同名的json文件是否存在
                """
                if os.path.exists(json_output_path + filename[:-4] + '.json'):
                    logger.info('视频已处理:【 {} 】'.format(source_video_name))
                    continue

                # 为了让每个视频的 人脸 ID 重新刷新，就重新初始化了跟踪器
                tracker = Sort()                # 创建 SORT tracker 实例
                KalmanBoxTracker.count = 0      # 重置类变量，这样每个视频的人脸会从 0 开始，

                logger.info('即将从视频[ {} / {} ]中检测人脸数据:【 {} 】'.format(video_ID, video_count, source_video_name))

                # 读取视频
                capture = cv2.VideoCapture(source_video_name)
                
                # 要保存的视频的名字
                processed_video_name = video_output_path + source_video_name[:-4] + '_processed' + source_video_name[-4:]
                
                # 构造视频写入器
                videoWriter = None
                
                if not no_display:
                    videoWriter, source_video_width, source_video_height = my_utils.create_videoWriter(capture, processed_video_name)
                else:
                    source_video_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                    source_video_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
                # 构造进度条
                tatal_frames_current_video = int(capture.get(7))
                pbar = tqdm(total=tatal_frames_current_video)
                
                # 构造JSON写入器
                jsWriter = my_utils.JsonUtils(filename, capture, json_output_path)
                
                # 帧计数器
                frame_ID = 0
                
                while True:
                    # 循环读取
                    final_faces = []
                    addtional_attribute_list = []

                    ret, frame = capture.read()
                    if not ret:
                        """
                        单个视频已经处理完成
                        """
                        pbar.close()

                        # logger.info("视频【%s】已检测完成" % processed_video_name)
                        if videoWriter != None:
                            videoWriter.close()
                        
                        sleep(5)
                        break

                    if frame is None:
                        logger.warning("未读取到当前帧，即将结束该视频的处理...")
                        break

                    # 对当前帧：resize， 颜色转换
                    frame = cv2.resize(frame, (0, 0), fx=scale_rate, fy=scale_rate)
                    r_g_b_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # 这里有一个间隔帧的设置，间隔几帧做一个检测和跟踪
                    if frame_ID % detect_interval == 0:
                        img_size = np.asarray(frame.shape)[0:2]
                        mtcnn_starttime = time()
                        """
                            检测当前帧的脸和关键点
                        """
                        faces, points = detect_face.detect_face(r_g_b_frame, minsize, pnet, rnet, onet, threshold, factor)
                        # mtcnn 检测时间 可能打印会比较慢
                        # logger.info("MTCNN detect face cost time : {} s".format(round(time() - mtcnn_starttime, 3)))  

                        face_sums = faces.shape[0]
                        # 如果检测到人脸 ...
                        if face_sums > 0:
                            face_list = []
                            for i, item in enumerate(faces):
                                score = round(faces[i, 4], 6)
                                if score > face_score_threshold:
                                    det = np.squeeze(faces[i, 0:4])

                                    # 包围脸的矩形
                                    det[0] = np.maximum(det[0] - margin, 0)
                                    det[1] = np.maximum(det[1] - margin, 0)
                                    det[2] = np.minimum(det[2] + margin, img_size[1])
                                    det[3] = np.minimum(det[3] + margin, img_size[0])
                                    face_list.append(item)
                                    
                                    # face cropped
                                    bb = np.array(det, dtype=np.int32)

                                    # 使用 5 face landmarks 脸部是侧着的还是正着
                                    squeeze_points = np.squeeze(points[:, i])
                                    tolist = squeeze_points.tolist()
                                    facial_landmarks = []
                                    for j in range(5):
                                        item = [tolist[j], tolist[(j + 5)]]
                                        facial_landmarks.append(item)
                                    if args.face_landmarks:
                                        for (x, y) in facial_landmarks:
                                            cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
                                    cropped = frame[bb[1]:bb[3], bb[0]:bb[2], :].copy()

                                    dist_rate, high_ratio_variance, width_rate = judge_side_face(
                                        np.array(facial_landmarks))

                                    # face addtional attribute(index 0:face score; index 1:0 represents front face and 1 for side face )
                                    item_list = [cropped, score, dist_rate, high_ratio_variance, width_rate]
                                    addtional_attribute_list.append(item_list)

                            final_faces = np.array(face_list)

                    trackers = tracker.update(final_faces, img_size, directoryname, addtional_attribute_list, detect_interval)
                    

                    """
                        标注结果：每个跟踪的人脸
                        从这里获取检测到的人脸位置信息，写入json
                    """
                    frame_info = {
                        "frame_id": frame_ID,
                        "face_info": []
                    }

                    for d in trackers:
                        d = d.astype(np.int32) 
                        x1 = int(d[0] / scale_rate)
                        y1 = int(d[1] / scale_rate)
                        x2 = int(d[2] / scale_rate)
                        y2 = int(d[3] / scale_rate)

                        """
                            对齐，防止越界，输出正方形
                        """
                        x1, y1, x2, y2 = pProcess.align_face([x1, y1, x2, y2], source_video_width, source_video_height, margin)
                        
                        ff_temp = {
                            "face_id": "%05d" % d[4], 
                            "count": "%05d" % jsWriter.get_count_4_faceID(frame_ID, d[4]), 
                            "position": [x1,y1,x2,y2]        # x1, y1, x2, y2
                        }
                        frame_info["face_info"].append(ff_temp)


                    #  To json
                    jsWriter.append_frame_content(frame_info)

                    """
                        写入视频还是窗口显示， 命令行参数 --no_display 控制 
                        加上就不显示和写入视频
                    """
                    if not no_display:
                        for d in trackers:
                            d = d.astype(np.int32)
                            # 画图
                            cv2.rectangle(frame, (d[0], d[1]), (d[2], d[3]), colours[d[4] % 32, :] * 255, 2)
                            if final_faces != []:
                                cv2.putText(frame, 'ID : %d  DETECT' % (d[4]), (d[0] - 10, d[1] - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.75,
                                            colours[d[4] % 32, :] * 255, 2)
                                cv2.putText(frame, 'DETECTOR', (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                                            (1, 1, 1), 2)
                            else:
                                cv2.putText(frame, 'ID : %d' % (d[4]), (d[0] - 10, d[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                            0.75,
                                            colours[d[4] % 32, :] * 255, 2)

                    if not no_display:
                        # 缩放展示图片的比例
                        # frame = cv2.resize(frame, (0, 0), fx=show_rate, fy=show_rate)
                        # 实时写入
                        cv2.imwrite(os.path.join(base_output_path, "Frame.jpg"), frame)
                        # 变回原来的大小
                        frame = cv2.resize(frame, (int(source_video_width), int(source_video_height)))

                        videoWriter.write(frame) 
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                    frame_ID += 1
                    pbar.update(1)
                    # end while

                del tracker
                t_save_json_name = jsWriter.save_json_name
                jsWriter.close()
                logger.info("人脸位置数据已写入 Json 文件 >>>>>> ：【 %s 】" % t_save_json_name)  
                
                logger.info("即将开始提取人脸图片： 【 %s 】......" % t_save_json_name)
                pProcess.process_single_video(source_video_name, t_save_json_name, base_output_path + '/images/' + filename[:-4], base_output_path + '/results/' + filename[:-4])  
                print('*' * 100)



def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos_dir", type=str,
                        help='你的输入视频的文件夹', 
                        default='input_videos')

    parser.add_argument('--output_path', type=str,
                        help='保存人脸图片和视频的文件夹', 
                        default='./output')

    parser.add_argument('--detect_interval',
                        help='每隔几帧做一次人脸检测', 
                        type=int, default=1)

    parser.add_argument('--margin',
                        help='添加人脸的间距',
                        type=int, default=10)

    parser.add_argument('--scale_rate',
                        help='对输入视频的原始图片进行降采样或者过采样',
                        type=float, default=0.7)

    parser.add_argument('--show_rate',
                        help='使用opencv在显示时进行放缩',
                        type=float, default=1)

    parser.add_argument('--face_score_threshold',
                        help='提取人脸的阈值, range 0 < x <= 1',
                        type=float, default=0.85)

    parser.add_argument('--face_landmarks',
                        help='开关：是否在提取出的人脸图像上画出 five face landmarks', action="store_true")

    parser.add_argument('--no_display',
                        help='是否显示，由于服务器不易显示，实际作用为，是否输出图片或视频', action='store_true')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
