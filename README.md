# 人脸检测跟踪和提取

![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg)

## 一、介绍

这是一个人脸检测跟踪和提取库，基于`MTCNN`和`SORT`跟踪算法实现。本项目主要贡献是，后半部分的人脸图像对齐、提取。

基于（特别感谢）：
> [Linzaer/Face-Track-Detect-Extract: 💎 Detect , track and extract the optimal face in multi-target faces (exclude side face and select the optimal face). (github.com)](https://github.com/Linzaer/Face-Track-Detect-Extract)

### 1、实现思路：

`MTCNN`实现人脸检测，`SORT`实现多目标跟踪

### 2、依赖:

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

> 如果环境还是不匹配，推荐先安装 `tensorflow==1.15`的包，再安装 `scikit-learn==0.21.2`的包，再安装其他包即可。

### 3、目录说明：

```
.
├── detect_align						# MTCNN 主要内容
│   ├── det1.npy						# 三个模型 
│   ├── det2.npy
│   ├── det3.npy
│   ├── detect_face.py
│   ├── __init__.py
│   └── __pycache__
├── input_videos					# 默认会处理这个文件夹里面的所有视频
├── judge_face.py                   # 测试代码
├── lib								# 作者提供的一些工具库
│   ├── face_utils.py
│   ├── __init__.py
│   ├── __pycache__
│   └── utils.py
├── LICENSE
├── logs							# 日志文件
│   └── MOT
├── output							# 输出文件夹
│   ├── example                         # 例子
│   ├── Frame.jpg                       # 可用于调试实时显示的
│   ├── images                          # 单个视频裁剪出来的人脸图片
│   ├── json                            # 单个视频处理后的json文件
│   └── videos                          # 处理后的视频	需要去除参数 --no_display才会保存视频	
├── post_processed.py               # （主要代码2）后处理部分，对齐，筛选人脸
├── project_root_dir.py
├── README.md						
├── requirements.txt				# 依赖库说明
├── tracker								# 这个是跟踪算法包
│   ├── data_association.py				# ...
│   ├── __init__.py
│   ├── kalman_tracker.py				# ...
│   ├── __pycache__
│   └── sort.py							# 跟踪算法主要实现
├── start.py						# ！！！程序入口（主要代码1）
├── my_utils.py						# 工具包：视频写入工具
└── 视频仓库						 # 视频仓库：缓存其他视频

```

主要看 `start.py`即可

### 4、效率

显存：`1.1 GB`

速度：720P 20帧+-

## 二、运行

- 输入视频：

把输入视频放入`input_videos`文件夹，会检测逐个视频里的人脸

* 运行命令 :
```sh
export CUDA_VISIBLE_DEVICES=0; python start.py --no_display --videos_dir="input_videos" 
```
* 输出文件夹

output文件夹内有：一部分是视频（框出人脸），另一部分是裁剪出来的单张人脸；还有 json 数据（记录每个视频，每帧的人脸信息）

* 如果需要 5 face landmarks，加入参数 **--face_landmarks**



### 1、调试运行：

文件夹根目录有一个 `Frame.jpg`缓存图像，`vscode`中打开该图像，可以随着代码运行实时刷新该图像，近似做到 `imshow`



## 三、结果
![alt text](output/example/example.gif)

## 四、提取音频

在图片提取完成之后，会生成图片文件夹和图片json文件夹

在这一部分输入为：

> 原始视频
>
> 图片文件夹
>
> 图片json【一个json对于一个视频】

输出为：

> 音频文件【每个id与图片id对应】
>
> 音频json【一个json对于一个视频】

每个

### 程序说明

0、获取已经处理好的`图片json`文件列表，循环处理每个视频

1、先检查是否已经处理过了，即是否存在`音频json`数据

2、检查是否有原视频

3、处理`图片json`，即根据id顺序，获取每个id的开始帧和结束帧。期间检查是否有这个id的图片，因为有些图片不合格会被删除；还会检查时间是否太短。

4、计算每个id的开始时间和结束时间，按顺序提取音频文件。

> 最后的结果是，有一个和视频同名文件夹，里面有许多音频，这些音频和图片序列的id从时间上是对应的，【从音频对齐】有音频必有图片
