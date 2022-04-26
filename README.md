# 人脸检测跟踪和提取

![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg)

## 介绍

这是一个人脸检测跟踪和提取库，基于`MTCNN`和`SORT`跟踪算法实现。

基于：[Linzaer/Face-Track-Detect-Extract: 💎 Detect , track and extract the optimal face in multi-target faces (exclude side face and select the optimal face). (github.com)](https://github.com/Linzaer/Face-Track-Detect-Extract)

### 实现思路：

`MTCNN`实现人脸检测

`SORT`实现多目标跟踪

### 依赖:

- python 3.7.*

- [**MTCNN**](https://github.com/davidsandberg/facenet/tree/master/src/align)

说明：这个版本似乎还是不太匹配（会报告一些警告，部分函数已经被废弃），`sklearn`库和`numpy`库应该还是要降级

`requirements.txt`：

```
filterpy==1.4.5
numba==0.55.1
numpy==1.21.1
opencv_python==4.5.5.64
scikit_learn==1.0.2
six==1.16.0
tensorflow==1.15.0
```

### 目录说明：

```
.
├── detect_align						# MTCNN 主要内容
│   ├── det1.npy						# 三个模型 
│   ├── det2.npy
│   ├── det3.npy
│   ├── detect_face.py
│   ├── __init__.py
│   └── __pycache__
├── example.json					# 输出 人脸信息
├── Frame.jpg
├── input_videos					# 会处理这个文件夹里面的所有视频
│   └── example.mp4
├── lib								# 作者提供的一些工具库
│   ├── face_utils.py
│   ├── __init__.py
│   ├── __pycache__
│   └── utils.py
├── LICENSE
├── logs							# 日志文件
│   └── MOT
├── output							# 输出文件夹
│   ├── videos							# 处理后的视频
│   └── example							# 单个视频裁剪出来的人脸图片
├── project_root_dir.py
├── README.md						
├── requirements.txt				# 依赖库说明
├── tracker								# 这个是跟踪算法包
│   ├── data_association.py				# ...
│   ├── __init__.py
│   ├── kalman_tracker.py				# ...
│   ├── __pycache__
│   └── sort.py							# 跟踪算法主要实现
├── start.py						# ！！！程序入口
├── my_utils.py						# 工具包：视频写入工具
└── 视频仓库						 # 视频仓库
    ├── 1_Hours Of _Harassment' In NYC!.mp4
    └── 2_Obama.mp4
```

主要看 `start.py`即可

### 效率

显卡：`TITAN Xp`

显存：`1.1 GB`

速度：20帧

## 运行

- 输入视频：

把输入视频放入`input_videos`文件夹，会检测逐个视频里的人脸

* 运行命令 :
```sh
export CUDA_VISIBLE_DEVICES=0; python start.py --videos_dir="input_videos" --no_display 
```
* 输出文件夹

output文件夹内有：一部分是视频（框出人脸），另一部分是裁剪出来的单张人脸；还有 json 数据（记录每个视频，每帧的人脸信息）

* 如果需要 5 face landmarks，加入参数 **--face_landmarks**



### 调试运行：

文件夹根目录有一个 `Frame.jpg`缓存图像，`vscode`中打开该图像，可以随着代码运行实时刷新该图像，近似做到 `imshow`



## 结果
![alt text](output/example/example.gif)

