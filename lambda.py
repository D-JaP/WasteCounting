# from flaskwebgui import FlaskUI # import FlaskUI
from run_program import analyze
# from PIL import Image
import os
import uuid
import shutil
import base64
from io import BytesIO
import PIL.Image as Image
import json
import boto3
from datetime import datetime
import logging
import requests

s3bucket = "parkvic-app"
bucketUrl = "https://parkvic-app.s3.ap-southeast-2.amazonaws.com/"
s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    # Access form data using the request object
    # Window suitable - cannot submit to lambda aws more than 6MB
    # body = json.loads(json.dumps(event["body"]))
    
    # files = to_dict(body)["images"]

    # only read public url

    body = json.loads(json.dumps(event["body"]))
    files = to_dict(body)
    print(files)
    file_urls = files["images"]
    

    if (len(file_urls) ==0) :
        raise RuntimeError("No file uploaded.")
    
    json_output = {}
    # save files to temp
    list_file = []
    for file in file_urls:
        temp_name = os.path.basename(os.path.dirname(file))
        print(temp_name)
        temp_folder = os.path.join('/tmp/input_images', temp_name)
        temp_output = os.path.join('/tmp/result', temp_name)

        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        if not os.path.exists(temp_output):
            os.makedirs(temp_output)

        filename = os.path.basename(file)
        foldername = os.path.dirname(file)
        file_extension = filename.rsplit('.', 1)[-1].lower()

        # Perform additional checks based on file properties
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        if '.' in filename and file_extension not in allowed_extensions:
            raise RuntimeError("Not support file extension. Skipped.")

        file_path = os.path.join(temp_folder, filename)
        file_key = file.split(bucketUrl)[-1]
        max_attempt = 30
        current =0
        print("bucket :" + s3bucket + "key:" + file_key + "path:" + file_path)
        while current < max_attempt:
            if s3download(s3bucket,file_key,file_path)== True:
                break
            else: 
                current+=1
                print(f"Error donwloading file {file_key}")
                print("Retrying...")
                if current == 3: 
                    raise RuntimeError("failed to download file")
                continue
        
        # send image to store in s3
        s3UploadPath = f'parkvic/lambda/{temp_name}/'
        output_data = analyze(file_path, temp_output, s3UploadPath)
        list_file.append({filename: output_data})
        os.remove(file_path)
    
    deleteDir(temp_folder)
    json_output["data"] = list_file

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.loads(json.dumps(json_output))
    }
        
def deleteDir(folder):
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    except:
        pass

def s3download(s3bucket,file_key,temp_folder) : 
    print(file_key)
    print(temp_folder)
    try: 
        s3.download_file(s3bucket, file_key, temp_folder)
        print(f"File downloaded successfully to {temp_folder}")
        return True
    except Exception as e:
        print(f"Error downloading file : {e}")
        return False
    

    
def to_dict(obj : object) -> dict:
    """ Serialize Object to Dictionary Recursively

    Arguments:
        obj {object} -- string, list, or dictionary to be serialize

    Returns:
        dict -- Serialized Dictionary
    """

    if isinstance(obj, dict):
        data = {}
        for k, v in obj.items():
            data[k] = to_dict(v)
        return data

    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())

    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]

    elif hasattr(obj, "__dict__"):
        data = {key : to_dict(value) for key, value in obj.__dict__.items() if 
                  not callable(value) and not key.startswith('_')}

    elif isinstance(obj, str):
        try:
            data = {}
            obj = json.loads(obj)
            for k, v in obj.items():
                data[k] = to_dict(v)
                return data
        except:
            return obj
    else:
        return obj
