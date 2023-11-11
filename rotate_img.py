import os 
from os.path import join
import cv2
import json
import time

# Loop through list of image -> and rotate, also fix json file
root = './'
# root_data is where you download the FDST dataset
root_data = '../data/new_img_w6/'


all_img_list=[]


def check_img_direction(img_path, img_json):

    image = cv2.imread(img_path)
    with open(img_json, 'r') as json_file:
        jsonFile = json.load(json_file)

    height, width, _ = image.shape
    # if vetical -> rotate image and change json bbox
    if(width<height) :
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        print("image rotated")
        for project_data in jsonFile["projects"].keys():            
            objects = jsonFile["projects"][project_data]["labels"][0]["annotations"]["objects"]
            
            for object in objects:
                print(object["bounding_box"])
                object["bounding_box"] = rotate90Deg(object["bounding_box"], width)
                
                print("bounding box modifying...")
                # time.sleep(1)
            
            with open(img_json, 'w') as json_file:
                json.dump(jsonFile, json_file, indent=4)
                print("json dumped")


        # Save the rotated image
        cv2.imwrite(img_path, rotated_image)



def rotate90Deg(bndbox, img_width): # just passing width of image is enough for 90 degree rotation.
   top = int(bndbox['top'])
   left = int(bndbox['left'])
   height = int(bndbox['height'])
   width = int(bndbox['width'])

   x_min = left
   y_min = top
   x_max = left + width
   y_max = top + height
#    x_min,y_min,x_max,y_max = bndbox

   new_xmin = y_min
   new_ymin = img_width-x_max
   new_xmax = y_max
   new_ymax = img_width-x_min

   return {"top": new_ymin,"left": new_xmin, "height": (new_ymax - new_ymin) ,"width" : (new_xmax -new_xmin)}


# main
for root,dirs, files in os.walk(root_data):
    for file_name in files:
        if file_name.endswith('.json'):
            img_path = join(root,file_name.split('.')[0] +'.jpg')
            img_json = join(root,file_name)
            print("solving " + img_json)
            check_img_direction(img_path, img_json)
            





