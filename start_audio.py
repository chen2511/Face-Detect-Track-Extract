import os
import my_utils
from moviepy.editor import AudioFileClip
from lib.utils import Logger
from tqdm import tqdm
import argparse

logger = Logger()
pbar = None

'''
获取视频中的音频
    以音频为准(切分出音频必定有图片)， 存放目录：./output/audio/*视频名字*/*ID*
'''

def main():
    '''获取基本数据路径，默认无标签数据'''
    # json 输出地址
    base_video_json_dir = './output/json/'
    base_audio_json_dir = './output/audio_json/'
    # 媒体文件输出地址
    base_audio_dir = './output/audio/'
    base_images_dir = './output/images/'
    '''
        视频源文件地址   会从这些文件夹里面查找原视频
        必须以  video  开头；
        当然也可以添加其他目录，添加到下面的列表就好了
    '''
    base_input_dir = []
    for dir in os.listdir('.'):
        if dir.startswith('video'):
            base_input_dir.append(dir)
    # 有的视频有问题，还有重复，尽量从前面开始找
    base_input_dir.sort()
    base_input_dir.remove('video-v1')
    base_input_dir.remove('video-v2')
    base_input_dir.append('video-v1')
    base_input_dir.append('video-v2')

    '''
        处理有标签数据库：会重新覆盖上面设置的那些路径
            数据库1：   mosei
            数据库2：   cheavd2
    '''
    if args.database != 'unlabel':
        logger.info('要处理的视频【有标签】数据库为: ', args.database)
        # 1 数据处理的输出文件夹
        database_output_dir = args.database_output_dir
        base_video_json_dir = database_output_dir + 'json/'
        base_audio_json_dir = database_output_dir + 'audio_json/'
        base_audio_dir = database_output_dir + 'audio/'
        base_images_dir = database_output_dir + 'images/'
        # 2 视频原文件地址
        base_input_dir = [args.base_input_dir]


    my_utils.JsonUtils.mkdir(base_audio_json_dir)

    # 获取video的json文件列表
    video_json_list = sorted(os.listdir(base_video_json_dir))
    # 获取audio的json文件列表
    audio_json_list = sorted(os.listdir(base_audio_json_dir))

    print('*' * 100)
    print('*' * 100)
    print('*' * 100)
    video_total = len(video_json_list)
    logger.info('要处理的视频文件【共有： %d 个】:' % video_total)
    print('*' * 100)
    print('*' * 100)
    print('*' * 100)

    # 处理每一个视频
    video_count = 0
    for cur in video_json_list:
        '''
            1、拿到一个处理好的视频json文件，检查是否可以继续处理，获取音频:
                1）、是否已经处理过
                2）、能否找到原视频
        '''
        if cur in audio_json_list:
            video_count += 1
            logger.info(f'[ {video_count} / {video_total} ]  {cur} 已经处理完成')
            continue
        
        source_video = check_video(cur[:-5]+'.mp4', base_input_dir)
        if source_video == None:
            source_video = check_video(cur[:-5]+'.avi', base_input_dir)
            
        if source_video == None: # 没找到原视频
            video_count += 1
            logger.error(f'[ {video_count} / {video_total} ]  {cur} 没找到原视频')
            continue
        '''
            2、开始处理
                逐帧处理，获取id信息，最终获得每个id在原视频中的开始帧和结束帧
        '''
        video_count += 1
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
        frame_size = images_info['frame_size']
        fps = images_info['fps']
        logger.info(f'[ {video_count} / {video_total} ]  {cur} 已找到原视频【分辨率{frame_size}, fps:{fps}】，即将开始处理...')

        content = {
            'source_video': source_video,
            'fps': images_info['fps'],
            'ID_count': 0,
            'list': {
            }
        }
        '''        2022-10-25 fix bug: fps修正
            处理一个特殊情况：msp-improv中的视频文件的文件头的帧率、帧数等信息与实际的视频不一致
            所以，为了截取音频的准确性，需要重新计算fps，即：读取视频json文件的帧数列表与头部信息的对比比例，一般来说是要除以2
        '''
        if args.database == 'msp-improv':
            actrually_frames_len = len(images_info['frames'])
            filehead_frames_len = images_info['total_frame']
            fps_fix_rate = actrually_frames_len / filehead_frames_len
            content['fps'] = content['fps'] * fps_fix_rate


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
        global pbar
        pbar = tqdm(total=content['ID_count'])

        '''
            切取音频
        '''
        cut(content, audio_dir)


# 检查是否有video源文件
def check_video(video_name, base_input_dir):
    for path in base_input_dir:
        video = os.path.join(path, video_name)
        if os.path.exists(video):
            return video
    return None

def cut(content, audio_dir):
    global pbar
    
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
        start_time = max(0, start_time)
        end_time = min(end_time, audio_clip.end)


        if end_time <= start_time:
            pbar.update(1)
            skip_count += 1
            continue 

        temp_clip = audio_clip.subclip(start_time, end_time)
        temp_clip.write_audiofile(f'{audio_dir}/{id}.wav', logger=None)
        audio_count += 1
        pbar.update(1)
    pbar.close()
    logger.info(f'已提取视频 {source_video} 中的音频 {audio_count + skip_count} 个，成功{audio_count} 个，跳过{skip_count} 个（时间太短、不符）')
    print('')


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=str, help='要处理的数据库，默认无标签，即不额外修改地址', default='unlabel')
    parser.add_argument("--database_output_dir", type=str, help='图片序列、音频、json文件保存的目录', default='')
    parser.add_argument("--base_input_dir", type=str, help='数据库原始视频地址', default='')
    args = parser.parse_args()

    assert args.database in ['unlabel', 'mosei', 'cheavd2', 'msp-improv']

    main()
    '''
        conda activate tfgpu
        
        运行方式：
        1、无标签，提取音频：
                python start_audio.py
        2、其他数据库：
            2.1 mosei:   
                python start_audio.py 
                        --database mosei 
                        --database_output_dir ./output/mosei/video/ 
                        --base_input_dir /public/home/zwchen209/Mosei/Combined

            2.2 cheavd 2.0:
                === train:
                python start_audio.py --database cheavd2  
                                        --database_output_dir ./output/cheavd2/train/ 
                                        --base_input_dir /public/home/zwchen209/CHEAVD2.0/cheavd2/MEC2017/data/train/avi
                === dev:
                python start_audio.py --database cheavd2  
                                        --database_output_dir ./output/cheavd2/dev/ 
                                        --base_input_dir /public/home/zwchen209/CHEAVD2.0/cheavd2/MEC2017/data/dev/avi

            2.3 msp-improv:
                python start_audio.py --database msp-improv  
                                        --database_output_dir ./output/mspimprov/ 
                                        --base_input_dir /public/home/zwchen209/MSP-IMPROV/Video/video
    '''