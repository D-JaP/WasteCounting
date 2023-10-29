import h5py
import json
import PIL.Image as Image
import numpy as np
import os
from image import *
from model import CANNet2s
import torch
from torch.autograd import Variable
import torch.nn.functional as F
import cv2
import os
import math

from matplotlib import cm

from torchvision import transforms


def plotDensity(density,plot_path):
    '''
    @density: np array of corresponding density map
    @plot_path: path to save the plot
    '''
    print(density)
    density= density*255.0

    #plot with overlay
    colormap_i = cm.jet(density)[:,:,0:3]

    overlay_i = colormap_i

    new_map = overlay_i.copy()
    new_map[:,:,0] = overlay_i[:,:,2]
    new_map[:,:,2] = overlay_i[:,:,0]
    cv2.imwrite(plot_path,new_map*255)

transform=transforms.Compose([
                       transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
                   ])

# json file contains the test images
test_json_path = './test.json'

# the folder to output density map and flow maps
output_folder = 'C:/Users/dzung/project/parkvic/WasteCounting/output'

with open(test_json_path, 'r') as outfile:
    img_paths = json.load(outfile)



model = CANNet2s()

model = model.cuda()

checkpoint = torch.load('model_best.pth.tar')

model.load_state_dict(checkpoint['state_dict'])

model.eval()

pred= []
gt = []

for i in range(len(img_paths)):
    img_path = img_paths[i].replace('\\', '/')
    img_folder = os.path.dirname(img_path)
    img_name = os.path.basename(img_path)
    index = int(img_name.split('.')[0])



    img = Image.open(img_path).convert('RGB')

    img = img.resize((1280,960))

    img = transform(img).cuda()

    gt_path = img_path.replace('.jpg','_resize.h5')
    gt_file = h5py.File(gt_path)
    target = np.asarray(gt_file['density'])


    img = img.cuda()
    img = Variable(img)


    img = img.unsqueeze(0)



    overall = (model(img)).data.cpu().numpy()
    overall = overall[0,0,:,:]

    base_name = os.path.basename(img_path)
    folder_name = os.path.dirname(img_path).split('/')[-1]

    os.makedirs(os.path.join(output_folder+'/'+folder_name), exist_ok=True)

    gt_path = os.path.join(output_folder+'/'+folder_name,base_name).replace('.jpg','_'+folder_name+'_gt.jpg')
    density_path = os.path.join(output_folder+'/'+folder_name,base_name).replace('.jpg','_'+folder_name+'_pred.jpg')
    print(overall.shape)
    pred = cv2.resize(overall,(overall.shape[1]*16,overall.shape[0]*16),interpolation = cv2.INTER_CUBIC)/256.0

    plotDensity(pred,density_path)
    plotDensity(target,gt_path)

    




    # print(os.path.join(output_folder+'/'+folder_name,base_name).replace('.jpg','_'+folder_name+'_hsv.jpg'))




    
