from flask import Flask, flash, request, redirect, url_for, render_template, session, send_from_directory
from werkzeug.utils import secure_filename
from PIL import ImageFilter
from PIL import Image
from google.cloud import storage
import random
import string
import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_UPLOAD = 'static/upload'
STATIC_BLURED = 'static/blured'
UPLOAD_FOLDER = os.path.join(APP_ROOT, STATIC_UPLOAD)
BLURED_FOLDER = os.path.join(APP_ROOT, STATIC_BLURED)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "secretkey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BLURED_FOLDER'] = BLURED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/")
def upload_form():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/blur', methods=['GET'])
def upload_file():
    return render_template('index.html')


@app.route('/blur', methods=['POST'])
def post_blur():
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
        filePath = uploadedFilePath()
        # Resize image and save
        file.save(filePath)
        resize_image(filePath)
        print(filePath)
        # Upload file to GCS bucket_upload_image
        fileUrl = gcsUploadFile(filePath)
        # Delete file from server
        print(fileUrl)
        bluredUrl = blur(filePath)
        print(bluredUrl)
        return render_template('blur.html', fileurl=fileUrl, bluredurl=bluredUrl)


def gcsUploadFile(filepath):
    client = storage.Client.from_service_account_json(
        'ced0f9b8731e.json')
    bucket = client.get_bucket('bucket_blured_image')
    blob = bucket.blob(filepath)
    blob.upload_from_filename(filepath)
    fileURL = blob.public_url
    return fileURL


def blur(filepath):
    client = storage.Client.from_service_account_json(
        'ced0f9b8731e.json')
    # Blur the image using PIL
    image = Image.open(filepath)
    bluredImage = image.filter(ImageFilter.GaussianBlur(15))
    bluredImage.save(filepath)
    # Upload blur image to 'bucket_blured_image'
    blur_bucket = client.get_bucket('bucket_blured_image')
    blur_blob = blur_bucket.blob(filepath)
    blur_blob.upload_from_filename(filepath)
    fileURL = blur_blob.public_url
    # Close and delete temp file
    os.remove(filepath)
    return fileURL


def resize_image(filepath):
    im = Image.open(filepath)
    im.resize((480, 240))
    im.save(filepath)
    im.close()


''' def blur(inputFilePath, outputFilePath):
    im = Image.open(inputFilePath)
    bluredImage = im.filter(ImageFilter.GaussianBlur(15))
    bluredImage.save(outputFilePath) '''


def uploadedFilePath():
    fileName = randomFileName()
    return os.path.join(STATIC_UPLOAD, fileName)


def bluredFilePath():
    fileName = randomFileName()
    return os.path.join(STATIC_BLURED, fileName)


def randomFileName():
    return randomString(7) + ".jpg"


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if __name__ == '__main__':
    app.run(debug=True)
