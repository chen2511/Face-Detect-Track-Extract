'''
统计音频长度信息
'''

from email.mime import audio
import os
import librosa
from tqdm import tqdm
from my_utils import JsonUtils
audio_json_filename = 'statistics_audio.json'


audio_info = {
    'total': 0,
    '0.1': 0,
    '0.25': 0,
    '0.5': 0,
    '0.75': 0,
    '1': 0,
    '1.5': 0,
    '2': 0,
    '3': 0,
    '4': 0,
    '5': 0,
    '6': 0,
    '10': 0,
    '>=20': 0
}

for root, dirs, _ in os.walk('./output/audio/'):
    for dir in tqdm(dirs):
        JsonUtils.save_json(audio_info, audio_json_filename)

        for wav_root, _, wavs in os.walk(root + dir):
            for wav in wavs:
                audio_name = wav_root + '/' + wav
                # print(audio_name)

                duration = librosa.get_duration(filename=audio_name)
                # print(duration)
                audio_info['total'] = audio_info['total'] + 1
                if duration >= 20:
                    audio_info['>=20'] = audio_info['>=20'] + 1
                elif duration >= 10:
                    audio_info['10'] = audio_info['10'] + 1
                elif duration >= 6:
                    audio_info['6'] = audio_info['6'] + 1
                elif duration >= 5:
                    audio_info['5'] = audio_info['5'] + 1
                elif duration >= 4:
                    audio_info['4'] = audio_info['4'] + 1
                elif duration >= 3:
                    audio_info['3'] = audio_info['3'] + 1
                elif duration >= 2:
                    audio_info['2'] = audio_info['2'] + 1
                elif duration >= 1.5:
                    audio_info['1.5'] = audio_info['1.5'] + 1
                elif duration >= 1:
                    audio_info['1'] = audio_info['1'] + 1
                elif duration >= 0.75:
                    audio_info['0.75'] = audio_info['0.75'] + 1
                elif duration >= 0.5:
                    audio_info['0.5'] = audio_info['0.5'] + 1
                elif duration >= 0.25:
                    audio_info['0.25'] = audio_info['0.25'] + 1
                elif duration >= 0.1:
                    audio_info['0.1'] = audio_info['0.1'] + 1
                
# print(audio_info)  

# JsonUtils.mkdir(audio_json_filename)
JsonUtils.save_json(audio_info, audio_json_filename)



