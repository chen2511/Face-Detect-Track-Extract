import os
import my_utils
import moviepy
from moviepy.editor import AudioFileClip

'''
获取视频中的音频
    以音频为准(切分出音频必定有图片)， 存放目录：./output/audio/*视频名字*/*ID*

'''

# json 输出地址
base_video_json_dir = './output/json/'
base_audio_json_dir = './output/audio_json/'
# 媒体文件输出地址
base_audio_dir = './output/audio/'
base_images_dir = './output/images/'
'''
# 视频源文件地址   会从这些文件夹里面查找原视频
    必须以  video  开头
'''
base_input_dir = []
for dir in os.listdir('.'):
    if dir.startswith('video'):
        base_input_dir.append(dir)

my_utils.JsonUtils.mkdir(base_audio_json_dir)

def main():
    # 获取video的json文件列表
    video_json_list = sorted(os.listdir(base_video_json_dir))
    # 获取audio的json文件列表
    audio_json_list = sorted(os.listdir(base_audio_json_dir))

    # 处理每一个视频
    for cur in video_json_list:
        '''
            1、拿到一个处理好的视频json文件，检查是否可以继续处理，获取音频:
                1）、是否已经处理过
                2）、能否找到原视频
        '''
        if cur in audio_json_list:
            print(cur, '已经处理')
            continue
        
        source_video = check_video(cur[:-5]+'.mp4')
        if source_video == None: # 没找到原视频
            print(cur, '没找到原视频')
            continue
        '''
            2、开始处理
                逐帧处理，获取id信息，最终获得每个id在原视频中的开始帧和结束帧
        '''
        # 图片json目录
        images_json = base_video_json_dir + cur
        # 图片保存目录
        images_dir = base_images_dir + cur[:-5]
        # 音频json目录
        audio_json = base_audio_json_dir + cur
        # 音频保存目录
        audio_dir = base_audio_dir + cur[:-5]
        my_utils.JsonUtils.mkdir(audio_dir)

        # 保存 每一个id的人的 开始帧和结束帧
        images_info = my_utils.JsonUtils.load_json(images_json)
        content = {
            'source_video': source_video,
            'fps': images_info['fps'],
            'ID_count': 0,
            'list': {
            }
        }
        frames = images_info['frames']
        for frame in frames:                    # 逐帧处理
            for face in frame['face_info']:     # 处理每一帧中存在的人脸
                faceID = face['face_id']

                ID_dir = os.path.join(images_dir, faceID)
                if not os.path.exists(ID_dir):  # 检查 某 ID 代表的人的数据是否被删除，因为有时候人脸太小会被删除
                    continue

                if faceID in content['list']:   # 人脸不是第一次出现，更新为结束帧
                    content['list'][faceID]['end'] = frame['frame_id']
                else:                           # 人脸是第一次出现，更新为 开始帧
                    content['list'][faceID] = {
                        'start': frame['frame_id'], 
                        'end': frame['frame_id']
                        }
        content['ID_count'] = len(content['list'])
        my_utils.JsonUtils.save_json(content, audio_json)

        '''
            切取音频
        '''
        cut(content, audio_dir)


# 检查是否有video源文件
def check_video(video_name):
    for path in base_input_dir:
        video = os.path.join(path, video_name)
        if os.path.exists(video):
            return video
    return None

def cut(content, audio_dir):
    
    source_video = content['source_video']
    fps = content['fps']
    audio_clip = AudioFileClip(source_video)

    audio_count = 0
    skip_count = 0

    for id in content['list']:
        # 计算音频开始时间和结束时间
        start = content['list'][id]['start']
        end = content['list'][id]['end']
        start_time = round(start / fps, 2)  
        end_time = round(end / fps, 2)     
        start = max(0, start_time)
        end_time = min(end_time, audio_clip.end)


        if end_time <= start_time:
            skip_count += 1
            continue 

        audio_clip.subclip(start_time, end_time).write_audiofile(f'{audio_dir}/{id}.wav')
        audio_count += 1
    print(f'已提取视频 {source_video} 中的音频 {audio_count + skip_count}个，成功{audio_count}个，跳过{skip_count}个（时间不符）')


if __name__=='__main__':
    main()