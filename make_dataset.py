import  h5py
import PIL.Image as Image
import numpy as np
import os
import glob
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter
import json
from image import *
from os.path  import join

#set the root to the path of FDST dataset you download
root = './'

#now generate the FDST's ground truth
root_data =  '../data/image/'
# path_sets = [os.path.join(train_folder,f) for f in os.listdir(train_folder) if os.path.isdir(os.path.join(train_folder,f))]+[os.path.join(test_folder,f) for f in os.listdir(test_folder) if os.path.isdir(os.path.join(test_folder,f))]

img_paths = []

class_name = "plastic_bottle"

for root,dirs, files in os.walk(root_data):
    for file_name in files:
        if file_name.endswith('.json'):
            img_paths.append(join(root,file_name.split('.')[0] +'.jpg'))

# for data analysis
count = []

for img_path in img_paths:
    print (img_path)
    gt_path = img_path.replace('.jpg','.json')
    with open (gt_path,'r') as f:
        gt = json.load(f)
    anno_list =[]


    for project_data in gt["projects"].keys(): 
        anno_list = gt["projects"][project_data]["labels"][0]["annotations"]["objects"]


    img= plt.imread(img_path)
    k = np.zeros((960,1280))
    rate_h = img.shape[0]/960.0
    rate_w = img.shape[1]/1280.0
    for i in anno_list:
        if i["name"] == class_name:
            y = i["bounding_box"]["top"] + i["bounding_box"]["height"] /2
            x = i["bounding_box"]["left"] + i["bounding_box"]["width"] /2

            y_anno = min(int(y/rate_h),960)
            x_anno = min(int(x/rate_w),1280)
            k[y_anno,x_anno]=1

    k = gaussian_filter(k,3)
    with h5py.File(img_path.replace('.jpg','_resize.h5'), 'w') as hf:
            hf['density'] = k
            hf.close()

