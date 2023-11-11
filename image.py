import os
from PIL import Image
import numpy as np
import h5py
import cv2


def load_data(img_path,train = True):
    img_folder = os.path.dirname(img_path)
    img_name = os.path.basename(img_path)
    # index = int(img_name.split('.')[0])



    gt_path = img_path.replace('.jpg','_resize.h5')

    img = Image.open(img_path).convert('RGB')

    img = img.resize((1200,900))

    gt_file = h5py.File(gt_path)
    target = np.asarray(gt_file['density'])
    gt_file.close()
    target = cv2.resize(target,(int(target.shape[1]/4),int(target.shape[0]/4)),interpolation = cv2.INTER_CUBIC)*16 # 


    return img, target

