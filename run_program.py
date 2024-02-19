import json
import PIL.Image as Image
import numpy as np
import os
from model_final import CANNet2s_bottle, CANNet2s_helmet, CANNet2s_spray, CANNet2s_ball, CANNet2s_foam
from torch import device as torchdevice
from torch import load as torch_load
from torch import cat as torch_cat
from torch.autograd import Variable
# import cv2
from torchvision import transforms
import argparse
from matplotlib import cm
import boto3

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

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
    return plot_path
    
    

# Modify the path of the saved checkpoint if necessary
def analyze(img_path, output_path, s3UploadPath = None):
    root_path = '/var/task'
    config_path =os.path.join(root_path,'config.json') 
    config_data = read_config(config_path)

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
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            weight_path = os.path.join(root_path, weight_path)

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
            del img1 , img2
            predicted_temp_1 = torch_cat((predicted1,predicted2), dim =3)
            del predicted1, predicted2
            predicted3 = model(img3)
            predicted4 = model(img4)
            del img3 , img4
            predicted_temp_2 = torch_cat((predicted3,predicted4), dim =3)
            del predicted3, predicted4

            output_density = torch_cat((predicted_temp_1, predicted_temp_2) , dim = 2)
            del predicted_temp_1, predicted_temp_2
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
        # Convert to Pillow Image
        output_print_pil = Image.fromarray(output_print)

        pred_pil = output_print_pil.resize((output_print_pil.width * downscale_level, output_print_pil.height * downscale_level), Image.BICUBIC) 
        pred_pil = pred_pil.point(lambda i : i / (downscale_level * downscale_level))
        pred_pil = pred_pil.resize((1280, 960))
        pred = np.array(pred_pil)

        
        output_data[class_name] = {"count": int(np.round(pred_sum)), "path": density_path}

        # plotDensity(pred,density_path)
        plot_path = plotDensityBlend(original_img.resize((1280,960)), pred, density_path, 0.5)
        # upload to s3
        if s3UploadPath != None:
            s3 = boto3.client('s3')
            s3.upload_file(plot_path, 'parkvic-app', s3UploadPath + plot_path.split("/")[-1])
            output_data[class_name]["path"] = "https://parkvic-app.s3.ap-southeast-2.amazonaws.com/" + s3UploadPath + plot_path.split("/")[-1]


    return output_data