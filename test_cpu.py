import h5py
import json
import PIL.Image as Image
import numpy as np
import os
import glob
import scipy
from image import *
from model import CANNet2s
from MobileCount import MobileCount
import torch
from torch.autograd import Variable
import torch.nn.functional as F
import cv2
import time
from torchvision import transforms

from sklearn.metrics import mean_squared_error, mean_absolute_error

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# the json file contains the path of test images
test_json_path = './test.json'

with open(test_json_path, 'r') as outfile:
    img_paths = json.load(outfile)

model = CANNet2s()

total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"Number of parameters: {total_params}")

# Remove .cuda() to keep the model on the CPU
# model = model.cuda()

# Modify the path of the saved checkpoint if necessary
checkpoint = torch.load('10.pth.tar', map_location=torch.device('cpu'))

model.load_state_dict(checkpoint['state_dict'])

model.eval()

pred = []
gt = []
_time = []
for i in range(len(img_paths)):
    img_path = img_paths[i]

    img_folder = os.path.dirname(img_path)
    img_name = os.path.basename(img_path)

    img = Image.open(img_path).convert('RGB')

    img = img.resize((640, 480))

    img = transform(img)

    gt_path = img_path.replace('.jpg', '_resize.h5')
    gt_file = h5py.File(gt_path)
    target = np.asarray(gt_file['density'])

    img = Variable(img)

    img = img.unsqueeze(0)

    t0 = time.time()
    output1 = model(img)

    output1 = output1.sum()
    elapsed_fp = time.time() - t0

    _time.append(elapsed_fp)

    if len(_time) > 3:
        print((sum(_time)/3))
        _time = []

    target = target

    pred_sum = output1.data.numpy()
    pred.append(pred_sum)
    gt.append(np.sum(target))

print(pred)
print(gt)

mae = mean_absolute_error(pred, gt)
rmse = np.sqrt(mean_squared_error(pred, gt))

print('MAE: ', mae)
print('RMSE: ', rmse)
