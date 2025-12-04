###
这个是关于blender的进行星体渲染的一些文件，至于每个文件能够干什么，好久了，忘记了，等我慢慢看，慢慢总结


### 切割ldem或者lroc的tif
```
python cut.py src_path src_lon_min src_lon_max src_lat_min src_lat_max lon_min lon_max lat_min lat_max 每度像素数(src的精度)
python cut_lroc.py # 在源码中修改lroc tif原图的范围值，以及你需要裁剪出来的值
```

### blender中应用渲染图
```
# preload_image_resources函数使用了预加载的图像的方法，后续如果相机没有出现在图像的位置时，不显示图像，减少渲染量
# select_and_materialize_region(obj, lat_min, lat_max, lon_min, lon_max, texture_path, normal_path, group_name="Selected_Faces_Group",scale=1.0)，这个函数用于在blender经纬球中选择切割出对应的部分，用经纬度来选择你需要切割的部分，texture_path用于加载一个模型的表面纹理，normal_path用于加载一个模型的dem图
```
```
python getPartMoon.py 
# 自己在源码中填入需要使用的预加载图像，同时自己添加或者修改select_and_materialize_region(obj, lat_min, lat_max, lon_min, lon_max, texture_path, normal_path, group_name="Selected_Faces_Group",scale=1.0,),让对应的区域加载你需要的图片
```

### 生成全月图
```
python all_moon.py
```
非极区用png 极区用tif
### 转换IMG文件
```
python img2tif.py
```

### 将32为浮点数tif图变成16位无符号的png图
```
python tif2png.py src_path dst_path
```

### test文件，真的就是test而已，没啥用，让你尝试你的代码是否可行，然后可行在自己生成新的文件(现在暂时就是用来测试getPartMoon的间断生成功能)
```
python test.py 
# 自己在源码中填入需要使用的预加载图像，同时自己添加或者修改select_and_materialize_region(obj, lat_min, lat_max, lon_min, lon_max, texture_path, normal_path, group_name="Selected_Faces_Group",scale=1.0,visible_start_frame=81,visible_end_frame=160),让对应的区域加载你需要的图片,选择渲染的时间
```

### 对极地立体投影进行一个旋转或者裁剪
#### 对png文件进行一个裁剪
```
python unroll.py "C:\Users\MushOtter\Pictures\s.png"
```
#### 对tif文件进行一个裁剪或者加上--rotate参数进行一个旋转
```
python unrolltest.py "C:\Users\MushOtter\Pictures\ldem_75s_30m_float.tif"
```

#### 八叉树实验
python eight.py