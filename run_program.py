import json
import PIL.Image as Image
import numpy as np
import os
from model_final import CANNet2s_bottle, CANNet2s_helmet, CANNet2s_spray, CANNet2s_ball, CANNet2s_foam
from torch import device as torchdevice
from torch import load as torch_load
from torch import cat as torch_cat
from torch.autograd import Variable
import cv2
from torchvision import transforms
import argparse
from matplotlib import cm

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config


def plotDensity(density,plot_path):
    '''
    @density: np array of corresponding density map
    @plot_path: path to save the plot
    '''

    density= density*255.0

    #plot with overlay
    colormap_i = cm.jet(density)[:,:,0:3]

    overlay_i = colormap_i

    new_map = overlay_i.copy()
    new_map[:,:,0] = overlay_i[:,:,2]
    new_map[:,:,2] = overlay_i[:,:,0]
    cv2.imwrite(plot_path,new_map*255)

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def plotDensityBlend(origin_img, density, plot_path, alpha=0.5 ):
    density= density*255.0

    #plot with overlay
    colormap_i = cm.jet(density)[:,:,0:3]

    overlay_i = colormap_i

    new_map = overlay_i.copy()
    new_map[:,:,0] = overlay_i[:,:,2]
    new_map[:,:,2] = overlay_i[:,:,0]

    blend = Image.blend(origin_img, Image.fromarray((new_map*255).astype(np.uint8)), alpha)
    blend.save(plot_path)

# Remove .cuda() to keep the model on the CPU
# model = model.cuda()

# Modify the path of the saved checkpoint if necessary
def analyze(img_path, output_path):
    
    config_path = './config.json'
    config_data = read_config(config_path)
    img_folder = os.path.dirname(img_path)
    img_name = os.path.basename(img_path)
    output_data = {}
    for class_data in config_data["class"]:
        # load model
        class_name = next(iter(class_data))
        class_info = class_data[class_name]
        img_width  = class_info["img_width"]
        img_height = class_info["img_height"]
        tile = class_info["tile"]
        downscale_level = class_info["downscale_level"]
        weight_path =  os.path.join(config_data["weight_localtion"] , class_info["model_name"])
        checkpoint = torch_load(weight_path, map_location=torchdevice('cpu'))
        model = None

        if (class_name == 'plastic_bottle'):
            model = CANNet2s_bottle()
        elif ( class_name == 'helmet'):
            model = CANNet2s_helmet()
        elif ( class_name == 'ball'):
            model = CANNet2s_ball()
        elif (class_name == 'spray_can'):
            model = CANNet2s_spray()
        elif (class_name == 'foam'):
            model = CANNet2s_foam()

        model.load_state_dict(checkpoint['state_dict'], strict = False)
        model.eval()

        #load image
        img = Image.open(img_path).convert('RGB')
        original_img = img
        img = img.resize((img_width, img_height))
        
        img = transform(img)

        img = Variable(img)

        img = img.unsqueeze(0)

        output_density = None
        if (tile == 0):
            output_density = model(img)
        elif (tile == 2):
            img1 =  img[:,:,:(int(img.shape[2]/2)),:(int(img.shape[3]/2)) ]
            img2 = img[:,:,:(int(img.shape[2]/2)) :,(int(img.shape[3]/2)): ]
            img3 = img[:,:,(int(img.shape[2]/2)) :,:(int(img.shape[3]/2)) ]
            img4 = img[:,:,(int(img.shape[2]/2)):,(int(img.shape[3]/2)): ]

            predicted1 = model(img1)
            predicted2 = model(img2)
            predicted3 = model(img3)
            predicted4 = model(img4)
            predicted_temp_1 = torch_cat((predicted1,predicted2), dim =3)
            predicted_temp_2 = torch_cat((predicted3,predicted4), dim =3)

            output_density = torch_cat((predicted_temp_1, predicted_temp_2) , dim = 2)
        else :
            print(f"tile {tile} is not supported. Program abort." , )
        
        output_sum = output_density.sum()

        pred_sum = output_sum.data.numpy()

        print(class_name + ' : '+ str(int(np.round(pred_sum))))
        # plot image
        base_name = os.path.basename(img_path)
        folder_name = os.path.dirname(img_path).split('/')[-1]
        density_path = os.path.join(output_path,class_name+'_'+ base_name.replace('.jpg','_pred.jpg'))
        
        output_print = output_density.data.numpy()[0,0,:,:]
        pred = cv2.resize(output_print,(output_print.shape[1]*downscale_level,output_print.shape[0]*downscale_level),interpolation = cv2.INTER_CUBIC)/(downscale_level*downscale_level)
        pred = cv2.resize(pred, (1280,960))

        # for pyinstaller only
        # density_path =  os.path.join('./', density_path.split("/",2)[-1])


        output_data[class_name] = {"count": int(np.round(pred_sum)), "path": density_path}
        
        # plotDensity(pred,density_path)
        plotDensityBlend(original_img.resize((1280,960)), pred, density_path, 0.5)

    # json_string = json.dumps(output_data, indent=2)
    # save output file to folder
    # with open('./result/output.json', 'w') as json_file:
    #     json_file.write(json_string)
    
    return output_data