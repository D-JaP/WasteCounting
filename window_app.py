from flask import Flask , request, jsonify, url_for
from flask import render_template
from flaskwebgui import FlaskUI # import FlaskUI
from run_program import analyze
from PIL import Image
import os
import uuid
import shutil
app = Flask(__name__)


@app.route("/")
def hello():  
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    # empty old files
    deleteDir('./_internal/static/result')

    # Access form data using the request object
    files = request.files.getlist('image_uploads')
    if files ==None:
        return render_template('index.html', popup_error = 'No selected image')
    temp_name = str(uuid.uuid1())
    temp_folder = os.path.join('./_internal/temp', temp_name)
    temp_output = os.path.join('./_internal/static/result', temp_name)
    print(temp_output)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    if not os.path.exists(temp_output):
        os.makedirs(temp_output)

    json_output = {}
    # save files to temp
    list_file = []
    for file in files:
        filename = file.filename
        file_extension = filename.rsplit('.', 1)[-1].lower()
        
        # Perform additional checks based on file properties
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' in filename and file_extension not in allowed_extensions:
            return render_template('index.html', popup_error='Invalid file type')


        file_path = os.path.join(temp_folder, filename)
        file.save(file_path)
        print(temp_output)
        output_data = analyze(file_path, temp_output)
        list_file.append({filename: output_data})
        os.remove(file_path)
    
    deleteDir(temp_folder)
    json_output["data"] = list_file

    return jsonify(json_output)
        
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


if __name__ == "__main__":
  # If you are debugging you can do that in the browser:
#   app.run()
  # If you want to view the flaskwebgui window:
    FlaskUI(app=app, server="flask", width = 1400, height = 1000).run()

