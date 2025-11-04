###
这个是关于blender的进行星体渲染的一些文件，至于每个文件能够干什么，好久了，忘记了，等我慢慢看，慢慢总结


### 切割ldem的tif
```
python cut.py # 在源码中修改tif原图的范围值，以及你需要裁剪出来的值
```

### blender中应用渲染图
```
# preload_image_resources函数使用了预加载的图像的方法，后续如果相机没有出现在图像的位置时，不显示图像，减少渲染量
# select_and_materialize_region(obj, lat_min, lat_max, lon_min, lon_max, texture_path, normal_path, group_name="Selected_Faces_Group",scale=1.0)，这个函数用于在blender经纬球中选择切割出对应的部分，用经纬度来选择你需要切割的部分，texture_path用于加载一个模型的表面纹理，normal_path用于加载一个模型的dem图
```
```
python getPartMoon.py 
# 自己在源码中填入需要使用的预加载图像，同时自己添加或者修改select_and_materialize_region(obj, lat_min, lat_max, lon_min, lon_max, texture_path, normal_path, group_name="Selected_Faces_Group",scale=1.0,)
```