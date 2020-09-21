from flask import Flask, flash, request, redirect, url_for, render_template, session, send_from_directory
from werkzeug.utils import secure_filename
from PIL import ImageFilter
from PIL import Image
from google.cloud import storage
import random
import string
import os
import datetime
import tempfile

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
        #filePath = uploadedFilePath()
        # Resize image and save
        #file.save(filePath)
        #resize_image(filePath)
        #print(filePath)
        # Upload file to GCS bucket_upload_image
        upload_url, upload_blob = gcsUploadFile()
        print(upload_blob)
        print(upload_url)
        # Delete file from server
        print(upload_url)
        bluredUrl = blur_image(upload_blob)
        print(bluredUrl)
        return render_template('blur.html', fileurl=upload_url, bluredurl=bluredUrl)


def gcsUploadFile():
    uploaded_file = request.files.get('file')

    if not uploaded_file:
        return 'No file uploaded.', 400

    #Tworzenie klienta GCS
    client = storage.Client.from_service_account_json(
        'ced0f9b8731e.json')

    #Pobranie bucket'a 
    bucket = client.get_bucket('bucket_upload_image')

    #Stworzenie obiektu blob i upload pliku
    blob = bucket.blob(uploaded_file.filename)
    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )
    #Tworzenie podpisanego URL z 30 minutowym czasem dostepu
    url_upload_image = blob.generate_signed_url(
        version = "v4",
        expiration = datetime.timedelta(minutes=30),
        method = "GET")
    return url_upload_image, blob

def blur_image(current_blob):
    file_name = current_blob.name
    print(file_name)
    extension = os.path.splitext(file_name)[1]
    print(extension)
    fd, temp_local_filename = tempfile.mkstemp(suffix=extension)
    #Pobranie obrazu z bucket_upload_image
    os.close(fd)

    print(temp_local_filename)
    current_blob.download_to_filename(temp_local_filename)
    image = Image.open(temp_local_filename)
    #Zmniejszenie i rozmywanie obrazu
    image_resized = image.resize(((480, 240)))
    blured_image = image_resized.filter(ImageFilter.GaussianBlur(15))
    image.close()
    blured_image.save(temp_local_filename)
    #Upload obrazu do bucket_blured_image
    client = storage.Client.from_service_account_json(
        'ced0f9b8731e.json')
    blur_bucket = client.get_bucket('bucket_blured_image')
    blur_blob = blur_bucket.blob(file_name)
    blur_blob.upload_from_filename(temp_local_filename)
    #Usuniecie tymczasowgo pliku
    os.remove(temp_local_filename)
    #Utworzenie url_signed 
    url_blured_image = blur_blob.generate_signed_url(
        version = "v4",
        expiration = datetime.timedelta(minutes=30),
        method = "GET")
    return url_blured_image

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
