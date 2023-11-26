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

def lambda_handler(event, context):
    # empty old files
    deleteDir('./static/result')
    
    # Access form data using the request object
    files = event["body"]['images']
    if (files == None) :
        raise RuntimeError("No file uploaded.")
    
    temp_name = str(uuid.uuid1())
    temp_folder = os.path.join('/tmp/input_images', temp_name)
    temp_output = os.path.join('/tmp/result', temp_name)
    print(temp_output)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    if not os.path.exists(temp_output):
        os.makedirs(temp_output)

    json_output = {}
    # save files to temp
    list_file = []
    for file in files:
        filename = file["filename"]
        base64Content = file["content"].split(';base64,')[-1]
        file_extension = filename.rsplit('.', 1)[-1].lower()
        
        # Perform additional checks based on file properties
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        if '.' in filename and file_extension not in allowed_extensions:
            raise RuntimeError("Not support file extension. Skipped.")


        file_path = os.path.join(temp_folder, filename)
        img_b64dec = base64.b64decode(base64Content)
        img_byteIO = BytesIO(img_b64dec)
        image = Image.open(img_byteIO)

        image.save(file_path)
        print(temp_output)
        output_data = analyze(file_path, temp_output)
        list_file.append({filename: output_data})
        os.remove(file_path)
    
    deleteDir(temp_folder)
    json_output["data"] = list_file

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(json_output)
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

