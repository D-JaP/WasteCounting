import h5py
import json
import PIL.Image as Image
import numpy as np
import os
import glob
import scipy
from image import *
from model import CANNet2s
import torch
from torch.autograd import Variable
import torch.nn.functional as F
import cv2
import time
from torchvision import transforms

from sklearn.metrics import mean_squared_error,mean_absolute_error, mean_absolute_percentage_error

transform=transforms.Compose([
                       transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
                   ])

# the json file contains path of test images
test_json_path = './test.json'

with open(test_json_path, 'r') as outfile:
    img_paths = json.load(outfile)



model = CANNet2s()

total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"Number of parameters: {total_params}")

model = model.cuda()

# modify the path of saved checkpoint if necessary
checkpoint = torch.load('model_best.pth.tar')

model.load_state_dict(checkpoint['state_dict'])

model.eval()

pred= []
gt = []
_time  = []
for i in range(len(img_paths)):
    img_path = img_paths[i]

    img_folder = os.path.dirname(img_path)
    img_name = os.path.basename(img_path)

    img = Image.open(img_path).convert('RGB')

    img = img.resize((960,720))

    img = transform(img).cuda()

    gt_path = img_path.replace('.jpg','_resize.h5')
    gt_file = h5py.File(gt_path)
    target = np.asarray(gt_file['density'])



    img = img.cuda()
    img = Variable(img)


    img = img.unsqueeze(0)


    
    
    torch.cuda.synchronize()
    t0 = time.time()
    img1 =  img[:,:,:(int(img.shape[2]/2)),:(int(img.shape[3]/2)) ]
    img2 = img[:,:,:(int(img.shape[2]/2)) :,(int(img.shape[3]/2)): ]
    img3 = img[:,:,(int(img.shape[2]/2)) :,:(int(img.shape[3]/2)) ]
    img4 = img[:,:,(int(img.shape[2]/2)):,(int(img.shape[3]/2)): ]


    predicted1 = model(img1)
    predicted2 = model(img2)
    predicted3 = model(img3)
    predicted4 = model(img4)
    predicted_temp_1 = torch.cat((predicted1,predicted2), dim =3)
    predicted_temp_2 = torch.cat((predicted3,predicted4), dim =3)

    output1 = torch.cat((predicted_temp_1, predicted_temp_2) , dim = 2)
    # output1 = model(img)

    
    output1 = output1.sum()
    elapsed_fp = time.time() - t0
    torch.cuda.synchronize()


    _time.append(elapsed_fp)

    if(len(_time)>3):
        # print((int)(1/(sum(_time)/3)))
        _time=[]

    target = target


    # pred_sum = output1.item()
    pred_sum = output1.data.cpu().numpy()
    pred.append(pred_sum)
    gt.append(np.sum(target))

print([np.round(i.item(),1) for i in pred] )
print([int(i) for i in gt])
mae = mean_absolute_error(pred,gt)
rmse = np.sqrt(mean_squared_error(pred,gt))
mape = mean_absolute_percentage_error([np.round(i) for i in pred],gt)
print ('MAE: ',mae)
print ('RMSE: ',rmse)
print ('MAPE: ', mape)

