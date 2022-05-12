import os
from PIL import Image

output_dir = "./output/images/无用人脸_s_3"
result_dir = "./output/results/无用人脸_s_3"

if __name__ == "__main__":
# 选取大小合适的图片 移动到result文件夹
    # if os.path.exists(result_dir):
    #     pass
    # else:
    #     os.makedirs(result_dir)
    for i in os.listdir(output_dir): # 遍历视频文件夹 得到单人文件夹sub_dir
        sub_dir = os.path.join(output_dir, i)
        # print(sub_dir)
        if os.path.isdir(sub_dir): # 如果sub_dir是文件夹 遍历sub_dir 得到单张图片pic
            # res_dir = os.path.join(result_dir, i)
            # if os.path.exists(res_dir):
            #     pass
            # else:
            #     os.makedirs(res_dir)
            
            for j in os.listdir(sub_dir):
                pic = os.path.join(sub_dir, j)
                # res = os.path.join(res_dir, j)
                if pic.split('.')[-1] == 'jpg': # 如果pic是图片 读取pic
                    # print(pic)
                    img = Image.open(pic)
                    imgSize = img.size
                    img.close()
                    # print(imgSize)
                    if imgSize[0] > 96 or imgSize[1] > 96:
                        # 图片进行resize操作
                        # img = Image.open(pic)
                        # resize_pic = img.resize((128,128), Image.ANTIALIAS)
                        # resize_pic.save(res)
                        # img.close()
                        # shutil.copyfile(pic,res) # 将pic移动到result文件夹
                        pass
                    else:
                        # print(pic)
                        # shutil.copyfile(pic,res)
                        # os.remove(pic) # 删除文件
                        for file in os.listdir(sub_dir):
                            #进入下一个文件夹中进行删除
                            os.remove(os.path.join(sub_dir,file))
                        #如果是空文件夹，直接删除
                        os.rmdir(sub_dir)
                        print(sub_dir,"文件夹删除成功")
                        # pass
                        break
                

# # 判断文件夹大小 分割大文件夹
#     for k in os.listdir(result_dir):
#         check_dir = os.path.join(result_dir, k)
#         # print(check_dir)
#         num = len(os.listdir(check_dir))
#         # print(k)
#         # print(num)
#         if num <= 50:
#             for file in os.listdir(check_dir):
#                 #进入下一个文件夹中进行删除
#                 os.remove(os.path.join(check_dir,file))
#             #如果是空文件夹，直接删除
#             os.rmdir(check_dir)
#             print(check_dir,"文件数",num,"删除成功")

#         t = 0
#         while num > 200: # 如果文件夹中图片数量超过200 将其分割
#             # print(k)
#             k_split = k+'_'+str(t)
#             # print(k_split)
#             mv_dir = os.path.join(result_dir, k_split)
#             if os.path.exists(mv_dir):
#                 pass
#             else:
#                 os.mkdir(mv_dir)
            
#             cnt = 0
#             for pics in sorted(os.listdir(check_dir)):
#                 pic = os.path.join(check_dir, pics)
#                 mv_pic = os.path.join(mv_dir, pics)
#                 shutil.move(pic, mv_pic)
#                 cnt += 1
#                 if cnt >= 200:
#                     break
#             num = len(os.listdir(check_dir))
#             t = t+1
        
#         if t != 0:
#             os.rename(check_dir, os.path.join(result_dir, k+'_'+str(t)))
        