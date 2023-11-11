import os 
from os.path import join
import cv2
import json
import time

# Loop through list of image -> and rotate, also fix json file
root = './'
# root_data is where you download the FDST dataset
root_data = '../data/image/'


all_img_list=[]


def create_mirror_image(img_path, img_json):

    image = cv2.imread(img_path)
    with open(img_json, 'r') as json_file:
        jsonFile = json.load(json_file)

    height, width, _ = image.shape
    # if vetical -> rotate image and change json bbox
    mirrored_image = cv2.flip(image, 1)
    print("image mirrored")
    for project_data in jsonFile["projects"].keys():            
        objects = jsonFile["projects"][project_data]["labels"][0]["annotations"]["objects"]
        
        for object in objects:
            # print(object["bounding_box"])
            object["bounding_box"] = mirror_bbox(object["bounding_box"], width)

            print("bounding box modifying...")
            # time.sleep(1)
        
        with open(mirror_path(img_json), 'w') as json_file:
            # print(flip_path(img_json))
            json.dump(jsonFile, json_file, indent=4)
            print("json dumped")


    # Save the rotated image
    cv2.imwrite(mirror_path(img_path), mirrored_image)
    # print(flip_path(img_path))

def mirror_path(path):
    print(path)
    postfix = path.rsplit('.', 1)[1]
    print(path.rsplit('.', 1)[0])
    return (path.rsplit('.', 1)[0] + '_m' + '.' + postfix) 

def mirror_bbox(bndbox, img_width): # just passing width of image is enough for 90 degree rotation.
   top = int(bndbox['top'])
   left = int(bndbox['left'])
   height = int(bndbox['height'])
   width = int(bndbox['width'])

   left_m = img_width - (left + width)


   return {"top": top,"left": left_m, "height": height ,"width" : width}


# main
for root,dirs, files in os.walk(root_data):
    for file_name in files:
        if file_name.endswith('.json'):
            img_path = join(root,file_name.split('.')[0] +'.jpg')
            img_json = join(root,file_name)
            print("solving " + img_json)
            create_mirror_image(img_path, img_json)
            





