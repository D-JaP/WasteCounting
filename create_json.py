import json
from os.path import join
import os
import random
from sklearn.model_selection import train_test_split


if __name__ == '__main__':
    # root is the path to your code, which is current directory
    root = './'
    # root_data is where you download the FDST dataset
    root_data = '../data/image/'
    # train_folders = join(root_data,'train_data')
    # test_folders = join(root_data,'test_data')
    output_train_all = join(root,'train_all.json')
    output_train = join(root,'train.json')
    output_val = join(root,'val.json')
    output_test = join(root,'test.json')
    all_img_list=[]
    train_all_img_list=[]
    test_img_list = []

    for root,dirs, files in os.walk(root_data):
        for file_name in files:
            if file_name.endswith('.json'):
                all_img_list.append(join(root,file_name.split('.')[0] +'.jpg'))

    

    all_num = len(all_img_list)
    train_num = int(all_num*0.8)

    # Split the data into training (70%), validation (15%), and test (15%) sets
    train_img_list, temp = train_test_split(all_img_list, test_size=0.2, random_state=42)
    val_img_list,test_img_list = train_test_split(temp, test_size=0.5, random_state=2)


    # with open(output_train_all,'w') as f:
    #     json.dump(train_all_img_list,f)

    with open(output_train,'w') as f:
        json.dump(train_img_list,f)

    with open(output_val,'w') as f:
        json.dump(val_img_list,f)

    with open(output_test,'w') as f:
        json.dump(test_img_list,f)
