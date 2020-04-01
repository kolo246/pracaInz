from flask import Flask, flash, request, redirect, url_for, render_template, session, send_from_directory
from werkzeug.utils import secure_filename
from PIL import ImageFilter
from PIL import Image
import os
import glob

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_UPLOAD = 'static/upload'
UPLOAD_FOLDER = os.path.join(APP_ROOT, STATIC_UPLOAD)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "secretkey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/")
def upload_form():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fileurl = os.path.join(STATIC_UPLOAD,filename)
            return render_template('sended_file.html', fileurl=fileurl)
    return render_template('index.html')

@app.route('/blur_image', methods=['GET','POST'])
def blur_image():
    
    if len(os.listdir(STATIC_UPLOAD)) == 0:
        return render_template('index.html')
    path = os.path.join(APP_ROOT,'static/')
    pathInPut = os.path.join(APP_ROOT,'static/upload/')
    filename = os.listdir(os.path.join(APP_ROOT,'static/upload'))
    im = Image.open(pathInPut + str(filename[0]))
    bluredImage = im.filter(ImageFilter.GaussianBlur(15))
    pathToSave = os.path.join(path + 'blur.jpg')
    bluredImage.save(pathToSave)
    return render_template('blur.html')

@app.route('/reset', methods=['GET'])
def reset():

    if len(os.listdir(STATIC_UPLOAD)) == 0:
        return render_template('index.html')

    fileUpload = glob.glob(os.path.join(APP_ROOT,'static/upload/*'))
    for f in fileUpload:
        os.remove(f)
    if len(os.listdir(os.path.join(APP_ROOT,'static'))) == 2:
        os.remove(os.path.join(APP_ROOT,'static/blur.jpg'))
    
    return render_template('index.html')
                                
if __name__ == '__main__':
    app.run(debug=True) 